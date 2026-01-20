"""
Script to add 20 real, high-quality URLs to Neo Alexandria.
These are real documentation and API resources that will provide good content for chunking and RAG.
"""

import requests
import time

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"

# 20 real, high-quality URLs for documentation and APIs
SAMPLE_URLS = [
    {
        "url": "https://fastapi.tiangolo.com/",
        "title": "FastAPI Documentation",
        "description": "Modern, fast web framework for building APIs with Python"
    },
    {
        "url": "https://docs.python.org/3/tutorial/",
        "title": "Python Tutorial",
        "description": "Official Python programming tutorial"
    },
    {
        "url": "https://react.dev/learn",
        "title": "React Documentation",
        "description": "Learn React - Official React documentation"
    },
    {
        "url": "https://www.postgresql.org/docs/current/tutorial.html",
        "title": "PostgreSQL Tutorial",
        "description": "Official PostgreSQL database tutorial"
    },
    {
        "url": "https://docs.docker.com/get-started/",
        "title": "Docker Getting Started",
        "description": "Introduction to Docker containers"
    },
    {
        "url": "https://kubernetes.io/docs/tutorials/",
        "title": "Kubernetes Tutorials",
        "description": "Learn Kubernetes container orchestration"
    },
    {
        "url": "https://www.tensorflow.org/tutorials",
        "title": "TensorFlow Tutorials",
        "description": "Machine learning with TensorFlow"
    },
    {
        "url": "https://pytorch.org/tutorials/",
        "title": "PyTorch Tutorials",
        "description": "Deep learning framework tutorials"
    },
    {
        "url": "https://docs.github.com/en/rest",
        "title": "GitHub REST API",
        "description": "GitHub API documentation"
    },
    {
        "url": "https://stripe.com/docs/api",
        "title": "Stripe API Documentation",
        "description": "Payment processing API reference"
    },
    {
        "url": "https://developers.google.com/maps/documentation",
        "title": "Google Maps API",
        "description": "Google Maps Platform documentation"
    },
    {
        "url": "https://aws.amazon.com/getting-started/",
        "title": "AWS Getting Started",
        "description": "Amazon Web Services tutorials"
    },
    {
        "url": "https://learn.microsoft.com/en-us/azure/",
        "title": "Azure Documentation",
        "description": "Microsoft Azure cloud platform docs"
    },
    {
        "url": "https://www.mongodb.com/docs/manual/tutorial/",
        "title": "MongoDB Tutorial",
        "description": "NoSQL database documentation"
    },
    {
        "url": "https://redis.io/docs/",
        "title": "Redis Documentation",
        "description": "In-memory data structure store docs"
    },
    {
        "url": "https://graphql.org/learn/",
        "title": "GraphQL Tutorial",
        "description": "Learn GraphQL query language"
    },
    {
        "url": "https://www.nginx.com/resources/wiki/start/",
        "title": "NGINX Beginner's Guide",
        "description": "Web server and reverse proxy documentation"
    },
    {
        "url": "https://git-scm.com/doc",
        "title": "Git Documentation",
        "description": "Version control system reference"
    },
    {
        "url": "https://nodejs.org/en/docs/guides/",
        "title": "Node.js Guides",
        "description": "JavaScript runtime documentation"
    },
    {
        "url": "https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html",
        "title": "Elasticsearch Guide",
        "description": "Search and analytics engine documentation"
    }
]


def add_resources():
    """Add all sample URLs to Neo Alexandria"""
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    print("="*80)
    print("ADDING 20 SAMPLE RESOURCES TO NEO ALEXANDRIA")
    print("="*80)
    print()
    
    successful = 0
    failed = 0
    
    for i, resource in enumerate(SAMPLE_URLS, 1):
        print(f"[{i}/20] Adding: {resource['title']}")
        print(f"        URL: {resource['url']}")
        
        try:
            resp = requests.post(
                f"{BASE_URL}/resources/",
                headers=headers,
                json=resource,
                timeout=30
            )
            
            if resp.status_code in [200, 201, 202]:
                data = resp.json()
                print(f"        ✓ Created (ID: {data.get('id')[:8]}...)")
                successful += 1
            else:
                print(f"        ✗ Failed: {resp.status_code} - {resp.text[:100]}")
                failed += 1
                
        except Exception as e:
            print(f"        ✗ Error: {str(e)[:100]}")
            failed += 1
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.5)
        print()
    
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total: 20 resources")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print()
    
    if successful > 0:
        print("✓ Resources are being ingested in the background")
        print("✓ Chunks will be created automatically")
        print("✓ Wait a few minutes for all ingestion to complete")
        print()
        print("To check progress:")
        print("  python check_database.py")
    
    return successful == 20


if __name__ == "__main__":
    success = add_resources()
    exit(0 if success else 1)
