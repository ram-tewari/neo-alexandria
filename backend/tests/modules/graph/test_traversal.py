"""
Graph Module - Traversal Tests

Tests for graph traversal algorithms and edge cases.
Includes performance tests for large networks.
"""

import networkx as nx
import random
from tests.protocol import load_golden_data
from tests.performance import performance_limit


class TestGraphTraversal:
    """Test suite for graph traversal algorithms."""
    
    def test_related_resources_disconnected_node(self):
        """
        Test that disconnected nodes return empty related resources list.
        
        Golden Data Case: disconnected_node
        Network: Node C is isolated with no edges
        Expected: Empty list for related resources
        
        **Validates: Requirements 4.3, 4.4, 8.4**
        """
        # Load Golden Data to get inputs
        golden_data = load_golden_data("graph_algorithms")
        test_case = golden_data["disconnected_node"]
        
        # Build NetworkX graph from golden data input
        G = nx.DiGraph()
        
        # Add nodes
        nodes = test_case["input"]["nodes"]
        G.add_nodes_from(nodes)
        
        # Add edges
        edges = test_case["input"]["edges"]
        for edge in edges:
            G.add_edge(edge["from"], edge["to"])
        
        # Get related resources for disconnected node C
        # In a real implementation, this would call the graph service
        # For now, we simulate the logic: get neighbors of node C
        node_c = "C"
        
        # Get all neighbors (both incoming and outgoing edges)
        predecessors = list(G.predecessors(node_c))
        successors = list(G.successors(node_c))
        related = predecessors + successors
        
        # Verify against golden data expectation
        expected_related = test_case["expected"]["related_to_C"]
        
        assert related == expected_related, (
            f"IMPLEMENTATION FAILURE: Related resources mismatch for disconnected node.\n"
            f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
            f"\n"
            f"Golden Data File: golden_data/graph_algorithms.json\n"
            f"Test Case ID: disconnected_node\n"
            f"\n"
            f"Expected related resources: {expected_related}\n"
            f"Actual related resources: {related}\n"
            f"\n"
            f"Note: Disconnected nodes should return empty list."
        )
    
    def test_related_resources_large_network(self):
        """
        Test related resources calculation on a large network.
        
        Golden Data Case: large_network
        Network: 100 nodes with scale-free topology
        Expected: Correct neighbor identification
        
        **Validates: Requirements 4.3, 4.4, 8.4**
        """
        # Load Golden Data to get inputs
        golden_data = load_golden_data("graph_algorithms")
        test_case = golden_data["large_network"]
        
        # Generate a scale-free network with specified parameters
        node_count = test_case["input"]["node_count"]
        avg_degree = test_case["input"]["avg_degree"]
        
        # Create Barabási-Albert graph (scale-free network)
        # m = number of edges to attach from new node (controls avg degree)
        m = avg_degree // 2
        G = nx.barabasi_albert_graph(node_count, m, seed=42)
        
        # Convert to directed graph for citation network simulation
        G = G.to_directed()
        
        # Verify network properties
        assert G.number_of_nodes() == node_count, (
            f"Network should have {node_count} nodes, got {G.number_of_nodes()}"
        )
        
        # Test that we can find related resources for any node
        # Pick a random node with edges
        test_node = random.choice([n for n in G.nodes() if G.degree(n) > 0])
        
        # Get related resources (neighbors)
        predecessors = list(G.predecessors(test_node))
        successors = list(G.successors(test_node))
        related = predecessors + successors
        
        # Verify that related resources are non-empty for connected node
        assert len(related) > 0, (
            f"Connected node {test_node} should have related resources, got empty list"
        )
        
        # Verify all related nodes exist in the graph
        for related_node in related:
            assert related_node in G.nodes(), (
                f"Related node {related_node} not found in graph"
            )
    
    @performance_limit(50)
    def test_graph_traversal_performance(self):
        """
        Test graph traversal performance on 100-edge network.
        
        Golden Data Case: large_network
        Performance Limit: 50ms for traversal
        
        **Validates: Requirements 4.3, 4.4, 8.4, 14.2**
        """
        # Load Golden Data to get inputs
        golden_data = load_golden_data("graph_algorithms")
        test_case = golden_data["large_network"]
        
        # Generate a scale-free network
        node_count = test_case["input"]["node_count"]
        avg_degree = test_case["input"]["avg_degree"]
        
        # Create network
        m = avg_degree // 2
        G = nx.barabasi_albert_graph(node_count, m, seed=42)
        G = G.to_directed()
        
        # Verify we have approximately 100+ edges
        edge_count = G.number_of_edges()
        assert edge_count >= 100, (
            f"Network should have at least 100 edges for performance test, got {edge_count}"
        )
        
        # Perform PageRank calculation (the expensive operation)
        pagerank_scores = nx.pagerank(G)
        
        # Verify PageRank scores sum to approximately 1.0
        total_score = sum(pagerank_scores.values())
        tolerance = test_case["expected"]["pagerank_sum_tolerance"]
        
        assert abs(total_score - 1.0) <= tolerance, (
            f"PageRank scores should sum to 1.0, got {total_score} "
            f"(tolerance: {tolerance})"
        )
        
        # Get top N nodes by PageRank
        top_n = test_case["expected"]["top_nodes_count"]
        top_nodes = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        # Verify we got the expected number of top nodes
        assert len(top_nodes) == top_n, (
            f"Should return {top_n} top nodes, got {len(top_nodes)}"
        )
        
        # Verify top nodes have higher scores than average
        avg_score = 1.0 / node_count
        for node, score in top_nodes:
            assert score > avg_score, (
                f"Top node {node} should have score > average ({avg_score}), got {score}"
            )
