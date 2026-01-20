"""
Collections Module - Aggregation Tests

Tests for collection embedding aggregation using Golden Data pattern.
All test expectations are loaded from golden_data/collections_logic.json.

NO inline expected values - all assertions use Golden Data.
"""

from tests.protocol import load_golden_data


class TestCollectionAggregation:
    """Test suite for collection embedding aggregation using Golden Data."""

    def test_mean_vector_calculation(
        self, db_session, create_test_resource, create_test_collection
    ):
        """
        Test mean vector calculation for collection embedding.

        Golden Data Case: mean_vector_calculation
        Input: 3 resources with specific embeddings
        Expected: Normalized mean vector with tolerance 0.001

        **Validates: Requirements 5.1, 5.2, 8.2, 8.3**
        """
        # Load Golden Data to get inputs and expected values
        golden_data = load_golden_data("collections_logic")
        test_case = golden_data["mean_vector_calculation"]

        # Create test collection
        collection = create_test_collection(
            name="Test Collection", owner_id="test_user"
        )

        # Create resources with embeddings from golden data
        resource_ids = []
        for resource_data in test_case["input"]["resources"]:
            resource = create_test_resource(
                title=f"Resource {resource_data['id']}",
                embedding=resource_data["embedding"],
            )
            resource_ids.append(resource.id)

        # Add resources to collection
        from app.modules.collections.service import CollectionService

        service = CollectionService(db_session)
        service.add_resources_to_collection(
            collection_id=collection.id, resource_ids=resource_ids, owner_id="test_user"
        )

        # Compute collection embedding
        result_embedding = service.compute_collection_embedding(collection.id)

        # Get expected values from golden data
        expected_embedding = test_case["expected"]["collection_embedding"]
        tolerance = test_case["expected"]["tolerance"]

        # Verify embedding matches golden data with tolerance
        assert result_embedding is not None, "Collection embedding should not be None"
        assert len(result_embedding) == len(expected_embedding), (
            f"Embedding dimension mismatch: expected {len(expected_embedding)}, got {len(result_embedding)}"
        )

        # Compare each dimension with tolerance
        for i, (actual, expected) in enumerate(
            zip(result_embedding, expected_embedding)
        ):
            diff = abs(actual - expected)
            assert diff <= tolerance, (
                f"IMPLEMENTATION FAILURE: Embedding dimension {i} mismatch.\n"
                f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
                f"\n"
                f"Golden Data File: golden_data/collections_logic.json\n"
                f"Test Case ID: mean_vector_calculation\n"
                f"\n"
                f"Expected value: {expected}\n"
                f"Actual value: {actual}\n"
                f"Difference: {diff} (tolerance: {tolerance})"
            )

    def test_empty_collection_embedding(self, db_session, create_test_collection):
        """
        Test embedding calculation for empty collection.

        Golden Data Case: empty_collection
        Input: Collection with no resources
        Expected: None (no embedding)

        **Validates: Requirements 5.1, 5.2, 8.4**
        """
        # Load Golden Data
        golden_data = load_golden_data("collections_logic")
        test_case = golden_data["empty_collection"]

        # Create empty collection
        collection = create_test_collection(
            name="Empty Collection", owner_id="test_user"
        )

        # Compute collection embedding
        from app.modules.collections.service import CollectionService

        service = CollectionService(db_session)
        result_embedding = service.compute_collection_embedding(collection.id)

        # Get expected value from golden data
        expected_embedding = test_case["expected"]["collection_embedding"]

        # Verify result matches golden data
        assert result_embedding == expected_embedding, (
            f"IMPLEMENTATION FAILURE: Empty collection embedding mismatch.\n"
            f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
            f"\n"
            f"Golden Data File: golden_data/collections_logic.json\n"
            f"Test Case ID: empty_collection\n"
            f"\n"
            f"Expected: {expected_embedding}\n"
            f"Actual: {result_embedding}"
        )

    def test_single_resource_embedding(
        self, db_session, create_test_resource, create_test_collection
    ):
        """
        Test embedding calculation for collection with single resource.

        Golden Data Case: single_resource
        Input: Collection with 1 resource
        Expected: Normalized resource embedding with tolerance 0.001

        **Validates: Requirements 5.1, 5.2, 8.2, 8.3**
        """
        # Load Golden Data
        golden_data = load_golden_data("collections_logic")
        test_case = golden_data["single_resource"]

        # Create test collection
        collection = create_test_collection(
            name="Single Resource Collection", owner_id="test_user"
        )

        # Create resource with embedding from golden data
        resource_data = test_case["input"]["resources"][0]
        resource = create_test_resource(
            title=f"Resource {resource_data['id']}",
            embedding=resource_data["embedding"],
        )

        # Add resource to collection
        from app.modules.collections.service import CollectionService

        service = CollectionService(db_session)
        service.add_resources_to_collection(
            collection_id=collection.id,
            resource_ids=[resource.id],
            owner_id="test_user",
        )

        # Compute collection embedding
        result_embedding = service.compute_collection_embedding(collection.id)

        # Get expected values from golden data
        expected_embedding = test_case["expected"]["collection_embedding"]
        tolerance = test_case["expected"]["tolerance"]

        # Verify embedding matches golden data with tolerance
        assert result_embedding is not None, "Collection embedding should not be None"
        assert len(result_embedding) == len(expected_embedding), (
            f"Embedding dimension mismatch: expected {len(expected_embedding)}, got {len(result_embedding)}"
        )

        # Compare each dimension with tolerance
        for i, (actual, expected) in enumerate(
            zip(result_embedding, expected_embedding)
        ):
            diff = abs(actual - expected)
            assert diff <= tolerance, (
                f"IMPLEMENTATION FAILURE: Embedding dimension {i} mismatch.\n"
                f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
                f"\n"
                f"Golden Data File: golden_data/collections_logic.json\n"
                f"Test Case ID: single_resource\n"
                f"\n"
                f"Expected value: {expected}\n"
                f"Actual value: {actual}\n"
                f"Difference: {diff} (tolerance: {tolerance})"
            )
