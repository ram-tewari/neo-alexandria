"""
Classification Coordination Service

Coordinates ML-based and rule-based classification methods.
Merges predictions, resolves conflicts, and applies final classification.

**Validates: Requirements 10.1-10.5**
"""

import logging
from typing import Dict, List, Optional
from collections import defaultdict
from sqlalchemy.orm import Session

from app.database.models import Resource, TaxonomyNode, ResourceTaxonomy
from app.shared.event_bus import event_bus
from app.modules.taxonomy.ml_service import MLClassificationService
from app.modules.taxonomy.rule_based import RuleBasedClassifier

logger = logging.getLogger(__name__)


class ClassificationService:
    """Service for coordinating resource classification."""
    
    def __init__(self, db: Session):
        """
        Initialize classification service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.ml_service = MLClassificationService(db)
        self.rule_based = RuleBasedClassifier(db)
    
    def classify_resource(
        self,
        resource_id: str,
        use_ml: bool = True,
        use_rules: bool = True,
        apply_to_resource: bool = True
    ) -> Dict:
        """
        Classify resource using multiple methods and merge predictions.
        
        Args:
            resource_id: ID of the resource to classify
            use_ml: Whether to use ML-based classification
            use_rules: Whether to use rule-based classification
            apply_to_resource: Whether to apply classification to resource
            
        Returns:
            Dictionary with classification results
            
        Raises:
            ValueError: If resource not found
            
        **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**
        """
        # Verify resource exists
        resource = self.db.query(Resource).filter_by(id=resource_id).first()
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")
        
        predictions = []
        
        # ML-based classification
        if use_ml:
            try:
                ml_predictions = self.ml_service.predict(resource_id, top_k=5)
                for pred in ml_predictions:
                    pred['method'] = 'ml'
                predictions.extend(ml_predictions)
                logger.info(f"ML classification: {len(ml_predictions)} predictions")
            except Exception as e:
                logger.warning(f"ML classification failed: {e}")
        
        # Rule-based classification
        if use_rules:
            try:
                rule_predictions = self.rule_based.classify(resource_id, top_k=5)
                for pred in rule_predictions:
                    pred['method'] = 'rule'
                predictions.extend(rule_predictions)
                logger.info(f"Rule-based classification: {len(rule_predictions)} predictions")
            except Exception as e:
                logger.warning(f"Rule-based classification failed: {e}")
        
        if not predictions:
            logger.warning(f"No predictions generated for resource {resource_id}")
            return {
                'resource_id': resource_id,
                'primary': None,
                'alternatives': [],
                'all_predictions': [],
                'error': 'No predictions generated'
            }
        
        # Merge and resolve conflicts
        final_classification = self._merge_predictions(predictions)
        final_classification['resource_id'] = resource_id
        
        # Apply to resource if requested
        if apply_to_resource and final_classification['primary']:
            self._apply_classification(resource_id, final_classification)
            
            # Emit event
            event_bus.emit("resource.classified", {
                "resource_id": resource_id,
                "node_id": final_classification['primary']['node_id'],
                "confidence": final_classification['primary']['confidence'],
                "methods": final_classification['primary']['methods']
            })
        
        return final_classification
    
    def _merge_predictions(
        self,
        predictions: List[Dict]
    ) -> Dict:
        """
        Merge predictions from multiple methods and resolve conflicts.
        
        When multiple methods predict the same node, their confidences
        are averaged and boosted. Conflicts are resolved by confidence.
        
        Args:
            predictions: List of prediction dictionaries
            
        Returns:
            Dictionary with merged predictions
            
        **Validates: Requirements 10.2, 10.3**
        """
        # Group predictions by node_id
        node_scores = defaultdict(list)
        
        for pred in predictions:
            node_scores[pred['node_id']].append({
                'confidence': pred['confidence'],
                'method': pred['method']
            })
        
        # Compute final scores
        final_predictions = []
        
        for node_id, scores in node_scores.items():
            # Average confidence across methods
            avg_confidence = sum(s['confidence'] for s in scores) / len(scores)
            
            # Boost if multiple methods agree (consensus bonus)
            if len(scores) > 1:
                # 20% boost for consensus, capped at 1.0
                avg_confidence *= 1.2
                avg_confidence = min(avg_confidence, 1.0)
            
            # Get node details
            node = self.db.query(TaxonomyNode).filter_by(id=node_id).first()
            
            final_predictions.append({
                'node_id': node_id,
                'node_name': node.name if node else 'Unknown',
                'confidence': round(avg_confidence, 4),
                'methods': list(set(s['method'] for s in scores)),
                'method_count': len(scores)
            })
        
        # Sort by confidence descending
        final_predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'primary': final_predictions[0] if final_predictions else None,
            'alternatives': final_predictions[1:5] if len(final_predictions) > 1 else [],
            'all_predictions': final_predictions
        }
    
    def _apply_classification(
        self,
        resource_id: str,
        classification: Dict
    ) -> None:
        """
        Apply classification to resource in database.
        
        Updates the resource with the primary classification and creates
        a ResourceTaxonomy record.
        
        Args:
            resource_id: ID of the resource
            classification: Classification result dictionary
            
        **Validates: Requirement 10.4**
        """
        resource = self.db.query(Resource).filter_by(id=resource_id).first()
        
        if not resource or not classification['primary']:
            return
        
        primary = classification['primary']
        
        # Update resource fields (handle missing fields gracefully)
        if hasattr(resource, 'taxonomy_node_id'):
            resource.taxonomy_node_id = primary['node_id']
        if hasattr(resource, 'classification_confidence'):
            resource.classification_confidence = primary['confidence']
        if hasattr(resource, 'classification_method'):
            resource.classification_method = ','.join(primary['methods'])
        
        # Create or update ResourceTaxonomy record
        resource_taxonomy = self.db.query(ResourceTaxonomy).filter_by(
            resource_id=resource_id
        ).first()
        
        if resource_taxonomy:
            # Update existing
            resource_taxonomy.taxonomy_node_id = primary['node_id']
            resource_taxonomy.confidence = primary['confidence']
        else:
            # Create new
            resource_taxonomy = ResourceTaxonomy(
                resource_id=resource_id,
                taxonomy_node_id=primary['node_id'],
                confidence=primary['confidence']
            )
            self.db.add(resource_taxonomy)
        
        self.db.commit()
        
        logger.info(
            f"Applied classification to resource {resource_id}: "
            f"{primary['node_name']} (confidence: {primary['confidence']})"
        )
    
    def batch_classify(
        self,
        resource_ids: List[str],
        use_ml: bool = True,
        use_rules: bool = True
    ) -> Dict[str, Dict]:
        """
        Classify multiple resources in batch.
        
        Args:
            resource_ids: List of resource IDs to classify
            use_ml: Whether to use ML-based classification
            use_rules: Whether to use rule-based classification
            
        Returns:
            Dictionary mapping resource IDs to classification results
        """
        results = {}
        
        for resource_id in resource_ids:
            try:
                result = self.classify_resource(
                    resource_id,
                    use_ml=use_ml,
                    use_rules=use_rules,
                    apply_to_resource=True
                )
                results[resource_id] = result
            except Exception as e:
                logger.error(f"Failed to classify resource {resource_id}: {e}")
                results[resource_id] = {
                    'error': str(e)
                }
        
        return results
    
    def get_classification(self, resource_id: str) -> Optional[Dict]:
        """
        Get existing classification for a resource.
        
        Args:
            resource_id: ID of the resource
            
        Returns:
            Classification dictionary or None
        """
        resource = self.db.query(Resource).filter_by(id=resource_id).first()
        
        if not resource or not resource.taxonomy_node_id:
            return None
        
        node = self.db.query(TaxonomyNode).filter_by(
            id=resource.taxonomy_node_id
        ).first()
        
        return {
            'resource_id': resource_id,
            'node_id': str(resource.taxonomy_node_id),
            'node_name': node.name if node else 'Unknown',
            'confidence': resource.classification_confidence,
            'method': resource.classification_method
        }
    
    def reclassify_uncertain(
        self,
        threshold: float = 0.5,
        limit: int = 100
    ) -> Dict:
        """
        Reclassify resources with uncertain classifications.
        
        Args:
            threshold: Confidence threshold below which to reclassify
            limit: Maximum number of resources to reclassify
            
        Returns:
            Dictionary with reclassification results
        """
        # Get uncertain resources
        uncertain_ids = self.ml_service.identify_uncertain_predictions(
            threshold=threshold,
            limit=limit
        )
        
        logger.info(f"Reclassifying {len(uncertain_ids)} uncertain resources")
        
        # Reclassify
        results = self.batch_classify(uncertain_ids)
        
        return {
            'total': len(uncertain_ids),
            'results': results
        }
