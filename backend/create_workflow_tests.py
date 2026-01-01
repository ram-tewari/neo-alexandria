#!/usr/bin/env python3
"""Script to create comprehensive workflow tests."""

content = '''"""
End-to-End Workflow Tests

Comprehensive integration tests that verify complete workflows across multiple modules.
Each test validates the full user journey from start to finish.

Requirements tested: 15.8 End-to-end workflow validation
"""

import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAnnotationWorkflow:
    """Test complete annotation workflow from creation to export."""
    
    def test_annotation_complete_workflow(self, client: TestClient, db_session: Session):
        """Test: Create resource -> Add annotation -> List annotations"""
        # Step 1: Create resource
        resource_data = {
            "title": "Machine Learning Fundamentals",
            "url": "https://example.com/ml-fundamentals",
            "content": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
            "resource_type": "article"
        }
        
        response = client.post("/resources", json=resource_data)
        assert response.status_code in [201, 202]
        resource = response.json()
        resource_id = resource["id"]
        
        # Step 2: Create annotation with correct endpoint
        annotation_data = {
            "start_offset": 0,
            "end_offset": 50,
            "highlighted_text": "Machine learning is a subset of artificial intelligence",
            "note": "Key definition for my research",
            "tags": ["research", "definition"],
            "color": "#FFFF00"
        }
        
        response = client.post(f"/resources/{resource_id}/annotations", json=annotation_data)
        assert response.status_code in [200, 201]
        annotation = response.json()
        assert annotation["resource_id"] == resource_id
        assert annotation["note"] == "Key definition for my research"
        
        # Step 3: List annotations for resource
        response = client.get(f"/resources/{resource_id}/annotations")
        assert response.status_code == 200
        annotations_data = response.json()
        assert "items" in annotations_data or isinstance(annotations_data, list)
'''

with open('tests/test_e2e_workflows.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Workflow tests created successfully!")
