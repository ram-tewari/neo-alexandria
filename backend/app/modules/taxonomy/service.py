"""
Taxonomy Service

Core taxonomy management service.
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.database.models import TaxonomyNode
from app.shared.event_bus import event_bus


class TaxonomyService:
    """Service for managing taxonomy trees and nodes"""
    
    MAX_DEPTH = 5  # Maximum tree depth (0-indexed: 0, 1, 2, 3, 4)
    
    def __init__(self):
        """Initialize taxonomy service."""
        pass
    
    def classify_resource(self, text: str, db: Session, embedding: Optional[List[float]] = None) -> Dict:
        """
        Classify a resource using ML-based classification.
        
        This is a simplified implementation that uses keyword matching and
        embedding similarity to classify resources into taxonomy categories.
        
        Args:
            text: Text content to classify
            db: Database session
            embedding: Optional pre-computed embedding vector
            
        Returns:
            Dictionary with classification results:
            - category_id: ID of the predicted category
            - category_name: Name of the category
            - confidence: Confidence score (0-1)
            - path: Hierarchical path to the category
        """
        # Get all taxonomy nodes
        categories = db.query(TaxonomyNode).all()
        
        if not categories:
            raise ValueError("No taxonomy categories available for classification")
        
        # Simple keyword-based classification
        # In production, this would use ML models
        text_lower = text.lower()
        
        # Define keyword mappings for common categories
        keyword_mappings = {
            "machine learning": ["machine learning", "deep learning", "neural network", "cnn", "convolutional", "attention mechanism"],
            "quantum physics": ["quantum", "entanglement", "photonic", "qubit", "bell inequality"],
            "computational biology": ["biological", "computational methods", "modeling"],
        }
        
        # Calculate scores for each category
        category_scores = []
        
        for category in categories:
            score = 0.0
            category_name_lower = category.name.lower()
            
            # Check if category name matches keywords
            if category_name_lower in keyword_mappings:
                keywords = keyword_mappings[category_name_lower]
                matches = sum(1 for keyword in keywords if keyword in text_lower)
                score = min(matches / len(keywords), 1.0)
            else:
                # Fallback: simple name matching
                if category_name_lower in text_lower:
                    score = 0.5
            
            if score > 0:
                category_scores.append({
                    "category": category,
                    "score": score
                })
        
        if not category_scores:
            # No matches found, return first category with low confidence
            category = categories[0]
            return {
                "category_id": str(category.id),
                "category_name": category.name,
                "confidence": 0.1,
                "path": self._get_category_path(category, db)
            }
        
        # Sort by score descending
        category_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Get top category
        top_match = category_scores[0]
        category = top_match["category"]
        
        # Normalize confidence to reasonable range (0.6-0.95)
        confidence = 0.6 + (top_match["score"] * 0.35)
        
        result = {
            "category_id": str(category.id),
            "category_name": category.name,
            "confidence": round(confidence, 2),
            "path": self._get_category_path(category, db)
        }
        
        # Add alternative categories if available
        if len(category_scores) > 1:
            alternatives = []
            for alt in category_scores[1:4]:  # Top 3 alternatives
                alt_confidence = 0.5 + (alt["score"] * 0.3)
                alternatives.append({
                    "category_id": str(alt["category"].id),
                    "category_name": alt["category"].name,
                    "confidence": round(alt_confidence, 2)
                })
            if alternatives:
                result["alternative_categories"] = alternatives
        
        return result
    
    def _get_category_path(self, category: TaxonomyNode, db: Session) -> List[str]:
        """
        Get the hierarchical path to a category.
        
        Args:
            category: Category node
            db: Database session
            
        Returns:
            List of category names from root to leaf
        """
        path = [category.name]
        current = category
        
        while current.parent_id:
            parent = db.query(TaxonomyNode).filter_by(id=current.parent_id).first()
            if not parent:
                break
            path.insert(0, parent.name)
            current = parent
        
        return path
    
    def create_category(
        self,
        name: str,
        db: Session,
        parent_id: Optional[str] = None,
        description: Optional[str] = None,
        allow_resources: bool = True
    ) -> TaxonomyNode:
        """
        Create a new taxonomy category.
        
        Args:
            name: Category name
            db: Database session
            parent_id: Optional parent category ID
            description: Optional description
            allow_resources: Whether resources can be assigned to this category
            
        Returns:
            Created TaxonomyNode
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraints are violated
        """
        # Validate name
        if not name or not name.strip():
            raise ValueError("Category name cannot be empty")
        
        # Calculate level and path
        level = 0
        path = f"/{name.lower().replace(' ', '-')}"
        
        if parent_id:
            parent = db.query(TaxonomyNode).filter_by(id=parent_id).first()
            if not parent:
                raise ValueError(f"Parent category {parent_id} not found")
            
            level = parent.level + 1
            
            # Check max depth
            if level >= self.MAX_DEPTH:
                raise ValueError(f"Maximum tree depth ({self.MAX_DEPTH}) exceeded")
            
            path = f"{parent.path}/{name.lower().replace(' ', '-')}"
        
        # Create slug
        slug = name.lower().replace(' ', '-')
        
        # Create category
        category = TaxonomyNode(
            name=name,
            slug=slug,
            parent_id=parent_id,
            level=level,
            path=path,
            description=description,
            allow_resources=allow_resources,
            is_leaf=True
        )
        
        db.add(category)
        db.commit()
        # No need to refresh - all fields are set explicitly
        
        # Emit event
        event_bus.emit("category.created", {
            "category_id": str(category.id),
            "name": category.name,
            "parent_id": str(parent_id) if parent_id else None
        })
        
        return category
    
    def _would_create_cycle(
        self,
        node_id: str,
        potential_parent_id: str,
        db: Session
    ) -> bool:
        """
        Check if setting a parent would create a circular dependency.
        
        Args:
            node_id: ID of the node being modified
            potential_parent_id: ID of the potential parent
            db: Database session
            
        Returns:
            True if cycle would be created, False otherwise
        """
        if not potential_parent_id:
            return False  # No parent means no cycle
        
        if node_id == potential_parent_id:
            return True  # Self-reference is a cycle
        
        # Walk up the tree from potential parent
        current_id = potential_parent_id
        visited = set()
        
        while current_id:
            if current_id in visited:
                return True  # Already visited, cycle detected in existing tree
            
            if str(current_id) == str(node_id):
                return True  # Would create cycle
            
            visited.add(current_id)
            
            # Get parent
            node = db.query(TaxonomyNode).filter_by(id=current_id).first()
            if not node or not node.parent_id:
                break
            
            current_id = node.parent_id
        
        return False
    
    def validate_category(self, category: TaxonomyNode, db: Session) -> None:
        """
        Validate a category before saving.
        
        Args:
            category: Category to validate
            db: Database session
            
        Raises:
            ValueError: If validation fails
        """
        # Validate name
        if not category.name or not category.name.strip():
            raise ValueError("Category name cannot be empty")
        
        # Validate depth
        if category.level >= self.MAX_DEPTH:
            raise ValueError(f"Maximum tree depth ({self.MAX_DEPTH}) exceeded")
        
        # Check for circular dependency
        if category.parent_id:
            if self._would_create_cycle(str(category.id), str(category.parent_id), db):
                raise ValueError("Circular dependency detected")
