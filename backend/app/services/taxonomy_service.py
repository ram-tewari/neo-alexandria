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

from sqlalchemy.orm import Session
from sqlalchemy import or_

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
    
    def _validate_node_name(self, name: str) -> None:
        """
        Validate node name is not empty.
        
        Args:
            name: Node name to validate
            
        Raises:
            ValueError: If name is empty or whitespace only
        """
        if not name or not name.strip():
            raise ValueError("Node name cannot be empty")
    
    def _validate_slug_uniqueness(self, slug: str, exclude_id: Optional[uuid.UUID] = None) -> None:
        """
        Check if slug is unique in the taxonomy.
        
        Args:
            slug: Slug to check
            exclude_id: Optional node ID to exclude from check (for updates)
            
        Raises:
            ValueError: If slug already exists
        """
        query = self.db.query(TaxonomyNode).filter(TaxonomyNode.slug == slug)
        if exclude_id:
            query = query.filter(TaxonomyNode.id != exclude_id)
        
        existing = query.first()
        if existing:
            raise ValueError(f"A node with slug '{slug}' already exists")
    
    def _generate_and_validate_slug(self, name: str, exclude_id: Optional[uuid.UUID] = None) -> str:
        """
        Generate slug from name and validate it.
        
        Args:
            name: Node name
            exclude_id: Optional node ID to exclude from uniqueness check
            
        Returns:
            Valid unique slug
            
        Raises:
            ValueError: If slug is empty or not unique
        """
        slug = self._slugify(name)
        if not slug:
            raise ValueError("Node name must contain at least one alphanumeric character")
        
        self._validate_slug_uniqueness(slug, exclude_id)
        return slug
    
    def _get_parent_and_compute_level(self, parent_id: Optional[uuid.UUID]) -> tuple[Optional[TaxonomyNode], int]:
        """
        Get parent node and compute level for new node.
        
        Args:
            parent_id: Parent node UUID (None for root nodes)
            
        Returns:
            Tuple of (parent_node, level)
            
        Raises:
            ValueError: If parent_id provided but parent not found
        """
        if parent_id:
            parent = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == parent_id).first()
            if not parent:
                raise ValueError(f"Parent node with id {parent_id} not found")
            return parent, parent.level + 1
        return None, 0
    
    def _update_parent_is_leaf(self, parent: Optional[TaxonomyNode], is_leaf: bool) -> None:
        """
        Update parent's is_leaf flag.
        
        Args:
            parent: Parent node to update
            is_leaf: New is_leaf value
        """
        if parent:
            parent.is_leaf = is_leaf

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
        # Validate and generate slug
        self._validate_node_name(name)
        slug = self._generate_and_validate_slug(name)
        
        # Get parent and compute level
        parent, level = self._get_parent_and_compute_level(parent_id)
        self._update_parent_is_leaf(parent, False)
        
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

    def _get_node_by_id(self, node_id: uuid.UUID) -> TaxonomyNode:
        """
        Get node by ID or raise error.
        
        Args:
            node_id: Node UUID
            
        Returns:
            TaxonomyNode object
            
        Raises:
            ValueError: If node not found
        """
        node = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
        if not node:
            raise ValueError(f"Node with id {node_id} not found")
        return node
    
    def _handle_node_name_change(self, node: TaxonomyNode, new_name: str) -> None:
        """
        Handle node name change including slug and path updates.
        
        Args:
            node: Node to update
            new_name: New name for the node
            
        Raises:
            ValueError: If slug validation fails
        """
        if new_name == node.name:
            return
        
        # Generate and validate new slug
        new_slug = self._generate_and_validate_slug(new_name, exclude_id=node.id)
        
        # Store old path for descendant updates
        old_path = node.path
        
        # Update name and slug
        node.name = new_name
        node.slug = new_slug
        
        # Recalculate path
        node.path = self._compute_path(node.parent_id, new_slug)
        
        # Update descendants if path changed
        if old_path != node.path:
            self._update_descendants(node, old_path)
    
    def _update_node_metadata(
        self,
        node: TaxonomyNode,
        description: Optional[str],
        keywords: Optional[List[str]],
        allow_resources: Optional[bool]
    ) -> None:
        """
        Update node metadata fields.
        
        Args:
            node: Node to update
            description: New description (None to skip)
            keywords: New keywords (None to skip)
            allow_resources: New allow_resources flag (None to skip)
        """
        if description is not None:
            node.description = description
        if keywords is not None:
            node.keywords = keywords
        if allow_resources is not None:
            node.allow_resources = allow_resources

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
        # Get node
        node = self._get_node_by_id(node_id)
        
        # Handle name change
        if name:
            self._handle_node_name_change(node, name)
        
        # Update other fields
        self._update_node_metadata(node, description, keywords, allow_resources)
        
        # Update timestamp
        node.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(node)
        
        return node
    
    def _validate_node_has_no_resources(self, node_id: uuid.UUID) -> None:
        """
        Validate that node has no assigned resources.
        
        Args:
            node_id: Node UUID to check
            
        Raises:
            ValueError: If node has assigned resources
        """
        resource_count = self.db.query(ResourceTaxonomy).filter(
            ResourceTaxonomy.taxonomy_node_id == node_id
        ).count()
        if resource_count > 0:
            raise ValueError(
                f"Cannot delete node with {resource_count} assigned resources. "
                "Please unassign resources first."
            )
    
    def _cascade_delete_descendants(self, node: TaxonomyNode) -> int:
        """
        Delete all descendants and their resource classifications.
        
        Args:
            node: Node whose descendants to delete
            
        Returns:
            Number of descendants deleted
        """
        # Get all descendants
        descendants = self.db.query(TaxonomyNode).filter(
            TaxonomyNode.path.like(f"{node.path}/%")
        ).all()
        
        # Delete resource classifications for descendants
        descendant_ids = [d.id for d in descendants] + [node.id]
        self.db.query(ResourceTaxonomy).filter(
            ResourceTaxonomy.taxonomy_node_id.in_(descendant_ids)
        ).delete(synchronize_session=False)
        
        # Delete descendants
        for descendant in descendants:
            self.db.delete(descendant)
        
        return len(descendants)
    
    def _reparent_children(self, node: TaxonomyNode) -> int:
        """
        Reparent node's children to node's parent.
        
        Args:
            node: Node whose children to reparent
            
        Returns:
            Number of children reparented
        """
        children = self.db.query(TaxonomyNode).filter(
            TaxonomyNode.parent_id == node.id
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
        
        return len(children)
    
    def _update_parent_is_leaf_after_deletion(self, node: TaxonomyNode) -> None:
        """
        Update parent's is_leaf flag after node deletion.
        
        Args:
            node: Node being deleted
        """
        if not node.parent_id:
            return
        
        parent = self.db.query(TaxonomyNode).filter(
            TaxonomyNode.id == node.parent_id
        ).first()
        if not parent:
            return
        
        # Check if parent has other children
        sibling_count = self.db.query(TaxonomyNode).filter(
            TaxonomyNode.parent_id == node.parent_id,
            TaxonomyNode.id != node.id
        ).count()
        parent.is_leaf = (sibling_count == 0)

    def delete_node(
        self,
        node_id: uuid.UUID,
        cascade: bool = False
    ) -> Dict[str, Any]:
        """
        Delete taxonomy node with cascade or reparenting options.
        
        Args:
            node_id: Node UUID to delete
            cascade: If True, delete descendants; if False, reparent children
            
        Returns:
            Dictionary with deletion summary (deleted_count, reparented_count)
            
        Raises:
            ValueError: If node not found or has assigned resources
        """
        # Get node and validate
        node = self._get_node_by_id(node_id)
        self._validate_node_has_no_resources(node_id)
        
        # Handle descendants
        deleted_count = 1
        reparented_count = 0
        
        if cascade:
            deleted_count += self._cascade_delete_descendants(node)
        else:
            reparented_count = self._reparent_children(node)
        
        # Update parent's is_leaf flag
        self._update_parent_is_leaf_after_deletion(node)
        
        # Delete node
        self.db.delete(node)
        self.db.commit()
        
        return {
            "deleted_count": deleted_count,
            "reparented_count": reparented_count
        }
    
    def _validate_move_target(
        self,
        node_id: uuid.UUID,
        new_parent_id: Optional[uuid.UUID]
    ) -> Optional[TaxonomyNode]:
        """
        Validate move target and prevent circular references.
        
        Args:
            node_id: Node being moved
            new_parent_id: Target parent UUID
            
        Returns:
            New parent node (or None for root)
            
        Raises:
            ValueError: If parent not found or circular reference detected
        """
        if not new_parent_id:
            return None
        
        new_parent = self.db.query(TaxonomyNode).filter(
            TaxonomyNode.id == new_parent_id
        ).first()
        if not new_parent:
            raise ValueError(f"New parent node with id {new_parent_id} not found")
        
        # Prevent moving to own descendant
        if new_parent_id == node_id or self._is_descendant(new_parent_id, node_id):
            raise ValueError("Cannot move node to its own descendant (circular reference)")
        
        return new_parent
    
    def _update_old_parent_after_move(self, node: TaxonomyNode) -> None:
        """
        Update old parent's is_leaf flag after node is moved.
        
        Args:
            node: Node being moved
        """
        if not node.parent_id:
            return
        
        old_parent = self.db.query(TaxonomyNode).filter(
            TaxonomyNode.id == node.parent_id
        ).first()
        if not old_parent:
            return
        
        # Check if old parent has other children
        sibling_count = self.db.query(TaxonomyNode).filter(
            TaxonomyNode.parent_id == node.parent_id,
            TaxonomyNode.id != node.id
        ).count()
        old_parent.is_leaf = (sibling_count == 0)
    
    def _update_node_hierarchy(
        self,
        node: TaxonomyNode,
        new_parent: Optional[TaxonomyNode],
        new_parent_id: Optional[uuid.UUID]
    ) -> None:
        """
        Update node's parent, level, and path.
        
        Args:
            node: Node to update
            new_parent: New parent node (or None for root)
            new_parent_id: New parent UUID
        """
        node.parent_id = new_parent_id
        
        if new_parent:
            node.level = new_parent.level + 1
            new_parent.is_leaf = False
        else:
            node.level = 0
        
        node.path = self._compute_path(new_parent_id, node.slug)
        node.updated_at = datetime.now(timezone.utc)

    def move_node(
        self,
        node_id: uuid.UUID,
        new_parent_id: Optional[uuid.UUID]
    ) -> TaxonomyNode:
        """
        Move taxonomy node to a new parent (reparenting).
        
        Args:
            node_id: Node UUID to move
            new_parent_id: New parent UUID (None for root level)
            
        Returns:
            Updated TaxonomyNode object
            
        Raises:
            ValueError: If node not found, parent not found, or circular reference detected
        """
        # Get node
        node = self._get_node_by_id(node_id)
        
        # Check if already at target parent
        if node.parent_id == new_parent_id:
            return node
        
        # Validate move target
        new_parent = self._validate_move_target(node_id, new_parent_id)
        
        # Store old path
        old_path = node.path
        
        # Update old parent's is_leaf flag
        self._update_old_parent_after_move(node)
        
        # Update node hierarchy
        self._update_node_hierarchy(node, new_parent, new_parent_id)
        
        # Update descendants
        self._update_descendants(node, old_path)
        
        self.db.commit()
        self.db.refresh(node)
        
        return node

    # Hierarchical queries
    
    def _query_subtree_nodes(
        self,
        root: TaxonomyNode,
        max_depth: Optional[int]
    ) -> List[TaxonomyNode]:
        """
        Query all nodes in a subtree.
        
        Args:
            root: Root node of subtree
            max_depth: Optional maximum depth relative to root
            
        Returns:
            List of nodes in subtree
        """
        query = self.db.query(TaxonomyNode).filter(
            or_(
                TaxonomyNode.id == root.id,
                TaxonomyNode.path.like(f"{root.path}/%")
            )
        )
        
        if max_depth is not None:
            max_level = root.level + max_depth
            query = query.filter(TaxonomyNode.level <= max_level)
        
        return query.all()
    
    def _query_full_tree_nodes(self, max_depth: Optional[int]) -> tuple[List[TaxonomyNode], List[TaxonomyNode]]:
        """
        Query root nodes and all nodes for full tree.
        
        Args:
            max_depth: Optional maximum depth
            
        Returns:
            Tuple of (root_nodes, all_nodes)
        """
        roots = self.db.query(TaxonomyNode).filter(TaxonomyNode.level == 0).all()
        
        if max_depth is not None:
            all_nodes = self.db.query(TaxonomyNode).filter(
                TaxonomyNode.level <= max_depth
            ).all()
        else:
            all_nodes = self.db.query(TaxonomyNode).all()
        
        return roots, all_nodes

    def get_tree(
        self,
        root_id: Optional[uuid.UUID] = None,
        max_depth: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve nested taxonomy tree structure.
        
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
            root = self._get_node_by_id(root_id)
            nodes = self._query_subtree_nodes(root, max_depth)
            return [self._build_tree_node(root, nodes, max_depth)]
        else:
            # Query full tree
            roots, all_nodes = self._query_full_tree_nodes(max_depth)
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
            ResourceTaxonomy.is_predicted
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
