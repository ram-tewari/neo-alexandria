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


