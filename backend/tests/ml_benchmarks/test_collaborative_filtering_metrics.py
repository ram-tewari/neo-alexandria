"""
Collaborative Filtering Benchmark Tests (Phase 11.5)

This module implements comprehensive benchmark tests for the NCF (Neural Collaborative Filtering) model.
Tests evaluate recommendation quality using industry-standard ranking metrics.

Test Metrics:
- NDCG@10 (baseline: 0.30, target: 0.50)
- Hit Rate@10 (baseline: 0.40, target: 0.60)
- Cold start performance (success rate > 0.5)

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

from typing import Dict, Any
from collections import defaultdict

import pytest
import numpy as np
from sklearn.metrics import ndcg_score


class TestCollaborativeFilteringMetrics:
    """
    Test suite for collaborative filtering algorithm benchmarking.
    
    This class evaluates the NCF model using a standardized test dataset
    with 50 users, 200 items, and 1000 interactions with 20% held-out for testing.
    """
    
    def test_ndcg_at_10(
        self,
        trained_ncf_model,
        recommendation_test_data: Dict[str, Any]
    ):
        """
        Test NDCG@10 for held-out test cases.
        
        Groups test cases by user_id, predicts scores for all candidate items,
        and computes NDCG@10 using sklearn.metrics.ndcg_score with k=10.
        Asserts average NDCG@10 > 0.30 baseline threshold.
        
        Args:
            trained_ncf_model: Pre-trained NCF model fixture
            recommendation_test_data: Test dataset with interactions and held-out test cases
        
        Requirements: 3.1
        """
        print("\n" + "="*80)
        print("TEST: NDCG@10 (Normalized Discounted Cumulative Gain)")
        print("="*80)
        
        held_out_test = recommendation_test_data["held_out_test"]
        print(f"Number of held-out test cases: {len(held_out_test)}")
        
        # Group test cases by user_id
        user_test_cases = defaultdict(list)
        for test_case in held_out_test:
            user_id = test_case["user_id"]
            resource_id = test_case["resource_id"]
            is_relevant = test_case["is_relevant"]
            user_test_cases[user_id].append((resource_id, is_relevant))
        
        print(f"Number of unique users in test set: {len(user_test_cases)}")
        
        # Compute NDCG@10 for each user
        ndcg_scores = []
        
        for user_id, test_items in user_test_cases.items():
            # Get all candidate items for this user
            candidate_ids = [item_id for item_id, _ in test_items]
            
            # Get predicted scores from NCF model
            try:
                # Predict scores for all candidate items
                predictions = trained_ncf_model.predict_batch(user_id, candidate_ids)
                
                if not predictions:
                    continue
                
                # Create true relevance array (1 for relevant, 0 for not relevant)
                true_relevance = [1 if is_rel else 0 for _, is_rel in test_items]
                
                # Create predicted scores array (aligned with candidate_ids)
                pred_scores = [predictions.get(item_id, 0.0) for item_id in candidate_ids]
                
                # Compute NDCG@10
                # sklearn expects shape (1, n_samples) for single query
                ndcg = ndcg_score(
                    [true_relevance],
                    [pred_scores],
                    k=10
                )
                
                ndcg_scores.append(ndcg)
                
            except Exception as e:
                # Skip users where prediction fails
                print(f"  Warning: Failed to predict for user {user_id}: {str(e)}")
                continue
        
        # Compute average NDCG@10
        if ndcg_scores:
            avg_ndcg = np.mean(ndcg_scores)
            std_ndcg = np.std(ndcg_scores)
        else:
            avg_ndcg = 0.0
            std_ndcg = 0.0
        
        # Baseline and target thresholds
        baseline_threshold = 0.30
        target_threshold = 0.50
        
        print("\nResults:")
        print(f"  Users evaluated: {len(ndcg_scores)}")
        print(f"  Average NDCG@10: {avg_ndcg:.4f} (±{std_ndcg:.4f})")
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
            f"Average NDCG@10 {avg_ndcg:.4f} does not meet baseline threshold {baseline_threshold:.4f}"
        )
    
    def test_hit_rate_at_10(
        self,
        trained_ncf_model,
        recommendation_test_data: Dict[str, Any]
    ):
        """
        Test Hit Rate@10.
        
        For each user, gets top-10 predictions and checks if any relevant item
        appears in top-10. Computes hit rate as proportion of users with hits.
        Asserts hit rate > 0.40 baseline threshold.
        
        Args:
            trained_ncf_model: Pre-trained NCF model fixture
            recommendation_test_data: Test dataset with interactions and held-out test cases
        
        Requirements: 3.2
        """
        print("\n" + "="*80)
        print("TEST: Hit Rate@10")
        print("="*80)
        
        held_out_test = recommendation_test_data["held_out_test"]
        print(f"Number of held-out test cases: {len(held_out_test)}")
        
        # Group test cases by user_id
        user_test_cases = defaultdict(list)
        for test_case in held_out_test:
            user_id = test_case["user_id"]
            resource_id = test_case["resource_id"]
            is_relevant = test_case["is_relevant"]
            user_test_cases[user_id].append((resource_id, is_relevant))
        
        print(f"Number of unique users in test set: {len(user_test_cases)}")
        
        # Compute hit rate
        hits = 0
        total_users = 0
        
        for user_id, test_items in user_test_cases.items():
            # Get all candidate items for this user
            candidate_ids = [item_id for item_id, _ in test_items]
            
            # Get relevant items for this user
            relevant_items = {item_id for item_id, is_rel in test_items if is_rel}
            
            if not relevant_items:
                # Skip users with no relevant items
                continue
            
            try:
                # Predict scores for all candidate items
                predictions = trained_ncf_model.predict_batch(user_id, candidate_ids)
                
                if not predictions:
                    total_users += 1
                    continue
                
                # Get top-10 predictions
                sorted_predictions = sorted(
                    predictions.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
                
                top_10_items = {item_id for item_id, _ in sorted_predictions}
                
                # Check if any relevant item in top-10
                if top_10_items.intersection(relevant_items):
                    hits += 1
                
                total_users += 1
                
            except Exception as e:
                # Skip users where prediction fails
                print(f"  Warning: Failed to predict for user {user_id}: {str(e)}")
                total_users += 1
                continue
        
        # Compute hit rate
        hit_rate = hits / total_users if total_users > 0 else 0.0
        
        # Baseline and target thresholds
        baseline_threshold = 0.40
        target_threshold = 0.60
        
        print("\nResults:")
        print(f"  Users evaluated: {total_users}")
        print(f"  Users with hits: {hits}")
        print(f"  Hit Rate@10: {hit_rate:.4f} ({hit_rate*100:.1f}%)")
        print(f"  Baseline: {baseline_threshold:.4f}")
        print(f"  Target:   {target_threshold:.4f}")
        
        if hit_rate >= target_threshold:
            print("  Status: ✅ EXCELLENT (above target)")
        elif hit_rate >= baseline_threshold:
            print("  Status: ⚠️  ACCEPTABLE (above baseline, below target)")
        else:
            print("  Status: ❌ FAILING (below baseline)")
        
        print("="*80)
        
        # Assert baseline threshold
        assert hit_rate > baseline_threshold, (
            f"Hit Rate@10 {hit_rate:.4f} does not meet baseline threshold {baseline_threshold:.4f}"
        )
    
    def test_cold_start_performance(
        self,
        trained_ncf_model,
        recommendation_test_data: Dict[str, Any]
    ):
        """
        Test cold start performance.
        
        Filters users with <5 interactions, attempts predictions for cold start users,
        and measures success rate (proportion of users with valid predictions).
        Asserts cold start success rate > 0.5.
        Logs number of cold start users and success rate.
        
        Args:
            trained_ncf_model: Pre-trained NCF model fixture
            recommendation_test_data: Test dataset with interactions and held-out test cases
        
        Requirements: 3.4
        """
        print("\n" + "="*80)
        print("TEST: Cold Start Performance")
        print("="*80)
        
        interactions = recommendation_test_data["interactions"]
        held_out_test = recommendation_test_data["held_out_test"]
        
        # Count interactions per user
        user_interaction_counts = defaultdict(int)
        for interaction in interactions:
            user_id = interaction["user_id"]
            user_interaction_counts[user_id] += 1
        
        # Identify cold start users (<5 interactions)
        cold_start_threshold = 5
        cold_start_users = {
            user_id for user_id, count in user_interaction_counts.items()
            if count < cold_start_threshold
        }
        
        print(f"Total users: {len(user_interaction_counts)}")
        print(f"Cold start users (<{cold_start_threshold} interactions): {len(cold_start_users)}")
        
        if not cold_start_users:
            print("\n⚠️  No cold start users in dataset")
            print("="*80)
            pytest.skip("No cold start users available for testing")
        
        # Group test cases by user_id for cold start users only
        cold_start_test_cases = defaultdict(list)
        for test_case in held_out_test:
            user_id = test_case["user_id"]
            if user_id in cold_start_users:
                resource_id = test_case["resource_id"]
                cold_start_test_cases[user_id].append(resource_id)
        
        print(f"Cold start users in test set: {len(cold_start_test_cases)}")
        
        # Attempt predictions for cold start users
        successful_predictions = 0
        total_cold_start_users = 0
        
        for user_id, candidate_ids in cold_start_test_cases.items():
            try:
                # Attempt to predict for cold start user
                predictions = trained_ncf_model.predict_batch(user_id, candidate_ids)
                
                # Check if we got valid predictions
                if predictions and len(predictions) > 0:
                    # Check if predictions have reasonable scores (not all zeros)
                    scores = list(predictions.values())
                    if any(score > 0 for score in scores):
                        successful_predictions += 1
                
                total_cold_start_users += 1
                
            except Exception:
                # Prediction failed for this cold start user
                total_cold_start_users += 1
                continue
        
        # Compute success rate
        success_rate = successful_predictions / total_cold_start_users if total_cold_start_users > 0 else 0.0
        
        # Baseline threshold
        baseline_threshold = 0.5
        
        print("\nResults:")
        print(f"  Cold start users tested: {total_cold_start_users}")
        print(f"  Successful predictions: {successful_predictions}")
        print(f"  Success rate: {success_rate:.4f} ({success_rate*100:.1f}%)")
        print(f"  Baseline: {baseline_threshold:.4f}")
        
        if success_rate >= baseline_threshold:
            print("  Status: ✅ ACCEPTABLE (above baseline)")
        else:
            print("  Status: ❌ FAILING (below baseline)")
        
        # Show interaction distribution for cold start users
        cold_start_interaction_counts = [
            user_interaction_counts[user_id]
            for user_id in cold_start_test_cases.keys()
        ]
        
        if cold_start_interaction_counts:
            print("\nCold Start User Interaction Distribution:")
            print(f"  Min interactions: {min(cold_start_interaction_counts)}")
            print(f"  Max interactions: {max(cold_start_interaction_counts)}")
            print(f"  Avg interactions: {np.mean(cold_start_interaction_counts):.2f}")
        
        print("="*80)
        
        # Assert baseline threshold
        assert success_rate > baseline_threshold, (
            f"Cold start success rate {success_rate:.4f} does not meet "
            f"baseline threshold {baseline_threshold:.4f}"
        )
