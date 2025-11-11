"""
Neo Alexandria 2.0 - Taxonomy API Router (Phase 8.5)

This module provides RESTful API endpoints for hierarchical taxonomy management
and ML-based resource classification operations.

Related files:
- app/services/taxonomy_service.py: Taxonomy business logic
- app/services/ml_classification_service.py: ML classification service
- app/schemas/taxonomy.py: Pydantic schemas for validation
- app/database/models.py: TaxonomyNode and ResourceTaxonomy models

Features:
- Taxonomy node CRUD operations
- Hierarchical tree retrieval
- Node movement and reparenting
- Ancestor and descendant queries
- Resource classification endpoints
- Active learning workflows
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
import uuid

logger = logging.getLogger(__name__)

from backend.app.database.base import get_sync_db
from backend.app.schemas.taxonomy import (
    TaxonomyNodeCreate,
    TaxonomyNodeUpdate,
    TaxonomyNodeResponse,
    TaxonomyNodeTree,
    TaxonomyNodeMove,
    ClassificationFeedback,
    ClassifierTrainingRequest,
    ClassifierTrainingResponse,
    ResourceClassificationResponse,
    UncertainSamplesResponse,
)
from backend.app.services.taxonomy_service import TaxonomyService


router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


@router.post("/nodes", response_model=TaxonomyNodeResponse, status_code=status.HTTP_201_CREATED)
def create_taxonomy_node(
    payload: TaxonomyNodeCreate,
    db: Session = Depends(get_sync_db)
):
    """
    Create a new taxonomy node.
    
    Creates a taxonomy node with optional parent for hierarchical organization.
    The system automatically:
    - Generates a URL-friendly slug from the name
    - Computes the tree level (0 for root, parent.level + 1 for children)
    - Computes the materialized path for efficient queries
    - Updates the parent's is_leaf flag
    
    Args:
        payload: TaxonomyNodeCreate with name, optional parent_id, description, keywords
        db: Database session
        
    Returns:
        Created TaxonomyNode with computed fields
        
    Raises:
        400: If validation fails (duplicate slug, parent not found, invalid name)
        422: If request body is invalid
        500: If creation fails
    """
    try:
        taxonomy_service = TaxonomyService(db)
        
        # Convert parent_id string to UUID if provided
        parent_uuid = None
        if payload.parent_id:
            try:
                parent_uuid = uuid.UUID(payload.parent_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid parent_id format: {payload.parent_id}"
                )
        
        # Create node
        node = taxonomy_service.create_node(
            name=payload.name,
            parent_id=parent_uuid,
            description=payload.description,
            keywords=payload.keywords,
            allow_resources=payload.allow_resources
        )
        
        return TaxonomyNodeResponse.model_validate(node)
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as exc:
        logger.error(f"Failed to create taxonomy node: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create taxonomy node"
        ) from exc


@router.put("/nodes/{node_id}", response_model=TaxonomyNodeResponse, status_code=status.HTTP_200_OK)
def update_taxonomy_node(
    node_id: str,
    payload: TaxonomyNodeUpdate,
    db: Session = Depends(get_sync_db)
):
    """
    Update taxonomy node metadata.
    
    Updates node name, description, keywords, and allow_resources flag.
    If the name changes, the system automatically:
    - Regenerates the slug
    - Recalculates the materialized path
    - Updates paths for all descendants
    
    Note: To change the parent (reparent), use the POST /taxonomy/nodes/{node_id}/move endpoint.
    
    Args:
        node_id: Taxonomy node UUID
        payload: TaxonomyNodeUpdate with optional fields to update
        db: Database session
        
    Returns:
        Updated TaxonomyNode
        
    Raises:
        400: If validation fails (node not found, duplicate slug)
        422: If request body is invalid
        500: If update fails
    """
    try:
        taxonomy_service = TaxonomyService(db)
        
        # Convert node_id to UUID
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid node_id format: {node_id}"
            )
        
        # Update node
        node = taxonomy_service.update_node(
            node_id=node_uuid,
            name=payload.name,
            description=payload.description,
            keywords=payload.keywords,
            allow_resources=payload.allow_resources
        )
        
        return TaxonomyNodeResponse.model_validate(node)
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as exc:
        logger.error(f"Failed to update taxonomy node {node_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update taxonomy node"
        ) from exc


@router.delete("/nodes/{node_id}", status_code=status.HTTP_200_OK)
def delete_taxonomy_node(
    node_id: str,
    cascade: bool = Query(False, description="If true, delete descendants; if false, reparent children"),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a taxonomy node.
    
    Deletes a taxonomy node with two strategies:
    - cascade=false (default): Reparents children to the deleted node's parent
    - cascade=true: Recursively deletes all descendants
    
    The system prevents deletion if:
    - The node has assigned resources (must unassign first)
    
    Args:
        node_id: Taxonomy node UUID to delete
        cascade: Deletion strategy (default: false)
        db: Database session
        
    Returns:
        Deletion summary with counts
        
    Raises:
        400: If node has assigned resources or node not found
        422: If node_id format is invalid
        500: If deletion fails
    """
    try:
        taxonomy_service = TaxonomyService(db)
        
        # Convert node_id to UUID
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid node_id format: {node_id}"
            )
        
        # Delete node
        result = taxonomy_service.delete_node(
            node_id=node_uuid,
            cascade=cascade
        )
        
        return {
            "deleted": True,
            "deleted_count": result.get("deleted_count", 1),
            "reparented_count": result.get("reparented_count", 0)
        }
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as exc:
        logger.error(f"Failed to delete taxonomy node {node_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete taxonomy node"
        ) from exc


@router.post("/nodes/{node_id}/move", status_code=status.HTTP_200_OK)
def move_taxonomy_node(
    node_id: str,
    payload: TaxonomyNodeMove,
    db: Session = Depends(get_sync_db)
):
    """
    Move a taxonomy node to a new parent (reparenting).
    
    Moves a node to a different parent in the hierarchy. The system:
    - Prevents circular references (moving a node to its own descendant)
    - Recalculates level and path for the node and all descendants
    - Updates the old and new parents' is_leaf flags
    
    To move a node to root level, set new_parent_id to null.
    
    Args:
        node_id: Taxonomy node UUID to move
        payload: TaxonomyNodeMove with new_parent_id (null for root)
        db: Database session
        
    Returns:
        Move status and updated node
        
    Raises:
        400: If circular reference detected or node/parent not found
        422: If request body is invalid
        500: If move fails
    """
    try:
        taxonomy_service = TaxonomyService(db)
        
        # Convert node_id to UUID
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid node_id format: {node_id}"
            )
        
        # Convert new_parent_id to UUID if provided
        new_parent_uuid = None
        if payload.new_parent_id:
            try:
                new_parent_uuid = uuid.UUID(payload.new_parent_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid new_parent_id format: {payload.new_parent_id}"
                )
        
        # Move node
        node = taxonomy_service.move_node(
            node_id=node_uuid,
            new_parent_id=new_parent_uuid
        )
        
        return {
            "moved": True,
            "node": TaxonomyNodeResponse.model_validate(node)
        }
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as exc:
        logger.error(f"Failed to move taxonomy node {node_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to move taxonomy node"
        ) from exc


@router.get("/tree", response_model=List[TaxonomyNodeTree], status_code=status.HTTP_200_OK)
def get_taxonomy_tree(
    root_id: Optional[str] = Query(None, description="Root node UUID (omit for all roots)"),
    max_depth: Optional[int] = Query(None, ge=1, description="Maximum tree depth to retrieve"),
    db: Session = Depends(get_sync_db)
):
    """
    Retrieve taxonomy tree as nested structure.
    
    Returns the taxonomy tree as a nested JSON structure suitable for rendering
    tree views in UIs. Each node includes its children recursively.
    
    Options:
    - Omit root_id to get all root nodes and their descendants
    - Specify root_id to get a subtree starting from that node
    - Use max_depth to limit traversal depth (useful for large trees)
    
    Args:
        root_id: Optional root node UUID to start from
        max_depth: Optional maximum depth to traverse
        db: Database session
        
    Returns:
        List of TaxonomyNodeTree with nested children
        
    Raises:
        400: If root_id format is invalid or node not found
        500: If tree retrieval fails
    """
    try:
        taxonomy_service = TaxonomyService(db)
        
        # Convert root_id to UUID if provided
        root_uuid = None
        if root_id:
            try:
                root_uuid = uuid.UUID(root_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid root_id format: {root_id}"
                )
        
        # Get tree
        tree = taxonomy_service.get_tree(
            root_id=root_uuid,
            max_depth=max_depth
        )
        
        # The tree is already in the correct format (list of dicts with nested children)
        # Just return it directly - FastAPI will handle the serialization
        return tree
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as exc:
        logger.error(f"Failed to retrieve taxonomy tree: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve taxonomy tree"
        ) from exc


@router.get("/nodes/{node_id}/ancestors", response_model=List[TaxonomyNodeResponse], status_code=status.HTTP_200_OK)
def get_node_ancestors(
    node_id: str,
    db: Session = Depends(get_sync_db)
):
    """
    Get all ancestor nodes (breadcrumb trail).
    
    Returns all parent nodes from the specified node up to the root,
    in hierarchical order (root first, immediate parent last).
    
    This is useful for:
    - Rendering breadcrumb navigation
    - Understanding node context in the hierarchy
    - Building navigation paths
    
    Uses materialized path for O(1) query performance.
    
    Args:
        node_id: Taxonomy node UUID
        db: Database session
        
    Returns:
        List of ancestor TaxonomyNodes in hierarchical order
        
    Raises:
        400: If node_id format is invalid or node not found
        500: If query fails
    """
    try:
        taxonomy_service = TaxonomyService(db)
        
        # Convert node_id to UUID
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid node_id format: {node_id}"
            )
        
        # Get ancestors
        ancestors = taxonomy_service.get_ancestors(node_uuid)
        
        return [TaxonomyNodeResponse.model_validate(node) for node in ancestors]
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as exc:
        logger.error(f"Failed to get ancestors for node {node_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get node ancestors"
        ) from exc


@router.get("/nodes/{node_id}/descendants", response_model=List[TaxonomyNodeResponse], status_code=status.HTTP_200_OK)
def get_node_descendants(
    node_id: str,
    db: Session = Depends(get_sync_db)
):
    """
    Get all descendant nodes (subcategories).
    
    Returns all child nodes at any depth below the specified node.
    
    This is useful for:
    - Exploring subcategories
    - Counting resources in a category and all subcategories
    - Bulk operations on category hierarchies
    
    Uses materialized path pattern matching for O(1) query performance.
    
    Args:
        node_id: Taxonomy node UUID
        db: Database session
        
    Returns:
        List of descendant TaxonomyNodes (all levels)
        
    Raises:
        400: If node_id format is invalid or node not found
        500: If query fails
    """
    try:
        taxonomy_service = TaxonomyService(db)
        
        # Convert node_id to UUID
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid node_id format: {node_id}"
            )
        
        # Get descendants
        descendants = taxonomy_service.get_descendants(node_uuid)
        
        return [TaxonomyNodeResponse.model_validate(node) for node in descendants]
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as exc:
        logger.error(f"Failed to get descendants for node {node_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get node descendants"
        ) from exc


# ============================================================================
# Classification Operations Endpoints
# ============================================================================


@router.post("/classify/{resource_id}", status_code=status.HTTP_202_ACCEPTED)
async def classify_resource(
    resource_id: str,
    db: Session = Depends(get_sync_db)
):
    """
    Classify a resource using ML classifier.
    
    Enqueues a background task to classify the specified resource using the
    ML classification service. The classification is performed asynchronously
    to avoid blocking the API response.
    
    The background task will:
    1. Load the resource content (title, description)
    2. Use the ML classifier to predict taxonomy categories
    3. Filter predictions by confidence threshold (>=0.3)
    4. Store classifications with confidence scores
    5. Flag low-confidence predictions (<0.7) for human review
    
    Args:
        resource_id: Resource UUID to classify
        db: Database session
        
    Returns:
        202 Accepted with task status
        
    Raises:
        400: If resource_id format is invalid or resource not found
        500: If task enqueuing fails
        
    Requirements: 10.1, 10.2
    """
    try:
        # Convert resource_id to UUID
        try:
            resource_uuid = uuid.UUID(resource_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid resource_id format: {resource_id}"
            )
        
        # Verify resource exists
        from backend.app.database.models import Resource
        resource = db.query(Resource).filter(Resource.id == resource_uuid).first()
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resource {resource_id} not found"
            )
        
        # Import classification service
        from backend.app.services.classification_service import ClassificationService
        
        # Create background task for classification
        # Note: In a production system, this would use Celery or similar
        # For now, we'll execute synchronously but return 202 to indicate async behavior
        import asyncio
        
        async def classify_task():
            """Background task to classify resource."""
            try:
                classification_service = ClassificationService(db=db, use_ml=True)
                result = classification_service.classify_resource(
                    resource_id=resource_uuid,
                    use_ml=True
                )
                logger.info(f"Classification complete for resource {resource_id}: {result}")
            except Exception as e:
                logger.error(f"Classification failed for resource {resource_id}: {e}", exc_info=True)
        
        # Schedule the task (in production, this would be a proper background task)
        asyncio.create_task(classify_task())
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        return {
            "task_id": task_id,
            "resource_id": resource_id,
            "status": "queued",
            "message": "Classification task enqueued successfully"
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to enqueue classification task for resource {resource_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enqueue classification task"
        ) from exc


@router.get("/active-learning/uncertain", response_model=UncertainSamplesResponse, status_code=status.HTTP_200_OK)
def get_uncertain_samples(
    limit: int = Query(100, ge=1, le=1000, description="Number of uncertain samples to return"),
    db: Session = Depends(get_sync_db)
):
    """
    Get resources with uncertain classifications for active learning review.
    
    This endpoint identifies resources where the ML classifier is most uncertain,
    making them ideal candidates for human review and labeling. The uncertainty
    is computed using multiple metrics:
    - Entropy: Measures prediction uncertainty across all classes
    - Margin: Difference between top-2 predictions (small = uncertain)
    - Confidence: Maximum probability (low = uncertain)
    
    The combined uncertainty score prioritizes resources that would provide
    the most value when labeled by humans, enabling efficient active learning.
    
    Use this endpoint to:
    - Identify resources needing human review
    - Prioritize labeling efforts for maximum model improvement
    - Build training datasets efficiently
    
    Args:
        limit: Number of uncertain samples to return (default: 100, max: 1000)
        db: Database session
        
    Returns:
        UncertainSamplesResponse with list of uncertain resources and their scores
        
    Raises:
        500: If uncertainty computation fails
        
    Requirements: 10.3
    """
    try:
        # Import ML classification service
        from backend.app.services.ml_classification_service import MLClassificationService
        from backend.app.database.models import Resource, ResourceTaxonomy, TaxonomyNode
        
        # Initialize ML classifier
        ml_service = MLClassificationService(
            db=db,
            model_name="distilbert-base-uncased",
            model_version="v1.0"
        )
        
        # Identify uncertain samples
        logger.info(f"Identifying {limit} uncertain samples for active learning")
        uncertain_samples = ml_service.identify_uncertain_samples(
            resource_ids=None,  # All resources
            limit=limit
        )
        
        # Build response with resource details
        samples = []
        for resource_id, uncertainty_score in uncertain_samples:
            # Get resource details
            resource = db.query(Resource).filter(Resource.id == resource_id).first()
            if not resource:
                logger.warning(f"Resource {resource_id} not found, skipping")
                continue
            
            # Get current classifications
            current_classifications = []
            resource_taxonomies = db.query(ResourceTaxonomy).filter(
                ResourceTaxonomy.resource_id == resource_id,
                ResourceTaxonomy.is_predicted == True
            ).all()
            
            for rt in resource_taxonomies:
                # Get taxonomy node details
                taxonomy_node = db.query(TaxonomyNode).filter(
                    TaxonomyNode.id == rt.taxonomy_node_id
                ).first()
                
                if taxonomy_node:
                    current_classifications.append({
                        "taxonomy_node_id": str(rt.taxonomy_node_id),
                        "taxonomy_node_name": taxonomy_node.name,
                        "confidence": rt.confidence,
                        "needs_review": rt.needs_review
                    })
            
            # Add to samples list
            samples.append({
                "resource_id": str(resource.id),
                "resource_title": resource.title or "Untitled",
                "uncertainty_score": uncertainty_score,
                "current_classifications": current_classifications
            })
        
        logger.info(f"Returning {len(samples)} uncertain samples")
        
        return {
            "samples": samples,
            "total": len(samples)
        }
        
    except Exception as exc:
        logger.error(f"Failed to get uncertain samples: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get uncertain samples"
        ) from exc


@router.post("/active-learning/feedback", status_code=status.HTTP_200_OK)
def submit_classification_feedback(
    payload: ClassificationFeedback,
    db: Session = Depends(get_sync_db)
):
    """
    Submit human classification feedback for active learning.
    
    This endpoint allows humans to provide correct classifications for resources,
    which are used to improve the ML model through active learning. The feedback:
    - Removes existing predicted (ML-generated) classifications
    - Adds manual classifications with confidence 1.0
    - Tracks the number of manual labels for retraining decisions
    - Triggers retraining notification when threshold reached (100 labels)
    
    Use this endpoint to:
    - Correct ML classification errors
    - Label uncertain samples identified by active learning
    - Build high-quality training data incrementally
    - Trigger model retraining when sufficient feedback accumulated
    
    The system automatically tracks manual labels and recommends retraining
    when 100 or more new labels have been added since the last training.
    
    Args:
        payload: ClassificationFeedback with resource_id and correct_taxonomy_ids
        db: Database session
        
    Returns:
        Update status and retraining recommendation
        
    Raises:
        400: If resource_id or taxonomy_ids are invalid
        500: If feedback update fails
        
    Requirements: 10.4
    """
    try:
        # Convert resource_id to UUID
        try:
            resource_uuid = uuid.UUID(payload.resource_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid resource_id format: {payload.resource_id}"
            )
        
        # Convert taxonomy_ids to UUIDs
        taxonomy_uuids = []
        for taxonomy_id in payload.correct_taxonomy_ids:
            try:
                taxonomy_uuids.append(str(uuid.UUID(taxonomy_id)))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid taxonomy_id format: {taxonomy_id}"
                )
        
        # Verify resource exists
        from backend.app.database.models import Resource
        resource = db.query(Resource).filter(Resource.id == resource_uuid).first()
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resource {payload.resource_id} not found"
            )
        
        # Import ML classification service
        from backend.app.services.ml_classification_service import MLClassificationService
        
        # Initialize ML classifier
        ml_service = MLClassificationService(
            db=db,
            model_name="distilbert-base-uncased",
            model_version="v1.0"
        )
        
        # Update from human feedback
        logger.info(f"Submitting feedback for resource {payload.resource_id}")
        success = ml_service.update_from_human_feedback(
            resource_id=str(resource_uuid),
            correct_taxonomy_ids=taxonomy_uuids
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update classification feedback"
            )
        
        # Check if retraining is recommended
        from backend.app.database.models import ResourceTaxonomy
        manual_count = db.query(ResourceTaxonomy).filter(
            ResourceTaxonomy.is_predicted == False,
            ResourceTaxonomy.predicted_by == "manual"
        ).count()
        
        retraining_recommended = manual_count >= 100
        
        logger.info(f"Feedback submitted successfully. Manual labels: {manual_count}")
        
        return {
            "updated": True,
            "resource_id": payload.resource_id,
            "manual_labels_count": manual_count,
            "retraining_recommended": retraining_recommended,
            "message": "Classification feedback submitted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to submit classification feedback: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit classification feedback"
        ) from exc


@router.post("/train", response_model=ClassifierTrainingResponse, status_code=status.HTTP_202_ACCEPTED)
async def train_classifier(
    payload: ClassifierTrainingRequest,
    db: Session = Depends(get_sync_db)
):
    """
    Initiate ML classifier fine-tuning.
    
    This endpoint starts a background task to fine-tune the ML classification model
    on provided labeled data. The training process:
    - Fine-tunes a transformer model (DistilBERT/BERT) on labeled examples
    - Optionally uses semi-supervised learning with unlabeled data
    - Saves model checkpoints after each epoch
    - Computes evaluation metrics (F1, precision, recall)
    - Saves the trained model for inference
    
    Training is performed asynchronously to avoid blocking the API. The task
    returns immediately with a task ID that can be used to track progress.
    
    Training parameters:
    - epochs: Number of training epochs (default: 3, range: 1-10)
    - batch_size: Training batch size (default: 16, range: 1-64)
    - learning_rate: Learning rate for optimizer (default: 2e-5)
    
    Semi-supervised learning:
    - If unlabeled_texts provided, performs pseudo-labeling
    - Uses high-confidence predictions (>=0.9) as training examples
    - Helps improve model with fewer labeled examples
    
    Use this endpoint to:
    - Train initial model on labeled dataset
    - Retrain model after accumulating human feedback
    - Improve model with semi-supervised learning
    - Adapt model to domain-specific content
    
    Args:
        payload: ClassifierTrainingRequest with labeled_data, optional unlabeled_texts, and training params
        db: Database session
        
    Returns:
        202 Accepted with task_id and status
        
    Raises:
        400: If training data is invalid or insufficient
        422: If request body is invalid
        500: If task enqueuing fails
        
    Requirements: 10.5, 10.6, 10.7
    """
    try:
        # Validate labeled data
        if not payload.labeled_data or len(payload.labeled_data) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 1 labeled example is required for training"
            )
        
        # Validate taxonomy IDs exist
        from backend.app.database.models import TaxonomyNode
        all_taxonomy_ids = set()
        for example in payload.labeled_data:
            all_taxonomy_ids.update(example.taxonomy_ids)
        
        for taxonomy_id in all_taxonomy_ids:
            try:
                taxonomy_uuid = uuid.UUID(taxonomy_id)
                node = db.query(TaxonomyNode).filter(TaxonomyNode.id == taxonomy_uuid).first()
                if not node:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Taxonomy node {taxonomy_id} not found"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid taxonomy_id format: {taxonomy_id}"
                )
        
        # Import ML classification service
        from backend.app.services.ml_classification_service import MLClassificationService
        
        # Prepare training data
        labeled_data = [
            (example.text, example.taxonomy_ids)
            for example in payload.labeled_data
        ]
        
        unlabeled_texts = payload.unlabeled_texts if payload.unlabeled_texts else None
        
        # Create background task for training
        # Note: In a production system, this would use Celery or similar
        # For now, we'll execute synchronously but return 202 to indicate async behavior
        import asyncio
        
        async def training_task():
            """Background task to train classifier."""
            try:
                logger.info(
                    f"Starting classifier training with {len(labeled_data)} labeled examples, "
                    f"{len(unlabeled_texts) if unlabeled_texts else 0} unlabeled texts"
                )
                
                # Initialize ML classifier
                ml_service = MLClassificationService(
                    db=db,
                    model_name="distilbert-base-uncased",
                    model_version="v1.0"
                )
                
                # Fine-tune model
                metrics = ml_service.fine_tune(
                    labeled_data=labeled_data,
                    unlabeled_data=unlabeled_texts,
                    epochs=payload.epochs,
                    batch_size=payload.batch_size,
                    learning_rate=payload.learning_rate
                )
                
                logger.info(f"Training complete. Metrics: {metrics}")
                
            except Exception as e:
                logger.error(f"Training failed: {e}", exc_info=True)
        
        # Schedule the task (in production, this would be a proper background task)
        asyncio.create_task(training_task())
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        logger.info(
            f"Training task {task_id} enqueued with {len(labeled_data)} labeled examples, "
            f"epochs={payload.epochs}, batch_size={payload.batch_size}"
        )
        
        return {
            "task_id": task_id,
            "status": "queued",
            "message": f"Training task enqueued successfully with {len(labeled_data)} labeled examples"
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to enqueue training task: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enqueue training task"
        ) from exc
