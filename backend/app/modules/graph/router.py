"""
Neo Alexandria 2.0 - Graph API Router for Phase 5

Provides REST endpoints for the hybrid knowledge graph system, enabling
mind-map neighbor exploration and global overview analysis.

Migrated from app/routers/graph.py to modules/graph/router.py (Phase 14)
"""

from __future__ import annotations

import json
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.shared.database import get_db, get_sync_db
from app.database import models as db_models
from app.modules.graph.schema import KnowledgeGraph
from app.modules.graph.service import (
    find_hybrid_neighbors,
    generate_global_overview,
)
from app.modules.graph.embeddings import GraphEmbeddingsService
from app.config.settings import get_settings
from app.shared.event_bus import event_bus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/graph", tags=["graph"])
settings = get_settings()


@router.post(
    "/resources/{resource_id}/extract-citations",
    summary="Extract citations from a resource",
    description=(
        "Extracts citations from a resource's content and creates citation edges in the graph. "
        "This endpoint triggers citation extraction and emits a citation.extracted event."
    ),
)
def extract_resource_citations(
    resource_id: UUID,
    db: Session = Depends(get_sync_db),
) -> dict:
    """
    Extract citations from a resource and update the graph.
    
    This endpoint:
    1. Extracts citation markers and references from the resource
    2. Creates citation edges in the graph database
    3. Emits a citation.extracted event for downstream processing
    
    Args:
        resource_id: UUID of the resource to extract citations from
        db: Database session dependency
        
    Returns:
        dict: Response with extraction status and citations found
        
    Raises:
        HTTPException: If resource is not found or extraction fails
    """
    try:
        # Verify resource exists using SQLAlchemy 2.0 style
        from sqlalchemy import select
        
        stmt = select(db_models.Resource).where(db_models.Resource.id == resource_id)
        result = db.execute(stmt)
        resource = result.scalar_one_or_none()
        
        if not resource:
            raise HTTPException(
                status_code=404,
                detail=f"Resource with ID {resource_id} not found"
            )
        
        # Extract citations from resource description/content
        # In a real implementation, this would parse the text for citation markers
        # For now, we'll create a simple mock extraction
        citations = []
        
        if resource.description:
            # Simple citation marker detection (e.g., [1], [2], etc.)
            import re
            citation_pattern = r'\[(\d+)\]'
            matches = re.finditer(citation_pattern, resource.description)
            
            for match in matches:
                marker = match.group(0)
                position = match.start()
                
                # Extract context around the citation
                start = max(0, position - 20)
                end = min(len(resource.description), position + 50)
                context = resource.description[start:end]
                
                citations.append({
                    "marker": marker,
                    "position": position,
                    "context": context,
                    "text": marker  # In real implementation, would extract actual reference text
                })
        
        # Emit citation.extracted event
        try:
            from app.shared.event_bus import EventPriority
            event_bus.emit(
                "citation.extracted",
                {
                    "resource_id": str(resource_id),
                    "citations": citations,
                    "count": len(citations)
                },
                priority=EventPriority.NORMAL
            )
            logger.debug(f"Emitted citation.extracted event for {resource_id}")
        except Exception as e:
            logger.error(f"Failed to emit citation.extracted event: {e}", exc_info=True)
        
        logger.info(
            f"Extracted {len(citations)} citations from resource {resource_id}"
        )
        
        return {
            "status": "success",
            "resource_id": str(resource_id),
            "citations": citations,
            "count": len(citations)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting citations for {resource_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while extracting citations"
        )


@router.get(
    "/resource/{resource_id}/neighbors",
    response_model=KnowledgeGraph,
    summary="Get hybrid neighbors for mind-map view",
    description=(
        "Returns a knowledge graph showing the most relevant neighbors for a given resource, "
        "ranked by hybrid scoring that combines vector similarity, shared subjects, and "
        "classification code matches. Suitable for mind-map visualization."
    ),
)
def get_resource_neighbors(
    resource_id: UUID,
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=20,
        description=f"Maximum number of neighbors to return (default: {settings.DEFAULT_GRAPH_NEIGHBORS})"
    ),
    db: Session = Depends(get_db),
) -> KnowledgeGraph:
    """
    Get hybrid-scored neighbors for a specific resource.
    
    This endpoint provides the data needed for a mind-map visualization
    centered on the specified resource. The returned graph includes:
    - The source resource as a node
    - Its top-ranked neighbor resources as nodes  
    - Weighted edges explaining the relationships
    
    The hybrid scoring considers:
    - Vector similarity between embeddings (60% weight by default)
    - Shared canonical subjects (30% weight by default)
    - Classification code matches (10% weight by default)
    
    Args:
        resource_id: UUID of the resource to find neighbors for
        limit: Maximum number of neighbors to return
        db: Database session dependency
        
    Returns:
        KnowledgeGraph: Graph with source node and its neighbors
        
    Raises:
        HTTPException: If resource is not found or other errors occur
    """
    try:
        graph = find_hybrid_neighbors(db, resource_id, limit)
        
        # Check if source resource was found (empty graph means resource not found)
        if not graph.nodes:
            raise HTTPException(
                status_code=404,
                detail=f"Resource with ID {resource_id} not found"
            )
        
        logger.info(
            f"Generated neighbor graph for resource {resource_id}: "
            f"{len(graph.nodes)} nodes, {len(graph.edges)} edges"
        )
        
        return graph
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating neighbor graph for {resource_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating neighbor graph"
        )


@router.get(
    "/overview",
    response_model=KnowledgeGraph,
    summary="Get global overview of strongest connections",
    description=(
        "Returns a knowledge graph showing the strongest relationships across the entire library. "
        "Combines high vector similarity pairs and significant tag overlap pairs, ranked by "
        "hybrid scoring. Suitable for global overview visualization."
    ),
)
def get_global_overview(
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description=f"Maximum number of edges to return (default: {settings.GRAPH_OVERVIEW_MAX_EDGES})"
    ),
    vector_threshold: Optional[float] = Query(
        None,
        ge=0.0,
        le=1.0,
        description=f"Minimum vector similarity threshold for candidates (default: {settings.GRAPH_VECTOR_MIN_SIM_THRESHOLD})"
    ),
    db: Session = Depends(get_db),
) -> KnowledgeGraph:
    """
    Get global overview of strongest connections across the library.
    
    This endpoint provides data for a global knowledge graph visualization
    showing the most significant relationships in the entire collection.
    
    The algorithm:
    1. Finds resource pairs with high vector similarity (above threshold)
    2. Finds resource pairs with significant tag overlap
    3. Scores all candidate pairs using hybrid weighting
    4. Returns the top-weighted edges and their involved nodes
    
    Args:
        limit: Maximum number of edges to include in the overview
        vector_threshold: Minimum cosine similarity for vector-based candidates
        db: Database session dependency
        
    Returns:
        KnowledgeGraph: Graph with strongest global connections
        
    Raises:
        HTTPException: If errors occur during graph generation
    """
    try:
        graph = generate_global_overview(db, limit, vector_threshold)
        
        logger.info(
            f"Generated global overview: "
            f"{len(graph.nodes)} nodes, {len(graph.edges)} edges, "
            f"limit={limit}, threshold={vector_threshold}"
        )
        
        return graph
        
    except Exception as e:
        logger.error(f"Error generating global overview: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating global overview"
        )


# Graph Embeddings Endpoints (Task 11.7)

@router.post(
    "/embeddings/generate",
    summary="Generate graph embeddings",
    description=(
        "Generate Node2Vec or DeepWalk embeddings for the citation graph. "
        "This endpoint computes embeddings for all nodes in the graph and caches them."
    ),
)
def generate_graph_embeddings(
    algorithm: str = Query("node2vec", description="Algorithm to use: 'node2vec' or 'deepwalk'"),
    dimensions: int = Query(128, ge=32, le=512, description="Embedding dimensionality"),
    walk_length: int = Query(80, ge=10, le=200, description="Length of random walks"),
    num_walks: int = Query(10, ge=1, le=100, description="Number of walks per node"),
    p: float = Query(1.0, ge=0.1, le=10.0, description="Return parameter (Node2Vec only)"),
    q: float = Query(1.0, ge=0.1, le=10.0, description="In-out parameter (Node2Vec only)"),
    db: Session = Depends(get_sync_db),
) -> dict:
    """
    Generate graph embeddings using Node2Vec or DeepWalk algorithm.
    
    This endpoint:
    1. Builds a NetworkX graph from citation data
    2. Trains the specified embedding algorithm
    3. Extracts embeddings for all nodes
    4. Caches embeddings for fast retrieval
    
    Args:
        algorithm: Algorithm to use ("node2vec" or "deepwalk")
        dimensions: Embedding dimensionality (default: 128)
        walk_length: Length of random walks (default: 80)
        num_walks: Number of walks per node (default: 10)
        p: Return parameter for Node2Vec (default: 1.0)
        q: In-out parameter for Node2Vec (default: 1.0)
        db: Database session dependency
        
    Returns:
        dict: Response with status, embeddings_computed, dimensions, and execution_time
        
    Raises:
        HTTPException: If embedding generation fails
    """
    try:
        embeddings_service = GraphEmbeddingsService(db)
        
        if algorithm.lower() == "deepwalk":
            result = embeddings_service.compute_deepwalk_embeddings(
                dimensions=dimensions,
                walk_length=walk_length,
                num_walks=num_walks
            )
        elif algorithm.lower() == "node2vec":
            result = embeddings_service.compute_node2vec_embeddings(
                dimensions=dimensions,
                walk_length=walk_length,
                num_walks=num_walks,
                p=p,
                q=q
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid algorithm: {algorithm}. Must be 'node2vec' or 'deepwalk'"
            )
        
        logger.info(
            f"Generated {algorithm} embeddings: "
            f"{result['embeddings_computed']} nodes, "
            f"{result['execution_time']:.2f}s"
        )
        
        return result
        
    except ImportError as e:
        logger.error(f"Missing dependency for graph embeddings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Missing required dependency: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating graph embeddings: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating embeddings"
        )


@router.get(
    "/embeddings/{node_id}",
    summary="Get embedding for a node",
    description=(
        "Retrieve the graph embedding vector for a specific node (resource). "
        "Returns None if embeddings have not been generated or node not found."
    ),
)
def get_node_embedding(
    node_id: UUID,
    db: Session = Depends(get_sync_db),
) -> dict:
    """
    Get the graph embedding for a specific node.
    
    Args:
        node_id: UUID of the resource/node
        db: Database session dependency
        
    Returns:
        dict: Response with node_id, embedding vector, and dimensions
        
    Raises:
        HTTPException: If node is not found or embeddings not generated
    """
    try:
        embeddings_service = GraphEmbeddingsService(db)
        embedding = embeddings_service.get_embedding(node_id)
        
        if embedding is None:
            raise HTTPException(
                status_code=404,
                detail=f"No embedding found for node {node_id}. Generate embeddings first."
            )
        
        return {
            "node_id": str(node_id),
            "embedding": embedding,
            "dimensions": len(embedding)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving embedding for {node_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving embedding"
        )


@router.get(
    "/embeddings/{node_id}/similar",
    summary="Find similar nodes using embeddings",
    description=(
        "Find the most similar nodes to a given node based on graph embedding similarity. "
        "Uses cosine similarity to rank nodes by their structural similarity in the citation graph."
    ),
)
def get_similar_nodes(
    node_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of similar nodes to return"),
    min_similarity: float = Query(0.0, ge=0.0, le=1.0, description="Minimum similarity threshold"),
    db: Session = Depends(get_sync_db),
) -> dict:
    """
    Find similar nodes based on graph embedding similarity.
    
    This endpoint:
    1. Retrieves the embedding for the source node
    2. Computes cosine similarity with all other nodes
    3. Returns the top-N most similar nodes with scores
    
    Args:
        node_id: UUID of the source resource/node
        limit: Maximum number of similar nodes to return (default: 10)
        min_similarity: Minimum similarity threshold (default: 0.0)
        db: Database session dependency
        
    Returns:
        dict: Response with node_id, similar_nodes list, and count
        
    Raises:
        HTTPException: If node is not found or embeddings not generated
    """
    try:
        embeddings_service = GraphEmbeddingsService(db)
        similar_nodes = embeddings_service.find_similar_nodes(
            node_id,
            limit=limit,
            min_similarity=min_similarity
        )
        
        if not similar_nodes:
            # Check if it's because embeddings don't exist
            embedding = embeddings_service.get_embedding(node_id)
            if embedding is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"No embedding found for node {node_id}. Generate embeddings first."
                )
        
        # Format response with resource details
        from app.database.models import Resource
        
        results = []
        for similar_node_id, similarity in similar_nodes:
            try:
                resource_id = UUID(similar_node_id)
                resource = db.query(Resource).filter(Resource.id == resource_id).first()
                
                result = {
                    "node_id": similar_node_id,
                    "similarity": float(similarity),
                }
                
                if resource:
                    result["title"] = resource.title
                    result["type"] = resource.type
                
                results.append(result)
            except (ValueError, AttributeError):
                # Skip invalid node IDs
                continue
        
        logger.info(f"Found {len(results)} similar nodes for {node_id}")
        
        return {
            "node_id": str(node_id),
            "similar_nodes": results,
            "count": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar nodes for {node_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while finding similar nodes"
        )


# Literature-Based Discovery (LBD) Endpoints (Task 12.7)

@router.post(
    "/discover",
    summary="Discover hypotheses using ABC pattern",
    description=(
        "Discover novel connections between two concepts using the ABC pattern. "
        "Finds bridging concepts B that connect concept A to concept C through "
        "the literature. Returns hypotheses ranked by support strength and novelty. "
        "Target response time: <5 seconds for typical queries."
    ),
)
def discover_hypotheses(
    concept_a: str = Query(..., description="Starting concept to search for"),
    concept_c: str = Query(..., description="Target concept to connect to"),
    limit: int = Query(50, ge=1, le=100, description="Maximum hypotheses to return"),
    start_date: Optional[str] = Query(None, description="Start date for time-slicing (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date for time-slicing (ISO format)"),
    db: Session = Depends(get_sync_db),
) -> dict:
    """
    Discover hypotheses connecting two concepts using ABC pattern.
    
    This endpoint implements Literature-Based Discovery (LBD) to find
    novel connections between concepts in the literature.
    
    The ABC pattern:
    - A: Starting concept (e.g., "machine learning")
    - B: Bridging concept(s) discovered by the algorithm
    - C: Target concept (e.g., "drug discovery")
    
    The algorithm:
    1. Finds resources mentioning concept A
    2. Finds resources mentioning concept C
    3. Identifies bridging concepts B appearing with both A and C
    4. Filters out known A-C connections
    5. Ranks hypotheses by support strength and novelty
    6. Builds evidence chains showing A→B and B→C connections
    
    Args:
        concept_a: Starting concept
        concept_c: Target concept
        limit: Maximum hypotheses to return (default: 50)
        start_date: Optional start date for temporal filtering
        end_date: Optional end date for temporal filtering
        db: Database session dependency
        
    Returns:
        dict: Response with hypotheses list, count, and execution time
        
    Raises:
        HTTPException: If discovery fails or times out
    """
    import time
    from datetime import datetime
    
    start_time = time.time()
    
    try:
        from app.modules.graph.discovery import LBDService
        
        lbd_service = LBDService(db)
        
        # Parse time slice if provided
        time_slice = None
        if start_date and end_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                time_slice = (start_dt, end_dt)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date format: {str(e)}. Use ISO format (YYYY-MM-DD)"
                )
        
        # Discover hypotheses
        hypotheses = lbd_service.discover_hypotheses(
            concept_a=concept_a,
            concept_c=concept_c,
            limit=limit,
            time_slice=time_slice
        )
        
        execution_time = time.time() - start_time
        
        # Check performance target
        if execution_time > 5.0:
            logger.warning(
                f"LBD discovery exceeded 5s target: {execution_time:.2f}s "
                f"(A='{concept_a}', C='{concept_c}')"
            )
        
        logger.info(
            f"LBD discovery completed: {len(hypotheses)} hypotheses, "
            f"{execution_time:.2f}s (A='{concept_a}', C='{concept_c}')"
        )
        
        return {
            "concept_a": concept_a,
            "concept_c": concept_c,
            "hypotheses": hypotheses,
            "count": len(hypotheses),
            "execution_time": execution_time,
            "time_slice": {
                "start_date": start_date,
                "end_date": end_date
            } if time_slice else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in LBD discovery (A='{concept_a}', C='{concept_c}'): {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during hypothesis discovery"
        )


@router.get(
    "/hypotheses/{hypothesis_id}",
    summary="Get hypothesis details",
    description=(
        "Retrieve detailed information about a specific hypothesis, "
        "including evidence chains and support metrics."
    ),
)
def get_hypothesis(
    hypothesis_id: str,
    db: Session = Depends(get_sync_db),
) -> dict:
    """
    Get details for a specific hypothesis.
    
    This endpoint retrieves a stored hypothesis from the database
    with all its associated metadata and evidence.
    
    Args:
        hypothesis_id: UUID of the hypothesis
        db: Database session dependency
        
    Returns:
        dict: Hypothesis details including concepts, support, and evidence
        
    Raises:
        HTTPException: If hypothesis is not found
    """
    try:
        from app.modules.graph.model import DiscoveryHypothesis
        from app.database.models import Resource
        
        # Query hypothesis
        hypothesis = db.query(DiscoveryHypothesis).filter(
            DiscoveryHypothesis.id == UUID(hypothesis_id)
        ).first()
        
        if not hypothesis:
            raise HTTPException(
                status_code=404,
                detail=f"Hypothesis {hypothesis_id} not found"
            )
        
        # Get resource details
        a_resource = db.query(Resource).filter(
            Resource.id == hypothesis.a_resource_id
        ).first()
        
        c_resource = db.query(Resource).filter(
            Resource.id == hypothesis.c_resource_id
        ).first()
        
        # Parse B resource IDs
        try:
            if isinstance(hypothesis.b_resource_ids, str):
                b_resource_ids = json.loads(hypothesis.b_resource_ids)
            else:
                b_resource_ids = hypothesis.b_resource_ids or []
        except (json.JSONDecodeError, TypeError):
            b_resource_ids = []
        
        # Get B resources
        b_resources = []
        if b_resource_ids:
            b_resources_query = db.query(Resource).filter(
                Resource.id.in_([UUID(bid) for bid in b_resource_ids])
            ).all()
            
            b_resources = [
                {
                    "id": str(r.id),
                    "title": r.title,
                    "type": r.type,
                    "publication_year": r.publication_year
                }
                for r in b_resources_query
            ]
        
        logger.info(f"Retrieved hypothesis {hypothesis_id}")
        
        return {
            "id": str(hypothesis.id),
            "hypothesis_type": hypothesis.hypothesis_type,
            "a_resource": {
                "id": str(a_resource.id),
                "title": a_resource.title,
                "type": a_resource.type
            } if a_resource else None,
            "c_resource": {
                "id": str(c_resource.id),
                "title": c_resource.title,
                "type": c_resource.type
            } if c_resource else None,
            "b_resources": b_resources,
            "plausibility_score": hypothesis.plausibility_score,
            "path_strength": hypothesis.path_strength,
            "path_length": hypothesis.path_length,
            "common_neighbors": hypothesis.common_neighbors,
            "discovered_at": hypothesis.discovered_at.isoformat(),
            "is_validated": bool(hypothesis.is_validated) if hypothesis.is_validated is not None else None,
            "validation_notes": hypothesis.validation_notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving hypothesis {hypothesis_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving hypothesis"
        )
