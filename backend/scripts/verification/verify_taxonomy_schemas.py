"""
Verification script for taxonomy schemas - direct import test.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import schemas directly without going through app/__init__.py

# Direct import to avoid app initialization
import importlib.util
spec = importlib.util.spec_from_file_location(
    "taxonomy_schemas",
    os.path.join(os.path.dirname(__file__), "app", "schemas", "taxonomy.py")
)
taxonomy_schemas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(taxonomy_schemas)

TaxonomyNodeCreate = taxonomy_schemas.TaxonomyNodeCreate
TaxonomyNodeUpdate = taxonomy_schemas.TaxonomyNodeUpdate
ClassificationFeedback = taxonomy_schemas.ClassificationFeedback
ClassifierTrainingRequest = taxonomy_schemas.ClassifierTrainingRequest
LabeledExample = taxonomy_schemas.LabeledExample


def test_schemas():
    """Test all required schemas."""
    
    print("Testing TaxonomyNodeCreate...")
    node = TaxonomyNodeCreate(
        name="Machine Learning",
        parent_id="parent-uuid",
        description="ML topics",
        keywords=["neural networks"],
        allow_resources=True
    )
    assert node.name == "Machine Learning"
    print("  ✓ TaxonomyNodeCreate works")
    
    print("\nTesting TaxonomyNodeUpdate...")
    update = TaxonomyNodeUpdate(name="Updated Name")
    assert update.name == "Updated Name"
    print("  ✓ TaxonomyNodeUpdate works")
    
    print("\nTesting ClassificationFeedback...")
    feedback = ClassificationFeedback(
        resource_id="resource-uuid",
        correct_taxonomy_ids=["node-1", "node-2"]
    )
    assert len(feedback.correct_taxonomy_ids) == 2
    print("  ✓ ClassificationFeedback works")
    
    print("\nTesting ClassifierTrainingRequest...")
    request = ClassifierTrainingRequest(
        labeled_data=[
            LabeledExample(text="Sample text", taxonomy_ids=["node-1"])
        ],
        epochs=3,
        batch_size=16
    )
    assert request.epochs == 3
    print("  ✓ ClassifierTrainingRequest works")
    
    print("\n" + "="*50)
    print("✅ All required schemas verified successfully!")
    print("="*50)
    print("\nSchemas created:")
    print("  - TaxonomyNodeCreate")
    print("  - TaxonomyNodeUpdate")
    print("  - ClassificationFeedback")
    print("  - ClassifierTrainingRequest")
    print("  - LabeledExample (helper)")
    print("\nAdditional schemas for API responses:")
    print("  - TaxonomyNodeResponse")
    print("  - TaxonomyNodeTree")
    print("  - TaxonomyNodeMove")
    print("  - ClassifierTrainingResponse")
    print("  - ClassificationResult")
    print("  - ResourceClassificationResponse")
    print("  - UncertainSample")
    print("  - UncertainSamplesResponse")
    print("  - ClassificationMetrics")
    print("  - TaxonomyStatsResponse")


if __name__ == "__main__":
    test_schemas()
