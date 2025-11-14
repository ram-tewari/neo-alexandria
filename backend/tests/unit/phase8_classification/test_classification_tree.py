#!/usr/bin/env python3
"""
Simple test script to verify the classification tree API response format.
"""

import sys
import os

from backend.app.services.classification_service import PersonalClassification
from backend.app.database.base import get_sync_db

def test_classification_tree():
    """Test that the classification tree returns the correct format."""
    print("Testing classification tree format...")
    
    # Get a database session
    db = next(get_sync_db())
    
    try:
        # Create classifier instance
        classifier = PersonalClassification()
        
        # Get the classification tree
        result = classifier.get_classification_tree(db)
        
        print(f"Result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        # Check if it has the expected 'tree' property
        if 'tree' in result:
            print("✓ Found 'tree' property")
            tree = result['tree']
            print(f"Tree type: {type(tree)}")
            print(f"Tree length: {len(tree) if isinstance(tree, list) else 'Not a list'}")
            
            if isinstance(tree, list) and len(tree) > 0:
                first_item = tree[0]
                print(f"First item type: {type(first_item)}")
                print(f"First item keys: {first_item.keys() if isinstance(first_item, dict) else 'Not a dict'}")
                
                # Check if it has the expected properties
                if 'code' in first_item and 'name' in first_item:
                    print("✓ First item has 'code' and 'name' properties")
                    print(f"First item code: {first_item['code']}")
                    print(f"First item name: {first_item['name']}")
                else:
                    print("✗ First item missing expected properties")
            else:
                print("✗ Tree is not a non-empty list")
        else:
            print("✗ Result does not have 'tree' property")
            print(f"Available keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        print("\nFull result:")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_classification_tree()





