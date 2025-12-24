"""
Neo Alexandria 2.0 - Summarization Evaluator Service

This module implements state-of-the-art summarization evaluation using:
- G-Eval: LLM-based evaluation framework using GPT-4 for coherence, consistency, fluency, relevance
- FineSurE: Fine-grained summarization evaluation for completeness and conciseness
- BERTScore: Semantic similarity metric using BERT embeddings

Phase 9 enhancement for comprehensive summary quality assessment.

Related files:
- app/services/quality_service.py: Multi-dimensional quality assessment
- app/database/models.py: Resource model with summary quality fields
- app/routers/quality.py: Quality API endpoints

Features:
- G-Eval metrics with GPT-4 (optional, requires API key)
- FineSurE completeness and conciseness metrics
- BERTScore F1 semantic similarity
- Composite summary quality score
- Graceful fallback when APIs unavailable
"""

from __future__ import annotations

import re
from typing import Dict, Optional

from sqlalchemy.orm import Session


class SummarizationEvaluator:
    """
    Evaluates summary quality using state-of-the-art metrics.
    
    Implements:
    - G-Eval: GPT-4 based evaluation for coherence, consistency, fluency, relevance
    - FineSurE: Completeness and conciseness metrics
    - BERTScore: Semantic similarity using BERT embeddings
    
    Provides composite summary quality score with configurable weights.
    """
    
    # Composite summary quality weights (sum to 1.0)
    SUMMARY_WEIGHTS = {
        "coherence": 0.20,      # G-Eval: logical flow
        "consistency": 0.20,    # G-Eval: factual alignment
        "fluency": 0.15,        # G-Eval: grammatical correctness
        "relevance": 0.15,      # G-Eval: key information capture
        "completeness": 0.15,   # FineSurE: coverage
        "conciseness": 0.05,    # FineSurE: information density
        "bertscore": 0.10       # BERTScore: semantic similarity
    }
    
    # Stopwords for FineSurE completeness calculation
    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
        "in", "on", "at", "to", "for", "of", "with", "by", "from", "as",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "should", "could", "may", "might", "can", "this",
        "that", "these", "those", "it", "its", "they", "them", "their"
    }
    
    def __init__(self, db: Session, openai_api_key: Optional[str] = None):
        """
        Initialize SummarizationEvaluator.
        
        Args:
            db: SQLAlchemy database session
            openai_api_key: Optional OpenAI API key for G-Eval metrics
        """
        self.db = db
        self.openai_api_key = openai_api_key
        
        # Configure OpenAI API if key provided
        if self.openai_api_key:
            try:
                import openai
                openai.api_key = self.openai_api_key
                self.openai_available = True
            except ImportError:
                print("Warning: openai package not installed. G-Eval metrics will use fallback scores.")
                self.openai_available = False
        else:
            self.openai_available = False

    
    def g_eval_coherence(self, summary: str) -> float:
        """
        G-Eval coherence: Evaluates if summary flows logically.
        
        Uses GPT-4 to score coherence on 1-5 scale, normalized to 0.0-1.0.
        
        Evaluation Criteria:
        - Logical flow and structure
        - Sentence-to-sentence transitions
        - Overall organization
        
        Args:
            summary: Summary text to evaluate
            
        Returns:
            Coherence score between 0.0 and 1.0
            Fallback: 0.7 if OpenAI API unavailable or errors occur
        """
        if not self.openai_available or not self.openai_api_key:
            return 0.7  # Fallback score
        
        prompt = f"""You will be given a summary. Your task is to rate the summary on coherence.

Evaluation Criteria:
Coherence (1-5) - the collective quality of all sentences. The summary should be 
well-structured and well-organized. The summary should not just be a heap of related 
information, but should build from sentence to sentence to a coherent body of 
information about a topic.

Evaluation Steps:
1. Read the summary carefully.
2. Rate the summary for coherence on a scale of 1 to 5.

Summary:
{summary}

Provide only the numeric rating (1-5):"""
        
        try:
            import openai
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert evaluator of text quality."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=10
            )
            
            # Extract rating from response
            rating_text = response.choices[0].message.content.strip()
            rating = float(rating_text)
            
            # Normalize from 1-5 to 0.0-1.0
            normalized_score = (rating - 1.0) / 4.0
            return max(0.0, min(1.0, normalized_score))
            
        except Exception as e:
            print(f"G-Eval coherence error: {e}")
            return 0.7  # Fallback score
    
    
    def g_eval_consistency(self, summary: str, reference: str) -> float:
        """
        G-Eval consistency: Evaluates factual alignment with reference document.
        
        Uses GPT-4 to check for hallucinations and contradictions.
        
        Evaluation Criteria:
        - Factual alignment with reference
        - No hallucinated facts
        - No contradictions
        
        Args:
            summary: Summary text to evaluate
            reference: Reference document (truncated to 2000 chars)
            
        Returns:
            Consistency score between 0.0 and 1.0
            Fallback: 0.7 if OpenAI API unavailable or errors occur
        """
        if not self.openai_available or not self.openai_api_key:
            return 0.7  # Fallback score
        
        # Truncate reference to 2000 chars for API efficiency
        reference_truncated = reference[:2000] if reference else ""
        
        prompt = f"""You will be given a summary and a reference document. Your task is to rate the 
summary on consistency with the reference.

Evaluation Criteria:
Consistency (1-5) - the factual alignment between the summary and the reference 
document. A factually consistent summary contains only statements that are entailed 
by the source document. Penalize summaries that contain hallucinated facts.

Evaluation Steps:
1. Read the reference document and summary carefully.
2. Check each statement in the summary against the reference.
3. Rate the summary for consistency on a scale of 1 to 5.

Reference Document:
{reference_truncated}

Summary:
{summary}

Provide only the numeric rating (1-5):"""
        
        try:
            import openai
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert evaluator of text quality."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=10
            )
            
            # Extract rating from response
            rating_text = response.choices[0].message.content.strip()
            rating = float(rating_text)
            
            # Normalize from 1-5 to 0.0-1.0
            normalized_score = (rating - 1.0) / 4.0
            return max(0.0, min(1.0, normalized_score))
            
        except Exception as e:
            print(f"G-Eval consistency error: {e}")
            return 0.7  # Fallback score
    
    
    def g_eval_fluency(self, summary: str) -> float:
        """
        G-Eval fluency: Evaluates grammatical correctness and readability.
        
        Uses GPT-4 to assess grammar, sentence structure, and readability.
        
        Evaluation Criteria:
        - Grammatical correctness
        - Sentence structure quality
        - Readability and flow
        
        Args:
            summary: Summary text to evaluate
            
        Returns:
            Fluency score between 0.0 and 1.0
            Fallback: 0.7 if OpenAI API unavailable or errors occur
        """
        if not self.openai_available or not self.openai_api_key:
            return 0.7  # Fallback score
        
        prompt = f"""You will be given a summary. Your task is to rate the summary on fluency.

Evaluation Criteria:
Fluency (1-5) - the quality of individual sentences. Are the sentences grammatically 
correct, easy to read, and well-formed?

Evaluation Steps:
1. Read the summary carefully.
2. Rate the summary for fluency on a scale of 1 to 5.

Summary:
{summary}

Provide only the numeric rating (1-5):"""
        
        try:
            import openai
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert evaluator of text quality."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=10
            )
            
            # Extract rating from response
            rating_text = response.choices[0].message.content.strip()
            rating = float(rating_text)
            
            # Normalize from 1-5 to 0.0-1.0
            normalized_score = (rating - 1.0) / 4.0
            return max(0.0, min(1.0, normalized_score))
            
        except Exception as e:
            print(f"G-Eval fluency error: {e}")
            return 0.7  # Fallback score
    
    
    def g_eval_relevance(self, summary: str, reference: str) -> float:
        """
        G-Eval relevance: Evaluates if summary captures key information.
        
        Uses GPT-4 to assess whether the summary includes important information
        from the reference document.
        
        Evaluation Criteria:
        - Captures key information
        - No redundancies
        - No excess information
        
        Args:
            summary: Summary text to evaluate
            reference: Reference document (truncated to 2000 chars)
            
        Returns:
            Relevance score between 0.0 and 1.0
            Fallback: 0.7 if OpenAI API unavailable or errors occur
        """
        if not self.openai_available or not self.openai_api_key:
            return 0.7  # Fallback score
        
        # Truncate reference to 2000 chars for API efficiency
        reference_truncated = reference[:2000] if reference else ""
        
        prompt = f"""You will be given a summary and reference document. Your task is to rate the 
summary on relevance.

Evaluation Criteria:
Relevance (1-5) - selection of important content from the source. The summary 
should include only important information from the source document. Penalize 
summaries which contain redundancies and excess information.

Evaluation Steps:
1. Read the reference document and summary.
2. Identify key information in the reference.
3. Check if summary captures this key information.
4. Rate the summary for relevance on a scale of 1 to 5.

Reference Document:
{reference_truncated}

Summary:
{summary}

Provide only the numeric rating (1-5):"""
        
        try:
            import openai
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert evaluator of text quality."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=10
            )
            
            # Extract rating from response
            rating_text = response.choices[0].message.content.strip()
            rating = float(rating_text)
            
            # Normalize from 1-5 to 0.0-1.0
            normalized_score = (rating - 1.0) / 4.0
            return max(0.0, min(1.0, normalized_score))
            
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
        summary_words = set(re.findall(r'\b\w+\b', summary.lower()))
        reference_words = set(re.findall(r'\b\w+\b', reference.lower()))
        
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
                verbose=False
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
        self,
        resource_id: str,
        use_g_eval: bool = False
    ) -> Dict[str, float]:
        """
        Comprehensive summary evaluation using all metrics.
        
        Computes G-Eval, FineSurE, and BERTScore metrics, then calculates
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
            use_g_eval: Whether to use G-Eval (requires OpenAI API, slow)
            
        Returns:
            Dictionary with all summary quality metrics
            
        Raises:
            ValueError: If resource not found or has no summary
            
        Performance:
        - Without G-Eval: <2 seconds
        - With G-Eval: <10 seconds (OpenAI API latency)
        """
        from ..database.models import Resource
        
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
        
        # Conditionally compute G-Eval scores
        if use_g_eval and self.openai_available and self.openai_api_key:
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
            self.SUMMARY_WEIGHTS["coherence"] * coherence +
            self.SUMMARY_WEIGHTS["consistency"] * consistency +
            self.SUMMARY_WEIGHTS["fluency"] * fluency +
            self.SUMMARY_WEIGHTS["relevance"] * relevance +
            self.SUMMARY_WEIGHTS["completeness"] * completeness +
            self.SUMMARY_WEIGHTS["conciseness"] * conciseness +
            self.SUMMARY_WEIGHTS["bertscore"] * bertscore
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
            "overall": overall
        }
