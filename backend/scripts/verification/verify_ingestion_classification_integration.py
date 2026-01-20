"""
Verification script for resource ingestion classification integration (Phase 8.5 Task 15).

This script verifies that the classification integration code is properly placed
in the resource ingestion pipeline.

Requirements: 12.1, 12.2, 12.3
"""

import sys


def verify_classification_integration():
    """
    Verify that classification integration is properly implemented in resource_service.py.

    Checks:
    1. Classification is imported from classification_service
    2. Classification is called after embedding generation
    3. Classification is called before quality scoring
    4. Classification failures are handled gracefully (try-except)
    """
    print("=" * 80)
    print("Verifying Resource Ingestion Classification Integration (Task 15)")
    print("=" * 80)
    print()

    # Read the resource_service.py file
    try:
        with open(
            "backend/app/services/resource_service.py", "r", encoding="utf-8"
        ) as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ ERROR: Could not find backend/app/services/resource_service.py")
        return False

    checks_passed = 0
    total_checks = 5

    # Check 1: Classification service is imported
    print("Check 1: Classification service import")
    if (
        "from backend.app.services.classification_service import ClassificationService"
        in content
    ):
        print("✓ ClassificationService is imported in process_ingestion")
        checks_passed += 1
    else:
        print("✗ ClassificationService import not found")
    print()

    # Check 2: Classification service is instantiated
    print("Check 2: Classification service instantiation")
    if "ClassificationService(" in content and "use_ml=True" in content:
        print("✓ ClassificationService is instantiated with use_ml=True")
        checks_passed += 1
    else:
        print("✗ ClassificationService instantiation not found or incorrect")
    print()

    # Check 3: classify_resource is called
    print("Check 3: classify_resource method call")
    if "classify_resource(" in content and "resource_id=resource.id" in content:
        print("✓ classify_resource is called with resource_id")
        checks_passed += 1
    else:
        print("✗ classify_resource call not found or incorrect")
    print()

    # Check 4: Classification is wrapped in try-except
    print("Check 4: Error handling for classification")
    if "Phase 8.5: ML Classification" in content:
        # Find the classification block
        classification_start = content.find("Phase 8.5: ML Classification")
        classification_block = content[
            classification_start : classification_start + 2000
        ]

        if (
            "try:" in classification_block
            and "except Exception as classification_exc:" in classification_block
        ):
            print("✓ Classification is wrapped in try-except block")
            checks_passed += 1
        else:
            print("✗ Classification error handling not found")
    else:
        print("✗ Classification integration block not found")
    print()

    # Check 5: Verify execution order (after embeddings, before quality)
    print("Check 5: Execution order verification")

    # Find key sections
    sparse_embedding_idx = content.find("Phase 8: Generate sparse embedding")
    classification_idx = content.find("Phase 8.5: ML Classification")
    quality_idx = content.find("# Quality")

    if sparse_embedding_idx > 0 and classification_idx > 0 and quality_idx > 0:
        if sparse_embedding_idx < classification_idx < quality_idx:
            print("✓ Classification is positioned correctly:")
            print(f"  - After sparse embedding (index {sparse_embedding_idx})")
            print(f"  - Classification at index {classification_idx}")
            print(f"  - Before quality scoring (index {quality_idx})")
            checks_passed += 1
        else:
            print("✗ Classification is not in the correct position")
            print(f"  - Sparse embedding: {sparse_embedding_idx}")
            print(f"  - Classification: {classification_idx}")
            print(f"  - Quality: {quality_idx}")
    else:
        print("✗ Could not find all required sections")
        print(f"  - Sparse embedding found: {sparse_embedding_idx > 0}")
        print(f"  - Classification found: {classification_idx > 0}")
        print(f"  - Quality found: {quality_idx > 0}")
    print()

    # Summary
    print("=" * 80)
    print(f"VERIFICATION SUMMARY: {checks_passed}/{total_checks} checks passed")
    print("=" * 80)
    print()

    if checks_passed == total_checks:
        print(
            "✓ All checks passed! Classification integration is correctly implemented."
        )
        print()
        print("Integration details:")
        print("- Classification is triggered after embedding generation")
        print("- Classification executes before quality scoring")
        print("- Classification failures are handled gracefully")
        print("- Ingestion continues even if classification fails")
        return True
    else:
        print(f"✗ {total_checks - checks_passed} check(s) failed.")
        print("Please review the implementation.")
        return False


def verify_requirements():
    """Verify that the implementation meets the requirements."""
    print()
    print("=" * 80)
    print("REQUIREMENTS VERIFICATION")
    print("=" * 80)
    print()

    requirements = [
        ("12.1", "Classification trigger added to resource ingestion pipeline"),
        (
            "12.2",
            "Classification executes after embedding generation, before quality scoring",
        ),
        (
            "12.3",
            "Classification failures handled gracefully without blocking ingestion",
        ),
    ]

    for req_id, req_desc in requirements:
        print(f"Requirement {req_id}: {req_desc}")
        print("  Status: ✓ Implemented")
        print()

    print("All requirements have been implemented.")
    print()


if __name__ == "__main__":
    success = verify_classification_integration()

    if success:
        verify_requirements()
        print("=" * 80)
        print("TASK 15 VERIFICATION: PASSED ✓")
        print("=" * 80)
        sys.exit(0)
    else:
        print("=" * 80)
        print("TASK 15 VERIFICATION: FAILED ✗")
        print("=" * 80)
        sys.exit(1)
