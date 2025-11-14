"""
Verification script for Summarization Evaluator Service (Phase 9 Task 6)

Tests the implementation of:
- SummarizationEvaluator class initialization
- G-Eval metrics (with fallback behavior)
- FineSurE metrics
- BERTScore metric
- evaluate_summary method

This script verifies the core functionality without requiring OpenAI API key.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Import directly without going through app/__init__.py to avoid Prometheus issues
from sqlalchemy import create_engine, Column, String, Text, Float, Integer, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
import uuid
from datetime import datetime, timezone

# Create minimal Base and Resource for testing
Base = declarative_base()

class Resource(Base):
    """Minimal Resource model for testing."""
    __tablename__ = "resources"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Summary quality fields
    summary_coherence = Column(Float, nullable=True)
    summary_consistency = Column(Float, nullable=True)
    summary_fluency = Column(Float, nullable=True)
    summary_relevance = Column(Float, nullable=True)
    summary_completeness = Column(Float, nullable=True)
    summary_conciseness = Column(Float, nullable=True)
    summary_bertscore = Column(Float, nullable=True)
    summary_quality_overall = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())

# Import the service module directly without going through app package
import importlib.util
spec = importlib.util.spec_from_file_location(
    "summarization_evaluator",
    os.path.join(os.path.dirname(__file__), "app", "services", "summarization_evaluator.py")
)
summarization_evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summarization_evaluator)
SummarizationEvaluator = summarization_evaluator.SummarizationEvaluator


def test_summarization_evaluator():
    """Test SummarizationEvaluator implementation."""
    
    print("=" * 80)
    print("PHASE 9 TASK 6: SUMMARIZATION EVALUATOR SERVICE VERIFICATION")
    print("=" * 80)
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Test 1: Initialize SummarizationEvaluator without API key
        print("\n[TEST 1] Initialize SummarizationEvaluator without API key")
        evaluator = SummarizationEvaluator(db=db)
        assert evaluator.db == db
        assert evaluator.openai_api_key is None
        assert evaluator.openai_available is False
        print("✓ SummarizationEvaluator initialized successfully")
        print(f"  - OpenAI available: {evaluator.openai_available}")
        print(f"  - Summary weights: {evaluator.SUMMARY_WEIGHTS}")
        
        # Test 2: Initialize with API key (won't actually use it)
        print("\n[TEST 2] Initialize SummarizationEvaluator with API key")
        evaluator_with_key = SummarizationEvaluator(db=db, openai_api_key="test-key")
        assert evaluator_with_key.openai_api_key == "test-key"
        print("✓ SummarizationEvaluator initialized with API key")
        
        # Test 3: Test G-Eval metrics (should use fallback)
        print("\n[TEST 3] Test G-Eval metrics (fallback behavior)")
        summary = "This is a test summary about machine learning."
        reference = "Machine learning is a field of artificial intelligence that uses statistical techniques."
        
        coherence = evaluator.g_eval_coherence(summary)
        consistency = evaluator.g_eval_consistency(summary, reference)
        fluency = evaluator.g_eval_fluency(summary)
        relevance = evaluator.g_eval_relevance(summary, reference)
        
        assert coherence == 0.7, f"Expected 0.7, got {coherence}"
        assert consistency == 0.7, f"Expected 0.7, got {consistency}"
        assert fluency == 0.7, f"Expected 0.7, got {fluency}"
        assert relevance == 0.7, f"Expected 0.7, got {relevance}"
        
        print("✓ G-Eval metrics use fallback scores correctly")
        print(f"  - Coherence: {coherence}")
        print(f"  - Consistency: {consistency}")
        print(f"  - Fluency: {fluency}")
        print(f"  - Relevance: {relevance}")
        
        # Test 4: Test FineSurE completeness
        print("\n[TEST 4] Test FineSurE completeness metric")
        
        # Test with good overlap
        summary1 = "machine learning artificial intelligence statistical techniques"
        reference1 = "Machine learning is a field of artificial intelligence that uses statistical techniques to enable computers to learn."
        completeness1 = evaluator.finesure_completeness(summary1, reference1)
        
        print(f"✓ FineSurE completeness calculated: {completeness1:.3f}")
        assert 0.0 <= completeness1 <= 1.0, f"Score out of range: {completeness1}"
        
        # Test with no overlap
        summary2 = "xyz abc def"
        reference2 = "completely different words here"
        completeness2 = evaluator.finesure_completeness(summary2, reference2)
        print(f"  - No overlap case: {completeness2:.3f}")
        assert completeness2 == 0.0, f"Expected 0.0, got {completeness2}"
        
        # Test 5: Test FineSurE conciseness
        print("\n[TEST 5] Test FineSurE conciseness metric")
        
        # Test optimal compression (10%)
        summary_optimal = "A" * 100
        reference_optimal = "B" * 1000
        conciseness_optimal = evaluator.finesure_conciseness(summary_optimal, reference_optimal)
        print(f"✓ Optimal compression (10%): {conciseness_optimal:.3f}")
        assert conciseness_optimal == 1.0, f"Expected 1.0, got {conciseness_optimal}"
        
        # Test too short (2%)
        summary_short = "A" * 20
        reference_short = "B" * 1000
        conciseness_short = evaluator.finesure_conciseness(summary_short, reference_short)
        print(f"  - Too short (2%): {conciseness_short:.3f}")
        assert 0.0 < conciseness_short < 1.0, f"Expected < 1.0, got {conciseness_short}"
        
        # Test too long (50%)
        summary_long = "A" * 500
        reference_long = "B" * 1000
        conciseness_long = evaluator.finesure_conciseness(summary_long, reference_long)
        print(f"  - Too long (50%): {conciseness_long:.3f}")
        assert conciseness_long == 0.0, f"Expected 0.0, got {conciseness_long}"
        
        # Test 6: Test BERTScore (with fallback)
        print("\n[TEST 6] Test BERTScore metric")
        bertscore = evaluator.bertscore_f1(summary, reference)
        print(f"✓ BERTScore calculated: {bertscore:.3f}")
        assert 0.0 <= bertscore <= 1.0, f"Score out of range: {bertscore}"
        
        # Test 7: Test evaluate_summary method
        print("\n[TEST 7] Test evaluate_summary method")
        
        # Create test resource
        resource = Resource(
            id=str(uuid.uuid4()),
            title="Test Resource",
            description="This is a comprehensive test summary about machine learning and artificial intelligence.",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(resource)
        db.commit()
        
        # Evaluate summary
        result = evaluator.evaluate_summary(
            resource_id=resource.id,
            use_g_eval=False  # Don't use G-Eval (no API key)
        )
        
        print("✓ Summary evaluation completed")
        print(f"  - Coherence: {result['coherence']:.3f}")
        print(f"  - Consistency: {result['consistency']:.3f}")
        print(f"  - Fluency: {result['fluency']:.3f}")
        print(f"  - Relevance: {result['relevance']:.3f}")
        print(f"  - Completeness: {result['completeness']:.3f}")
        print(f"  - Conciseness: {result['conciseness']:.3f}")
        print(f"  - BERTScore: {result['bertscore']:.3f}")
        print(f"  - Overall: {result['overall']:.3f}")
        
        # Verify all scores are in valid range
        for metric, score in result.items():
            if metric != "error":
                assert 0.0 <= score <= 1.0, f"{metric} score out of range: {score}"
        
        # Verify resource was updated
        db.refresh(resource)
        assert resource.summary_coherence == result['coherence']
        assert resource.summary_consistency == result['consistency']
        assert resource.summary_fluency == result['fluency']
        assert resource.summary_relevance == result['relevance']
        assert resource.summary_completeness == result['completeness']
        assert resource.summary_conciseness == result['conciseness']
        assert resource.summary_bertscore == result['bertscore']
        assert resource.summary_quality_overall == result['overall']
        print("✓ Resource updated with summary quality scores")
        
        # Test 8: Test error handling - resource not found
        print("\n[TEST 8] Test error handling - resource not found")
        try:
            evaluator.evaluate_summary(
                resource_id=str(uuid.uuid4()),
                use_g_eval=False
            )
            print("✗ Should have raised ValueError")
            sys.exit(1)
        except ValueError as e:
            print(f"✓ Correctly raised ValueError: {e}")
        
        # Test 9: Test error handling - no summary
        print("\n[TEST 9] Test error handling - no summary")
        resource_no_summary = Resource(
            id=str(uuid.uuid4()),
            title="Test Resource No Summary",
            description=None,  # No summary
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(resource_no_summary)
        db.commit()
        
        result_no_summary = evaluator.evaluate_summary(
            resource_id=resource_no_summary.id,
            use_g_eval=False
        )
        assert "error" in result_no_summary
        print(f"✓ Correctly returned error: {result_no_summary['error']}")
        
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED!")
        print("=" * 80)
        print("\nSummarization Evaluator Service implementation verified successfully.")
        print("\nImplemented features:")
        print("  ✓ SummarizationEvaluator class with initialization")
        print("  ✓ G-Eval metrics (coherence, consistency, fluency, relevance)")
        print("  ✓ FineSurE metrics (completeness, conciseness)")
        print("  ✓ BERTScore F1 metric")
        print("  ✓ evaluate_summary method with composite scoring")
        print("  ✓ Graceful fallback when APIs unavailable")
        print("  ✓ Error handling for missing resources and summaries")
        print("  ✓ Database updates with all summary quality scores")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    test_summarization_evaluator()
