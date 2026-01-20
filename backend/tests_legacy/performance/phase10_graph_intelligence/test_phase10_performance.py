"""
Performance tests for Phase 10: Advanced Graph Intelligence & Literature-Based Discovery

Tests performance requirements:
- 2-hop query latency (<500ms for 5,000 nodes)
- HNSW query latency (<100ms for 10,000 nodes)
- Graph construction time (<30s for 10,000 resources)
- Graph2Vec computation rate (>100 nodes/minute)
- Memory usage monitoring
"""

import pytest
import time
import psutil
import os
from sqlalchemy.orm import Session
from backend.app.database.models import Resource, Citation, GraphEmbedding
from backend.app.services.graph_service import GraphService
from backend.app.services.graph_embeddings_service import GraphEmbeddingsService
from backend.app.services.lbd_service import LBDService
import uuid
import json


class PerformanceMonitor:
    """Helper class to monitor performance metrics."""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_time = None
        self.start_memory = None

    def start(self):
        """Start monitoring."""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB

    def stop(self):
        """Stop monitoring and return metrics."""
        elapsed_time = time.time() - self.start_time
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = end_memory - self.start_memory

        return {
            "elapsed_time": elapsed_time,
            "start_memory_mb": self.start_memory,
            "end_memory_mb": end_memory,
            "memory_delta_mb": memory_delta,
        }


def create_large_test_dataset(db_session: Session, size: int = 1000):
    """Create a large test dataset for performance testing."""
    resources = []

    print(f"\nCreating {size} test resources...")

    # Create resources in batches
    batch_size = 100
    for batch_start in range(0, size, batch_size):
        batch_resources = []
        for i in range(batch_start, min(batch_start + batch_size, size)):
            resource = Resource(
                id=uuid.uuid4(),
                title=f"Performance Test Resource {i}",
                authors=json.dumps([f"Author {i % 100}", f"Author {(i + 1) % 100}"]),
                publication_year=2000 + (i % 24),
                type="article",
                embedding=[0.001 * (i % 768)] * 768,
                quality_overall=0.5 + (i % 50) * 0.01,
            )
            batch_resources.append(resource)
            resources.append(resource)

        db_session.bulk_save_objects(batch_resources)
        db_session.commit()

        if (batch_start + batch_size) % 500 == 0:
            print(f"  Created {batch_start + batch_size} resources...")

    print(f"Created {len(resources)} resources")

    # Create citation network (sparse, ~2 citations per resource on average)
    print("Creating citation network...")
    citations = []
    for i in range(0, size - 1, 1):
        if i + 1 < size:
            citation = Citation(
                id=uuid.uuid4(),
                source_resource_id=resources[i].id,
                target_resource_id=resources[i + 1].id,
                target_url=f"https://example.com/resource-{i + 1}",
                citation_type="direct",
                context_snippet=f"Citation {i}",
            )
            citations.append(citation)

            # Add some random citations for connectivity
            if i % 10 == 0 and i + 10 < size:
                citation2 = Citation(
                    id=uuid.uuid4(),
                    source_resource_id=resources[i].id,
                    target_resource_id=resources[i + 10].id,
                    target_url=f"https://example.com/resource-{i + 10}",
                    citation_type="direct",
                    context_snippet=f"Citation {i}-skip",
                )
                citations.append(citation2)

    db_session.bulk_save_objects(citations)
    db_session.commit()

    print(f"Created {len(citations)} citations")

    return resources


class TestGraphConstructionPerformance:
    """Test graph construction performance."""

    @pytest.mark.performance
    @pytest.mark.parametrize("size", [1000, 5000])
    def test_graph_construction_time(self, test_db, size: int):
        """
        Test graph construction completes within time limits.

        Requirements:
        - Less than 30s for 10,000 resources
        - Proportionally faster for smaller graphs
        """
        db_session = test_db()
        # Create test dataset
        create_large_test_dataset(db_session, size=size)

        # Monitor performance
        monitor = PerformanceMonitor()
        monitor.start()

        # Build graph
        graph_service = GraphService(db_session)
        graph = graph_service.build_multilayer_graph(refresh_cache=True)

        metrics = monitor.stop()

        # Calculate expected time (linear scaling from 30s for 10k)
        expected_time = (size / 10000) * 30

        print(f"\n=== Graph Construction Performance ({size} nodes) ===")
        print(f"Time: {metrics['elapsed_time']:.2f}s (expected: <{expected_time:.2f}s)")
        print(f"Memory: {metrics['memory_delta_mb']:.2f} MB")
        print(f"Nodes: {graph.number_of_nodes()}")
        print(f"Edges: {graph.number_of_edges()}")

        # Assert performance requirements
        assert metrics["elapsed_time"] < expected_time, (
            f"Graph construction took {metrics['elapsed_time']:.2f}s, expected <{expected_time:.2f}s"
        )

        # Memory should be reasonable (<500MB for 10k nodes)
        expected_memory = (size / 10000) * 500
        assert metrics["memory_delta_mb"] < expected_memory, (
            f"Memory usage {metrics['memory_delta_mb']:.2f}MB exceeds expected {expected_memory:.2f}MB"
        )


class TestTwoHopQueryPerformance:
    """Test 2-hop neighbor query performance."""

    @pytest.mark.performance
    @pytest.mark.parametrize("size", [1000, 5000])
    def test_two_hop_query_latency(self, test_db, size: int):
        """
        Test 2-hop neighbor queries complete within latency limits.

        Requirements:
        - Less than 500ms for 5,000 node graphs
        - Proportionally faster for smaller graphs
        """
        db_session = test_db()
        # Create test dataset and build graph
        resources = create_large_test_dataset(db_session, size=size)
        graph_service = GraphService(db_session)
        graph_service.build_multilayer_graph(refresh_cache=True)

        # Test multiple queries to get average latency
        num_queries = 10
        total_time = 0

        print(f"\n=== 2-Hop Query Performance ({size} nodes) ===")

        for i in range(num_queries):
            # Pick a random resource
            test_resource = resources[i * (size // num_queries)]

            monitor = PerformanceMonitor()
            monitor.start()

            # Perform 2-hop query
            neighbors = graph_service.get_neighbors_multihop(
                resource_id=str(test_resource.id), hops=2, limit=50
            )

            metrics = monitor.stop()
            total_time += metrics["elapsed_time"]

            print(
                f"Query {i + 1}: {metrics['elapsed_time'] * 1000:.2f}ms, found {len(neighbors)} neighbors"
            )

        avg_time = total_time / num_queries

        # Calculate expected time (linear scaling from 500ms for 5k)
        expected_time = (size / 5000) * 0.5

        print(
            f"Average latency: {avg_time * 1000:.2f}ms (expected: <{expected_time * 1000:.2f}ms)"
        )

        # Assert performance requirements
        assert avg_time < expected_time, (
            f"Average 2-hop query took {avg_time * 1000:.2f}ms, expected <{expected_time * 1000:.2f}ms"
        )


class TestHNSWQueryPerformance:
    """Test HNSW index query performance."""

    @pytest.mark.performance
    @pytest.mark.parametrize("size", [1000, 5000, 10000])
    def test_hnsw_query_latency(self, test_db, size: int):
        """
        Test HNSW k-NN queries complete within latency limits.

        Requirements:
        - Less than 100ms for 10,000 node graphs
        """
        db_session = test_db()
        # Create test dataset
        resources = create_large_test_dataset(db_session, size=size)

        # Create graph embeddings
        print(f"\nCreating {size} graph embeddings...")
        for i, resource in enumerate(resources):
            graph_embedding = GraphEmbedding(
                id=uuid.uuid4(),
                resource_id=resource.id,
                structural_embedding=[0.01 * (i % 128)] * 128,
                fusion_embedding=[0.01 * (i % 128)] * 128,
                embedding_method="fusion",
                embedding_version="v1.0",
            )
            db_session.add(graph_embedding)

            if (i + 1) % 1000 == 0:
                db_session.commit()
                print(f"  Created {i + 1} embeddings...")

        db_session.commit()

        # Build HNSW index
        print("Building HNSW index...")
        embeddings_service = GraphEmbeddingsService(db_session)

        build_monitor = PerformanceMonitor()
        build_monitor.start()

        embeddings_service.build_hnsw_index()

        build_metrics = build_monitor.stop()
        print(f"Index build time: {build_metrics['elapsed_time']:.2f}s")

        # Test multiple queries
        num_queries = 20
        total_time = 0

        print(f"\n=== HNSW Query Performance ({size} nodes) ===")

        for i in range(num_queries):
            test_resource = resources[i * (size // num_queries)]

            monitor = PerformanceMonitor()
            monitor.start()

            # Perform k-NN query
            neighbors = embeddings_service.query_hnsw_index(
                resource_id=str(test_resource.id), k=10
            )

            metrics = monitor.stop()
            total_time += metrics["elapsed_time"]

            if i < 5:  # Print first 5 queries
                print(
                    f"Query {i + 1}: {metrics['elapsed_time'] * 1000:.2f}ms, found {len(neighbors)} neighbors"
                )

        avg_time = total_time / num_queries

        print(f"Average latency: {avg_time * 1000:.2f}ms (expected: <100ms)")

        # Assert performance requirements
        assert avg_time < 0.1, (
            f"Average HNSW query took {avg_time * 1000:.2f}ms, expected <100ms"
        )


class TestGraph2VecPerformance:
    """Test Graph2Vec embedding computation performance."""

    @pytest.mark.performance
    @pytest.mark.slow
    def test_graph2vec_computation_rate(self, test_db):
        """
        Test Graph2Vec computes embeddings at required rate.

        Requirements:
        - Greater than 100 nodes/minute
        """
        db_session = test_db()
        # Create smaller test dataset for Graph2Vec (it's computationally expensive)
        size = 200
        create_large_test_dataset(db_session, size=size)

        # Build graph
        graph_service = GraphService(db_session)
        graph_service.build_multilayer_graph(refresh_cache=True)

        # Compute Graph2Vec embeddings
        print(f"\n=== Graph2Vec Performance ({size} nodes) ===")

        embeddings_service = GraphEmbeddingsService(db_session)

        monitor = PerformanceMonitor()
        monitor.start()

        embeddings_service.compute_graph2vec_embeddings(dimensions=128, wl_iterations=2)

        metrics = monitor.stop()

        # Calculate rate
        nodes_per_minute = (size / metrics["elapsed_time"]) * 60

        print(f"Time: {metrics['elapsed_time']:.2f}s")
        print(f"Rate: {nodes_per_minute:.2f} nodes/minute (expected: >100)")
        print(f"Memory: {metrics['memory_delta_mb']:.2f} MB")

        # Assert performance requirements
        assert nodes_per_minute > 100, (
            f"Graph2Vec computed at {nodes_per_minute:.2f} nodes/minute, expected >100"
        )


class TestMemoryUsage:
    """Test memory usage stays within acceptable limits."""

    @pytest.mark.performance
    def test_graph_cache_memory(self, test_db):
        """
        Test graph cache memory usage.

        Requirements:
        - Less than 500MB for 10,000 nodes
        """
        db_session = test_db()
        size = 5000  # Test with 5k nodes
        create_large_test_dataset(db_session, size=size)

        # Get baseline memory
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Build and cache graph
        graph_service = GraphService(db_session)
        graph = graph_service.build_multilayer_graph(refresh_cache=True)

        # Measure memory after caching
        cached_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = cached_memory - baseline_memory

        # Calculate expected memory (linear scaling from 500MB for 10k)
        expected_memory = (size / 10000) * 500

        print(f"\n=== Graph Cache Memory ({size} nodes) ===")
        print(f"Baseline: {baseline_memory:.2f} MB")
        print(f"Cached: {cached_memory:.2f} MB")
        print(f"Delta: {memory_delta:.2f} MB (expected: <{expected_memory:.2f} MB)")
        print(f"Nodes: {graph.number_of_nodes()}")
        print(f"Edges: {graph.number_of_edges()}")

        # Assert memory requirements
        assert memory_delta < expected_memory, (
            f"Graph cache used {memory_delta:.2f}MB, expected <{expected_memory:.2f}MB"
        )

    @pytest.mark.performance
    def test_hnsw_index_memory(self, test_db):
        """
        Test HNSW index memory usage.

        Requirements:
        - Less than 200MB for 10,000 nodes with 128-dim embeddings
        """
        db_session = test_db()
        size = 5000
        resources = create_large_test_dataset(db_session, size=size)

        # Create embeddings
        for resource in resources:
            graph_embedding = GraphEmbedding(
                id=uuid.uuid4(),
                resource_id=resource.id,
                fusion_embedding=[0.01] * 128,
                embedding_method="fusion",
                embedding_version="v1.0",
            )
            db_session.add(graph_embedding)

        db_session.commit()

        # Get baseline memory
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Build HNSW index
        embeddings_service = GraphEmbeddingsService(db_session)
        embeddings_service.build_hnsw_index()

        # Measure memory after indexing
        indexed_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = indexed_memory - baseline_memory

        # Calculate expected memory (linear scaling from 200MB for 10k)
        expected_memory = (size / 10000) * 200

        print(f"\n=== HNSW Index Memory ({size} nodes) ===")
        print(f"Baseline: {baseline_memory:.2f} MB")
        print(f"Indexed: {indexed_memory:.2f} MB")
        print(f"Delta: {memory_delta:.2f} MB (expected: <{expected_memory:.2f} MB)")

        # Assert memory requirements
        assert memory_delta < expected_memory, (
            f"HNSW index used {memory_delta:.2f}MB, expected <{expected_memory:.2f}MB"
        )


class TestDiscoveryPerformance:
    """Test LBD discovery performance."""

    @pytest.mark.performance
    def test_open_discovery_latency(self, test_db):
        """Test open discovery completes in reasonable time."""
        db_session = test_db()
        size = 1000
        resources = create_large_test_dataset(db_session, size=size)

        # Build graph
        graph_service = GraphService(db_session)
        graph_service.build_multilayer_graph(refresh_cache=True)

        # Test open discovery
        lbd_service = LBDService(db_session)

        monitor = PerformanceMonitor()
        monitor.start()

        hypotheses = lbd_service.open_discovery(
            a_resource_id=str(resources[0].id), limit=20, min_plausibility=0.0
        )

        metrics = monitor.stop()

        print("\n=== Open Discovery Performance ===")
        print(f"Time: {metrics['elapsed_time'] * 1000:.2f}ms")
        print(f"Hypotheses found: {len(hypotheses)}")

        # Should complete in under 2 seconds
        assert metrics["elapsed_time"] < 2.0, (
            f"Open discovery took {metrics['elapsed_time']:.2f}s, expected <2s"
        )

    @pytest.mark.performance
    def test_closed_discovery_latency(self, test_db):
        """Test closed discovery completes in reasonable time."""
        db_session = test_db()
        size = 1000
        resources = create_large_test_dataset(db_session, size=size)

        # Build graph
        graph_service = GraphService(db_session)
        graph_service.build_multilayer_graph(refresh_cache=True)

        # Test closed discovery
        lbd_service = LBDService(db_session)

        monitor = PerformanceMonitor()
        monitor.start()

        paths = lbd_service.closed_discovery(
            a_resource_id=str(resources[0].id),
            c_resource_id=str(resources[10].id),
            max_hops=3,
        )

        metrics = monitor.stop()

        print("\n=== Closed Discovery Performance ===")
        print(f"Time: {metrics['elapsed_time'] * 1000:.2f}ms")
        print(f"Paths found: {len(paths)}")

        # Should complete in under 1 second
        assert metrics["elapsed_time"] < 1.0, (
            f"Closed discovery took {metrics['elapsed_time']:.2f}s, expected <1s"
        )


# Pytest configuration for performance tests
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-m", "performance"])
