"""
Example usage of classification domain objects.

This demonstrates how to use ClassificationPrediction and ClassificationResult
to replace primitive obsession in the ML classification service.
"""

import sys
from pathlib import Path

# Add backend to path for standalone execution
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.domain.classification import (
    ClassificationPrediction,
    ClassificationResult,
)


def example_basic_usage():
    """Basic usage example."""
    print("=" * 70)
    print("Example 1: Basic Usage")
    print("=" * 70)

    # Create individual predictions
    pred1 = ClassificationPrediction(
        taxonomy_id="science/physics", confidence=0.95, rank=1
    )

    pred2 = ClassificationPrediction(
        taxonomy_id="science/astronomy", confidence=0.87, rank=2
    )

    pred3 = ClassificationPrediction(
        taxonomy_id="science/mathematics", confidence=0.65, rank=3
    )

    # Create classification result
    result = ClassificationResult(
        predictions=[pred1, pred2, pred3],
        model_version="bert-base-v1.0.0",
        inference_time_ms=42.5,
        resource_id="resource_12345",
    )

    print(f"Total predictions: {len(result.predictions)}")
    print(f"Model version: {result.model_version}")
    print(f"Inference time: {result.inference_time_ms}ms")
    print()


def example_filtering():
    """Filtering predictions by confidence."""
    print("=" * 70)
    print("Example 2: Filtering by Confidence")
    print("=" * 70)

    predictions = [
        ClassificationPrediction("category_1", 0.95, 1),
        ClassificationPrediction("category_2", 0.87, 2),
        ClassificationPrediction("category_3", 0.65, 3),
        ClassificationPrediction("category_4", 0.45, 4),
        ClassificationPrediction("category_5", 0.30, 5),
    ]

    result = ClassificationResult(
        predictions=predictions, model_version="v1.0.0", inference_time_ms=50.0
    )

    # Get high confidence predictions
    high_conf = result.get_high_confidence()
    print(f"High confidence predictions (≥0.8): {len(high_conf)}")
    for pred in high_conf:
        print(f"  - {pred.taxonomy_id}: {pred.confidence:.2f}")

    # Get medium confidence predictions
    medium_conf = result.get_medium_confidence()
    print(f"\nMedium confidence predictions (0.5-0.8): {len(medium_conf)}")
    for pred in medium_conf:
        print(f"  - {pred.taxonomy_id}: {pred.confidence:.2f}")

    # Get low confidence predictions
    low_conf = result.get_low_confidence()
    print(f"\nLow confidence predictions (<0.5): {len(low_conf)}")
    for pred in low_conf:
        print(f"  - {pred.taxonomy_id}: {pred.confidence:.2f}")

    print()


def example_top_k():
    """Getting top K predictions."""
    print("=" * 70)
    print("Example 3: Top K Predictions")
    print("=" * 70)

    predictions = [
        ClassificationPrediction("physics", 0.75, 1),
        ClassificationPrediction("chemistry", 0.95, 2),
        ClassificationPrediction("biology", 0.85, 3),
        ClassificationPrediction("mathematics", 0.65, 4),
    ]

    result = ClassificationResult(
        predictions=predictions, model_version="v1.0.0", inference_time_ms=50.0
    )

    # Get top 3 by confidence
    top_3 = result.get_top_k(3)
    print("Top 3 predictions by confidence:")
    for i, pred in enumerate(top_3, 1):
        print(f"  {i}. {pred.taxonomy_id}: {pred.confidence:.2f}")

    # Get best prediction
    best = result.get_best_prediction()
    print(f"\nBest prediction: {best.taxonomy_id} ({best.confidence:.2f})")
    print()


def example_analysis():
    """Analyzing classification results."""
    print("=" * 70)
    print("Example 4: Result Analysis")
    print("=" * 70)

    predictions = [
        ClassificationPrediction("cat_1", 0.95, 1),
        ClassificationPrediction("cat_2", 0.88, 2),
        ClassificationPrediction("cat_3", 0.70, 3),
        ClassificationPrediction("cat_4", 0.55, 4),
        ClassificationPrediction("cat_5", 0.40, 5),
    ]

    result = ClassificationResult(
        predictions=predictions, model_version="v1.0.0", inference_time_ms=50.0
    )

    # Check if we have high confidence predictions
    has_high = result.has_high_confidence_predictions()
    print(f"Has high confidence predictions: {has_high}")

    # Count by confidence level
    counts = result.count_by_confidence_level()
    print("\nConfidence distribution:")
    print(f"  High (≥0.8): {counts['high']}")
    print(f"  Medium (0.5-0.8): {counts['medium']}")
    print(f"  Low (<0.5): {counts['low']}")
    print()


def example_api_compatibility():
    """Converting to/from dictionaries for API compatibility."""
    print("=" * 70)
    print("Example 5: API Compatibility")
    print("=" * 70)

    # Create result
    predictions = [
        ClassificationPrediction("science", 0.95, 1),
        ClassificationPrediction("technology", 0.85, 2),
    ]

    result = ClassificationResult(
        predictions=predictions,
        model_version="v1.0.0",
        inference_time_ms=45.2,
        resource_id="res_123",
    )

    # Convert to dictionary (for API response)
    api_response = result.to_dict()
    print("API Response:")
    print(f"  Model: {api_response['model_version']}")
    print(f"  Inference time: {api_response['inference_time_ms']}ms")
    print(f"  Total predictions: {api_response['metadata']['total_predictions']}")
    print(f"  Best confidence: {api_response['metadata']['best_confidence']:.2f}")
    print(
        f"  Confidence distribution: {api_response['metadata']['confidence_distribution']}"
    )

    # Convert back from dictionary
    restored = ClassificationResult.from_dict(api_response)
    print(f"\nRestored result has {len(restored.predictions)} predictions")
    print()


def example_before_after():
    """Show before/after comparison with primitive obsession."""
    print("=" * 70)
    print("Example 6: Before/After Comparison")
    print("=" * 70)

    print("BEFORE (Primitive Obsession):")
    print("-" * 70)
    print("""
    # Old way - using dictionaries
    result = {
        'predictions': [
            {'taxonomy_id': 'science', 'confidence': 0.95, 'rank': 1},
            {'taxonomy_id': 'tech', 'confidence': 0.85, 'rank': 2}
        ],
        'model_version': 'v1.0.0',
        'inference_time_ms': 45.2
    }
    
    # No validation - can have invalid data
    result['predictions'][0]['confidence'] = 1.5  # Invalid!
    
    # No business logic - must implement everywhere
    high_conf = [p for p in result['predictions'] if p['confidence'] >= 0.8]
    """)

    print("\nAFTER (Domain Objects):")
    print("-" * 70)
    print("""
    # New way - using domain objects
    result = ClassificationResult(
        predictions=[
            ClassificationPrediction('science', 0.95, 1),
            ClassificationPrediction('tech', 0.85, 2)
        ],
        model_version='v1.0.0',
        inference_time_ms=45.2
    )
    
    # Automatic validation - raises ValueError for invalid data
    # ClassificationPrediction('invalid', 1.5, 1)  # Raises ValueError!
    
    # Business logic encapsulated in domain object
    high_conf = result.get_high_confidence()
    best = result.get_best_prediction()
    counts = result.count_by_confidence_level()
    """)
    print()


def main():
    """Run all examples."""
    example_basic_usage()
    example_filtering()
    example_top_k()
    example_analysis()
    example_api_compatibility()
    example_before_after()

    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
