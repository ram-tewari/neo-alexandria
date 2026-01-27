"""
Seeding Script for Performance Audit
Generates synthetic Resources and Annotations with pre-calculated embeddings.
"""
import sys
import json
import random
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Resource, Annotation, Base

# Import your embedding logic
try:
    from sentence_transformers import SentenceTransformer
    from FlagEmbedding import BGEM3FlagModel
except ImportError:
    print("CRITICAL: ml-dependencies not found. Run 'pip install sentence-transformers FlagEmbedding'")
    sys.exit(1)

# --- Configuration ---
DB_URL = "sqlite:///./backend.db"  # Change if using Postgres
DENSE_MODEL_ID = "nomic-ai/nomic-embed-text-v1"
SPARSE_MODEL_ID = "BAAI/bge-m3"

# --- Synthetic Data Corpus ---
# Three distinct clusters to test vector separation
DATASET = [
    {
        "cluster": "CODING",
        "title": "Understanding Python Asyncio",
        "content": "Asyncio is a library to write concurrent code using the async/await syntax. It is used as a foundation for multiple Python asynchronous frameworks that provide high-performance network and web-servers, database connection libraries, distributed task queues, etc.",
        "annotations": [
            "Asyncio uses async/await syntax",  # Exact match (FTS bait)
            "Library for concurrent programming in Python"  # Semantic (Vector bait)
        ]
    },
    {
        "cluster": "CODING",
        "title": "Database Indexing Strategies",
        "content": "A B-Tree index is a self-balancing tree data structure that maintains sorted data and allows searches, sequential access, insertions, and deletions in logarithmic time. It is the default index type in PostgreSQL.",
        "annotations": [
            "B-Tree is the default index in Postgres",
            "Data structure for logarithmic time searches"
        ]
    },
    {
        "cluster": "CODING",
        "title": "REST API Design Principles",
        "content": "RESTful APIs use HTTP methods (GET, POST, PUT, DELETE) to perform CRUD operations. Resources are identified by URIs, and the API should be stateless. Proper status codes and JSON responses are essential.",
        "annotations": [
            "REST uses HTTP methods for CRUD",
            "Stateless API design with proper status codes"
        ]
    },
    {
        "cluster": "CODING",
        "title": "Docker Container Orchestration",
        "content": "Docker containers package applications with their dependencies. Orchestration tools like Kubernetes manage container deployment, scaling, and networking across clusters of machines.",
        "annotations": [
            "Docker packages apps with dependencies",
            "Kubernetes orchestrates container clusters"
        ]
    },
    {
        "cluster": "COOKING",
        "title": "The Science of Sourdough",
        "content": "Sourdough is a naturally leavened bread that uses a 'starter' of fermented flour and water. The wild yeast and lactobacilli in the starter create the rise and the characteristic tang. Temperature controls fermentation speed.",
        "annotations": [
            "Wild yeast and lactobacilli create the rise",
            "How temperature affects bread fermentation"
        ]
    },
    {
        "cluster": "COOKING",
        "title": "Techniques for Carbonara",
        "content": "Authentic Carbonara uses guanciale, pecorino romano, eggs, and black pepper. No cream is used. The heat of the pasta cooks the eggs to create a creamy sauce without curdling.",
        "annotations": [
            "Authentic Carbonara contains no cream",
            "Using pasta heat to cook eggs for sauce"
        ]
    },
    {
        "cluster": "COOKING",
        "title": "Knife Skills for Chefs",
        "content": "Proper knife technique involves the pinch grip, rocking motion, and keeping the blade sharp. Different cuts like julienne, brunoise, and chiffonade serve specific culinary purposes.",
        "annotations": [
            "Pinch grip and rocking motion for cutting",
            "Julienne and brunoise are precision cuts"
        ]
    },
    {
        "cluster": "COOKING",
        "title": "Sous Vide Cooking Method",
        "content": "Sous vide involves vacuum-sealing food and cooking it in a water bath at precise temperatures. This method ensures even cooking and moisture retention, popular for steaks and fish.",
        "annotations": [
            "Vacuum-sealed food in water bath",
            "Precise temperature control for even cooking"
        ]
    },
    {
        "cluster": "HISTORY",
        "title": "The Fall of Rome",
        "content": "The Fall of the Western Roman Empire was the process of decline in the Western Roman Empire in which the Empire failed to enforce its rule, and its vast territory was divided into several successor polities.",
        "annotations": [
            "Decline of the Western Roman Empire",
            "Empire failed to enforce rule and split up"
        ]
    },
    {
        "cluster": "HISTORY",
        "title": "The Renaissance Period",
        "content": "The Renaissance was a period of cultural rebirth in Europe from the 14th to 17th century. It saw advances in art, science, and philosophy, with figures like Leonardo da Vinci and Michelangelo.",
        "annotations": [
            "Cultural rebirth from 14th to 17th century",
            "Leonardo da Vinci and Michelangelo were key figures"
        ]
    },
    {
        "cluster": "HISTORY",
        "title": "The Industrial Revolution",
        "content": "The Industrial Revolution began in Britain in the late 18th century. It transformed economies from agrarian to industrial, introducing factories, steam power, and mass production.",
        "annotations": [
            "Britain in late 18th century transformation",
            "Factories and steam power changed production"
        ]
    },
    {
        "cluster": "HISTORY",
        "title": "World War II Timeline",
        "content": "World War II lasted from 1939 to 1945, involving most of the world's nations. Key events include the invasion of Poland, Pearl Harbor, D-Day, and the atomic bombings of Japan.",
        "annotations": [
            "War from 1939 to 1945 globally",
            "Pearl Harbor and D-Day were pivotal events"
        ]
    }
]


def generate_synthetic_data():
    print("=" * 60)
    print("SEEDING AUDIT DATA")
    print("=" * 60)

    # 1. Setup DB
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Check if DB needs init
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        print(f"Schema check skipped/failed: {e}")

    # 2. Load Models
    print("--> Loading Dense Model (Nomic)...")
    dense_model = SentenceTransformer(DENSE_MODEL_ID, trust_remote_code=True)
    
    print("--> Loading Sparse Model (BGE-M3)...")
    sparse_model = BGEM3FlagModel(SPARSE_MODEL_ID, use_fp16=True)
    
    print("--> Models Loaded. Generating Data...")

    resources_created = 0
    annotations_created = 0

    for item in DATASET:
        # Generate Embeddings
        # Dense
        dense_vec = dense_model.encode(item["content"]).tolist()
        
        # Sparse (BGE-M3 returns dictionary of token weights)
        sparse_out = sparse_model.encode(
            item["content"], 
            return_dense=False, 
            return_sparse=True, 
            return_colbert_vecs=False
        )
        sparse_vec = sparse_out['lexical_weights']

        # Create Resource
        res = Resource(
            title=item["title"],
            description=item["content"][:200],
            embedding=json.dumps(dense_vec)  # Convert to JSON string
        )

        # Set sparse embedding if column exists
        if hasattr(Resource, 'sparse_embedding'):
            # Convert numpy float32 to Python float
            sparse_dict = {k: float(v) for k, v in sparse_vec.items()}
            res.sparse_embedding = json.dumps(sparse_dict)

        session.add(res)
        session.flush()  # get ID

        # Add Annotations
        for note in item["annotations"]:
            ann = Annotation(
                resource_id=res.id,
                text=note,
                created_at=datetime.utcnow()
            )
            session.add(ann)
            annotations_created += 1

        resources_created += 1
        print(f"   + Added: {item['title']}")

    session.commit()
    
    print("=" * 60)
    print(f"SUCCESS: Created {resources_created} Resources and {annotations_created} Annotations.")
    print("You can now run 'python backend/scripts/audit_retrieval.py'")
    print("=" * 60)


if __name__ == "__main__":
    generate_synthetic_data()
