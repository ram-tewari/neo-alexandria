"""
Debug script to check what's happening with search
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from app.database.models import Resource, Annotation

# Setup database
engine = create_engine("sqlite:///./backend.db")
Session = sessionmaker(bind=engine)
db = Session()

# Check annotations
annotations = db.query(Annotation).filter(
    Annotation.highlighted_text.isnot(None),
    Annotation.highlighted_text != ""
).all()

print(f"Total annotations: {len(annotations)}")
print("\nFirst 3 annotations:")
for ann in annotations[:3]:
    print(f"\nAnnotation ID: {ann.id}")
    print(f"  Text: {ann.highlighted_text}")
    print(f"  Resource ID: {ann.resource_id}")
    
    # Try to find the resource
    resource = db.query(Resource).filter(Resource.id == ann.resource_id).first()
    if resource:
        print(f"  Resource Title: {resource.title}")
        print(f"  Resource Description: {resource.description[:100] if resource.description else 'None'}")
    else:
        print(f"  Resource NOT FOUND!")

# Now test FTS search with the first annotation
if annotations:
    test_query = annotations[0].highlighted_text
    target_id = str(annotations[0].resource_id)
    
    print(f"\n\n{'='*80}")
    print(f"TEST SEARCH")
    print(f"{'='*80}")
    print(f"Query: {test_query}")
    print(f"Target Resource ID: {target_id}")
    
    # Try FTS search
    results = db.query(Resource).filter(
        or_(
            Resource.title.ilike(f"%{test_query}%"),
            Resource.description.ilike(f"%{test_query}%"),
        )
    ).limit(10).all()
    
    print(f"\nFTS Results: {len(results)} found")
    for r in results:
        print(f"  - ID: {r.id}, Title: {r.title}")
    
    if target_id in [str(r.id) for r in results]:
        print(f"\n[SUCCESS] Target resource {target_id} FOUND in results!")
    else:
        print(f"\n[FAIL] Target resource {target_id} NOT in results")
        print(f"\nDEBUG: Let's check if the resource content contains the query...")
        target_resource = db.query(Resource).filter(Resource.id == target_id).first()
        if target_resource:
            print(f"  Resource Title: {target_resource.title}")
            print(f"  Resource Description: {target_resource.description}")
            print(f"  Query '{test_query}' in title: {test_query.lower() in target_resource.title.lower() if target_resource.title else False}")
            print(f"  Query '{test_query}' in description: {test_query.lower() in target_resource.description.lower() if target_resource.description else False}")

db.close()
