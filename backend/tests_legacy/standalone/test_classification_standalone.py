"""
Standalone tests for classification domain objects.

This script can be run directly without pytest or complex imports.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent  # Go up to backend root
sys.path.insert(0, str(backend_path))

# Import directly from module to avoid app/__init__.py dependencies
import importlib.util

spec = importlib.util.spec_from_file_location(
    "classification", backend_path / "app" / "domain" / "classification.py"
)
classification = importlib.util.module_from_spec(spec)

# Also need to load base module
base_spec = importlib.util.spec_from_file_location(
    "base", backend_path / "app" / "domain" / "base.py"
)
base_module = importlib.util.module_from_spec(base_spec)
sys.modules["backend.app.domain"] = type(sys)("backend.app.domain")
sys.modules["backend.app.domain"].ValueObject = None
sys.modules["backend.app.domain"].validate_range = None
sys.modules["backend.app.domain"].validate_positive = None

base_spec.loader.exec_module(base_module)
sys.modules["backend.app.domain"].ValueObject = base_module.ValueObject
sys.modules["backend.app.domain"].validate_range = base_module.validate_range
sys.modules["backend.app.domain"].validate_positive = base_module.validate_positive

spec.loader.exec_module(classification)

ClassificationPrediction = classification.ClassificationPrediction
ClassificationResult = classification.ClassificationResult


def test_classification_prediction_creation():
    """Test creating valid predictions."""
    print("Testing ClassificationPrediction creation...")

    pred = ClassificationPrediction(taxonomy_id="node_123", confidence=0.95, rank=1)

    assert pred.taxonomy_id == "node_123"
    assert pred.confidence == 0.95
    assert pred.rank == 1
    print("✓ Valid prediction created successfully")


def test_classification_prediction_validation():
    """Test prediction validation."""
    print("\nTesting ClassificationPrediction validation...")

    # Test confidence validation
    try:
        ClassificationPrediction("node_1", -0.1, 1)
        assert False, "Should have raised ValueError for negative confidence"
    except ValueError as e:
        assert "confidence must be between 0.0 and 1.0" in str(e)
        print("✓ Confidence validation works (too low)")

    try:
        ClassificationPrediction("node_1", 1.5, 1)
        assert False, "Should have raised ValueError for confidence > 1.0"
    except ValueError as e:
        assert "confidence must be between 0.0 and 1.0" in str(e)
        print("✓ Confidence validation works (too high)")

    # Test rank validation
    try:
        ClassificationPrediction("node_1", 0.95, 0)
        assert False, "Should have raised ValueError for rank = 0"
    except ValueError as e:
        assert "rank must be positive" in str(e)
        print("✓ Rank validation works (zero)")

    # Test taxonomy_id validation
    try:
        ClassificationPrediction("", 0.95, 1)
        assert False, "Should have raised ValueError for empty taxonomy_id"
    except ValueError as e:
        assert "taxonomy_id cannot be empty" in str(e)
        print("✓ Taxonomy ID validation works (empty)")


def test_classification_prediction_confidence_methods():
    """Test confidence level methods."""
    print("\nTesting ClassificationPrediction confidence methods...")

    pred_high = ClassificationPrediction("node_1", 0.85, 1)
    pred_medium = ClassificationPrediction("node_2", 0.65, 2)
    pred_low = ClassificationPrediction("node_3", 0.45, 3)

    assert pred_high.is_high_confidence() is True
    assert pred_medium.is_high_confidence() is False
    assert pred_low.is_high_confidence() is False
    print("✓ is_high_confidence() works")

    assert pred_low.is_low_confidence() is True
    assert pred_medium.is_low_confidence() is False
    assert pred_high.is_low_confidence() is False
    print("✓ is_low_confidence() works")

    assert pred_medium.is_medium_confidence() is True
    assert pred_low.is_medium_confidence() is False
    assert pred_high.is_medium_confidence() is False
    print("✓ is_medium_confidence() works")


def test_classification_prediction_to_dict():
    """Test to_dict serialization."""
    print("\nTesting ClassificationPrediction to_dict...")

    pred = ClassificationPrediction("node_1", 0.95, 1)
    data = pred.to_dict()

    assert data == {"taxonomy_id": "node_1", "confidence": 0.95, "rank": 1}
    print("✓ to_dict() serialization works")


def test_classification_result_creation():
    """Test creating valid classification results."""
    print("\nTesting ClassificationResult creation...")

    predictions = [
        ClassificationPrediction("node_1", 0.95, 1),
        ClassificationPrediction("node_2", 0.87, 2),
    ]

    result = ClassificationResult(
        predictions=predictions, model_version="v1.0.0", inference_time_ms=45.2
    )

    assert len(result.predictions) == 2
    assert result.model_version == "v1.0.0"
    assert result.inference_time_ms == 45.2
    assert result.resource_id is None
    print("✓ Valid result created successfully")


def test_classification_result_validation():
    """Test result validation."""
    print("\nTesting ClassificationResult validation...")

    # Test empty predictions
    try:
        ClassificationResult(
            predictions=[], model_version="v1.0.0", inference_time_ms=45.2
        )
        assert False, "Should have raised ValueError for empty predictions"
    except ValueError as e:
        assert "predictions cannot be empty" in str(e)
        print("✓ Empty predictions validation works")

    # Test empty model_version
    predictions = [ClassificationPrediction("node_1", 0.95, 1)]
    try:
        ClassificationResult(
            predictions=predictions, model_version="", inference_time_ms=45.2
        )
        assert False, "Should have raised ValueError for empty model_version"
    except ValueError as e:
        assert "model_version cannot be empty" in str(e)
        print("✓ Empty model_version validation works")

    # Test negative inference time
    try:
        ClassificationResult(
            predictions=predictions, model_version="v1.0.0", inference_time_ms=-10.0
        )
        assert False, "Should have raised ValueError for negative inference_time_ms"
    except ValueError as e:
        assert "inference_time_ms must be non-negative" in str(e)
        print("✓ Negative inference time validation works")


def test_classification_result_filtering():
    """Test filtering methods."""
    print("\nTesting ClassificationResult filtering methods...")

    predictions = [
        ClassificationPrediction("node_1", 0.95, 1),  # high
        ClassificationPrediction("node_2", 0.85, 2),  # high
        ClassificationPrediction("node_3", 0.65, 3),  # medium
        ClassificationPrediction("node_4", 0.45, 4),  # low
    ]

    result = ClassificationResult(
        predictions=predictions, model_version="v1.0.0", inference_time_ms=45.2
    )

    # Test get_high_confidence
    high_conf = result.get_high_confidence()
    assert len(high_conf) == 2
    assert all(p.confidence >= 0.8 for p in high_conf)
    print("✓ get_high_confidence() works")

    # Test get_low_confidence
    low_conf = result.get_low_confidence()
    assert len(low_conf) == 1
    assert all(p.confidence < 0.5 for p in low_conf)
    print("✓ get_low_confidence() works")

    # Test get_medium_confidence
    medium_conf = result.get_medium_confidence()
    assert len(medium_conf) == 1
    assert all(0.5 <= p.confidence < 0.8 for p in medium_conf)
    print("✓ get_medium_confidence() works")

    # Test get_top_k
    top_2 = result.get_top_k(2)
    assert len(top_2) == 2
    assert top_2[0].confidence == 0.95
    assert top_2[1].confidence == 0.85
    print("✓ get_top_k() works")

    # Test get_by_rank
    top_ranks = result.get_by_rank(2)
    assert len(top_ranks) == 2
    assert all(p.rank <= 2 for p in top_ranks)
    print("✓ get_by_rank() works")

    # Test get_best_prediction
    best = result.get_best_prediction()
    assert best.confidence == 0.95
    print("✓ get_best_prediction() works")


def test_classification_result_analysis():
    """Test analysis methods."""
    print("\nTesting ClassificationResult analysis methods...")

    predictions = [
        ClassificationPrediction("node_1", 0.95, 1),  # high
        ClassificationPrediction("node_2", 0.85, 2),  # high
        ClassificationPrediction("node_3", 0.65, 3),  # medium
        ClassificationPrediction("node_4", 0.45, 4),  # low
    ]

    result = ClassificationResult(
        predictions=predictions, model_version="v1.0.0", inference_time_ms=45.2
    )

    # Test has_high_confidence_predictions
    assert result.has_high_confidence_predictions() is True
    print("✓ has_high_confidence_predictions() works")

    # Test count_by_confidence_level
    counts = result.count_by_confidence_level()
    assert counts == {"low": 1, "medium": 1, "high": 2}
    print("✓ count_by_confidence_level() works")


def test_classification_result_serialization():
    """Test serialization methods."""
    print("\nTesting ClassificationResult serialization...")

    predictions = [
        ClassificationPrediction("node_1", 0.95, 1),
        ClassificationPrediction("node_2", 0.85, 2),
    ]

    result = ClassificationResult(
        predictions=predictions,
        model_version="v1.0.0",
        inference_time_ms=45.2,
        resource_id="resource_123",
    )

    # Test to_dict
    data = result.to_dict()
    assert "predictions" in data
    assert len(data["predictions"]) == 2
    assert data["model_version"] == "v1.0.0"
    assert data["inference_time_ms"] == 45.2
    assert data["resource_id"] == "resource_123"
    assert "metadata" in data
    assert data["metadata"]["total_predictions"] == 2
    print("✓ to_dict() works")

    # Test from_dict
    restored = ClassificationResult.from_dict(data)
    assert len(restored.predictions) == 2
    assert restored.model_version == "v1.0.0"
    assert restored.inference_time_ms == 45.2
    assert restored.resource_id == "resource_123"
    print("✓ from_dict() works")

    # Test round-trip
    data2 = restored.to_dict()
    assert data["model_version"] == data2["model_version"]
    assert data["inference_time_ms"] == data2["inference_time_ms"]
    print("✓ Round-trip serialization works")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("Running Classification Domain Objects Tests")
    print("=" * 70)

    try:
        test_classification_prediction_creation()
        test_classification_prediction_validation()
        test_classification_prediction_confidence_methods()
        test_classification_prediction_to_dict()
        test_classification_result_creation()
        test_classification_result_validation()
        test_classification_result_filtering()
        test_classification_result_analysis()
        test_classification_result_serialization()

        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED!")
        print("=" * 70)
        return True
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
