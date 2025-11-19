"""
Unit tests for Summarization Evaluator Service (Phase 9 Task 6)

Tests individual methods without requiring full database integration.
"""

import sys
from pathlib import Path

# Import the service module directly
import importlib.util

backend_path = Path(__file__).parent.parent.parent.parent
spec = importlib.util.spec_from_file_location(
    "summarization_evaluator",
    backend_path / "app" / "services" / "summarization_evaluator.py"
)
summarization_evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summarization_evaluator)
SummarizationEvaluator = summarization_evaluator.SummarizationEvaluator


def test_initialization():
    """Test SummarizationEvaluator initialization."""
    print("\n[TEST] SummarizationEvaluator Initialization")
    
    # Test without API key
    evaluator = SummarizationEvaluator(db=None)
    assert evaluator.db is None
    assert evaluator.openai_api_key is None
    assert evaluator.openai_available is False
    print("✓ Initialized without API key")
    
    # Test with API key
    evaluator_with_key = SummarizationEvaluator(db=None, openai_api_key="test-key")
    assert evaluator_with_key.openai_api_key == "test-key"
    print("✓ Initialized with API key")
    
    # Check weights
    assert sum(evaluator.SUMMARY_WEIGHTS.values()) == 1.0
    print(f"✓ Summary weights sum to 1.0: {evaluator.SUMMARY_WEIGHTS}")


def test_g_eval_fallback():
    """Test G-Eval metrics use fallback scores when API unavailable."""
    print("\n[TEST] G-Eval Fallback Behavior")
    
    evaluator = SummarizationEvaluator(db=None)
    summary = "This is a test summary."
    reference = "This is a reference document."
    
    # All G-Eval methods should return 0.7 fallback
    assert evaluator.g_eval_coherence(summary) == 0.7
    assert evaluator.g_eval_consistency(summary, reference) == 0.7
    assert evaluator.g_eval_fluency(summary) == 0.7
    assert evaluator.g_eval_relevance(summary, reference) == 0.7
    print("✓ All G-Eval metrics return 0.7 fallback")


def test_finesure_completeness():
    """Test FineSurE completeness metric."""
    print("\n[TEST] FineSurE Completeness")
    
    evaluator = SummarizationEvaluator(db=None)
    
    # Test with good overlap
    summary = "machine learning artificial intelligence"
    reference = "Machine learning is a field of artificial intelligence."
    completeness = evaluator.finesure_completeness(summary, reference)
    assert 0.0 <= completeness <= 1.0
    print(f"✓ Good overlap: {completeness:.3f}")
    
    # Test with no overlap
    summary_no_overlap = "xyz abc"
    reference_no_overlap = "completely different words"
    completeness_no = evaluator.finesure_completeness(summary_no_overlap, reference_no_overlap)
    assert completeness_no == 0.0
    print(f"✓ No overlap: {completeness_no:.3f}")
    
    # Test with empty inputs
    assert evaluator.finesure_completeness("", reference) == 0.0
    assert evaluator.finesure_completeness(summary, "") == 0.0
    print("✓ Empty inputs handled correctly")


def test_finesure_conciseness():
    """Test FineSurE conciseness metric."""
    print("\n[TEST] FineSurE Conciseness")
    
    evaluator = SummarizationEvaluator(db=None)
    
    # Test optimal compression (10%)
    summary_optimal = "A" * 100
    reference_optimal = "B" * 1000
    conciseness_optimal = evaluator.finesure_conciseness(summary_optimal, reference_optimal)
    assert conciseness_optimal == 1.0
    print(f"✓ Optimal (10%): {conciseness_optimal:.3f}")
    
    # Test too short (2%)
    summary_short = "A" * 20
    reference_short = "B" * 1000
    conciseness_short = evaluator.finesure_conciseness(summary_short, reference_short)
    assert 0.0 < conciseness_short < 1.0
    assert abs(conciseness_short - 0.4) < 0.01  # Should be 0.02/0.05 = 0.4
    print(f"✓ Too short (2%): {conciseness_short:.3f}")
    
    # Test too long (50%)
    summary_long = "A" * 500
    reference_long = "B" * 1000
    conciseness_long = evaluator.finesure_conciseness(summary_long, reference_long)
    assert conciseness_long == 0.0
    print(f"✓ Too long (50%): {conciseness_long:.3f}")
    
    # Test edge case: 5% (lower bound of optimal)
    summary_5 = "A" * 50
    reference_5 = "B" * 1000
    conciseness_5 = evaluator.finesure_conciseness(summary_5, reference_5)
    assert conciseness_5 == 1.0
    print(f"✓ Lower bound (5%): {conciseness_5:.3f}")
    
    # Test edge case: 15% (upper bound of optimal)
    summary_15 = "A" * 150
    reference_15 = "B" * 1000
    conciseness_15 = evaluator.finesure_conciseness(summary_15, reference_15)
    assert conciseness_15 == 1.0
    print(f"✓ Upper bound (15%): {conciseness_15:.3f}")


def test_bertscore_fallback():
    """Test BERTScore metric with fallback."""
    print("\n[TEST] BERTScore Fallback")
    
    evaluator = SummarizationEvaluator(db=None)
    summary = "This is a test summary."
    reference = "This is a reference document."
    
    # Should return fallback score (0.5) if bert_score not installed
    bertscore = evaluator.bertscore_f1(summary, reference)
    assert 0.0 <= bertscore <= 1.0
    print(f"✓ BERTScore: {bertscore:.3f}")
    
    # Test with empty inputs
    assert evaluator.bertscore_f1("", reference) == 0.5
    assert evaluator.bertscore_f1(summary, "") == 0.5
    print("✓ Empty inputs return fallback")


def test_stopwords():
    """Test stopwords are properly defined."""
    print("\n[TEST] Stopwords")
    
    evaluator = SummarizationEvaluator(db=None)
    assert len(evaluator.STOPWORDS) > 0
    assert "the" in evaluator.STOPWORDS
    assert "and" in evaluator.STOPWORDS
    assert "is" in evaluator.STOPWORDS
    print(f"✓ {len(evaluator.STOPWORDS)} stopwords defined")


def run_all_tests():
    """Run all unit tests."""
    print("=" * 80)
    print("PHASE 9 TASK 6: SUMMARIZATION EVALUATOR UNIT TESTS")
    print("=" * 80)
    
    try:
        test_initialization()
        test_g_eval_fallback()
        test_finesure_completeness()
        test_finesure_conciseness()
        test_bertscore_fallback()
        test_stopwords()
        
        print("\n" + "=" * 80)
        print("ALL UNIT TESTS PASSED!")
        print("=" * 80)
        print("\nSummarization Evaluator Service core functionality verified:")
        print("  ✓ Initialization with and without API key")
        print("  ✓ G-Eval fallback behavior")
        print("  ✓ FineSurE completeness calculation")
        print("  ✓ FineSurE conciseness calculation")
        print("  ✓ BERTScore fallback behavior")
        print("  ✓ Stopwords configuration")
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
