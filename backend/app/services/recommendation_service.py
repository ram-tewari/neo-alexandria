"""
Neo Alexandria 2.0 - Phase 5.5 Personalized Recommendation Engine Service

This module implements the core recommendation system that learns user preferences
from existing library content and suggests fresh web content via cosine similarity.

Related files:
- app/schemas/recommendation.py: Pydantic models for API responses
- app/routers/recommendation.py: HTTP endpoints that use this service
- app/config/settings.py: Configuration parameters for recommendation behavior
- app/database/models.py: Resource and AuthoritySubject models
- app/services/dependencies.py: AI core for embedding generation

Features:
- User profile generation from top-quality library embeddings
- Seed keyword extraction from authority subjects by usage count
- External candidate sourcing via pluggable search providers (DDGS)
- Lightweight in-memory scoring using cosine similarity
- Caching and deduplication for performance and quality
- Graceful degradation on external service failures

Core Functions:
- generate_user_profile_vector(): Average embeddings of top-quality resources
- get_top_subjects(): Extract seed keywords from authority subjects
- fetch_candidates(): Source fresh content from external search providers
- prepare_candidate(): Generate embeddings and filter duplicates
- score_candidates(): Rank by cosine similarity to user profile
- generate_recommendations(): Orchestrate the complete recommendation pipeline

Configuration:
- RECOMMENDATION_PROFILE_SIZE: Number of top resources for profile (default: 50)
- RECOMMENDATION_KEYWORD_COUNT: Number of seed keywords (default: 5)
- RECOMMENDATION_CANDIDATES_PER_KEYWORD: Candidates per keyword (default: 10)
- SEARCH_PROVIDER: External search provider (default: "ddgs")
- SEARCH_TIMEOUT: Search timeout in seconds (default: 10)
"""

from __future__ import annotations

import math
import time
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from backend.app.config.settings import get_settings
from backend.app.database import models as db_models
from backend.app.services.dependencies import get_ai_core


settings = get_settings()

# Optional provider import for test patchability
try:  # pragma: no cover - import exercised in runtime, patched in tests
    from duckduckgo_search import DDGS  # type: ignore
except Exception:  # pragma: no cover
    DDGS = None  # type: ignore


def _to_numpy_vector(vec_like: Sequence[float] | None) -> np.ndarray:
    if not vec_like:
        return np.array([], dtype=float)
    try:
        arr = np.array(list(vec_like), dtype=float)
    except Exception:
        return np.array([], dtype=float)
    return arr


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return 0.0
    if a.shape != b.shape:
        return 0.0
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    sim = float(np.dot(a, b) / denom)
    # Clamp to [0,1]
    if sim < 0.0:
        return 0.0
    if sim > 1.0:
        return 1.0
    return sim


def generate_user_profile_vector(db: Session) -> np.ndarray:
    """Average embeddings of top-quality resources to form a profile vector.

    Returns zero-length vector if no suitable embeddings found.
    """
    limit = int(settings.RECOMMENDATION_PROFILE_SIZE)
    stmt = (
        select(db_models.Resource)
        .where(db_models.Resource.embedding.isnot(None))
        .order_by(desc(db_models.Resource.quality_score))
        .limit(limit)
    )
    resources = list(db.execute(stmt).scalars())
    embeddings: List[np.ndarray] = []
    for r in resources:
        arr = _to_numpy_vector(r.embedding)
        if arr.size > 0:
            embeddings.append(arr)

    if not embeddings:
        return np.array([], dtype=float)

    # Ensure same dimensionality
    dim = embeddings[0].shape[0]
    filtered = [e for e in embeddings if e.shape[0] == dim]
    if not filtered:
        return np.array([], dtype=float)

    profile = np.mean(filtered, axis=0)
    if not np.any(profile):
        return np.array([], dtype=float)
    return profile.astype(float)


def get_top_subjects(db: Session) -> List[str]:
    """Return top canonical subjects by usage_count."""
    k = int(settings.RECOMMENDATION_KEYWORD_COUNT)
    stmt = select(db_models.AuthoritySubject).order_by(desc(db_models.AuthoritySubject.usage_count)).limit(k)
    subjects = list(db.execute(stmt).scalars())
    return [s.canonical_form for s in subjects if s.canonical_form]


_search_cache: Dict[str, Tuple[float, List[Dict[str, str]]]] = {}
_SEARCH_CACHE_TTL_SECONDS = 300


def _ddgs_search(keyword: str, max_results: int, timeout: int) -> List[Dict[str, str]]:
    if DDGS is None:
        return []
    results: List[Dict[str, str]] = []
    try:
        with DDGS(timeout=timeout) as ddgs:
            for item in ddgs.text(keyword, max_results=max_results):
                url = str(item.get("href") or item.get("url") or "").strip()
                title = str(item.get("title") or "").strip()
                snippet = str(item.get("body") or item.get("snippet") or "").strip()
                if url:
                    results.append({"url": url, "title": title, "snippet": snippet})
    except Exception:
        # Gracefully degrade on provider errors/timeouts
        return []
    return results


def fetch_candidates(keywords: List[str]) -> List[Dict[str, str]]:
    """Fetch unique candidates across keywords using the configured provider.

    Deduplicates by URL.
    """
    provider = (settings.SEARCH_PROVIDER or "ddgs").lower()
    per_kw = int(settings.RECOMMENDATION_CANDIDATES_PER_KEYWORD)
    timeout = int(settings.SEARCH_TIMEOUT)

    seen: set[str] = set()
    out: List[Dict[str, str]] = []

    for kw in keywords:
        cache_key = f"{provider}:{kw}:{per_kw}"
        now = time.time()
        cached = _search_cache.get(cache_key)
        if cached and now - cached[0] < _SEARCH_CACHE_TTL_SECONDS:
            items = cached[1]
        else:
            if provider == "ddgs":
                items = _ddgs_search(kw, per_kw, timeout)
            else:
                items = []
            _search_cache[cache_key] = (now, items)

        for it in items:
            url = it.get("url") or ""
            if not url or url in seen:
                continue
            seen.add(url)
            out.append(it)

    return out


def _url_exists(db: Session, url: str) -> bool:
    if not url:
        return False
    stmt = select(db_models.Resource).where(db_models.Resource.source == url).limit(1)
    return db.execute(stmt).scalar_one_or_none() is not None


def _fallback_text_embedding(text: str, dim: int) -> np.ndarray:
    """Deterministic bag-of-words hashing into fixed dimension.

    Provides a lightweight embedding when the heavy model isn't available.
    """
    if dim <= 0:
        return np.array([], dtype=float)
    vec = np.zeros(dim, dtype=float)
    for token in (text or "").lower().split():
        h = hash(token) % dim
        vec[h] += 1.0
    # Normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def prepare_candidate(db: Session, url: str, title: str, snippet: str, expected_dim: int | None = None) -> Optional[Tuple[np.ndarray, Dict[str, str]]]:
    """Return embedding vector and meta for a candidate, or None if duplicate/invalid."""
    if _url_exists(db, url):
        return None

    # Use title + snippet as composite text
    composite = " ".join([t for t in [title, snippet] if t]).strip()
    if not composite:
        composite = url

    ai = get_ai_core()
    emb_list = ai.generate_embedding(composite) or []
    vec = _to_numpy_vector(emb_list)
    if vec.size == 0 and expected_dim is not None and expected_dim > 0:
        # Lightweight fallback to enable tests without heavy model
        vec = _fallback_text_embedding(composite, expected_dim)
    if vec.size == 0:
        return None
    return vec, {"url": url, "title": title or url, "snippet": snippet or ""}


def score_candidates(profile: np.ndarray, candidates: List[Tuple[np.ndarray, Dict[str, str]]], seed_keywords: List[str], limit: int) -> List[Dict[str, object]]:
    """Compute cosine sim against profile and build recommendation dicts."""
    if profile.size == 0:
        return []
    scored: List[Tuple[float, Dict[str, str]]] = []
    for vec, meta in candidates:
        if vec.shape != profile.shape:
            # dimensionality mismatch: reject
            continue
        sim = _cosine_similarity(vec, profile)
        scored.append((sim, meta))

    scored.sort(key=lambda x: x[0], reverse=True)

    top = scored[: max(0, int(limit))]
    reasons = []
    if seed_keywords:
        # Build a single consistent reason template per item
        highlight = ", ".join(seed_keywords[: min(3, len(seed_keywords))])
        reasons = [f"Aligned with {highlight}"]

    recommendations: List[Dict[str, object]] = []
    for sim, meta in top:
        recommendations.append(
            {
                "url": meta["url"],
                "title": meta.get("title") or meta["url"],
                "snippet": meta.get("snippet") or "",
                "relevance_score": float(max(0.0, min(1.0, sim))),
                "reasoning": list(reasons),
            }
        )
    return recommendations


def generate_recommendations(db: Session, limit: int = 10) -> List[Dict[str, object]]:
    """Orchestrate profile -> subjects -> candidates -> embeddings -> scoring."""
    profile = generate_user_profile_vector(db)
    if profile.size == 0:
        return []

    seed_keywords = get_top_subjects(db)
    candidates_raw = fetch_candidates(seed_keywords)

    prepared: List[Tuple[np.ndarray, Dict[str, str]]] = []
    for item in candidates_raw:
        pc = prepare_candidate(
            db,
            item.get("url", ""),
            item.get("title", ""),
            item.get("snippet", ""),
            expected_dim=int(profile.shape[0]) if profile.size > 0 else None,
        )
        if pc is not None:
            prepared.append(pc)

    return score_candidates(profile, prepared, seed_keywords, limit)


def recommend_based_on_annotations(db: Session, user_id: str, limit: int = 10) -> List[db_models.Resource]:
    """
    Generate recommendations based on user's annotation patterns.
    
    Algorithm:
    1. Get recent annotations (last 100) for the user
    2. Extract annotated resource IDs to exclude from recommendations
    3. Aggregate annotation content:
       - Combine all note text
       - Extract and count all tags
    4. Get top 5 most frequent tags
    5. Generate embedding from aggregated notes (if available)
    6. Find similar resources by embedding (exclude already-annotated)
    7. Search resources by top tags (exclude already-annotated)
    8. Merge and deduplicate results
    9. Return top N resources
    
    Args:
        db: Database session
        user_id: User ID to generate recommendations for
        limit: Maximum number of recommendations to return (default: 10)
        
    Returns:
        List of Resource objects recommended based on annotation patterns
    """
    from collections import Counter
    import json
    from sqlalchemy import and_, or_
    
    try:
        from backend.app.services.annotation_service import AnnotationService
        
        annotation_service = AnnotationService(db)
        
        # Get recent annotations (last 100)
        annotations = annotation_service.get_annotations_for_user(
            user_id=user_id,
            limit=100,
            sort_by="recent"
        )
        
        if not annotations:
            return []
        
        # Extract annotated resource IDs (to exclude)
        annotated_resource_ids = list(set(str(ann.resource_id) for ann in annotations))
        
        # Aggregate annotation content
        all_notes = " ".join([ann.note for ann in annotations if ann.note])
        all_tags = []
        for ann in annotations:
            if ann.tags:
                try:
                    # Parse JSON tags
                    tags = json.loads(ann.tags) if isinstance(ann.tags, str) else ann.tags
                    if isinstance(tags, list):
                        all_tags.extend(tags)
                except (json.JSONDecodeError, TypeError):
                    continue
        
        # Get tag frequencies
        tag_counts = Counter(all_tags)
        top_tags = [tag for tag, _ in tag_counts.most_common(5)]
        
        similar_resources = []
        
        # Generate embedding from notes (if available)
        if all_notes.strip():
            try:
                ai = get_ai_core()
                notes_embedding = ai.generate_embedding(all_notes)
                
                if notes_embedding:
                    # Find similar resources by embedding
                    # Query resources with embeddings (exclude annotated ones)
                    from sqlalchemy import select
                    import uuid as uuid_module
                    
                    # Convert annotated_resource_ids to UUIDs
                    exclude_uuids = []
                    for rid in annotated_resource_ids:
                        try:
                            exclude_uuids.append(uuid_module.UUID(rid))
                        except (ValueError, TypeError):
                            continue
                    
                    query = select(db_models.Resource).filter(
                        db_models.Resource.embedding.isnot(None)
                    )
                    
                    if exclude_uuids:
                        query = query.filter(~db_models.Resource.id.in_(exclude_uuids))
                    
                    query = query.limit(limit * 2)
                    
                    result = db.execute(query)
                    candidates = result.scalars().all()
                    
                    # Compute cosine similarity
                    notes_vec = _to_numpy_vector(notes_embedding)
                    scored = []
                    for resource in candidates:
                        resource_vec = _to_numpy_vector(resource.embedding)
                        if resource_vec.size > 0 and notes_vec.size > 0:
                            sim = _cosine_similarity(notes_vec, resource_vec)
                            scored.append((sim, resource))
                    
                    # Sort by similarity and take top results
                    scored.sort(key=lambda x: x[0], reverse=True)
                    similar_resources = [r for _, r in scored[:limit]]
                    
            except Exception as e:
                print(f"Warning: Embedding-based recommendation failed: {e}")
        
        # Also search by top tags
        tag_resources = []
        if top_tags:
            try:
                # Convert annotated_resource_ids to UUIDs
                import uuid as uuid_module
                exclude_uuids = []
                for rid in annotated_resource_ids:
                    try:
                        exclude_uuids.append(uuid_module.UUID(rid))
                    except (ValueError, TypeError):
                        continue
                
                # Build query for resources matching top tags
                query = db.query(db_models.Resource)
                
                if exclude_uuids:
                    query = query.filter(~db_models.Resource.id.in_(exclude_uuids))
                
                # Search in subject field (JSON array) using portable string matching
                from sqlalchemy import cast, String, func
                ser = func.lower(cast(db_models.Resource.subject, String))
                tag_conditions = [ser.like(f"%{tag.lower()}%") for tag in top_tags]
                
                if tag_conditions:
                    query = query.filter(or_(*tag_conditions))
                
                tag_resources = query.limit(limit).all()
                
            except Exception as e:
                print(f"Warning: Tag-based recommendation failed: {e}")
        
        # Merge and deduplicate
        combined = similar_resources + tag_resources
        seen = set()
        unique = []
        for res in combined:
            if res.id not in seen:
                seen.add(res.id)
                unique.append(res)
        
        return unique[:limit]
        
    except Exception as e:
        print(f"Warning: Annotation-based recommendations failed: {e}")
        return []


