"""
Neo Alexandria 2.0 - AI Processing and Vector Embeddings (Phase 4)

This module provides AI-powered content processing capabilities for Neo Alexandria 2.0.
It handles text summarization, zero-shot tagging, and vector embedding generation
using Hugging Face transformers and sentence-transformers.

Related files:
- app/services/resource_service.py: Uses AI processing during ingestion
- app/services/hybrid_search_methods.py: Uses embeddings for vector search
- app/config/settings.py: AI model configuration settings

Features:
- Text summarization using BART-based models (facebook/bart-large-cnn)
- Zero-shot classification for automatic tagging (facebook/bart-large-mnli)
- Vector embedding generation using sentence-transformers (nomic-ai/nomic-embed-text-v1)
- Lazy loading and caching for optimal performance
- Graceful fallback when AI dependencies are unavailable
- Thread-safe model loading and inference
"""

from __future__ import annotations

from typing import List, Optional, Sequence
import threading

# Lazy import transformers to avoid heavy import at module load in tests
try:
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover - allows tests without transformers installed
    pipeline = None  # type: ignore

# Lazy import sentence-transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - allows tests without sentence-transformers installed
    SentenceTransformer = None  # type: ignore


class Summarizer:
    """Abstraction around a text summarization model.

    Uses transformers pipeline('summarization') with a configurable model.
    """

    def __init__(
        self,
        model_name: str = "sshleifer/distilbart-cnn-12-6",
        max_length: int = 180,
        min_length: int = 50,
    ) -> None:
        self.model_name = model_name
        self.max_length = max_length
        self.min_length = min_length
        self._pipe = None

    def _ensure_loaded(self):
        if self._pipe is None:
            if pipeline is None:  # pragma: no cover
                # Leave pipe as None; caller will use fallback
                return
            self._pipe = pipeline("summarization", model=self.model_name)

    def summarize(self, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return ""
        self._ensure_loaded()
        if self._pipe is not None:
            try:
                result = self._pipe(text, max_length=self.max_length, min_length=self.min_length, do_sample=False)
                if isinstance(result, list) and result:
                    summary_text = result[0].get("summary_text") or ""
                    return summary_text.strip()
            except Exception:  # pragma: no cover - model-specific failures
                pass
        # Fallbacks when transformers unavailable or failed
        if len(text) <= 280:
            return text
        trimmed = text[:280]
        return trimmed + "…"


class ZeroShotTagger:
    """Zero-shot classification tagger producing labels from candidate set.

    Uses transformers pipeline('zero-shot-classification') with a configurable model.
    """

    def __init__(
        self,
        model_name: str = "facebook/bart-large-mnli",
        candidate_labels: Optional[Sequence[str]] = None,
        multi_label: bool = True,
        threshold: float = 0.3,
    ) -> None:
        self.model_name = model_name
        self.multi_label = multi_label
        self.threshold = float(threshold)
        self._pipe = None
        # Default broad candidate set; AuthorityControl will normalize downstream
        default_candidates = [
            "Artificial Intelligence",
            "Machine Learning",
            "Deep Learning",
            "Neural Networks",
            "Natural Language Processing",
            "Language",
            "Linguistics",
            "Programming",
            "Python",
            "Data Science",
            "Mathematics",
            "Physics",
            "Biology",
            "Chemistry",
            "Economics",
            "History",
        ]
        self.candidate_labels: List[str] = list(candidate_labels) if candidate_labels else default_candidates

    def _ensure_loaded(self):
        if self._pipe is None:
            if pipeline is None:  # pragma: no cover
                # Leave pipe as None; caller will use heuristics
                return
            self._pipe = pipeline("zero-shot-classification", model=self.model_name)

    def generate_tags(self, text: str) -> List[str]:
        text = (text or "").strip()
        if not text:
            return []
        self._ensure_loaded()
        if self._pipe is not None:
            try:
                res = self._pipe(
                    text,
                    candidate_labels=self.candidate_labels,
                    multi_label=self.multi_label,
                )
                labels = res.get("labels") or []
                scores = res.get("scores") or []
                out: List[str] = []
                for label, score in zip(labels, scores):
                    try:
                        sc = float(score)
                    except Exception:
                        sc = 0.0
                    if sc >= self.threshold:
                        out.append(str(label))
                return out
            except Exception:  # pragma: no cover
                pass
        # Fallback: simple heuristic keywords
        lower = text.lower()
        tags: List[str] = []
        if "artificial intelligence" in lower or " ai " in f" {lower} ":
            tags.append("Artificial Intelligence")
        if "machine learning" in lower or " ml " in f" {lower} ":
            tags.append("Machine Learning")
        if "linguistic" in lower or "language" in lower:
            tags.append("Language")
        if "python" in lower:
            tags.append("Python")
        return tags


class EmbeddingGenerator:
    """Abstraction around a sentence embedding model.
    
    Uses sentence-transformers with a configurable model for generating
    vector embeddings from text content.
    """
    
    def __init__(self, model_name: str = "nomic-ai/nomic-embed-text-v1") -> None:
        self.model_name = model_name
        self._model = None
        self._model_lock = threading.Lock()
    
    def _ensure_loaded(self):
        """Lazy load the embedding model in a thread-safe manner."""
        if self._model is None:
            with self._model_lock:
                if self._model is None:  # Double-check locking pattern
                    if SentenceTransformer is None:  # pragma: no cover
                        # Leave model as None; caller will use fallback
                        return
                    try:
                        self._model = SentenceTransformer(self.model_name)
                    except Exception:  # pragma: no cover - model loading failures
                        # Model loading failed, leave as None for fallback
                        pass
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for the given text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of float values representing the embedding vector.
            Returns empty list if model unavailable or text is empty.
        """
        text = (text or "").strip()
        if not text:
            return []
            
        self._ensure_loaded()
        if self._model is not None:
            try:
                # sentence-transformers returns numpy array, convert to list
                embedding = self._model.encode(text, convert_to_tensor=False)
                return embedding.tolist()
            except Exception:  # pragma: no cover - encoding failures
                pass
        
        # Fallback: return empty embedding
        return []


def load_embedding_model(model_name: str = "nomic-ai/nomic-embed-text-v1") -> Optional[EmbeddingGenerator]:
    """Global function to load and cache embedding model.
    
    This function provides a singleton-like access to the embedding model
    for use across the application.
    """
    return EmbeddingGenerator(model_name)


def generate_embedding(text: str, model_name: str = "nomic-ai/nomic-embed-text-v1") -> List[float]:
    """Convenience function to generate embedding using default model."""
    generator = load_embedding_model(model_name)
    return generator.generate_embedding(text)


def create_composite_text(resource) -> str:
    """Create composite text from resource for embedding generation.
    
    Combines title, description, and subjects into a single text string
    optimized for semantic embedding.
    
    Args:
        resource: Resource object with title, description, and subject fields
        
    Returns:
        Composite text string suitable for embedding generation
    """
    parts = []
    
    # Add title (most important)
    if hasattr(resource, 'title') and resource.title:
        parts.append(resource.title)
    
    # Add description 
    if hasattr(resource, 'description') and resource.description:
        parts.append(resource.description)
    
    # Add subjects as keywords
    if hasattr(resource, 'subject') and resource.subject:
        try:
            if isinstance(resource.subject, list):
                subjects_text = " ".join(resource.subject)
                if subjects_text.strip():
                    parts.append(f"Keywords: {subjects_text}")
        except Exception:
            pass
    
    return " ".join(parts)


class AICore:
    """Facade to real AI capabilities used by the ingestion pipeline.

    Designed for dependency injection in services and easy testing.
    """

    def __init__(
        self, 
        summarizer: Optional[Summarizer] = None, 
        tagger: Optional[ZeroShotTagger] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None
    ) -> None:
        self.summarizer = summarizer or Summarizer()
        self.tagger = tagger or ZeroShotTagger()
        self.embedding_generator = embedding_generator or EmbeddingGenerator()

    def generate_summary(self, text: str) -> str:
        return self.summarizer.summarize(text)

    def generate_tags(self, text: str) -> List[str]:
        return self.tagger.generate_tags(text)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for text using the configured model."""
        return self.embedding_generator.generate_embedding(text)
