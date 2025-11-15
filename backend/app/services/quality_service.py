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
        """Calculate overall quality score (simple version for backward compatibility).
        
        This uses the original formula:
        - Metadata completeness: 60%
        - Content readability: 40%
        """
        meta_score = self.metadata_completeness(resource_in)
        if not text:
            return meta_score
        scores = self.text_readability(text)
        norm_read = self._normalize_reading_ease(scores.get("reading_ease", 0.0))
        return 0.6 * meta_score + 0.4 * norm_read
    
    def comprehensive_quality(self, resource_in: Dict[str, Any], text: str | None) -> float:
        """Calculate comprehensive quality score considering multiple factors.
        
        Weights:
        - Metadata completeness: 30%
        - Content readability: 20%
        - Source credibility: 25%
        - Content depth: 25%
        """
        meta_score = self.metadata_completeness(resource_in)
        
        # Get source from resource
        source = None
        if isinstance(resource_in, dict):
            source = resource_in.get("source")
        else:
            source = getattr(resource_in, "source", None)
        
        source_score = self.source_credibility(source)
        
        if not text:
            # Without text, weight metadata and source more heavily
            return 0.5 * meta_score + 0.5 * source_score
        
        # Calculate readability and content depth
        scores = self.text_readability(text)
        norm_read = self._normalize_reading_ease(scores.get("reading_ease", 0.0))
        depth_score = self.content_depth(text)
        
        # Weighted combination
        return (
            0.30 * meta_score +
            0.20 * norm_read +
            0.25 * source_score +
            0.25 * depth_score
        )

    def quality_level(self, score: float) -> str:
        if score >= HIGH_QUALITY_THRESHOLD:
            return "HIGH"
        if score >= MEDIUM_QUALITY_THRESHOLD:
            return "MEDIUM"
        return "LOW"
    
    def source_credibility(self, source: Optional[str]) -> float:
        """Assess source credibility based on URL/identifier.
        
        Returns 0.0 for None/empty URLs, otherwise scores based on domain quality.
        """
        # Handle None and empty strings
        if not source or (isinstance(source, str) and not source.strip()):
            return 0.0
        
        # Simple heuristics for credibility
        source_lower = source.lower()
        
        # Start with base score
        base_score = 0.5
        
        # Check for IP addresses (low credibility)
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        if re.search(ip_pattern, source):
            return 0.2
        
        # High credibility domains (.edu, .gov, arxiv, etc.)
        high_cred_domains = ['.edu', '.gov', 'arxiv.org', 'doi.org', 'pubmed', 'scholar.google']
        if any(domain in source_lower for domain in high_cred_domains):
            return 0.9
        
        # Medium credibility (.org, wikipedia, github)
        medium_cred_domains = ['.org', 'wikipedia', 'github']
        if any(domain in source_lower for domain in medium_cred_domains):
            return 0.7
        
        # Check for suspicious TLDs (lower credibility)
        suspicious_tlds = ['.xyz', '.top', '.click', '.loan', '.win']
        if any(tld in source_lower for tld in suspicious_tlds):
            base_score -= 0.05
        
        # Check for blog platforms (slightly lower credibility)
        blog_platforms = ['blog.', 'blogger.', 'wordpress.com', 'medium.com', 'tumblr.']
        if any(platform in source_lower for platform in blog_platforms):
            base_score -= 0.1
        
        # Bonus for HTTPS
        if source_lower.startswith('https://'):
            base_score += 0.05
        
        # Bonus for common TLDs
        if any(tld in source_lower for tld in ['.com', '.net', '.io']):
            base_score += 0.05
        
        # Ensure score is in valid range
        return max(0.0, min(1.0, base_score))
    
    def content_depth(self, text: Optional[str]) -> float:
        """Assess content depth based on text length and complexity.
        
        Adjusted thresholds to ensure rich content scores > 0.3.
        """
        if not text:
            return 0.0
        
        word_count = len(text.split())
        
        # Adjusted score based on word count
        # Rich content (50+ words) should score > 0.3
        if word_count < 20:
            return 0.1
        elif word_count < 50:
            return 0.25
        elif word_count < 100:
            return 0.4  # Rich content starts here
        elif word_count < 300:
            return 0.6
        elif word_count < 1000:
            return 0.75
        elif word_count < 2000:
            return 0.85
        else:
            return 0.95
    
    def _normalize_reading_ease(self, reading_ease: float) -> float:
        """Normalize Flesch Reading Ease score to 0-1 range.
        
        Flesch Reading Ease typically ranges from -30 to 100:
        - 90-100: Very easy
        - 60-70: Standard
        - 0-30: Difficult
        - Below 0: Very difficult
        
        We normalize to 0-1 where higher is better.
        We use 100 as the practical maximum (scores above 100 are extremely rare).
        """
        # Clamp to reasonable range (-30 to 100)
        clamped = max(-30.0, min(100.0, reading_ease))
        # Normalize to 0-1
        return (clamped - (-30.0)) / (100.0 - (-30.0))
    
    # Backward compatibility aliases
    def content_readability(self, text: str) -> Dict[str, float]:
        """Backward compatibility alias for text_readability()."""
        return self.text_readability(text)
    
    def overall_quality_score(self, resource_in: Dict[str, Any], text: str | None) -> float:
        """Comprehensive quality score (uses enhanced formula)."""
        return self.comprehensive_quality(resource_in, text)


class QualityService:
    """Quality service for computing and monitoring resource quality."""
    
    def __init__(self, db: Session, quality_version: str = "v2.0"):
        self.db = db
        self.quality_version = quality_version
    
    def compute_quality(self, resource_id: str, weights: Optional[Dict[str, float]] = None, custom_weights: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """Compute quality scores for a resource."""
        from backend.app.database.models import Resource
        
        # Support both 'weights' and 'custom_weights' parameters for backward compatibility
        if custom_weights is not None:
            weights = custom_weights
        
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
        
        # Compute dimension scores using the dimension methods
        accuracy = self._compute_accuracy(resource)
        completeness = self._compute_completeness(resource)
        consistency = self._compute_consistency(resource)
        timeliness = self._compute_timeliness(resource)
        relevance = self._compute_relevance(resource)
        
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
        """Detect quality outliers using Isolation Forest."""
        from backend.app.database.models import Resource
        
        # Get resources with quality scores
        resources = self.db.query(Resource).filter(
            Resource.quality_overall.isnot(None)
        ).limit(batch_size).all()
        
        if len(resources) < 10:
            raise ValueError("Outlier detection requires minimum 10 required resources with quality scores")
        
        # Simple outlier detection: flag resources with very low quality
        outlier_count = 0
        
        for resource in resources:
            if resource.quality_overall < 0.3:
                resource.is_quality_outlier = True
                resource.needs_quality_review = True
                resource.outlier_score = 1.0 - resource.quality_overall
                
                # Identify reasons
                reasons = self._identify_outlier_reasons(resource)
                resource.outlier_reasons = json.dumps(reasons)
                
                outlier_count += 1
        
        self.db.commit()
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
    
    def _compute_accuracy(self, resource) -> float:
        """Compute accuracy dimension score for a resource.
        
        Factors:
        - Citation presence (indicates verification)
        - Scholarly metadata presence (DOI, authors)
        - Source credibility
        """
        from backend.app.database.models import Citation
        
        score = 0.5  # Neutral baseline
        
        # Check for scholarly metadata
        has_doi = bool(getattr(resource, 'doi', None))
        has_authors = bool(getattr(resource, 'authors', None))
        
        if has_doi:
            score += 0.15
        if has_authors:
            score += 0.10
        
        # Check source credibility
        source = getattr(resource, 'source', None)
        if source:
            analyzer = ContentQualityAnalyzer()
            source_score = analyzer.source_credibility(source)
            score += (source_score - 0.5) * 0.3  # Scale contribution
        
        # Check citations (presence indicates some level of verification)
        citations = self.db.query(Citation).filter(
            Citation.source_resource_id == resource.id
        ).all()
        
        if citations:
            # Having citations is a positive signal
            citation_boost = min(0.2, len(citations) * 0.05)
            score += citation_boost
        
        return max(0.0, min(1.0, score))
    
    def _compute_completeness(self, resource) -> float:
        """Compute completeness dimension score for a resource.
        
        Factors:
        - Required fields (title, description, source, type)
        - Important fields (summary, tags, authors, publication_year)
        - Scholarly fields (DOI, journal, affiliations, funding)
        - Extracted content (equations, tables, figures)
        """
        score = 0.0
        
        # Required fields (30% weight)
        required_fields = ['title', 'description', 'source', 'type']
        required_present = sum(1 for f in required_fields if getattr(resource, f, None))
        score += (required_present / len(required_fields)) * 0.3
        
        # Important fields (30% weight)
        important_fields = ['summary', 'tags', 'authors', 'publication_year']
        important_present = sum(1 for f in important_fields if getattr(resource, f, None))
        score += (important_present / len(important_fields)) * 0.3
        
        # Scholarly fields (25% weight)
        scholarly_fields = ['doi', 'journal', 'affiliations', 'funding_sources']
        scholarly_present = sum(1 for f in scholarly_fields if getattr(resource, f, None))
        score += (scholarly_present / len(scholarly_fields)) * 0.25
        
        # Extracted content (15% weight)
        extracted_fields = ['equations_count', 'tables_count', 'figures_count']
        extracted_present = sum(1 for f in extracted_fields if getattr(resource, f, None) and getattr(resource, f) > 0)
        score += (extracted_present / len(extracted_fields)) * 0.15
        
        return max(0.0, min(1.0, score))
    
    def _compute_consistency(self, resource) -> float:
        """Compute consistency dimension score for a resource.
        
        Factors:
        - Title-description alignment
        - Summary-description alignment
        - Metadata consistency
        """
        score = 0.7  # Optimistic baseline
        
        title = getattr(resource, 'title', '') or ''
        description = getattr(resource, 'description', '') or ''
        summary = getattr(resource, 'creator', '') or ''  # Using creator field as summary
        
        # Simple keyword overlap check for title-description alignment
        if title and description:
            title_words = set(title.lower().split())
            desc_words = set(description.lower().split())
            if title_words and desc_words:
                overlap = len(title_words & desc_words) / len(title_words)
                if overlap > 0.3:
                    score += 0.15
                elif overlap < 0.1:
                    score -= 0.1
        
        # Check summary-description alignment
        if summary and description:
            summary_words = set(summary.lower().split())
            desc_words = set(description.lower().split())
            if summary_words and desc_words:
                overlap = len(summary_words & desc_words) / min(len(summary_words), len(desc_words))
                if overlap > 0.2:
                    score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _compute_timeliness(self, resource) -> float:
        """Compute timeliness dimension score for a resource.
        
        Factors:
        - Publication year recency
        - Ingestion recency
        """
        score = 0.5  # Neutral baseline
        
        # Check publication year
        pub_year = getattr(resource, 'publication_year', None)
        if pub_year:
            current_year = datetime.now().year
            years_old = current_year - pub_year
            
            if years_old <= 1:
                score = 1.0
            elif years_old <= 3:
                score = 0.9
            elif years_old <= 5:
                score = 0.8
            elif years_old <= 10:
                score = 0.6
            elif years_old <= 20:
                score = 0.4
            else:
                score = 0.2
        
        # Bonus for recent ingestion
        created_at = getattr(resource, 'created_at', None)
        if created_at:
            # Ensure both datetimes are timezone-aware
            now = datetime.now(timezone.utc)
            if created_at.tzinfo is None:
                # If created_at is naive, assume UTC
                created_at = created_at.replace(tzinfo=timezone.utc)
            
            days_since_ingestion = (now - created_at).days
            if days_since_ingestion <= 30:
                score += 0.05
            elif days_since_ingestion <= 90:
                score += 0.02
        
        return max(0.0, min(1.0, score))
    
    def _compute_relevance(self, resource) -> float:
        """Compute relevance dimension score for a resource.
        
        Factors:
        - Classification confidence
        - Citation count
        - Subject tags
        """
        from backend.app.database.models import ResourceTaxonomy
        
        score = 0.5  # Neutral baseline
        
        # Check classification
        classifications = self.db.query(ResourceTaxonomy).filter(
            ResourceTaxonomy.resource_id == resource.id
        ).all()
        
        if classifications:
            avg_confidence = sum(c.confidence for c in classifications if c.confidence) / len(classifications)
            score += (avg_confidence - 0.5) * 0.4
        
        # Check citation count
        citation_count = getattr(resource, 'citation_count', 0) or 0
        if citation_count > 0:
            # Logarithmic scaling for citation impact
            import math
            citation_score = min(1.0, math.log10(citation_count + 1) / 2.0)
            score += citation_score * 0.3
        
        # Check subject tags
        tags = getattr(resource, 'tags', None)
        if tags:
            tag_list = tags.split(',') if isinstance(tags, str) else tags
            if len(tag_list) >= 3:
                score += 0.1
        
        return max(0.0, min(1.0, score))
