"""
Scholarly Event Handlers

Emits scholarly metadata extraction events.

Events Emitted:
- metadata.extracted: When scholarly metadata is extracted from a resource
- equations.parsed: When equations are parsed from content
- tables.extracted: When tables are extracted from content
"""

import logging
from typing import Dict, Any, List

from app.shared.event_bus import event_bus, EventPriority

logger = logging.getLogger(__name__)


def emit_metadata_extracted(
    resource_id: str,
    metadata: Dict[str, Any],
    equation_count: int = 0,
    table_count: int = 0,
    figure_count: int = 0,
):
    """
    Emit metadata.extracted event.

    This should be called by the metadata extractor after extracting scholarly metadata.

    Args:
        resource_id: UUID of the resource
        metadata: Dictionary of extracted metadata
        equation_count: Number of equations extracted
        table_count: Number of tables extracted
        figure_count: Number of figures extracted
    """
    try:
        event_bus.emit(
            "metadata.extracted",
            {
                "resource_id": resource_id,
                "metadata": metadata,
                "equation_count": equation_count,
                "table_count": table_count,
                "figure_count": figure_count,
            },
            priority=EventPriority.LOW,
        )
        logger.debug(f"Emitted metadata.extracted event for resource {resource_id}")
    except Exception as e:
        logger.error(
            f"Error emitting metadata.extracted event: {str(e)}", exc_info=True
        )


def emit_equations_parsed(
    resource_id: str, equations: List[Dict[str, Any]], equation_count: int
):
    """
    Emit equations.parsed event.

    This should be called after parsing equations from content.

    Args:
        resource_id: UUID of the resource
        equations: List of parsed equation dictionaries
        equation_count: Number of equations parsed
    """
    try:
        event_bus.emit(
            "equations.parsed",
            {
                "resource_id": resource_id,
                "equations": equations,
                "equation_count": equation_count,
            },
            priority=EventPriority.LOW,
        )
        logger.debug(f"Emitted equations.parsed event for resource {resource_id}")
    except Exception as e:
        logger.error(f"Error emitting equations.parsed event: {str(e)}", exc_info=True)


def emit_tables_extracted(
    resource_id: str, tables: List[Dict[str, Any]], table_count: int
):
    """
    Emit tables.extracted event.

    This should be called after extracting tables from content.

    Args:
        resource_id: UUID of the resource
        tables: List of extracted table dictionaries
        table_count: Number of tables extracted
    """
    try:
        event_bus.emit(
            "tables.extracted",
            {"resource_id": resource_id, "tables": tables, "table_count": table_count},
            priority=EventPriority.LOW,
        )
        logger.debug(f"Emitted tables.extracted event for resource {resource_id}")
    except Exception as e:
        logger.error(f"Error emitting tables.extracted event: {str(e)}", exc_info=True)


def register_handlers():
    """
    Register all event handlers for the scholarly module.

    This function should be called during application startup.
    Currently, scholarly module only emits events and doesn't subscribe to any.
    """
    logger.info("Scholarly module event handlers registered")
