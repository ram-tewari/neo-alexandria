"""
End-to-End Workflow Tests

Comprehensive integration tests that verify complete workflows across multiple modules.
Each test validates the full user journey from start to finish.

Requirements tested: 15.8 (End-to-end workflow validation)
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAnnotationWorkflow:
    """Test complete annotation workflow from creation to export."""

    def test_annotation_complete_workflow(
        self, client: TestClient, db_session: Session
    ):
        """
        Test: Create resource → Add annotation → Search annotations → Export

        Requirements: 15.8 (End-to-end workflow validation)
        Validates: Complete annotation workflow from creation through search to export
        """
        # Step 1: Create resource directly in database for testing
        from app.database.models import Resource
        import uuid
        from datetime import datetime

        resource_id = str(uuid.uuid4())
        resource = Resource(
            id=resource_id,
            title="Machine Learning Fundamentals",
            url="https://example.com/ml-fundamentals",
            content="Machine learning is a subset of artificial intelligence. "
            "It enables computers to learn from data without explicit programming. "
            "Deep learning is a specialized form of machine learning.",
            resource_type="article",
            status="completed",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(resource)
        db_session.commit()
        print(f"✓ Step 1: Created resource {resource_id}")

        # Step 2: Create multiple annotations
        annotations = []
        annotation_data_list = [
            {
                "resource_id": resource_id,
                "start_offset": 0,
                "end_offset": 28,
                "highlighted_text": "Machine learning is a subset",
                "note": "Key definition of machine learning",
                "tags": ["definition", "ml"],
                "color": "#FFFF00",
            },
            {
                "resource_id": resource_id,
                "start_offset": 65,
                "end_offset": 130,
                "highlighted_text": "enables computers to learn from data without explicit programming",
                "note": "Core concept of ML - learning from data",
                "tags": ["concept", "ml"],
                "color": "#00FF00",
            },
            {
                "resource_id": resource_id,
                "start_offset": 132,
                "end_offset": 185,
                "highlighted_text": "Deep learning is a specialized form of machine learning",
                "note": "Deep learning relationship to ML",
                "tags": ["deep-learning", "ml"],
                "color": "#FF00FF",
            },
        ]

        for ann_data in annotation_data_list:
            response = client.post(
                f"/resources/{resource_id}/annotations", json=ann_data
            )
            assert response.status_code in [200, 201], (
                f"Annotation creation failed: {response.status_code} - {response.text}"
            )
            annotation = response.json()
            assert annotation["resource_id"] == resource_id
            assert annotation["note"] == ann_data["note"]
            annotations.append(annotation)

        print(f"✓ Step 2: Created {len(annotations)} annotations")

        # Step 3: Test fulltext search
        response = client.get(
            "/annotations/search/fulltext", params={"query": "learning"}
        )
        assert response.status_code == 200
        search_results = response.json()
        assert (
            len(search_results) >= 2
        )  # Should find multiple annotations with "learning"
        print(f"✓ Step 3: Fulltext search found {len(search_results)} annotations")

        # Step 4: Test semantic search (if embeddings are available)
        response = client.get(
            "/annotations/search/semantic",
            params={"query": "what is machine learning", "limit": 5},
        )
        assert response.status_code == 200
        semantic_results = response.json()
        # Semantic search should return results with similarity scores
        if semantic_results:
            assert "similarity" in semantic_results[0] or "score" in semantic_results[0]
            print(
                f"✓ Step 4: Semantic search found {len(semantic_results)} annotations"
            )
        else:
            print("✓ Step 4: Semantic search completed (no embeddings yet)")

        # Step 5: Test tag-based search
        response = client.get("/annotations/search/tags", params={"tags": "ml"})
        assert response.status_code == 200
        tag_results = response.json()
        assert len(tag_results) == 3  # All three annotations have "ml" tag
        print(f"✓ Step 5: Tag search found {len(tag_results)} annotations")

        # Step 6: Export to Markdown
        response = client.get("/annotations/export/markdown")
        assert response.status_code == 200
        markdown_export = response.text
        assert "Machine Learning Fundamentals" in markdown_export
        assert "Key definition" in markdown_export
        assert len(markdown_export) > 100  # Should have substantial content
        print(f"✓ Step 6: Exported {len(markdown_export)} characters to Markdown")

        # Step 7: Export to JSON
        response = client.get("/annotations/export/json")
        assert response.status_code == 200
        json_export = response.json()
        assert isinstance(json_export, list)
        assert len(json_export) >= 3
        # Verify JSON structure
        for item in json_export:
            assert "id" in item
            assert "resource_id" in item
            assert "note" in item
            assert "highlighted_text" in item
        print(f"✓ Step 7: Exported {len(json_export)} annotations to JSON")

        # Step 8: Verify annotation retrieval by resource
        response = client.get(f"/resources/{resource_id}/annotations")
        assert response.status_code == 200
        resource_annotations = response.json()
        assert len(resource_annotations) == 3
        print(
            f"✓ Step 8: Retrieved {len(resource_annotations)} annotations for resource"
        )

        # Step 9: Update an annotation
        annotation_id = annotations[0]["id"]
        update_data = {
            "note": "Updated: Key definition of machine learning",
            "tags": ["definition", "ml", "updated"],
        }
        response = client.put(f"/annotations/{annotation_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["note"] == update_data["note"]
        assert "updated" in updated["tags"]
        print(f"✓ Step 9: Updated annotation {annotation_id}")

        # Step 10: Delete an annotation
        annotation_to_delete = annotations[2]["id"]
        response = client.delete(f"/annotations/{annotation_to_delete}")
        assert response.status_code == 200 or response.status_code == 204

        # Verify deletion
        response = client.get(f"/annotations/{annotation_to_delete}")
        assert response.status_code == 404
        print(f"✓ Step 10: Deleted annotation {annotation_to_delete}")

        print("\n✅ Complete annotation workflow test passed!")
        print(f"   - Created resource with {len(annotation_data_list)} annotations")
        print("   - Tested fulltext, semantic, and tag-based search")
        print("   - Exported to Markdown and JSON formats")
        print("   - Verified CRUD operations")

        return True


class TestSearchWorkflow:
    """Test complete search workflow with hybrid search."""

    def test_search_complete_workflow(self, client: TestClient, db_session: Session):
        """Test: Create resources → Keyword search → Semantic search → Hybrid search"""
        # Create test resources
        for i in range(3):
            resource_data = {
                "title": f"ML Article {i}",
                "url": f"https://example.com/ml-{i}",
                "content": f"Machine learning content {i}",
                "resource_type": "article",
            }
            response = client.post("/resources/", json=resource_data)
            assert response.status_code == 201
