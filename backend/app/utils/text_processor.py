"""
Neo Alexandria 2.0 - Text Processing and Quality Analysis

This module provides text processing utilities for content quality assessment and analysis.
It calculates readability metrics, text statistics, and quality scores to help evaluate
content quality and readability.

Related files:
- app/services/quality_service.py: Uses text processing for quality scoring
- app/services/resource_service.py: Applies quality analysis during ingestion
- app/utils/content_extractor.py: Provides text for processing

Features:
- Readability metrics calculation (Flesch-Kincaid, Gunning Fog, etc.)
- Text statistics (word count, sentence count, character count)
- Quality scoring based on multiple factors
- Fallback handling for optional dependencies
- Unicode-aware text processing
"""

from __future__ import annotations

import math
import re
from typing import Dict

try:
    import textstat  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    textstat = None  # type: ignore


_WHITESPACE_RE = re.compile(r"\s+", re.UNICODE)
_WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:'[A-Za-zÀ-ÖØ-öø-ÿ]+)?")
_SENTENCE_RE = re.compile(r"[.!?]+\s+|\n", re.MULTILINE)


def clean_text(txt: str) -> str:
    """Normalize whitespace and strip control characters."""
    if not txt:
        return ""
    # Replace control characters with spaces
    normalized = ''.join(ch if ch >= ' ' else ' ' for ch in txt)
    normalized = _WHITESPACE_RE.sub(' ', normalized)
    return normalized.strip()


def _estimate_syllables(word: str) -> int:
    word = word.lower()
    if len(word) <= 3:
        return 1
    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def _split_sentences(text: str) -> int:
    # Simple sentence boundary estimate
    if not text:
        return 0
    parts = [p for p in _SENTENCE_RE.split(text) if p.strip()]
    return max(len(parts), 1)


def readability_scores(txt: str) -> Dict[str, float]:
    """Compute Flesch Reading Ease and Flesch–Kincaid Grade.

    Prefer textstat if available; otherwise use internal approximation.
    Returns dict with keys: reading_ease, fk_grade, word_count, sentence_count,
    avg_words_per_sentence, unique_word_ratio, long_word_ratio, paragraph_count
    """
    text = clean_text(txt)
    if not text:
        return {
            "reading_ease": 0.0, 
            "fk_grade": 0.0, 
            "word_count": 0, 
            "sentence_count": 0,
            "avg_words_per_sentence": 0.0,
            "unique_word_ratio": 0.0,
            "long_word_ratio": 0.0,
            "paragraph_count": 0.0
        }

    words = _WORD_RE.findall(text)
    num_words = max(len(words), 1)
    num_sentences = _split_sentences(text)
    
    # Calculate additional metrics
    avg_words_per_sentence = num_words / num_sentences if num_sentences > 0 else 0.0
    
    # Unique word ratio
    unique_words = set(w.lower() for w in words)
    unique_word_ratio = len(unique_words) / num_words if num_words > 0 else 0.0
    
    # Long word ratio (words with 7+ characters)
    long_words = [w for w in words if len(w) >= 7]
    long_word_ratio = len(long_words) / num_words if num_words > 0 else 0.0
    
    # Paragraph count (split by double newlines or single newlines)
    paragraphs = [p.strip() for p in txt.split('\n') if p.strip()]
    paragraph_count = len(paragraphs) if paragraphs else 1
    
    if textstat is not None:
        try:
            return {
                "reading_ease": float(textstat.flesch_reading_ease(text)),
                "fk_grade": float(textstat.flesch_kincaid_grade(text)),
                "word_count": len(words),
                "sentence_count": num_sentences,
                "avg_words_per_sentence": float(avg_words_per_sentence),
                "unique_word_ratio": float(unique_word_ratio),
                "long_word_ratio": float(long_word_ratio),
                "paragraph_count": float(paragraph_count),
            }
        except Exception:
            # fall back to internal
            pass

    syllables = sum(_estimate_syllables(w) for w in words) or 1

    words_per_sentence = num_words / num_sentences
    syllables_per_word = syllables / num_words

    reading_ease = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
    fk_grade = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59

    # Clamp to reasonable ranges
    if math.isnan(reading_ease):
        reading_ease = 0.0
    if math.isnan(fk_grade):
        fk_grade = 0.0
    return {
        "reading_ease": float(reading_ease), 
        "fk_grade": float(fk_grade),
        "word_count": len(words),
        "sentence_count": num_sentences,
        "avg_words_per_sentence": float(avg_words_per_sentence),
        "unique_word_ratio": float(unique_word_ratio),
        "long_word_ratio": float(long_word_ratio),
        "paragraph_count": float(paragraph_count),
    }


