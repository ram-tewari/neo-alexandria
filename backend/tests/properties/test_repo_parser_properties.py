"""
Property-based tests for Repository Parser (Phase 19).

**Feature: phase19-hybrid-edge-cloud-orchestration**

These tests verify universal properties of the repository parser service
using property-based testing with hypothesis.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck, assume

from app.utils.repo_parser import RepositoryParser, DependencyGraph


# ============================================================================
# Test Helpers
# ============================================================================


def create_test_repository(num_python_files: int = 5, num_js_files: int = 3) -> str:
    """
    Create a temporary test repository with source files.
    
    Args:
        num_python_files: Number of Python files to create
        num_js_files: Number of JavaScript files to create
        
    Returns:
        Path to temporary repository
    """
    temp_dir = tempfile.mkdtemp(prefix="test_repo_")
    
    # Create Python files
    for i in range(num_python_files):
        file_path = Path(temp_dir) / f"module_{i}.py"
        with open(file_path, 'w') as f:
            f.write(f"# Python module {i}\n")
            if i > 0:
                f.write(f"import module_{i-1}\n")
            f.write(f"def function_{i}():\n    pass\n")
    
    # Create JavaScript files
    for i in range(num_js_files):
        file_path = Path(temp_dir) / f"script_{i}.js"
        with open(file_path, 'w') as f:
            f.write(f"// JavaScript module {i}\n")
            if i > 0:
                f.write(f"import {{ func }} from './script_{i-1}.js';\n")
            f.write(f"export function func{i}() {{}}\n")
    
    return temp_dir


# ============================================================================
# Property 5: Repository Processing Pipeline Completeness
# **Validates: Requirements 4.1, 4.2, 4.3**
# ============================================================================


@settings(
    max_examples=10,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
@given(
    num_python_files=st.integers(min_value=1, max_value=10),
    num_js_files=st.integers(min_value=0, max_value=5),
)
def test_property_5_repository_processing_completeness(
    num_python_files: int,
    num_js_files: int
):
    """
    **Feature: phase19-hybrid-edge-cloud-orchestration, Property 5: Repository Processing Pipeline Completeness**
    
    For any successfully cloned repository, all source files should be parsed,
    a dependency graph should be built, and the graph should have at least as
    many nodes as there are source files.
    
    **Validates: Requirements 4.1, 4.2, 4.3**
    """
    # Create test repository
    repo_path = create_test_repository(num_python_files, num_js_files)
    
    try:
        # Initialize parser
        parser = RepositoryParser()
        
        # Build dependency graph
        graph = parser.build_dependency_graph(repo_path)
        
        # Verify graph properties
        total_files = num_python_files + num_js_files
        
        # Property 1: Graph should have at least as many nodes as source files
        assert graph.num_nodes >= total_files, \
            f"Graph has {graph.num_nodes} nodes but expected at least {total_files}"
        
        # Property 2: All file paths should be valid
        for file_path in graph.file_paths:
            if file_path != "<empty>":  # Skip empty placeholder
                assert os.path.exists(file_path) or file_path.startswith(repo_path), \
                    f"File path {file_path} is invalid"
        
        # Property 3: Edge index should have correct shape
        assert graph.edge_index.shape[0] == 2, \
            f"Edge index should have 2 rows, got {graph.edge_index.shape[0]}"
        
        # Property 4: Edge index should have at least one edge (self-loops if nothing else)
        assert graph.edge_index.shape[1] > 0, \
            "Edge index should have at least one edge"
        
        # Property 5: All edge indices should be valid node indices
        max_node_idx = graph.num_nodes - 1
        for edge_idx in graph.edge_index.flatten():
            assert 0 <= edge_idx <= max_node_idx, \
                f"Edge index {edge_idx} is out of bounds [0, {max_node_idx}]"
        
    finally:
        # Cleanup
        shutil.rmtree(repo_path, ignore_errors=True)


# ============================================================================
# Additional Property Tests
# ============================================================================


@settings(
    max_examples=10,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
@given(
    num_files=st.integers(min_value=1, max_value=10),
)
def test_property_all_source_files_discovered(num_files: int):
    """
    Property: All source files in repository should be discovered.
    
    For any repository with N source files, the parser should find all N files.
    """
    repo_path = create_test_repository(num_python_files=num_files, num_js_files=0)
    
    try:
        parser = RepositoryParser()
        
        # Find source files
        found_files = parser._find_source_files(repo_path)
        
        # Should find exactly num_files Python files
        assert len(found_files) == num_files, \
            f"Expected {num_files} files, found {len(found_files)}"
        
        # All found files should exist
        for file_path in found_files:
            assert os.path.exists(file_path), f"File {file_path} does not exist"
        
    finally:
        shutil.rmtree(repo_path, ignore_errors=True)


@settings(
    max_examples=10,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
@given(
    num_files=st.integers(min_value=2, max_value=8),
)
def test_property_import_extraction_consistency(num_files: int):
    """
    Property: Import extraction should be consistent across multiple runs.
    
    For any file, extracting imports multiple times should yield the same result.
    """
    repo_path = create_test_repository(num_python_files=num_files, num_js_files=0)
    
    try:
        parser = RepositoryParser()
        
        # Get a source file
        files = parser._find_source_files(repo_path)
        assume(len(files) > 0)
        
        test_file = files[0]
        
        # Extract imports multiple times
        imports_1 = parser._extract_imports(test_file)
        imports_2 = parser._extract_imports(test_file)
        imports_3 = parser._extract_imports(test_file)
        
        # Should be consistent
        assert imports_1 == imports_2 == imports_3, \
            "Import extraction should be deterministic"
        
    finally:
        shutil.rmtree(repo_path, ignore_errors=True)


@settings(
    max_examples=5,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
@given(dummy=st.just(None))  # Add dummy parameter for hypothesis
def test_property_empty_repository_handling(dummy):
    """
    Property: Empty repositories should be handled gracefully.
    
    For any empty repository, the parser should return a valid graph with
    a single empty node and self-loop.
    """
    # Create empty repository
    temp_dir = tempfile.mkdtemp(prefix="empty_repo_")
    
    try:
        parser = RepositoryParser()
        
        # Build graph for empty repository
        graph = parser.build_dependency_graph(temp_dir)
        
        # Should have exactly 1 node (empty placeholder)
        assert graph.num_nodes == 1, \
            f"Empty repository should have 1 node, got {graph.num_nodes}"
        
        # Should have exactly 1 edge (self-loop)
        assert graph.edge_index.shape[1] == 1, \
            f"Empty repository should have 1 edge, got {graph.edge_index.shape[1]}"
        
        # File paths should contain empty placeholder
        assert graph.file_paths == ["<empty>"], \
            f"Empty repository should have ['<empty>'] file paths, got {graph.file_paths}"
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@settings(
    max_examples=10,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
@given(
    num_files=st.integers(min_value=1, max_value=8),
)
def test_property_cleanup_removes_files(num_files: int):
    """
    Property: Cleanup should remove all temporary files.
    
    For any repository path, calling cleanup should remove the directory.
    """
    repo_path = create_test_repository(num_python_files=num_files, num_js_files=0)
    
    # Verify directory exists
    assert os.path.exists(repo_path), "Repository should exist before cleanup"
    
    # Cleanup
    parser = RepositoryParser()
    parser.cleanup(repo_path)
    
    # Verify directory is removed
    assert not os.path.exists(repo_path), \
        "Repository should be removed after cleanup"
