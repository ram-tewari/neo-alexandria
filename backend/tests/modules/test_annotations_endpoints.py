"""Test suite for Annotations API endpoints - Rewritten from scratch."""

class TestAnnotationEndpoints:
    def test_create_annotation_success(self, client, create_test_resource, db):
        resource = create_test_resource(title="Test Resource")
        annotation_data = {
            "start_offset": 0,
            "end_offset": 10,
            "highlighted_text": "Test text",
            "note": "Test annotation",
            "tags": ["test"],
            "color": "#FFFF00"
        }
        response = client.post(f"/annotations/resources/{str(resource.id)}/annotations", json=annotation_data)
        assert response.status_code == 201
