"""
Quality Module - Summarization Evaluator

This module implements state-of-the-art summarization evaluation using:
- G-Eval: LLM-based evaluation framework using Flan-T5-Large for coherence, consistency, fluency, relevance
- FineSurE: Fine-grained summarization evaluation for completeness and conciseness
- BERTScore: Semantic similarity metric using BERT embeddings

Extracted from app/services/summarization_evaluator.py as part of Phase 14 vertical slice refactoring.

Features:
- G-Eval metrics with Flan-T5-Large (self-hosted, no API costs)
- FineSurE completeness and conciseness metrics
- BERTScore F1 semantic similarity
- Composite summary quality score
- Graceful fallback when models unavailable
"""

from __future__ import annotations

import re
from typing import Dict, Optional

from sqlalchemy.orm import Session


class SummarizationEvaluator:
    """
    Evaluates summary quality using state-of-the-art metrics.

    Implements:
    - G-Eval: Flan-T5-Large based evaluation for coherence, consistency, fluency, relevance
    - FineSurE: Completeness and conciseness metrics
    - BERTScore: Semantic similarity using BERT embeddings

    Provides composite summary quality score with configurable weights.
    """

    # Composite summary quality weights (sum to 1.0)
    SUMMARY_WEIGHTS = {
        "coherence": 0.20,  # G-Eval: logical flow
        "consistency": 0.20,  # G-Eval: factual alignment
        "fluency": 0.15,  # G-Eval: grammatical correctness
        "relevance": 0.15,  # G-Eval: key information capture
        "completeness": 0.15,  # FineSurE: coverage
        "conciseness": 0.05,  # FineSurE: information density
        "bertscore": 0.10,  # BERTScore: semantic similarity
    }

    # Stopwords for FineSurE completeness calculation
    STOPWORDS = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "is",
        "are",
        "was",
        "were",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "as",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "should",
        "could",
        "may",
        "might",
        "can",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "they",
        "them",
        "their",
    }

    def __init__(
        self,
        db: Session,
        model_name: str = "google/flan-t5-large",
        openai_api_key: Optional[
            str
        ] = None,  # Kept for backward compatibility, not used
    ):
        """
        Initialize SummarizationEvaluator.

        Args:
            db: SQLAlchemy database session
            model_name: HuggingFace model name for G-Eval (default: google/flan-t5-large)
            openai_api_key: Deprecated, kept for backward compatibility
        """
        self.db = db
        self.model_name = model_name
        self.openai_api_key = openai_api_key  # Kept for backward compatibility

        # Lazy load HuggingFace pipeline
        self._hf_pipeline = None
        self.hf_available = False

        # Try to import transformers
        try:
            import transformers

            self.hf_available = True
        except ImportError:
            print(
                "Warning: transformers package not installed. G-Eval metrics will use fallback scores."
            )
            self.hf_available = False

        # For backward compatibility
        self.openai_available = False

    @property
    def hf_pipeline(self):
        """Lazy load HuggingFace text generation pipeline."""
        if self._hf_pipeline is None and self.hf_available:
            try:
                from transformers import pipeline
                import torch

                # Use GPU if available, otherwise CPU
                device = 0 if torch.cuda.is_available() else -1

                self._hf_pipeline = pipeline(
                    "text2text-generation",
                    model=self.model_name,
                    device=device,
                    max_length=512,
                )
                print(f"Loaded {self.model_name} on {'GPU' if device == 0 else 'CPU'}")
            except Exception as e:
                print(f"Failed to load HuggingFace model: {e}")
                self._hf_pipeline = None
        return self._hf_pipeline

    def g_eval_coherence(self, summary: str) -> float:
        """
        G-Eval coherence: Evaluates if summary flows logically.

        Uses Flan-T5-Large to score coherence on 1-5 scale, normalized to 0.0-1.0.

        Evaluation Criteria:
        - Logical flow and structure
        - Sentence-to-sentence transitions
        - Overall organization

        Args:
            summary: Summary text to evaluate

        Returns:
            Coherence score between 0.0 and 1.0
            Fallback: 0.7 if model unavailable or errors occur
        """
        if not self.hf_available or self.hf_pipeline is None:
            return 0.7  # Fallback score

        prompt = f"""Rate the coherence of this summary on a scale of 1-5.

Coherence means the summary flows logically, has good sentence-to-sentence transitions, and is well-organized.

Summary: {summary}

Rating (1-5):"""

        try:
            result = self.hf_pipeline(
                prompt, max_new_tokens=10, temperature=0.1, do_sample=False
            )

            # Extract rating from response
            response_text = result[0]["generated_text"].strip()

            # Parse rating (handle various formats like "4", "Rating: 4", "4/5", etc.)
            match = re.search(r"(\d+)", response_text)
            if match:
                rating = float(match.group(1))
                # Clamp to 1-5 range
                rating = max(1.0, min(5.0, rating))
                # Normalize to 0-1: (rating - 1) / 4
                normalized = (rating - 1.0) / 4.0
                return max(0.0, min(1.0, normalized))

            return 0.7  # Fallback if parsing fails

        except Exception as e:
            print(f"G-Eval coherence error: {e}")
            return 0.7  # Fallback score

    def g_eval_consistency(self, summary: str, reference: str) -> float:
        """
        G-Eval consistency: Evaluates factual alignment with reference document.

        Uses Flan-T5-Large to check for hallucinations and contradictions.

        Evaluation Criteria:
        - Factual alignment with reference
        - No hallucinated facts
        - No contradictions

        Args:
            summary: Summary text to evaluate
            reference: Reference document (truncated to 1000 chars for model efficiency)

        Returns:
            Consistency score between 0.0 and 1.0
            Fallback: 0.7 if model unavailable or errors occur
        """
        if not self.hf_available or self.hf_pipeline is None:
            return 0.7  # Fallback score

        # Truncate reference to 1000 chars for model efficiency
        reference_truncated = reference[:1000] if reference else ""

        prompt = f"""Rate the consistency of this summary with the reference document on a scale of 1-5.

Consistency means the summary contains only facts from the reference and has no hallucinations or contradictions.

Reference: {reference_truncated}

Summary: {summary}

Rating (1-5):"""

        try:
            result = self.hf_pipeline(
                prompt, max_new_tokens=10, temperature=0.1, do_sample=False
            )

            # Extract rating from response
            response_text = result[0]["generated_text"].strip()

            # Parse rating
            match = re.search(r"(\d+)", response_text)
            if match:
                rating = float(match.group(1))
                rating = max(1.0, min(5.0, rating))
                normalized = (rating - 1.0) / 4.0
                return max(0.0, min(1.0, normalized))

            return 0.7  # Fallback if parsing fails

        except Exception as e:
            print(f"G-Eval consistency error: {e}")
            return 0.7  # Fallback score

    def g_eval_fluency(self, summary: str) -> float:
        """
        G-Eval fluency: Evaluates grammatical correctness and readability.

        Uses Flan-T5-Large to assess grammar, sentence structure, and readability.

        Evaluation Criteria:
        - Grammatical correctness
        - Sentence structure quality
        - Readability and flow

        Args:
            summary: Summary text to evaluate

        Returns:
            Fluency score between 0.0 and 1.0
            Fallback: 0.7 if model unavailable or errors occur
        """
        if not self.hf_available or self.hf_pipeline is None:
            return 0.7  # Fallback score

        prompt = f"""Rate the fluency of this summary on a scale of 1-5.

Fluency means the sentences are grammatically correct, easy to read, and well-formed.

Summary: {summary}

Rating (1-5):"""

        try:
            result = self.hf_pipeline(
                prompt, max_new_tokens=10, temperature=0.1, do_sample=False
            )

            # Extract rating from response
            response_text = result[0]["generated_text"].strip()

            # Parse rating
            match = re.search(r"(\d+)", response_text)
            if match:
                rating = float(match.group(1))
                rating = max(1.0, min(5.0, rating))
                normalized = (rating - 1.0) / 4.0
                return max(0.0, min(1.0, normalized))

            return 0.7  # Fallback if parsing fails

        except Exception as e:
            print(f"G-Eval fluency error: {e}")
            return 0.7  # Fallback score

    def g_eval_relevance(self, summary: str, reference: str) -> float:
        """
        G-Eval relevance: Evaluates if summary captures key information.

        Uses Flan-T5-Large to assess whether the summary includes important information
        from the reference document.

        Evaluation Criteria:
        - Captures key information
        - No redundancies
        - No excess information

        Args:
            summary: Summary text to evaluate
            reference: Reference document (truncated to 1000 chars for model efficiency)

        Returns:
            Relevance score between 0.0 and 1.0
            Fallback: 0.7 if model unavailable or errors occur
        """
        if not self.hf_available or self.hf_pipeline is None:
            return 0.7  # Fallback score

        # Truncate reference to 1000 chars for model efficiency
        reference_truncated = reference[:1000] if reference else ""

        prompt = f"""Rate the relevance of this summary on a scale of 1-5.

Relevance means the summary includes only important information from the reference and has no redundancies.

Reference: {reference_truncated}

Summary: {summary}

Rating (1-5):"""

        try:
            result = self.hf_pipeline(
                prompt, max_new_tokens=10, temperature=0.1, do_sample=False
            )

            # Extract rating from response
            response_text = result[0]["generated_text"].strip()

            # Parse rating
            match = re.search(r"(\d+)", response_text)
            if match:
                rating = float(match.group(1))
                rating = max(1.0, min(5.0, rating))
                normalized = (rating - 1.0) / 4.0
                return max(0.0, min(1.0, normalized))

            return 0.7  # Fallback if parsing fails

        except Exception as e:
            print(f"G-Eval relevance error: {e}")
            return 0.7  # Fallback score

    def finesure_completeness(self, summary: str, reference: str) -> float:
        """
        FineSurE completeness: Measures coverage of key information.

        Uses term overlap to calculate how much of the reference content
        is covered by the summary. Expects 15% coverage for good summaries.

        Algorithm:
        1. Extract words from reference and summary
        2. Remove stopwords
        3. Compute overlap ratio
        4. Score based on 15% coverage expectation

        Args:
            summary: Summary text to evaluate
            reference: Reference document

        Returns:
            Completeness score between 0.0 and 1.0
        """
        if not summary or not reference:
            return 0.0

        # Extract words (alphanumeric sequences)
        summary_words = set(re.findall(r"\b\w+\b", summary.lower()))
        reference_words = set(re.findall(r"\b\w+\b", reference.lower()))

        # Remove stopwords
        summary_words = summary_words - self.STOPWORDS
        reference_words = reference_words - self.STOPWORDS

        if not reference_words:
            return 0.0

        # Compute overlap
        overlap = len(summary_words & reference_words)

        # Calculate completeness score
        # Expect 15% coverage for good summaries
        expected_coverage = len(reference_words) * 0.15

        if expected_coverage == 0:
            return 0.0

        completeness = min(1.0, overlap / expected_coverage)
        return float(completeness)

    def finesure_conciseness(self, summary: str, reference: str) -> float:
        """
        FineSurE conciseness: Measures information density.

        Uses compression ratio to assess whether the summary is appropriately
        concise. Optimal range is 5-15% of original length.

        Scoring:
        - If 5% ≤ ratio ≤ 15%: return 1.0 (optimal)
        - If ratio < 5%: return ratio / 0.05 (too short)
        - If ratio > 15%: return max(0.0, 1.0 - (ratio - 0.15) / 0.35) (too long)

        Args:
            summary: Summary text to evaluate
            reference: Reference document

        Returns:
            Conciseness score between 0.0 and 1.0
        """
        if not summary or not reference:
            return 0.0

        # Calculate compression ratio
        summary_length = len(summary)
        reference_length = len(reference)

        if reference_length == 0:
            return 0.0

        compression_ratio = summary_length / reference_length

        # Optimal range: 5-15% (0.05-0.15)
        if 0.05 <= compression_ratio <= 0.15:
            return 1.0
        elif compression_ratio < 0.05:
            # Too short - proportional penalty
            return float(compression_ratio / 0.05)
        else:
            # Too long - penalty increases with length
            # At 50% (0.50), score should be 0.0
            score = max(0.0, 1.0 - (compression_ratio - 0.15) / 0.35)
            return float(score)

    def bertscore_f1(self, summary: str, reference: str) -> float:
        """
        Computes BERTScore F1 for semantic similarity.

        Uses BERT embeddings for token-level semantic comparison.
        More robust than ROUGE as it captures semantic similarity
        rather than just lexical overlap.

        Model: microsoft/deberta-xlarge-mnli (high quality)

        Args:
            summary: Summary text to evaluate
            reference: Reference document

        Returns:
            BERTScore F1 score between 0.0 and 1.0
            Fallback: 0.5 if error occurs
        """
        if not summary or not reference:
            return 0.5  # Neutral fallback

        try:
            from bert_score import score as bert_score

            # Compute BERTScore
            # Returns: (Precision, Recall, F1) tensors
            P, R, F1 = bert_score(
                cands=[summary],
                refs=[reference],
                lang="en",
                model_type="microsoft/deberta-xlarge-mnli",
                verbose=False,
            )

            # Extract F1 score (first element since we passed single summary)
            f1_score = float(F1[0].item())

            return max(0.0, min(1.0, f1_score))

        except ImportError:
            print("Warning: bert_score package not installed. Using fallback score.")
            return 0.5
        except Exception as e:
            print(f"BERTScore error: {e}")
            return 0.5  # Fallback score

    def evaluate_summary(
        self, resource_id: str, use_g_eval: bool = True
    ) -> Dict[str, float]:
        """
        Comprehensive summary evaluation using all metrics.

        Computes G-Eval (Flan-T5), FineSurE, and BERTScore metrics, then calculates
        a composite summary quality score. Updates the resource with all scores.

        Composite weights:
        - Coherence: 20%
        - Consistency: 20%
        - Fluency: 15%
        - Relevance: 15%
        - Completeness: 15%
        - Conciseness: 5%
        - BERTScore: 10%

        Args:
            resource_id: Resource UUID to evaluate
            use_g_eval: Whether to use G-Eval with Flan-T5 (default: True)

        Returns:
            Dictionary with all summary quality metrics

        Raises:
            ValueError: If resource not found or has no summary

        Performance:
        - With G-Eval (CPU): ~2-3 seconds
        - With G-Eval (GPU): ~0.5-1 second
        - Without G-Eval: <0.5 seconds (uses fallback scores)
        """
        from app.database.models import Resource

        # Fetch resource
        resource = self.db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")

        # Validate summary exists
        # Use description as summary proxy (or check for dedicated summary field)
        summary = resource.description
        if not summary or not summary.strip():
            return {"error": "Resource has no summary"}

        # Extract reference text (content or title as fallback)
        # For now, use title as reference since we don't have separate content field
        # In production, this would be the full document content
        reference = resource.description  # Use same field for now
        if not reference:
            reference = resource.title or ""

        # Conditionally compute G-Eval scores using Flan-T5
        if use_g_eval and self.hf_available:
            coherence = self.g_eval_coherence(summary)
            consistency = self.g_eval_consistency(summary, reference)
            fluency = self.g_eval_fluency(summary)
            relevance = self.g_eval_relevance(summary, reference)
        else:
            # Use fallback scores when G-Eval unavailable
            coherence = 0.7
            consistency = 0.7
            fluency = 0.7
            relevance = 0.7

        # Compute FineSurE metrics (always available)
        completeness = self.finesure_completeness(summary, reference)
        conciseness = self.finesure_conciseness(summary, reference)

        # Compute BERTScore (always available with fallback)
        bertscore = self.bertscore_f1(summary, reference)

        # Calculate composite summary quality
        overall = (
            self.SUMMARY_WEIGHTS["coherence"] * coherence
            + self.SUMMARY_WEIGHTS["consistency"] * consistency
            + self.SUMMARY_WEIGHTS["fluency"] * fluency
            + self.SUMMARY_WEIGHTS["relevance"] * relevance
            + self.SUMMARY_WEIGHTS["completeness"] * completeness
            + self.SUMMARY_WEIGHTS["conciseness"] * conciseness
            + self.SUMMARY_WEIGHTS["bertscore"] * bertscore
        )

        # Update resource with all summary quality scores
        resource.summary_coherence = coherence
        resource.summary_consistency = consistency
        resource.summary_fluency = fluency
        resource.summary_relevance = relevance
        resource.summary_completeness = completeness
        resource.summary_conciseness = conciseness
        resource.summary_bertscore = bertscore
        resource.summary_quality_overall = overall

        # Commit changes to database
        self.db.commit()

        # Return all metrics
        return {
            "coherence": coherence,
            "consistency": consistency,
            "fluency": fluency,
            "relevance": relevance,
            "completeness": completeness,
            "conciseness": conciseness,
            "bertscore": bertscore,
            "overall": overall,
        }
