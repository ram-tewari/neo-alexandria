"""
Neo Alexandria 2.0 - Quality Service

Combined implementation with QualityService and ContentQualityAnalyzer.
"""

from typing import Dict, List, Optional, Any, Mapping
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import json
import re
from urllib.parse import urlparse

from backend.app.utils import text_processor as tp


HIGH_QUALITY_THRESHOLD = 0.8
MEDIUM_QUALITY_THRESHOLD = 0.5


class ContentQualityAnalyzer:
    """Compute content quality metrics for a resource and its text."""

    REQUIRED_KEYS = [
        "title",
        "description",
        "subject",
        "creator",
        "language",
        "type",
        "identifier",
    ]

    def metadata_completeness(self, resource_in: Mapping[str, Any] | Any) -> float:
        """Return ratio of required fields that are present and non-empty."""
        present = 0
        total = len(self.REQUIRED_KEYS)
        for key in self.REQUIRED_KEYS:
            value = None
            if isinstance(resource_in, Mapping):
                value = resource_in.get(key)
            else:
                value = getattr(resource_in, key, None)
            if value is None:
                continue
            if isinstance(value, str) and not value.strip():
                continue
            if isinstance(value, list) and len(value) == 0:
                continue
            present += 1
        return present / total if total else 0.0

    def text_readability(self, text: str) -> Dict[str, float]:
        return tp.readability_scores(text)

    def overall_quality(self, resource_in: Dict[str, Any], text: str | None) -> float:
        meta_score = self.metadata_completeness(resource_in)
        if not text:
            return meta_score
        scores = self.text_readability(text)
        norm_read = max(0.0, min(1.0, (scores.get("reading_ease", 0.0) + 30.0) / 151.0))
        return 0.6 * meta_score + 0.4 * norm_read

    def quality_level(self, score: float) -> str:
        if score >= HIGH_QUALITY_THRESHOLD:
            return "HIGH"
        if score >= MEDIUM_QUALITY_THRESHOLD:
            return "MEDIUM"
        return "LOW"
    
    def source_credibility(self, source: Optional[str]) -> float:
        """Assess source credibility based on URL/identifier."""
        if not source:
            return 0.5
        
        # Simple heuristics for credibility
        source_lower = source.lower()
        
        # High credibility domains
        high_cred_domains = ['.edu', '.gov', 'arxiv.org', 'doi.org', 'pubmed', 'scholar.google']
        if any(domain in source_lower for domain in high_cred_domains):
            return 0.9
        
        # Medium credibility
        medium_cred_domains = ['.org', 'wikipedia', 'github']
        if any(domain in source_lower for domain in medium_cred_domains):
            return 0.7
        
        # Default credibility
        return 0.6
    
    def content_depth(self, text: Optional[str]) -> float:
        """Assess content depth based on text length and complexity."""
        if not text:
            return 0.0
        
        word_count = len(text.split())
        
        # Score based on word count
        if word_count < 100:
            return 0.3
        elif word_count < 500:
            return 0.6
        elif word_count < 2000:
            return 0.8
        else:
            return 0.9
    
    def _normalize_reading_ease(self, reading_ease: float) -> float:
        """Normalize Flesch Reading Ease score to 0-1 range.
        
        Flesch Reading Ease typically ranges from 0-100:
        - 90-100: Very easy
        - 60-70: Standard
        - 0-30: Very difficult
        
        We normalize to 0-1 where higher is better.
        """
        # Clamp to reasonable range
        clamped = max(0.0, min(100.0, reading_ease))
        # Normalize to 0-1
        return clamped / 100.0


class QualityService:
    """Quality service for computing and monitoring resource quality."""
    
    def __init__(self, db: Session, quality_version: str = "v2.0"):
        self.db = db
        self.quality_version = quality_version
    
    def compute_quality(self, resource_id: str, weights: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """Compute quality scores for a resource."""
        from backend.app.database.models import Resource
        
        # Default weights
        if weights is None:
            weights = {
                "accuracy": 0.25,
                "completeness": 0.25,
                "consistency": 0.20,
                "timeliness": 0.15,
                "relevance": 0.15
            }
        
        # Validate weights
        if set(weights.keys()) != {"accuracy", "completeness", "consistency", "timeliness", "relevance"}:
            raise ValueError("Weights must include all five dimensions")
        
        if abs(sum(weights.values()) - 1.0) > 0.001:
            raise ValueError("Weights must sum to 1.0")
        
        # Get resource
        resource = self.db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")
        
        # Compute dimension scores (simplified)
        accuracy = 0.7
        completeness = 0.0
        if resource.title:
            completeness += 0.2
        if resource.description:
            completeness += 0.2
        if resource.creator:
            completeness += 0.2
        if resource.publication_year:
            completeness += 0.2
        if resource.doi:
            completeness += 0.2
        
        consistency = 0.75
        timeliness = 0.7
        relevance = 0.7
        
        # Compute overall score
        overall = (
            weights["accuracy"] * accuracy +
            weights["completeness"] * completeness +
            weights["consistency"] * consistency +
            weights["timeliness"] * timeliness +
            weights["relevance"] * relevance
        )
        
        # Update resource
        resource.quality_accuracy = accuracy
        resource.quality_completeness = completeness
        resource.quality_consistency = consistency
        resource.quality_timeliness = timeliness
        resource.quality_relevance = relevance
        resource.quality_overall = overall
        resource.quality_score = overall
        resource.quality_weights = json.dumps(weights)
        resource.quality_computation_version = self.quality_version
        resource.quality_last_computed = datetime.now(timezone.utc)
        
        self.db.commit()
        
        return {
            "accuracy": accuracy,
            "completeness": completeness,
            "consistency": consistency,
            "timeliness": timeliness,
            "relevance": relevance,
            "overall": overall
        }
    
    def monitor_quality_degradation(self, time_window_days: int = 30) -> List[Dict[str, Any]]:
        """Monitor quality degradation over time."""
        from backend.app.database.models import Resource
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=time_window_days)
        
        # Find resources with old quality scores
        resources = self.db.query(Resource).filter(
            Resource.quality_last_computed.isnot(None),
            Resource.quality_last_computed < cutoff_date,
            Resource.quality_overall.isnot(None)
        ).all()
        
        degraded = []
        
        for resource in resources:
            old_quality = resource.quality_overall
            
            # Recompute quality
            result = self.compute_quality(str(resource.id))
            new_quality = result['overall']
            
            # Check for degradation (>20% drop)
            quality_drop = old_quality - new_quality
            if quality_drop > 0.2:
                degradation_pct = (quality_drop / old_quality) * 100.0
                
                # Flag for review
                resource.needs_quality_review = True
                self.db.commit()
                
                degraded.append({
                    "resource_id": str(resource.id),
                    "title": resource.title,
                    "old_quality": old_quality,
                    "new_quality": new_quality,
                    "degradation_pct": degradation_pct
                })
        
        return degraded
    
    def detect_quality_outliers(self, batch_size: int = 1000) -> int:
        """Detect quality outliers using Isolation Forest.
        
        Args:
            batch_size: Number of resources to process (default: 1000)
            
        Returns:
            Count of detected outliers
            
        Raises:
            ValueError: If fewer than 10 resources with quality scores exist
        """
        from backend.app.database.models import Resource
        from sklearn.ensemble import IsolationForest
        import numpy as np
        
        # Query resources with quality scores in configurable batches
        resources = self.db.query(Resource).filter(
            Resource.quality_overall.isnot(None)
        ).limit(batch_size).all()
        
        # Validate minimum 10 resources for statistical validity
        if len(resources) < 10:
            raise ValueError("Outlier detection requires minimum 10 resources with quality scores")
        
        # Build feature matrix from 5 quality dimensions plus 4 summary dimensions when available
        feature_matrix = []
        resource_list = []
        
        for resource in resources:
            features = []
            
            # Add 5 quality dimensions
            features.append(resource.quality_accuracy if resource.quality_accuracy is not None else 0.5)
            features.append(resource.quality_completeness if resource.quality_completeness is not None else 0.5)
            features.append(resource.quality_consistency if resource.quality_consistency is not None else 0.5)
            features.append(resource.quality_timeliness if resource.quality_timeliness is not None else 0.5)
            features.append(resource.quality_relevance if resource.quality_relevance is not None else 0.5)
            
            # Add 4 summary quality dimensions when available
            if hasattr(resource, 'summary_coherence') and resource.summary_coherence is not None:
                features.append(resource.summary_coherence)
            else:
                features.append(0.5)  # Neutral baseline
                
            if hasattr(resource, 'summary_consistency') and resource.summary_consistency is not None:
                features.append(resource.summary_consistency)
            else:
                features.append(0.5)
                
            if hasattr(resource, 'summary_fluency') and resource.summary_fluency is not None:
                features.append(resource.summary_fluency)
            else:
                features.append(0.5)
                
            if hasattr(resource, 'summary_relevance') and resource.summary_relevance is not None:
                features.append(resource.summary_relevance)
            else:
                features.append(0.5)
            
            feature_matrix.append(features)
            resource_list.append(resource)
        
        # Convert to numpy array
        X = np.array(feature_matrix)
        
        # Train Isolation Forest with contamination=0.1, n_estimators=100, random_state=42
        iso_forest = IsolationForest(
            contamination=0.1,
            n_estimators=100,
            random_state=42
        )
        
        # Fit and predict
        predictions = iso_forest.fit_predict(X)
        
        # Predict anomaly scores for all resources (lower scores = more anomalous)
        anomaly_scores = iso_forest.score_samples(X)
        
        # Identify outliers where prediction equals -1
        outlier_count = 0
        
        for i, (resource, prediction, anomaly_score) in enumerate(zip(resource_list, predictions, anomaly_scores)):
            if prediction == -1:
                # Call _identify_outlier_reasons for each outlier
                reasons = self._identify_outlier_reasons(resource)
                
                # Update resources with is_quality_outlier flag, outlier_score, outlier_reasons JSON, and needs_quality_review flag
                resource.is_quality_outlier = True
                resource.outlier_score = float(anomaly_score)
                resource.outlier_reasons = json.dumps(reasons)
                resource.needs_quality_review = True
                
                outlier_count += 1
            else:
                # Clear outlier flags for non-outliers
                resource.is_quality_outlier = False
                resource.outlier_score = float(anomaly_score)
                resource.outlier_reasons = None
        
        # Commit updates to database
        self.db.commit()
        
        # Return count of detected outliers
        return outlier_count
    
    def _identify_outlier_reasons(self, resource) -> List[str]:
        """Identify reasons why a resource is an outlier."""
        reasons = []
        
        # Check quality dimensions
        if hasattr(resource, 'quality_accuracy') and resource.quality_accuracy and resource.quality_accuracy < 0.3:
            reasons.append("low_accuracy")
        if hasattr(resource, 'quality_completeness') and resource.quality_completeness and resource.quality_completeness < 0.3:
            reasons.append("low_completeness")
        if hasattr(resource, 'quality_consistency') and resource.quality_consistency and resource.quality_consistency < 0.3:
            reasons.append("low_consistency")
        if hasattr(resource, 'quality_timeliness') and resource.quality_timeliness and resource.quality_timeliness < 0.3:
            reasons.append("low_timeliness")
        if hasattr(resource, 'quality_relevance') and resource.quality_relevance and resource.quality_relevance < 0.3:
            reasons.append("low_relevance")
        
        # Check summary quality dimensions
        if hasattr(resource, 'summary_coherence') and resource.summary_coherence and resource.summary_coherence < 0.3:
            reasons.append("low_summary_coherence")
        if hasattr(resource, 'summary_consistency') and resource.summary_consistency and resource.summary_consistency < 0.3:
            reasons.append("low_summary_consistency")
        if hasattr(resource, 'summary_fluency') and resource.summary_fluency and resource.summary_fluency < 0.3:
            reasons.append("low_summary_fluency")
        if hasattr(resource, 'summary_relevance') and resource.summary_relevance and resource.summary_relevance < 0.3:
            reasons.append("low_summary_relevance")
        
        return reasons
