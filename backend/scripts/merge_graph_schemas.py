"""
Script to merge graph-related schemas into modules/graph/schema.py
"""

from pathlib import Path

def main():
    """Merge graph, discovery, and citation schemas."""
    base_dir = Path(__file__).parent.parent
    schemas_dir = base_dir / "app" / "schemas"
    graph_module_dir = base_dir / "app" / "modules" / "graph"
    
    # Read source files
    graph_schema = (schemas_dir / "graph.py").read_text(encoding='utf-8')
    discovery_schema = (schemas_dir / "discovery.py").read_text(encoding='utf-8')
    citation_schema = (schemas_dir / "citation.py").read_text(encoding='utf-8')
    
    # Create merged content
    merged_content = '''"""
Neo Alexandria 2.0 - Graph Module Schemas

Pydantic models for graph, citation, and discovery operations.
Merged from app/schemas/graph.py, app/schemas/discovery.py, and app/schemas/citation.py

Related files:
- app/modules/graph/service.py: Core graph operations
- app/modules/graph/citations.py: Citation service
- app/modules/graph/discovery.py: LBD service
- app/modules/graph/router.py: Graph API endpoints
- app/modules/graph/citations_router.py: Citation API endpoints
- app/modules/graph/discovery_router.py: Discovery API endpoints
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# GRAPH SCHEMAS (from app/schemas/graph.py)
# ============================================================================

'''
    
    # Extract class definitions from graph.py (skip imports and docstring)
    lines = graph_schema.split('\n')
    in_class = False
    class_content = []
    for line in lines:
        if line.startswith('class '):
            in_class = True
        if in_class:
            class_content.append(line)
    
    merged_content += '\n'.join(class_content)
    
    merged_content += '''

# ============================================================================
# DISCOVERY SCHEMAS (from app/schemas/discovery.py)
# ============================================================================

'''
    
    # Extract class definitions from discovery.py
    lines = discovery_schema.split('\n')
    in_class = False
    class_content = []
    skip_resource_summary = False
    for line in lines:
        if line.startswith('class ResourceSummary'):
            skip_resource_summary = True
            continue
        if skip_resource_summary and line and not line[0].isspace():
            skip_resource_summary = False
        if skip_resource_summary:
            continue
        if line.startswith('class '):
            in_class = True
        if in_class:
            class_content.append(line)
    
    merged_content += '\n'.join(class_content)
    
    merged_content += '''

# ============================================================================
# CITATION SCHEMAS (from app/schemas/citation.py)
# ============================================================================

'''
    
    # Extract class definitions from citation.py (skip duplicates)
    lines = citation_schema.split('\n')
    in_class = False
    class_content = []
    skip_classes = {'ResourceSummary', 'GraphNode', 'GraphEdge'}
    current_class = None
    skip_current = False
    
    for line in lines:
        if line.startswith('class '):
            current_class = line.split('class ')[1].split('(')[0].strip()
            if current_class in skip_classes:
                skip_current = True
                continue
            else:
                skip_current = False
                in_class = True
        
        if skip_current:
            if line and not line[0].isspace() and not line.startswith('class '):
                skip_current = False
            else:
                continue
        
        if in_class:
            class_content.append(line)
    
    merged_content += '\n'.join(class_content)
    
    # Write merged file
    dest_path = graph_module_dir / "schema.py"
    dest_path.write_text(merged_content, encoding='utf-8')
    
    print(f"✓ Merged schemas into {dest_path}")

if __name__ == "__main__":
    main()
