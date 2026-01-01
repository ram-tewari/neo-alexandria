"""
Graph Module - PageRank Tests

Tests for PageRank algorithm using Golden Data pattern.
All test expectations are loaded from golden_data/graph_algorithms.json.

NO inline expected values - all assertions use Golden Data.
"""

import networkx as nx
from tests.protocol import load_golden_data


class TestPageRank:
    """Test suite for PageRank algorithm using Golden Data."""
    
    def test_pagerank_simple_network(self):
        """
        Test PageRank calculation on a simple citation network.
        
        Golden Data Case: simple_citation_network
        Network: 4 nodes (A, B, C, D) with directed edges
        Expected: PageRank scores with tolerance 0.01
        
        **Validates: Requirements 4.1, 4.2, 8.2, 8.3**
        """
        # Load Golden Data to get inputs
        golden_data = load_golden_data("graph_algorithms")
        test_case = golden_data["simple_citation_network"]
        
        # Build NetworkX graph from golden data input
        G = nx.DiGraph()
        
        # Add nodes
        nodes = test_case["input"]["nodes"]
        G.add_nodes_from(nodes)
        
        # Add edges
        edges = test_case["input"]["edges"]
        for edge in edges:
            G.add_edge(edge["from"], edge["to"])
        
        # Calculate PageRank scores
        pagerank_scores = nx.pagerank(G)
        
        # Get expected values and tolerance from golden data
        expected_scores = test_case["expected"]["pagerank"]
        tolerance = test_case["expected"]["tolerance"]
        
        # Verify each node's PageRank score against golden data
        for node in nodes:
            actual_score = pagerank_scores[node]
            expected_score = expected_scores[node]
            
            # Use tolerance-based comparison
            assert abs(actual_score - expected_score) <= tolerance, (
                f"IMPLEMENTATION FAILURE: PageRank score mismatch for node '{node}'.\n"
                f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
                f"\n"
                f"Golden Data File: golden_data/graph_algorithms.json\n"
                f"Test Case ID: simple_citation_network\n"
                f"\n"
                f"Expected score: {expected_score}\n"
                f"Actual score: {actual_score}\n"
                f"Difference: {abs(actual_score - expected_score)} (tolerance: {tolerance})"
            )
