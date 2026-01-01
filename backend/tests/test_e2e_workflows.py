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
    
    def test_annotation_complete_workflow(self, client: TestClient, db_session: Session):
        """Test: Create resource -> Add annotation -> Search annotations -> Export"""
        # Step 1: Create resource
        resource_data = {
            "title": "Machine Learning Fundamentals",
            "url": "https://example.com/ml-fundamentals",
            "content": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
            "resource_type": "article"
        }
        
        response = client.post("/resources/", json=resource_data)
        assert response.status_code in [201, 202]
        resource = response.json()
        resource_id = resource["id"]
        
        # Step 2: Create annotation
        annotation_data = {
            "resource_id": resource_id,
            "start_offset": 0,
            "end_offset": 50,
            "highlighted_text": "Machine learning is a subset of artificial intelligence",
            "note": "Key definition for my research",
            "tags": ["research", "definition"],
            "color": "#FFFF00"
        }
        
        response = client.post("/annotations/", json=annotation_data)
        assert response.status_code in [200, 201]
        annotation = response.json()
        assert annotation["resource_id"] == resource_id
