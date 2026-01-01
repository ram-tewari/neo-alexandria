"""
Graph Event Handlers

Emits graph-related events for knowledge graph updates and discoveries.

Events Emitted:
- citation.extracted: When citations are extracted from a resource
- graph.updated: When the knowledge graph is updated
- hypothesis.discovered: When a new hypothesis is discovered via LBD
"""

import logging
from typing import Dict, Any, List

from app.shared.event_bus import event_bus, EventPriority

logger = logging.getLogger(__name__)


def emit_citation_extracted(
    resource_id: str,
    citations: List[Dict[str, Any]],
    citation_count: int
):
    """
    Emit citation.extracted event.
    
    This should be called after extracting citations from a resource.
    
    Args:
        resource_id: UUID of the resource
        citations: List of extracted citation dictionaries
        citation_count: Number of citations extracted
    """
    try:
        event_bus.emit(
            'citation.extracted',
            {
                'resource_id': resource_id,
                'citations': citations,
                'count': citation_count
            },
            priority=EventPriority.NORMAL
        )
        logger.debug(f"Emitted citation.extracted event for resource {resource_id}")
    except Exception as e:
        logger.error(f"Error emitting citation.extracted event: {str(e)}", exc_info=True)


def emit_graph_updated(
    update_type: str,
    node_count: int = 0,
    edge_count: int = 0,
    affected_nodes: List[str] = None
):
    """
    Emit graph.updated event.
    
    This should be called when the knowledge graph structure is updated.
    
    Args:
        update_type: Type of update (node_added, edge_added, node_removed, edge_removed, bulk_update)
        node_count: Number of nodes affected
        edge_count: Number of edges affected
        affected_nodes: Optional list of affected node IDs
    """
    try:
        payload = {
            'update_type': update_type,
            'node_count': node_count,
            'edge_count': edge_count
        }
        
        if affected_nodes:
            payload['affected_nodes'] = affected_nodes
        
        event_bus.emit(
            'graph.updated',
            payload,
            priority=EventPriority.NORMAL
        )
        logger.debug(f"Emitted graph.updated event: {update_type}")
    except Exception as e:
        logger.error(f"Error emitting graph.updated event: {str(e)}", exc_info=True)


def emit_hypothesis_discovered(
    hypothesis_id: str,
    concept_a: str,
    concept_c: str,
    bridging_concepts: List[str],
    plausibility_score: float,
    evidence_count: int
):
    """
    Emit hypothesis.discovered event.
    
    This should be called when a new hypothesis is discovered via Literature-Based Discovery.
    
    Args:
        hypothesis_id: UUID of the discovered hypothesis
        concept_a: Starting concept
        concept_c: Target concept
        bridging_concepts: List of bridging concepts (B)
        plausibility_score: Plausibility score of the hypothesis
        evidence_count: Number of evidence chains supporting the hypothesis
    """
    try:
        event_bus.emit(
            'hypothesis.discovered',
            {
                'hypothesis_id': hypothesis_id,
                'concept_a': concept_a,
                'concept_c': concept_c,
                'bridging_concepts': bridging_concepts,
                'plausibility_score': plausibility_score,
                'evidence_count': evidence_count
            },
            priority=EventPriority.HIGH
        )
        logger.info(f"Emitted hypothesis.discovered event for hypothesis {hypothesis_id}")
    except Exception as e:
        logger.error(f"Error emitting hypothesis.discovered event: {str(e)}", exc_info=True)


def register_handlers():
    """
    Register all event handlers for the graph module.
    
    This function should be called during application startup.
    Currently, graph module only emits events and doesn't subscribe to any.
    """
    logger.info("Graph module event handlers registered")
