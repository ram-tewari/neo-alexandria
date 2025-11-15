"""
Recommendation quality and diversity metrics for Phase 11.

This module provides functions to measure recommendation system performance:
- Gini coefficient for diversity measurement
- Click-through rate (CTR) tracking by strategy
- Novelty score calculation

Related files:
- app/services/hybrid_recommendation_service.py: Uses these metrics
- app/routers/recommendations.py: Returns metrics in API responses
- app/database/models.py: RecommendationFeedback model for CTR tracking
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database.models import RecommendationFeedback, UserInteraction

logger = logging.getLogger(__name__)


def compute_gini_coefficient(scores: List[float]) -> float:
    """
    Compute Gini coefficient to measure diversity of recommendation scores.
    
    The Gini coefficient measures inequality in a distribution:
    - 0.0 = perfect equality (all scores are the same, maximum diversity)
    - 1.0 = perfect inequality (one score dominates, no diversity)
    
    For recommendations, we want Gini < 0.3 to ensure diverse results.
    
    Args:
        scores: List of recommendation scores (hybrid scores, relevance scores, etc.)
        
    Returns:
        Gini coefficient between 0.0 and 1.0
        
    Requirements: 6.4, 9.5
    
    Example:
        >>> scores = [0.9, 0.8, 0.7, 0.6, 0.5]
        >>> gini = compute_gini_coefficient(scores)
        >>> print(f"Gini: {gini:.3f}")  # Should be < 0.3 for diverse recommendations
    """
    if not scores or len(scores) == 0:
        logger.warning("Empty scores list provided to compute_gini_coefficient")
        return 0.0
    
    if len(scores) == 1:
        return 0.0  # Single score has perfect equality
    
    try:
        # Convert to numpy array and sort
        sorted_scores = np.sort(np.array(scores, dtype=float))
        n = len(sorted_scores)
        
        # Handle all zeros case
        if np.sum(sorted_scores) == 0:
            return 0.0
        
        # Compute Gini coefficient using the formula:
        # G = (2 * sum(i * x_i)) / (n * sum(x_i)) - (n + 1) / n
        # where x_i are sorted values and i is the rank (1-indexed)
        cumsum = np.cumsum(sorted_scores)
        gini = (2.0 * np.sum((np.arange(1, n + 1)) * sorted_scores)) / (n * cumsum[-1]) - (n + 1) / n
        
        # Ensure result is in valid range [0, 1]
        gini = max(0.0, min(1.0, gini))
        
        logger.debug(f"Computed Gini coefficient: {gini:.4f} for {n} scores")
        return gini
        
    except Exception as e:
        logger.error(f"Error computing Gini coefficient: {str(e)}", exc_info=True)
        return 0.0


def compute_ctr(
    db: Session,
    user_id: str,
    time_window_days: int = 30,
    strategy: Optional[str] = None
) -> Dict[str, float]:
    """
    Compute click-through rate (CTR) for recommendations.
    
    CTR = (number of clicked recommendations) / (total recommendations shown)
    
    Tracks CTR overall and by strategy (collaborative, content, graph, hybrid).
    Target: 40% improvement over baseline content-only recommendations.
    
    Args:
        db: Database session
        user_id: User ID to compute CTR for
        time_window_days: Number of days to look back (default 30)
        strategy: Optional strategy filter ("collaborative", "content", "graph", "hybrid")
        
    Returns:
        Dictionary with CTR metrics:
        {
            "overall_ctr": 0.35,
            "collaborative_ctr": 0.42,
            "content_ctr": 0.30,
            "graph_ctr": 0.38,
            "hybrid_ctr": 0.45,
            "total_recommendations": 100,
            "total_clicks": 35
        }
        
    Requirements: 9.4, 9.5
    
    Example:
        >>> ctr_metrics = compute_ctr(db, user_id="user123", time_window_days=30)
        >>> print(f"Overall CTR: {ctr_metrics['overall_ctr']:.2%}")
    """
    try:
        # Calculate time window
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        
        # Base query for recommendations in time window
        base_query = db.query(RecommendationFeedback).filter(
            RecommendationFeedback.user_id == user_id,
            RecommendationFeedback.recommended_at >= cutoff_date
        )
        
        # Apply strategy filter if provided
        if strategy:
            base_query = base_query.filter(
                RecommendationFeedback.recommendation_strategy == strategy
            )
        
        # Get total recommendations
        total_recommendations = base_query.count()
        
        if total_recommendations == 0:
            logger.info(f"No recommendations found for user {user_id} in last {time_window_days} days")
            return {
                "overall_ctr": 0.0,
                "collaborative_ctr": 0.0,
                "content_ctr": 0.0,
                "graph_ctr": 0.0,
                "hybrid_ctr": 0.0,
                "total_recommendations": 0,
                "total_clicks": 0
            }
        
        # Get total clicks
        total_clicks = base_query.filter(
            RecommendationFeedback.was_clicked == 1
        ).count()
        
        # Calculate overall CTR
        overall_ctr = total_clicks / total_recommendations if total_recommendations > 0 else 0.0
        
        # Calculate CTR by strategy
        strategy_ctrs = {}
        for strat in ["collaborative", "content", "graph", "hybrid"]:
            strat_query = db.query(RecommendationFeedback).filter(
                RecommendationFeedback.user_id == user_id,
                RecommendationFeedback.recommended_at >= cutoff_date,
                RecommendationFeedback.recommendation_strategy == strat
            )
            
            strat_total = strat_query.count()
            strat_clicks = strat_query.filter(
                RecommendationFeedback.was_clicked == 1
            ).count()
            
            strategy_ctrs[f"{strat}_ctr"] = (
                strat_clicks / strat_total if strat_total > 0 else 0.0
            )
        
        result = {
            "overall_ctr": overall_ctr,
            **strategy_ctrs,
            "total_recommendations": total_recommendations,
            "total_clicks": total_clicks
        }
        
        logger.info(
            f"CTR for user {user_id} (last {time_window_days} days): "
            f"{overall_ctr:.2%} ({total_clicks}/{total_recommendations})"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error computing CTR for user {user_id}: {str(e)}", exc_info=True)
        return {
            "overall_ctr": 0.0,
            "collaborative_ctr": 0.0,
            "content_ctr": 0.0,
            "graph_ctr": 0.0,
            "hybrid_ctr": 0.0,
            "total_recommendations": 0,
            "total_clicks": 0
        }


def compute_novelty_score(
    db: Session,
    recommendations: List[Dict],
    top_viewed_threshold: int = 100
) -> Dict[str, float]:
    """
    Compute novelty metrics for a set of recommendations.
    
    Novelty measures how many recommendations come from outside the most popular
    (top-viewed) resources. Novel recommendations help users discover hidden gems.
    
    Target: 20%+ of recommendations should be novel (outside top-viewed resources).
    
    Args:
        db: Database session
        recommendations: List of recommendation dicts with 'resource_id' keys
        top_viewed_threshold: Number of resources to consider as "top-viewed" (default 100)
        
    Returns:
        Dictionary with novelty metrics:
        {
            "novelty_percentage": 0.25,  # 25% of recommendations are novel
            "novel_count": 5,
            "total_count": 20,
            "avg_novelty_score": 0.35  # Average novelty score across all recommendations
        }
        
    Requirements: 7.3, 9.5
    
    Example:
        >>> recommendations = [{"resource_id": "uuid1", "score": 0.9}, ...]
        >>> novelty = compute_novelty_score(db, recommendations)
        >>> print(f"Novel recommendations: {novelty['novelty_percentage']:.1%}")
    """
    if not recommendations or len(recommendations) == 0:
        logger.warning("Empty recommendations list provided to compute_novelty_score")
        return {
            "novelty_percentage": 0.0,
            "novel_count": 0,
            "total_count": 0,
            "avg_novelty_score": 0.0
        }
    
    try:
        # Get resource IDs from recommendations
        resource_ids = [rec.get("resource_id") for rec in recommendations if rec.get("resource_id")]
        
        if not resource_ids:
            logger.warning("No valid resource_ids in recommendations")
            return {
                "novelty_percentage": 0.0,
                "novel_count": 0,
                "total_count": len(recommendations),
                "avg_novelty_score": 0.0
            }
        
        # Get view counts for recommended resources
        # Count interactions of type "view" for each resource
        view_counts_query = db.query(
            UserInteraction.resource_id,
            func.count(UserInteraction.id).label('view_count')
        ).filter(
            UserInteraction.resource_id.in_(resource_ids),
            UserInteraction.interaction_type == 'view'
        ).group_by(
            UserInteraction.resource_id
        ).all()
        
        # Create mapping of resource_id to view_count
        view_counts = {str(row.resource_id): row.view_count for row in view_counts_query}
        
        # Get top-viewed resources globally (for comparison)
        top_viewed_query = db.query(
            UserInteraction.resource_id,
            func.count(UserInteraction.id).label('view_count')
        ).filter(
            UserInteraction.interaction_type == 'view'
        ).group_by(
            UserInteraction.resource_id
        ).order_by(
            func.count(UserInteraction.id).desc()
        ).limit(top_viewed_threshold).all()
        
        # Get the minimum view count to be in top-viewed
        if top_viewed_query:
            top_viewed_ids = {str(row.resource_id) for row in top_viewed_query}
            median_view_count = np.median([row.view_count for row in top_viewed_query])
        else:
            top_viewed_ids = set()
            median_view_count = 1.0
        
        # Calculate novelty for each recommendation
        novelty_scores = []
        novel_count = 0
        
        for rec in recommendations:
            resource_id = str(rec.get("resource_id", ""))
            if not resource_id:
                continue
            
            # Check if resource is in top-viewed
            is_novel = resource_id not in top_viewed_ids
            if is_novel:
                novel_count += 1
            
            # Calculate novelty score: 1.0 - (view_count / median_view_count)
            # Higher score = more novel (less viewed)
            view_count = view_counts.get(resource_id, 0)
            if median_view_count > 0:
                novelty_score = max(0.0, 1.0 - (view_count / median_view_count))
            else:
                novelty_score = 1.0  # No views = maximum novelty
            
            novelty_scores.append(novelty_score)
        
        # Calculate metrics
        total_count = len(resource_ids)
        novelty_percentage = novel_count / total_count if total_count > 0 else 0.0
        avg_novelty_score = np.mean(novelty_scores) if novelty_scores else 0.0
        
        result = {
            "novelty_percentage": novelty_percentage,
            "novel_count": novel_count,
            "total_count": total_count,
            "avg_novelty_score": float(avg_novelty_score)
        }
        
        logger.info(
            f"Novelty metrics: {novelty_percentage:.1%} novel "
            f"({novel_count}/{total_count}), avg score: {avg_novelty_score:.3f}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error computing novelty score: {str(e)}", exc_info=True)
        return {
            "novelty_percentage": 0.0,
            "novel_count": 0,
            "total_count": len(recommendations),
            "avg_novelty_score": 0.0
        }
