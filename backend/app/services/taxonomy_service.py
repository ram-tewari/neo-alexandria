"""
Neo Alexandria 2.0 - Taxonomy Service (Phase 8.5)

This module handles hierarchical taxonomy management and resource classification operations.
It provides CRUD operations for taxonomy nodes, hierarchical queries using materialized paths,
and resource classification assignment with confidence scores.

Related files:
- app/database/models.py: TaxonomyNode and ResourceTaxonomy models
- app/routers/taxonomy.py: Taxonomy API endpoints
- app/schemas/taxonomy.py: Pydantic schemas for API validation
- app/services/ml_classification_service.py: ML classification integration

Features:
- Taxonomy node CRUD with parent-child relationships
- Materialized path pattern for efficient hierarchical queries
- Circular reference prevention
- Resource classification with confidence scores
- Cached resource counts (direct and descendant)
"""

from __future__ import annotations

import uuid
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, delete, or_

from backend.app.database.models import TaxonomyNode, ResourceTaxonomy, Resource
from backend.app.database.base import Base


class TaxonomyService:
    """
    Handles taxonomy management and resource classification operations.
    
    This service provides methods for creating, reading, updating, and deleting taxonomy nodes,
    managing hierarchical relationships, querying ancestors and descendants, and assigning
    classifications to resources with confidence scores.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the taxonomy service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        
        # Ensure tables exist (safety check)
        try:
            Base.metadata.create_all(bind=db.get_bind())
        except Exception:
            pass

    # Helper methods
    
    def _slugify(self, text: str) -> str:
        """
        Convert text to URL-friendly slug.
        
        Algorithm:
        1. Convert to lowercase
        2. Replace spaces and special characters with hyphens
        3. Remove consecutive hyphens
        4. Strip leading/trailing hyphens
        
        Args:
            text: Input text to slugify
            
        Returns:
            URL-friendly slug string
        """
        # Convert to lowercase
        slug = text.lower()
        # Replace spaces and special characters with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        # Remove consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        # Strip leading/trailing hyphens
        slug = slug.strip('-')
        return slug
    
    def _compute_path(self, parent_id: Optional[uuid.UUID], slug: str) -> str:
        """
        Compute materialized path for a node.
        
        Algorithm:
        1. If no parent, return "/slug"
        2. Query parent node
        3. Return parent.path + "/slug"
        
        Args:
            parent_id: Parent node UUID (None for root nodes)
            slug: Node slug
            
        Returns:
            Materialized path string (e.g., "/parent/child")
            
        Raises:
            ValueError: If parent_id provided but parent not found
        """
        if parent_id is None:
            return f"/{slug}"
        
        # Query parent
        parent = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == parent_id).first()
        if not parent:
            raise ValueError(f"Parent node with id {parent_id} not found")
        
        return f"{parent.path}/{slug}"
    
    def _is_descendant(self, node_id: uuid.UUID, potential_ancestor_id: uuid.UUID) -> bool:
        """
        Check if a node is a descendant of another node.
        
        Algorithm:
        1. Query the node
        2. Query the potential ancestor
        3. Check if node.path starts with potential_ancestor.path + "/"
        
        Args:
            node_id: Node to check
            potential_ancestor_id: Potential ancestor node
            
        Returns:
            True if node is a descendant of potential_ancestor, False otherwise
        """
        node = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
        ancestor = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == potential_ancestor_id).first()
        
        if not node or not ancestor:
            return False
        
        # Check if node's path starts with ancestor's path followed by "/"
        return node.path.startswith(f"{ancestor.path}/")
    
    def _update_descendants(self, node: TaxonomyNode, old_path: str) -> None:
        """
        Update level and path for all descendants after a node move.
        
        Algorithm:
        1. Query all descendants using old_path pattern
        2. For each descendant:
           - Compute new path by replacing old_path prefix with node.path
           - Compute new level based on path depth (count('/') - 1, since root is "/slug" with level 0)
           - Update descendant
        3. Commit changes
        
        Args:
            node: Node that was moved
            old_path: Previous path of the node
        """
        # Query descendants using old path pattern
        descendants = self.db.query(TaxonomyNode).filter(
            TaxonomyNode.path.like(f"{old_path}/%")
        ).all()
        
        for descendant in descendants:
            # Replace old path prefix with new path
            new_path = descendant.path.replace(old_path, node.path, 1)
            descendant.path = new_path
            # Compute new level from path depth (root path "/slug" has 1 slash and level 0)
            descendant.level = new_path.count('/') - 1
        
        self.db.commit()

    # Core CRUD operations
    
    def create_node(
        self,
        name: str,
        parent_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        allow_resources: bool = True
    ) -> TaxonomyNode:
        """
        Create a new taxonomy node with parent validation and path computation.
        
        Algorithm:
        1. Validate name is not empty
        2. Generate slug from name
        3. Check slug uniqueness
        4. If parent_id provided:
           - Validate parent exists
           - Compute level as parent.level + 1
           - Update parent.is_leaf to False
        5. Else:
           - Set level to 0
        6. Compute materialized path
        7. Create TaxonomyNode instance
        8. Commit and return
        
        Args:
            name: Node name (required)
            parent_id: Parent node UUID (None for root nodes)
            description: Optional node description
            keywords: Optional list of keywords
            allow_resources: Whether resources can be assigned to this node
            
        Returns:
            Created TaxonomyNode object
            
        Raises:
            ValueError: If validation fails (empty name, duplicate slug, parent not found)
        """
        # Validate name
        if not name or not name.strip():
            raise ValueError("Node name cannot be empty")
        
        # Generate slug
        slug = self._slugify(name)
        if not slug:
            raise ValueError("Node name must contain at least one alphanumeric character")
        
        # Check slug uniqueness
        existing = self.db.query(TaxonomyNode).filter(TaxonomyNode.slug == slug).first()
        if existing:
            raise ValueError(f"A node with slug '{slug}' already exists")
        
        # Determine level and update parent
        level = 0
        if parent_id:
            parent = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == parent_id).first()
            if not parent:
                raise ValueError(f"Parent node with id {parent_id} not found")
            
            level = parent.level + 1
            # Update parent is_leaf flag
            parent.is_leaf = False
        
        # Compute path
        path = self._compute_path(parent_id, slug)
        
        # Create node
        node = TaxonomyNode(
            id=uuid.uuid4(),
            name=name,
            slug=slug,
            parent_id=parent_id,
            level=level,
            path=path,
            description=description,
            keywords=keywords or [],
            resource_count=0,
            descendant_resource_count=0,
            is_leaf=True,
            allow_resources=allow_resources,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        
        return node

    def update_node(
        self,
        node_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        allow_resources: Optional[bool] = None
    ) -> TaxonomyNode:
        """
        Update taxonomy node metadata.
        
        Algorithm:
        1. Query node by id
        2. If name changed:
           - Generate new slug
           - Check slug uniqueness
           - Recalculate path for node and descendants
        3. Update other fields if provided
        4. Update updated_at timestamp
        5. Commit and return
        
        Args:
            node_id: Node UUID to update
            name: New name (triggers slug and path recalculation)
            description: New description
            keywords: New keywords list
            allow_resources: New allow_resources flag
            
        Returns:
            Updated TaxonomyNode object
            
        Raises:
            ValueError: If node not found or slug conflict
        """
        # Query node
        node = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
        if not node:
            raise ValueError(f"Node with id {node_id} not found")
        
        # Handle name change
        if name and name != node.name:
            # Generate new slug
            new_slug = self._slugify(name)
            if not new_slug:
                raise ValueError("Node name must contain at least one alphanumeric character")
            
            # Check slug uniqueness
            existing = self.db.query(TaxonomyNode).filter(
                TaxonomyNode.slug == new_slug,
                TaxonomyNode.id != node_id
            ).first()
            if existing:
                raise ValueError(f"A node with slug '{new_slug}' already exists")
            
            # Store old path for descendant updates
            old_path = node.path
            
            # Update name and slug
            node.name = name
            node.slug = new_slug
            
            # Recalculate path
            node.path = self._compute_path(node.parent_id, new_slug)
            
            # Update descendants if path changed
            if old_path != node.path:
                self._update_descendants(node, old_path)
        
        # Update other fields
        if description is not None:
            node.description = description
        if keywords is not None:
            node.keywords = keywords
        if allow_resources is not None:
            node.allow_resources = allow_resources
        
        # Update timestamp
        node.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(node)
        
        return node
    
    def delete_node(
        self,
        node_id: uuid.UUID,
        cascade: bool = False
    ) -> Dict[str, Any]:
        """
        Delete taxonomy node with cascade or reparenting options.
        
        Algorithm:
        1. Query node by id
        2. Check if node has assigned resources
           - If yes, raise error (must unassign first)
        3. If cascade=True:
           - Delete all descendants recursively
           - Delete all resource classifications for descendants
        4. Else:
           - Reparent children to node's parent
           - Update children's level and path
        5. Update parent's is_leaf flag if needed
        6. Delete node
        7. Return deletion summary
        
        Args:
            node_id: Node UUID to delete
            cascade: If True, delete descendants; if False, reparent children
            
        Returns:
            Dictionary with deletion summary (deleted_count, reparented_count)
            
        Raises:
            ValueError: If node not found or has assigned resources
        """
        # Query node
        node = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
        if not node:
            raise ValueError(f"Node with id {node_id} not found")
        
        # Check for assigned resources
        resource_count = self.db.query(ResourceTaxonomy).filter(
            ResourceTaxonomy.taxonomy_node_id == node_id
        ).count()
        if resource_count > 0:
            raise ValueError(
                f"Cannot delete node with {resource_count} assigned resources. "
                "Please unassign resources first."
            )
        
        deleted_count = 1
        reparented_count = 0
        
        if cascade:
            # Get all descendants
            descendants = self.db.query(TaxonomyNode).filter(
                TaxonomyNode.path.like(f"{node.path}/%")
            ).all()
            
            # Delete resource classifications for descendants
            descendant_ids = [d.id for d in descendants] + [node_id]
            self.db.query(ResourceTaxonomy).filter(
                ResourceTaxonomy.taxonomy_node_id.in_(descendant_ids)
            ).delete(synchronize_session=False)
            
            # Delete descendants
            for descendant in descendants:
                self.db.delete(descendant)
            
            deleted_count += len(descendants)
        else:
            # Reparent children to node's parent
            children = self.db.query(TaxonomyNode).filter(
                TaxonomyNode.parent_id == node_id
            ).all()
            
            for child in children:
                old_path = child.path
                child.parent_id = node.parent_id
                
                # Update level
                if node.parent_id:
                    parent = self.db.query(TaxonomyNode).filter(
                        TaxonomyNode.id == node.parent_id
                    ).first()
                    child.level = parent.level + 1
                else:
                    child.level = 0
                
                # Update path
                child.path = self._compute_path(child.parent_id, child.slug)
                
                # Update descendants
                self._update_descendants(child, old_path)
                
                reparented_count += 1
        
        # Update parent's is_leaf flag if needed
        if node.parent_id:
            parent = self.db.query(TaxonomyNode).filter(
                TaxonomyNode.id == node.parent_id
            ).first()
            if parent:
                # Check if parent has other children
                sibling_count = self.db.query(TaxonomyNode).filter(
                    TaxonomyNode.parent_id == node.parent_id,
                    TaxonomyNode.id != node_id
                ).count()
                parent.is_leaf = (sibling_count == 0)
        
        # Delete node
        self.db.delete(node)
        self.db.commit()
        
        return {
            "deleted_count": deleted_count,
            "reparented_count": reparented_count
        }
    
    def move_node(
        self,
        node_id: uuid.UUID,
        new_parent_id: Optional[uuid.UUID]
    ) -> TaxonomyNode:
        """
        Move taxonomy node to a new parent (reparenting).
        
        Algorithm:
        1. Query node by id
        2. If new_parent_id is same as current, return node unchanged
        3. If new_parent_id provided:
           - Validate new parent exists
           - Prevent circular reference (node cannot be moved to its own descendant)
        4. Store old path
        5. Update old parent's is_leaf flag
        6. Update node's parent_id, level, and path
        7. Update new parent's is_leaf flag
        8. Update all descendants' level and path
        9. Commit and return
        
        Args:
            node_id: Node UUID to move
            new_parent_id: New parent UUID (None for root level)
            
        Returns:
            Updated TaxonomyNode object
            
        Raises:
            ValueError: If node not found, parent not found, or circular reference detected
        """
        # Query node
        node = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
        if not node:
            raise ValueError(f"Node with id {node_id} not found")
        
        # Check if already at target parent
        if node.parent_id == new_parent_id:
            return node
        
        # Validate new parent and prevent circular references
        if new_parent_id:
            new_parent = self.db.query(TaxonomyNode).filter(
                TaxonomyNode.id == new_parent_id
            ).first()
            if not new_parent:
                raise ValueError(f"New parent node with id {new_parent_id} not found")
            
            # Prevent moving to own descendant
            if new_parent_id == node_id or self._is_descendant(new_parent_id, node_id):
                raise ValueError("Cannot move node to its own descendant (circular reference)")
        
        # Store old path and parent
        old_path = node.path
        old_parent_id = node.parent_id
        
        # Update old parent's is_leaf flag
        if old_parent_id:
            old_parent = self.db.query(TaxonomyNode).filter(
                TaxonomyNode.id == old_parent_id
            ).first()
            if old_parent:
                # Check if old parent has other children
                sibling_count = self.db.query(TaxonomyNode).filter(
                    TaxonomyNode.parent_id == old_parent_id,
                    TaxonomyNode.id != node_id
                ).count()
                old_parent.is_leaf = (sibling_count == 0)
        
        # Update node
        node.parent_id = new_parent_id
        
        # Update level
        if new_parent_id:
            new_parent = self.db.query(TaxonomyNode).filter(
                TaxonomyNode.id == new_parent_id
            ).first()
            node.level = new_parent.level + 1
            # Update new parent's is_leaf flag
            new_parent.is_leaf = False
        else:
            node.level = 0
        
        # Update path
        node.path = self._compute_path(new_parent_id, node.slug)
        
        # Update timestamp
        node.updated_at = datetime.now(timezone.utc)
        
        # Update descendants
        self._update_descendants(node, old_path)
        
        self.db.commit()
        self.db.refresh(node)
        
        return node

    # Hierarchical queries
    
    def get_tree(
        self,
        root_id: Optional[uuid.UUID] = None,
        max_depth: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve nested taxonomy tree structure.
        
        Algorithm:
        1. If root_id provided, query subtree starting from root
        2. Else, query all root nodes (level=0)
        3. For each node, recursively build children
        4. Respect max_depth limit if provided
        5. Return nested structure
        
        Args:
            root_id: Optional root node UUID for subtree (None for full tree)
            max_depth: Optional maximum depth to retrieve
            
        Returns:
            List of nested dictionaries representing tree structure
            
        Raises:
            ValueError: If root_id provided but node not found
        """
        if root_id:
            # Query specific subtree
            root = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == root_id).first()
            if not root:
                raise ValueError(f"Root node with id {root_id} not found")
            
            # Query all descendants
            if max_depth is not None:
                max_level = root.level + max_depth
                nodes = self.db.query(TaxonomyNode).filter(
                    or_(
                        TaxonomyNode.id == root_id,
                        TaxonomyNode.path.like(f"{root.path}/%")
                    ),
                    TaxonomyNode.level <= max_level
                ).all()
            else:
                nodes = self.db.query(TaxonomyNode).filter(
                    or_(
                        TaxonomyNode.id == root_id,
                        TaxonomyNode.path.like(f"{root.path}/%")
                    )
                ).all()
            
            # Build tree starting from root
            return [self._build_tree_node(root, nodes, max_depth)]
        else:
            # Query all root nodes
            roots = self.db.query(TaxonomyNode).filter(TaxonomyNode.level == 0).all()
            
            # Query all nodes if needed
            if max_depth is not None:
                all_nodes = self.db.query(TaxonomyNode).filter(
                    TaxonomyNode.level <= max_depth
                ).all()
            else:
                all_nodes = self.db.query(TaxonomyNode).all()
            
            # Build tree for each root
            return [self._build_tree_node(root, all_nodes, max_depth) for root in roots]
    
    def _build_tree_node(
        self,
        node: TaxonomyNode,
        all_nodes: List[TaxonomyNode],
        max_depth: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Recursively build tree node with children.
        
        Args:
            node: Current node
            all_nodes: All nodes in the tree
            max_depth: Maximum depth limit
            
        Returns:
            Dictionary with node data and nested children
        """
        node_dict = {
            "id": str(node.id),
            "name": node.name,
            "slug": node.slug,
            "level": node.level,
            "path": node.path,
            "description": node.description,
            "keywords": node.keywords,
            "resource_count": node.resource_count,
            "descendant_resource_count": node.descendant_resource_count,
            "is_leaf": node.is_leaf,
            "allow_resources": node.allow_resources,
            "children": []
        }
        
        # Check depth limit
        if max_depth is not None and node.level >= max_depth:
            return node_dict
        
        # Find children
        children = [n for n in all_nodes if n.parent_id == node.id]
        
        # Recursively build children
        for child in children:
            node_dict["children"].append(self._build_tree_node(child, all_nodes, max_depth))
        
        return node_dict
    
    def get_ancestors(self, node_id: uuid.UUID) -> List[TaxonomyNode]:
        """
        Get all ancestors of a node using materialized path.
        
        Algorithm:
        1. Query node by id
        2. Parse path to extract ancestor slugs
        3. Query ancestors by path pattern
        4. Return in hierarchical order (root to parent)
        
        Args:
            node_id: Node UUID
            
        Returns:
            List of ancestor TaxonomyNode objects (root to parent)
            
        Raises:
            ValueError: If node not found
        """
        # Query node
        node = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
        if not node:
            raise ValueError(f"Node with id {node_id} not found")
        
        # If root node, no ancestors
        if node.level == 0:
            return []
        
        # Parse path to get ancestor paths
        path_parts = node.path.strip('/').split('/')
        ancestor_paths = []
        for i in range(len(path_parts) - 1):
            ancestor_path = '/' + '/'.join(path_parts[:i+1])
            ancestor_paths.append(ancestor_path)
        
        # Query ancestors
        ancestors = self.db.query(TaxonomyNode).filter(
            TaxonomyNode.path.in_(ancestor_paths)
        ).order_by(TaxonomyNode.level).all()
        
        return ancestors
    
    def get_descendants(self, node_id: uuid.UUID) -> List[TaxonomyNode]:
        """
        Get all descendants of a node using path pattern matching.
        
        Algorithm:
        1. Query node by id
        2. Query all nodes with path LIKE "node.path/%"
        3. Return descendants
        
        Args:
            node_id: Node UUID
            
        Returns:
            List of descendant TaxonomyNode objects
            
        Raises:
            ValueError: If node not found
        """
        # Query node
        node = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
        if not node:
            raise ValueError(f"Node with id {node_id} not found")
        
        # Query descendants
        descendants = self.db.query(TaxonomyNode).filter(
            TaxonomyNode.path.like(f"{node.path}/%")
        ).order_by(TaxonomyNode.level, TaxonomyNode.name).all()
        
        return descendants
    
    # Resource classification
    
    def classify_resource(
        self,
        resource_id: uuid.UUID,
        classifications: List[Dict[str, Any]],
        predicted_by: str = "ml_model"
    ) -> List[ResourceTaxonomy]:
        """
        Assign classifications to a resource.
        
        Algorithm:
        1. Validate resource exists
        2. Remove existing predicted classifications for resource
        3. For each classification:
           - Validate taxonomy node exists
           - Create ResourceTaxonomy entry
           - Set needs_review flag if confidence < 0.7
           - Compute review_priority score
        4. Update resource counts for affected nodes
        5. Commit and return classifications
        
        Args:
            resource_id: Resource UUID
            classifications: List of dicts with taxonomy_node_id and confidence
            predicted_by: Model identifier (default: "ml_model")
            
        Returns:
            List of created ResourceTaxonomy objects
            
        Raises:
            ValueError: If resource or taxonomy nodes not found
        """
        # Validate resource exists
        resource = self.db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            raise ValueError(f"Resource with id {resource_id} not found")
        
        # Remove existing predicted classifications
        self.db.query(ResourceTaxonomy).filter(
            ResourceTaxonomy.resource_id == resource_id,
            ResourceTaxonomy.is_predicted == True
        ).delete(synchronize_session=False)
        
        # Create new classifications
        created_classifications = []
        for classification in classifications:
            taxonomy_node_id = classification.get("taxonomy_node_id")
            confidence = classification.get("confidence", 0.0)
            
            # Validate taxonomy node exists
            node = self.db.query(TaxonomyNode).filter(
                TaxonomyNode.id == taxonomy_node_id
            ).first()
            if not node:
                raise ValueError(f"Taxonomy node with id {taxonomy_node_id} not found")
            
            # Check if node allows resources
            if not node.allow_resources:
                continue
            
            # Determine if needs review
            needs_review = confidence < 0.7
            
            # Compute review priority (inverse of confidence for low confidence items)
            review_priority = (1.0 - confidence) if needs_review else None
            
            # Create classification
            resource_taxonomy = ResourceTaxonomy(
                id=uuid.uuid4(),
                resource_id=resource_id,
                taxonomy_node_id=taxonomy_node_id,
                confidence=confidence,
                is_predicted=True,
                predicted_by=predicted_by,
                needs_review=needs_review,
                review_priority=review_priority,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            self.db.add(resource_taxonomy)
            created_classifications.append(resource_taxonomy)
        
        # Commit classifications
        self.db.commit()
        
        # Update resource counts
        affected_node_ids = [c.taxonomy_node_id for c in created_classifications]
        for node_id in affected_node_ids:
            self._update_resource_counts(node_id)
        
        # Refresh objects
        for classification in created_classifications:
            self.db.refresh(classification)
        
        return created_classifications
    
    def _update_resource_counts(self, node_id: uuid.UUID) -> None:
        """
        Update cached resource counts for a node and its ancestors.
        
        Algorithm:
        1. Query node
        2. Count direct resources assigned to node
        3. Count descendant resources using path query
        4. Update node counts
        5. Recursively update ancestor counts
        
        Args:
            node_id: Node UUID to update
        """
        # Query node
        node = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
        if not node:
            return
        
        # Count direct resources
        direct_count = self.db.query(ResourceTaxonomy).filter(
            ResourceTaxonomy.taxonomy_node_id == node_id
        ).count()
        
        # Count descendant resources
        descendants = self.db.query(TaxonomyNode).filter(
            TaxonomyNode.path.like(f"{node.path}/%")
        ).all()
        descendant_ids = [d.id for d in descendants]
        
        if descendant_ids:
            descendant_count = self.db.query(ResourceTaxonomy).filter(
                ResourceTaxonomy.taxonomy_node_id.in_(descendant_ids)
            ).count()
        else:
            descendant_count = 0
        
        # Update counts
        node.resource_count = direct_count
        node.descendant_resource_count = descendant_count
        
        self.db.commit()
        
        # Update ancestors recursively
        if node.parent_id:
            self._update_resource_counts(node.parent_id)
