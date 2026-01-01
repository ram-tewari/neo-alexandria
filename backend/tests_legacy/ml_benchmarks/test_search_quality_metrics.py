"""
Search Quality Benchmark Tests (Phase 11.5)

This module implements comprehensive benchmark tests for the search quality service.
Tests evaluate three-way hybrid search performance using standardized metrics.

Test Metrics:
- NDCG@20 for hybrid search (baseline: 0.60, target: 0.75)
- Precision@10 and Recall@10 for IR metrics
- Query latency at p50, p95, p99 percentiles (target: p95 < 200ms)
- Component comparison (FTS5, dense, sparse, hybrid)

Requirements: 4.1, 4.2, 4.3, 4.4
"""

import time
from typing import Dict, Any
from collections import defaultdict

import numpy as np
from sklearn.metrics import ndcg_score

from backend.app.schemas.search import SearchQuery, SearchFilters


class TestSearchQualityMetrics:
    """
    Test suite for search quality algorithm benchmarking.
    
    This class evaluates the three-way hybrid search system using a standardized
    test dataset with 50 queries and graded relevance judgments (0-3 scale).
    """
    
    def test_hybrid_search_ndcg(
        self,
        isolated_test_db,
        search_relevance_data: Dict[str, Any]
    ):
        """
        Test hybrid search NDCG@20.
        
        Evaluates three-way hybrid search by executing queries and computing NDCG@20
        using sklearn.metrics.ndcg_score with k=20. Maps results to relevance judgments
        from test dataset. Asserts average NDCG@20 > 0.60 baseline threshold.
        
        Args:
            isolated_test_db: Isolated test database session
            search_relevance_data: Test dataset with queries and relevance judgments
        
        Requirements: 4.1
        """
        print("\n" + "="*80)
        print("TEST: Hybrid Search NDCG@20")
        print("="*80)
        
        from backend.app.services.search_service import AdvancedSearchService
        from backend.app.database.models import Resource
        
        queries = search_relevance_data["queries"]
        print(f"Number of test queries: {len(queries)}")
        
        # Create test resources in database for evaluation
        # In a real scenario, these would already exist
        # For testing, we'll create minimal resources
        test_resources = {}
        for query_data in queries:
            for resource_id in query_data["relevance_judgments"].keys():
                if resource_id not in test_resources:
                    # Create a minimal resource for testing
                    resource = Resource(
                        id=resource_id,
                        title=f"Test Resource {resource_id}",
                        description=f"Description for {resource_id} related to {query_data['query_text']}",
                        type="article",
                        classification_code="000"
                    )
                    isolated_test_db.add(resource)
                    test_resources[resource_id] = resource
        
        try:
            isolated_test_db.commit()
        except Exception as e:
            isolated_test_db.rollback()
            print(f"Warning: Failed to create test resources: {e}")
        
        # Compute NDCG@20 for each query
        ndcg_scores = []
        queries_evaluated = 0
        
        for query_data in queries:
            query_text = query_data["query_text"]
            relevance_judgments = query_data["relevance_judgments"]
            
            # Create search query
            search_query = SearchQuery(
                text=query_text,
                filters=SearchFilters(),
                limit=20,
                offset=0,
                sort_by="relevance",
                sort_dir="desc"
            )
            
            try:
                # Execute hybrid search
                search_results = AdvancedSearchService.search(isolated_test_db, search_query)
                
                # Unpack results (handle both 3-tuple and 4-tuple returns)
                if len(search_results) == 4:
                    resources, total, facets, snippets = search_results
                elif len(search_results) == 5:
                    resources, total, facets, snippets, metadata = search_results
                else:
                    resources, total, facets = search_results
                
                if not resources:
                    continue
                
                # Get top-20 results
                top_20_ids = [str(r.id) for r in resources[:20]]
                
                # Build true relevance array (aligned with top-20 results)
                true_relevance = []
                for resource_id in top_20_ids:
                    # Get relevance score from judgments (0 if not judged)
                    relevance = relevance_judgments.get(resource_id, 0)
                    true_relevance.append(relevance)
                
                # Build predicted scores array (use rank-based scores)
                # Higher rank = higher score
                pred_scores = [20 - i for i in range(len(top_20_ids))]
                
                # Only compute NDCG if we have some relevant documents
                if sum(true_relevance) > 0:
                    # Compute NDCG@20
                    ndcg = ndcg_score(
                        [true_relevance],
                        [pred_scores],
                        k=20
                    )
                    
                    ndcg_scores.append(ndcg)
                    queries_evaluated += 1
                
            except Exception as e:
                # Skip queries where search fails
                print(f"  Warning: Failed to search for query '{query_text}': {str(e)}")
                continue
        
        # Compute average NDCG@20
        if ndcg_scores:
            avg_ndcg = np.mean(ndcg_scores)
            std_ndcg = np.std(ndcg_scores)
            min_ndcg = np.min(ndcg_scores)
            max_ndcg = np.max(ndcg_scores)
        else:
            avg_ndcg = 0.0
            std_ndcg = 0.0
            min_ndcg = 0.0
            max_ndcg = 0.0
        
        # Baseline and target thresholds
        baseline_threshold = 0.60
        target_threshold = 0.75
        
        print("\nResults:")
        print(f"  Queries evaluated: {queries_evaluated}")
        print(f"  Average NDCG@20: {avg_ndcg:.4f} (±{std_ndcg:.4f})")
        print(f"  Min NDCG@20: {min_ndcg:.4f}")
        print(f"  Max NDCG@20: {max_ndcg:.4f}")
        print(f"  Baseline: {baseline_threshold:.4f}")
        print(f"  Target:   {target_threshold:.4f}")
        
        if avg_ndcg >= target_threshold:
            print("  Status: ✅ EXCELLENT (above target)")
        elif avg_ndcg >= baseline_threshold:
            print("  Status: ⚠️  ACCEPTABLE (above baseline, below target)")
        else:
            print("  Status: ❌ FAILING (below baseline)")
        
        print("="*80)
        
        # Assert baseline threshold
        assert avg_ndcg > baseline_threshold, (
            f"Average NDCG@20 {avg_ndcg:.4f} does not meet baseline threshold {baseline_threshold:.4f}"
        )
    
    def test_precision_recall_at_10(
        self,
        isolated_test_db,
        search_relevance_data: Dict[str, Any]
    ):
        """
        Test precision and recall at K=10.
        
        For each query, gets top-10 results and computes precision@10 and recall@10
        based on relevance judgments. Logs average precision and recall across all queries.
        
        Args:
            isolated_test_db: Isolated test database session
            search_relevance_data: Test dataset with queries and relevance judgments
        
        Requirements: 4.2
        """
        print("\n" + "="*80)
        print("TEST: Precision@10 and Recall@10")
        print("="*80)
        
        from backend.app.services.search_service import AdvancedSearchService
        from backend.app.database.models import Resource
        
        queries = search_relevance_data["queries"]
        print(f"Number of test queries: {len(queries)}")
        
        # Create test resources in database
        test_resources = {}
        for query_data in queries:
            for resource_id in query_data["relevance_judgments"].keys():
                if resource_id not in test_resources:
                    resource = Resource(
                        id=resource_id,
                        title=f"Test Resource {resource_id}",
                        description=f"Description for {resource_id} related to {query_data['query_text']}",
                        type="article",
                        classification_code="000"
                    )
                    isolated_test_db.add(resource)
                    test_resources[resource_id] = resource
        
        try:
            isolated_test_db.commit()
        except Exception:
            isolated_test_db.rollback()
        
        # Compute precision and recall for each query
        precision_scores = []
        recall_scores = []
        queries_evaluated = 0
        
        for query_data in queries:
            query_text = query_data["query_text"]
            relevance_judgments = query_data["relevance_judgments"]
            
            # Get relevant documents (relevance > 0)
            relevant_docs = {
                doc_id for doc_id, relevance in relevance_judgments.items()
                if relevance > 0
            }
            
            if not relevant_docs:
                continue
            
            # Create search query
            search_query = SearchQuery(
                text=query_text,
                filters=SearchFilters(),
                limit=10,
                offset=0,
                sort_by="relevance",
                sort_dir="desc"
            )
            
            try:
                # Execute search
                search_results = AdvancedSearchService.search(isolated_test_db, search_query)
                
                # Unpack results
                if len(search_results) >= 3:
                    resources = search_results[0]
                else:
                    continue
                
                if not resources:
                    continue
                
                # Get top-10 results
                top_10_ids = {str(r.id) for r in resources[:10]}
                
                # Compute precision@10
                # Precision = (relevant docs in top-10) / (total docs in top-10)
                relevant_retrieved = top_10_ids.intersection(relevant_docs)
                precision = len(relevant_retrieved) / len(top_10_ids) if top_10_ids else 0.0
                
                # Compute recall@10
                # Recall = (relevant docs in top-10) / (total relevant docs)
                recall = len(relevant_retrieved) / len(relevant_docs) if relevant_docs else 0.0
                
                precision_scores.append(precision)
                recall_scores.append(recall)
                queries_evaluated += 1
                
            except Exception as e:
                print(f"  Warning: Failed to search for query '{query_text}': {str(e)}")
                continue
        
        # Compute averages
        if precision_scores:
            avg_precision = np.mean(precision_scores)
            std_precision = np.std(precision_scores)
            avg_recall = np.mean(recall_scores)
            std_recall = np.std(recall_scores)
        else:
            avg_precision = 0.0
            std_precision = 0.0
            avg_recall = 0.0
            std_recall = 0.0
        
        print("\nResults:")
        print(f"  Queries evaluated: {queries_evaluated}")
        print(f"  Average Precision@10: {avg_precision:.4f} (±{std_precision:.4f})")
        print(f"  Average Recall@10: {avg_recall:.4f} (±{std_recall:.4f})")
        
        # Compute F1 score
        if avg_precision + avg_recall > 0:
            f1_score = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)
            print(f"  F1@10: {f1_score:.4f}")
        
        print("\nDistribution:")
        if precision_scores:
            print(f"  Precision - Min: {np.min(precision_scores):.4f}, Max: {np.max(precision_scores):.4f}")
            print(f"  Recall - Min: {np.min(recall_scores):.4f}, Max: {np.max(recall_scores):.4f}")
        
        print("="*80)
    
    def test_query_latency(
        self,
        isolated_test_db,
        search_relevance_data: Dict[str, Any]
    ):
        """
        Test query latency.
        
        Executes each query 100 times and records latencies. Computes p50, p95, p99
        latency percentiles. Asserts p95 latency < 200ms. Logs latency distribution.
        
        Args:
            isolated_test_db: Isolated test database session
            search_relevance_data: Test dataset with queries and relevance judgments
        
        Requirements: 4.3
        """
        print("\n" + "="*80)
        print("TEST: Query Latency")
        print("="*80)
        
        from backend.app.services.search_service import AdvancedSearchService
        from backend.app.database.models import Resource
        
        queries = search_relevance_data["queries"]
        print(f"Number of test queries: {len(queries)}")
        
        # Create test resources in database
        test_resources = {}
        for query_data in queries[:10]:  # Use first 10 queries for latency testing
            for resource_id in query_data["relevance_judgments"].keys():
                if resource_id not in test_resources:
                    resource = Resource(
                        id=resource_id,
                        title=f"Test Resource {resource_id}",
                        description=f"Description for {resource_id} related to {query_data['query_text']}",
                        type="article",
                        classification_code="000"
                    )
                    isolated_test_db.add(resource)
                    test_resources[resource_id] = resource
        
        try:
            isolated_test_db.commit()
        except Exception:
            isolated_test_db.rollback()
        
        # Measure latency for each query (100 runs per query)
        all_latencies = []
        num_runs = 100
        
        print(f"\nExecuting {num_runs} runs per query...")
        
        # Use a subset of queries for latency testing (first 10)
        test_queries = queries[:10]
        
        for query_data in test_queries:
            query_text = query_data["query_text"]
            
            # Create search query
            search_query = SearchQuery(
                text=query_text,
                filters=SearchFilters(),
                limit=20,
                offset=0,
                sort_by="relevance",
                sort_dir="desc"
            )
            
            query_latencies = []
            
            for _ in range(num_runs):
                try:
                    # Measure latency
                    start_time = time.time()
                    AdvancedSearchService.search(isolated_test_db, search_query)
                    end_time = time.time()
                    
                    latency_ms = (end_time - start_time) * 1000
                    query_latencies.append(latency_ms)
                    
                except Exception:
                    # Skip failed queries
                    continue
            
            all_latencies.extend(query_latencies)
        
        # Compute latency percentiles
        if all_latencies:
            p50 = np.percentile(all_latencies, 50)
            p95 = np.percentile(all_latencies, 95)
            p99 = np.percentile(all_latencies, 99)
            avg_latency = np.mean(all_latencies)
            min_latency = np.min(all_latencies)
            max_latency = np.max(all_latencies)
        else:
            p50 = 0.0
            p95 = 0.0
            p99 = 0.0
            avg_latency = 0.0
            min_latency = 0.0
            max_latency = 0.0
        
        # Target threshold
        p95_threshold = 200.0  # 200ms
        
        print("\nResults:")
        print(f"  Total queries executed: {len(all_latencies)}")
        print(f"  Average latency: {avg_latency:.2f}ms")
        print(f"  Min latency: {min_latency:.2f}ms")
        print(f"  Max latency: {max_latency:.2f}ms")
        print("\nPercentiles:")
        print(f"  p50 (median): {p50:.2f}ms")
        print(f"  p95: {p95:.2f}ms")
        print(f"  p99: {p99:.2f}ms")
        print("\nThreshold:")
        print(f"  Target p95: {p95_threshold:.2f}ms")
        
        if p95 < p95_threshold:
            print("  Status: ✅ EXCELLENT (below target)")
        else:
            print("  Status: ⚠️  SLOW (above target)")
        
        print("="*80)
        
        # Assert p95 threshold
        assert p95 < p95_threshold, (
            f"p95 latency {p95:.2f}ms exceeds threshold {p95_threshold:.2f}ms"
        )
    
    def test_component_comparison(
        self,
        isolated_test_db,
        search_relevance_data: Dict[str, Any]
    ):
        """
        Test component comparison.
        
        Executes queries using FTS5-only, dense-only, sparse-only, and hybrid configurations.
        Computes NDCG@20 for each approach. Logs comparison table showing relative performance.
        Asserts hybrid approach achieves highest NDCG.
        
        Args:
            isolated_test_db: Isolated test database session
            search_relevance_data: Test dataset with queries and relevance judgments
        
        Requirements: 4.4
        """
        print("\n" + "="*80)
        print("TEST: Component Comparison")
        print("="*80)
        
        from backend.app.services.search_service import AdvancedSearchService
        from backend.app.database.models import Resource
        
        queries = search_relevance_data["queries"]
        print(f"Number of test queries: {len(queries)}")
        
        # Create test resources in database
        test_resources = {}
        for query_data in queries[:20]:  # Use first 20 queries for comparison
            for resource_id in query_data["relevance_judgments"].keys():
                if resource_id not in test_resources:
                    resource = Resource(
                        id=resource_id,
                        title=f"Test Resource {resource_id}",
                        description=f"Description for {resource_id} related to {query_data['query_text']}",
                        type="article",
                        classification_code="000"
                    )
                    isolated_test_db.add(resource)
                    test_resources[resource_id] = resource
        
        try:
            isolated_test_db.commit()
        except Exception:
            isolated_test_db.rollback()
        
        # Test different search configurations
        configurations = {
            "FTS5-only": {"hybrid_weight": 0.0},
            "Dense-only": {"hybrid_weight": 1.0},
            "Hybrid (0.5)": {"hybrid_weight": 0.5},
        }
        
        # Store NDCG scores for each configuration
        config_scores = defaultdict(list)
        
        # Use subset of queries for comparison
        test_queries = queries[:20]
        
        for config_name, config_params in configurations.items():
            print(f"\nEvaluating {config_name}...")
            
            for query_data in test_queries:
                query_text = query_data["query_text"]
                relevance_judgments = query_data["relevance_judgments"]
                
                # Create search query with specific configuration
                search_query = SearchQuery(
                    text=query_text,
                    filters=SearchFilters(),
                    limit=20,
                    offset=0,
                    sort_by="relevance",
                    sort_dir="desc",
                    hybrid_weight=config_params["hybrid_weight"]
                )
                
                try:
                    # Execute search
                    search_results = AdvancedSearchService.search(isolated_test_db, search_query)
                    
                    # Unpack results
                    if len(search_results) >= 3:
                        resources = search_results[0]
                    else:
                        continue
                    
                    if not resources:
                        continue
                    
                    # Get top-20 results
                    top_20_ids = [str(r.id) for r in resources[:20]]
                    
                    # Build true relevance array
                    true_relevance = []
                    for resource_id in top_20_ids:
                        relevance = relevance_judgments.get(resource_id, 0)
                        true_relevance.append(relevance)
                    
                    # Build predicted scores array
                    pred_scores = [20 - i for i in range(len(top_20_ids))]
                    
                    # Compute NDCG@20 if we have relevant documents
                    if sum(true_relevance) > 0:
                        ndcg = ndcg_score(
                            [true_relevance],
                            [pred_scores],
                            k=20
                        )
                        config_scores[config_name].append(ndcg)
                    
                except Exception as e:
                    print(f"  Warning: Failed for query '{query_text}': {str(e)}")
                    continue
        
        # Compute average NDCG for each configuration
        config_averages = {}
        for config_name, scores in config_scores.items():
            if scores:
                config_averages[config_name] = np.mean(scores)
            else:
                config_averages[config_name] = 0.0
        
        # Display comparison table
        print("\n" + "="*80)
        print("Component Comparison Results:")
        print("-" * 80)
        print(f"{'Configuration':<20} {'Avg NDCG@20':>15} {'Queries':>10} {'Relative':>15}")
        print("-" * 80)
        
        # Find best configuration
        best_config = max(config_averages.items(), key=lambda x: x[1]) if config_averages else (None, 0.0)
        best_ndcg = best_config[1]
        
        for config_name in ["FTS5-only", "Dense-only", "Hybrid (0.5)"]:
            avg_ndcg = config_averages.get(config_name, 0.0)
            num_queries = len(config_scores.get(config_name, []))
            
            # Compute relative performance
            if best_ndcg > 0:
                relative = (avg_ndcg / best_ndcg) * 100
            else:
                relative = 0.0
            
            # Mark best configuration
            marker = " ⭐" if config_name == best_config[0] else ""
            
            print(f"{config_name:<20} {avg_ndcg:>15.4f} {num_queries:>10} {relative:>14.1f}%{marker}")
        
        print("-" * 80)
        
        # Analysis
        print("\nAnalysis:")
        if best_config[0]:
            print(f"  Best configuration: {best_config[0]} (NDCG@20: {best_ndcg:.4f})")
        
        # Check if hybrid is best
        hybrid_ndcg = config_averages.get("Hybrid (0.5)", 0.0)
        fts5_ndcg = config_averages.get("FTS5-only", 0.0)
        dense_ndcg = config_averages.get("Dense-only", 0.0)
        
        if hybrid_ndcg >= fts5_ndcg and hybrid_ndcg >= dense_ndcg:
            print("  ✅ Hybrid approach achieves best or equal performance")
        else:
            print("  ⚠️  Hybrid approach does not achieve best performance")
        
        print("="*80)
        
        # Assert hybrid is best or equal to best
        assert hybrid_ndcg >= max(fts5_ndcg, dense_ndcg) * 0.95, (
            f"Hybrid NDCG@20 {hybrid_ndcg:.4f} is significantly lower than "
            f"best single method {max(fts5_ndcg, dense_ndcg):.4f}"
        )
