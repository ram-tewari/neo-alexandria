"""
Rule-Based Classification Service

Keyword-based classification rules for taxonomy prediction.
Provides deterministic classification based on content patterns.

**Validates: Requirement 10.8**
"""

import logging
from typing import Dict, List
from sqlalchemy.orm import Session

from app.database.models import Resource, TaxonomyNode

logger = logging.getLogger(__name__)


class RuleBasedClassifier:
    """Rule-based classifier using keyword matching."""
    
    def __init__(self, db: Session):
        """
        Initialize rule-based classifier.
        
        Args:
            db: Database session
        """
        self.db = db
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Dict]:
        """
        Load classification rules.
        
        Rules map keywords to taxonomy nodes with confidence scores.
        In production, these would be loaded from a configuration file
        or database.
        
        Returns:
            Dictionary mapping node identifiers to rule definitions
        """
        # Define keyword-based rules
        # Format: {node_identifier: {keywords: [...], confidence: float}}
        rules = {
            'machine_learning': {
                'keywords': [
                    'machine learning', 'deep learning', 'neural network',
                    'convolutional', 'cnn', 'rnn', 'lstm', 'transformer',
                    'attention mechanism', 'bert', 'gpt', 'reinforcement learning'
                ],
                'confidence': 0.85,
                'node_name': 'Machine Learning'
            },
            'quantum_physics': {
                'keywords': [
                    'quantum', 'entanglement', 'photonic', 'qubit',
                    'bell inequality', 'quantum computing', 'quantum mechanics',
                    'superposition', 'quantum state'
                ],
                'confidence': 0.85,
                'node_name': 'Quantum Physics'
            },
            'computational_biology': {
                'keywords': [
                    'computational biology', 'bioinformatics', 'genomics',
                    'protein folding', 'molecular dynamics', 'systems biology',
                    'biological modeling', 'gene expression'
                ],
                'confidence': 0.80,
                'node_name': 'Computational Biology'
            },
            'computer_vision': {
                'keywords': [
                    'computer vision', 'image recognition', 'object detection',
                    'image segmentation', 'face recognition', 'visual recognition',
                    'image classification', 'semantic segmentation'
                ],
                'confidence': 0.85,
                'node_name': 'Computer Vision'
            },
            'natural_language_processing': {
                'keywords': [
                    'natural language processing', 'nlp', 'text mining',
                    'sentiment analysis', 'named entity recognition', 'ner',
                    'language model', 'text classification', 'machine translation'
                ],
                'confidence': 0.85,
                'node_name': 'Natural Language Processing'
            },
            'astrophysics': {
                'keywords': [
                    'astrophysics', 'cosmology', 'galaxy', 'star formation',
                    'black hole', 'dark matter', 'dark energy', 'gravitational waves'
                ],
                'confidence': 0.80,
                'node_name': 'Astrophysics'
            },
            'materials_science': {
                'keywords': [
                    'materials science', 'nanomaterials', 'polymer',
                    'crystallography', 'metallurgy', 'semiconductor',
                    'material properties', 'composite materials'
                ],
                'confidence': 0.80,
                'node_name': 'Materials Science'
            }
        }
        
        return rules
    
    def classify(
        self,
        resource_id: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Apply rule-based classification to a resource.
        
        Args:
            resource_id: ID of the resource to classify
            top_k: Maximum number of predictions to return
            
        Returns:
            List of predictions with node_id, node_name, confidence
            
        Raises:
            ValueError: If resource not found
            
        **Validates: Requirement 10.8**
        """
        # Fetch resource
        resource = self.db.query(Resource).filter_by(id=resource_id).first()
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")
        
        # Extract text content
        content = self._extract_content(resource)
        content_lower = content.lower()
        
        # Apply rules
        predictions = []
        
        for rule_id, rule in self.rules.items():
            score = self._compute_rule_score(content_lower, rule['keywords'])
            
            if score > 0:
                # Find matching taxonomy node
                node = self._find_node_by_name(rule['node_name'])
                
                if node:
                    # Adjust confidence based on keyword match strength
                    confidence = rule['confidence'] * score
                    
                    predictions.append({
                        'node_id': str(node.id),
                        'node_name': node.name,
                        'confidence': round(confidence, 4),
                        'rule_id': rule_id,
                        'matched_keywords': self._get_matched_keywords(
                            content_lower,
                            rule['keywords']
                        )
                    })
        
        # Sort by confidence descending
        predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Return top K
        return predictions[:top_k]
    
    def _extract_content(self, resource: Resource) -> str:
        """
        Extract text content from resource for classification.
        
        Args:
            resource: Resource object
            
        Returns:
            Combined text content
        """
        parts = []
        
        if resource.title:
            parts.append(resource.title)
        
        if resource.description:
            parts.append(resource.description)
        
        # Check if abstract field exists
        if hasattr(resource, 'abstract') and resource.abstract:
            parts.append(resource.abstract)
        
        # Could also include content, but that might be too long
        # For rule-based classification, title + description is usually sufficient
        
        return ' '.join(parts)
    
    def _compute_rule_score(
        self,
        content: str,
        keywords: List[str]
    ) -> float:
        """
        Compute rule match score based on keyword presence.
        
        Args:
            content: Text content (lowercase)
            keywords: List of keywords to match
            
        Returns:
            Score between 0 and 1
        """
        if not keywords:
            return 0.0
        
        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword in content)
        
        # Normalize by total keywords
        score = matches / len(keywords)
        
        return score
    
    def _get_matched_keywords(
        self,
        content: str,
        keywords: List[str]
    ) -> List[str]:
        """
        Get list of keywords that matched in the content.
        
        Args:
            content: Text content (lowercase)
            keywords: List of keywords to check
            
        Returns:
            List of matched keywords
        """
        matched = [kw for kw in keywords if kw in content]
        return matched
    
    def _find_node_by_name(self, node_name: str) -> TaxonomyNode:
        """
        Find taxonomy node by name.
        
        Args:
            node_name: Name of the node to find
            
        Returns:
            TaxonomyNode object or None
        """
        node = self.db.query(TaxonomyNode).filter(
            TaxonomyNode.name == node_name
        ).first()
        
        return node
    
    def add_rule(
        self,
        rule_id: str,
        node_name: str,
        keywords: List[str],
        confidence: float = 0.8
    ) -> None:
        """
        Add a new classification rule.
        
        Args:
            rule_id: Unique identifier for the rule
            node_name: Name of the taxonomy node
            keywords: List of keywords to match
            confidence: Base confidence score for this rule
        """
        self.rules[rule_id] = {
            'keywords': keywords,
            'confidence': confidence,
            'node_name': node_name
        }
        
        logger.info(f"Added rule '{rule_id}' for node '{node_name}'")
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove a classification rule.
        
        Args:
            rule_id: Identifier of the rule to remove
            
        Returns:
            True if rule was removed, False if not found
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed rule '{rule_id}'")
            return True
        
        return False
    
    def get_rules(self) -> Dict[str, Dict]:
        """
        Get all classification rules.
        
        Returns:
            Dictionary of all rules
        """
        return self.rules.copy()
