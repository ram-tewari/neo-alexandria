"""
Test script for Phase 8.5 Taxonomy API Endpoints

This script tests all taxonomy management endpoints to verify they work correctly.
"""


from fastapi.testclient import TestClient
from backend.app import app
from backend.app.database.base import get_sync_db, sync_engine
from backend.app.database.models import Base, TaxonomyNode, ResourceTaxonomy
from sqlalchemy.orm import Session
import uuid


def setup_test_db():
    """Create test database tables."""
    Base.metadata.create_all(bind=sync_engine)


def cleanup_test_db(db: Session):
    """Clean up test data."""
    db.query(ResourceTaxonomy).delete()
    db.query(TaxonomyNode).delete()
    db.commit()


def test_taxonomy_endpoints():
    """Test all taxonomy management endpoints."""
    print("=" * 80)
    print("Testing Phase 8.5 Taxonomy API Endpoints")
    print("=" * 80)
    
    # Setup
    setup_test_db()
    client = TestClient(app)
    db = next(get_sync_db())
    
    try:
        cleanup_test_db(db)
        
        # Test 1: Create root node (POST /taxonomy/nodes)
        print("\n1. Testing POST /taxonomy/nodes (create root node)...")
        response = client.post("/taxonomy/nodes", json={
            "name": "Computer Science",
            "description": "Computer science and programming topics",
            "keywords": ["programming", "algorithms", "software"],
            "allow_resources": True
        })
        print(f"   Status: {response.status_code}")
        if response.status_code != 201:
            print(f"   Error: {response.json()}")
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        root_node = response.json()
        print(f"   Created node: {root_node['name']} (id: {root_node['id']})")
        print(f"   Slug: {root_node['slug']}, Level: {root_node['level']}, Path: {root_node['path']}")
        assert root_node['level'] == 0
        assert root_node['path'] == '/computer-science'
        assert root_node['is_leaf']
        print("   ✓ Root node created successfully")
        
        # Test 2: Create child node
        print("\n2. Testing POST /taxonomy/nodes (create child node)...")
        response = client.post("/taxonomy/nodes", json={
            "name": "Machine Learning",
            "parent_id": root_node['id'],
            "description": "ML and AI topics",
            "keywords": ["neural networks", "deep learning"],
            "allow_resources": True
        })
        print(f"   Status: {response.status_code}")
        assert response.status_code == 201
        child_node = response.json()
        print(f"   Created node: {child_node['name']} (id: {child_node['id']})")
        print(f"   Slug: {child_node['slug']}, Level: {child_node['level']}, Path: {child_node['path']}")
        assert child_node['level'] == 1
        assert child_node['path'] == '/computer-science/machine-learning'
        assert child_node['parent_id'] == root_node['id']
        print("   ✓ Child node created successfully")
        
        # Test 3: Create grandchild node
        print("\n3. Testing POST /taxonomy/nodes (create grandchild node)...")
        response = client.post("/taxonomy/nodes", json={
            "name": "Deep Learning",
            "parent_id": child_node['id'],
            "description": "Deep neural networks",
            "keywords": ["CNN", "RNN", "transformers"],
            "allow_resources": True
        })
        print(f"   Status: {response.status_code}")
        assert response.status_code == 201
        grandchild_node = response.json()
        print(f"   Created node: {grandchild_node['name']} (id: {grandchild_node['id']})")
        print(f"   Level: {grandchild_node['level']}, Path: {grandchild_node['path']}")
        assert grandchild_node['level'] == 2
        assert grandchild_node['path'] == '/computer-science/machine-learning/deep-learning'
        print("   ✓ Grandchild node created successfully")
        
        # Test 4: Update node (PUT /taxonomy/nodes/{node_id})
        print("\n4. Testing PUT /taxonomy/nodes/{node_id}...")
        response = client.put(f"/taxonomy/nodes/{child_node['id']}", json={
            "description": "Machine Learning and Artificial Intelligence",
            "keywords": ["ML", "AI", "neural networks", "deep learning"]
        })
        print(f"   Status: {response.status_code}")
        assert response.status_code == 200
        updated_node = response.json()
        print(f"   Updated description: {updated_node['description']}")
        print(f"   Updated keywords: {updated_node['keywords']}")
        assert updated_node['description'] == "Machine Learning and Artificial Intelligence"
        assert len(updated_node['keywords']) == 4
        print("   ✓ Node updated successfully")
        
        # Test 5: Get tree (GET /taxonomy/tree)
        print("\n5. Testing GET /taxonomy/tree...")
        response = client.get("/taxonomy/tree")
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
        assert response.status_code == 200
        tree = response.json()
        print(f"   Retrieved {len(tree)} root node(s)")
        assert len(tree) > 0
        assert tree[0]['name'] == 'Computer Science'
        assert len(tree[0]['children']) > 0
        print(f"   Root node has {len(tree[0]['children'])} child(ren)")
        print("   ✓ Tree retrieved successfully")
        
        # Test 6: Get tree with root_id
        print("\n6. Testing GET /taxonomy/tree?root_id=...")
        response = client.get(f"/taxonomy/tree?root_id={child_node['id']}")
        print(f"   Status: {response.status_code}")
        assert response.status_code == 200
        subtree = response.json()
        print(f"   Retrieved subtree starting from: {subtree[0]['name']}")
        assert subtree[0]['name'] == 'Machine Learning'
        print("   ✓ Subtree retrieved successfully")
        
        # Test 7: Get ancestors (GET /taxonomy/nodes/{node_id}/ancestors)
        print("\n7. Testing GET /taxonomy/nodes/{node_id}/ancestors...")
        response = client.get(f"/taxonomy/nodes/{grandchild_node['id']}/ancestors")
        print(f"   Status: {response.status_code}")
        assert response.status_code == 200
        ancestors = response.json()
        print(f"   Retrieved {len(ancestors)} ancestor(s)")
        assert len(ancestors) == 2  # Computer Science and Machine Learning
        print(f"   Ancestors: {' > '.join([a['name'] for a in ancestors])}")
        assert ancestors[0]['name'] == 'Computer Science'
        assert ancestors[1]['name'] == 'Machine Learning'
        print("   ✓ Ancestors retrieved successfully")
        
        # Test 8: Get descendants (GET /taxonomy/nodes/{node_id}/descendants)
        print("\n8. Testing GET /taxonomy/nodes/{node_id}/descendants...")
        response = client.get(f"/taxonomy/nodes/{root_node['id']}/descendants")
        print(f"   Status: {response.status_code}")
        assert response.status_code == 200
        descendants = response.json()
        print(f"   Retrieved {len(descendants)} descendant(s)")
        assert len(descendants) >= 2  # At least Machine Learning and Deep Learning
        print(f"   Descendants: {', '.join([d['name'] for d in descendants])}")
        print("   ✓ Descendants retrieved successfully")
        
        # Test 9: Move node (POST /taxonomy/nodes/{node_id}/move)
        print("\n9. Testing POST /taxonomy/nodes/{node_id}/move...")
        # Create a new parent to move to
        response = client.post("/taxonomy/nodes", json={
            "name": "Artificial Intelligence",
            "parent_id": root_node['id'],
            "description": "AI topics",
            "allow_resources": True
        })
        assert response.status_code == 201
        new_parent = response.json()
        
        # Move Deep Learning from Machine Learning to Artificial Intelligence
        response = client.post(f"/taxonomy/nodes/{grandchild_node['id']}/move", json={
            "new_parent_id": new_parent['id']
        })
        print(f"   Status: {response.status_code}")
        assert response.status_code == 200
        move_result = response.json()
        print(f"   Moved: {move_result['moved']}")
        moved_node = move_result['node']
        print(f"   New path: {moved_node['path']}")
        assert moved_node['path'] == '/computer-science/artificial-intelligence/deep-learning'
        assert moved_node['parent_id'] == new_parent['id']
        print("   ✓ Node moved successfully")
        
        # Test 10: Delete node without cascade (DELETE /taxonomy/nodes/{node_id})
        print("\n10. Testing DELETE /taxonomy/nodes/{node_id} (without cascade)...")
        # Create a node to delete
        response = client.post("/taxonomy/nodes", json={
            "name": "Test Node",
            "parent_id": root_node['id'],
            "allow_resources": True
        })
        assert response.status_code == 201
        test_node = response.json()
        
        # Delete it
        response = client.delete(f"/taxonomy/nodes/{test_node['id']}")
        print(f"   Status: {response.status_code}")
        assert response.status_code == 200
        delete_result = response.json()
        print(f"   Deleted: {delete_result['deleted']}")
        print(f"   Deleted count: {delete_result['deleted_count']}")
        assert delete_result['deleted']
        print("   ✓ Node deleted successfully")
        
        # Test 11: Error handling - duplicate slug
        print("\n11. Testing error handling (duplicate slug)...")
        response = client.post("/taxonomy/nodes", json={
            "name": "Computer Science",  # Duplicate name
            "allow_resources": True
        })
        print(f"   Status: {response.status_code}")
        assert response.status_code == 400
        error = response.json()
        print(f"   Error: {error['detail']}")
        assert 'already exists' in error['detail'].lower()
        print("   ✓ Duplicate slug error handled correctly")
        
        # Test 12: Error handling - invalid parent
        print("\n12. Testing error handling (invalid parent)...")
        fake_uuid = str(uuid.uuid4())
        response = client.post("/taxonomy/nodes", json={
            "name": "Invalid Node",
            "parent_id": fake_uuid,
            "allow_resources": True
        })
        print(f"   Status: {response.status_code}")
        assert response.status_code == 400
        error = response.json()
        print(f"   Error: {error['detail']}")
        assert 'not found' in error['detail'].lower()
        print("   ✓ Invalid parent error handled correctly")
        
        print("\n" + "=" * 80)
        print("✓ All taxonomy API endpoint tests passed!")
        print("=" * 80)
        
    finally:
        cleanup_test_db(db)
        db.close()


if __name__ == "__main__":
    test_taxonomy_endpoints()
