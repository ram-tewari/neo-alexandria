"""
Large Synthetic Dataset Seeder
Creates 50 resources with 100 annotations for robust testing
"""
import sys
import json
from pathlib import Path
from datetime import datetime

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Resource, Annotation, Base

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("CRITICAL: sentence-transformers not found. Run 'pip install sentence-transformers'")
    sys.exit(1)

DB_URL = "sqlite:///./backend.db"
DENSE_MODEL_ID = "nomic-ai/nomic-embed-text-v1"

# Expanded dataset: 50 resources across 5 clusters
DATASET = [
    # PYTHON PROGRAMMING (10 resources)
    {"cluster": "PYTHON", "title": "Python Asyncio Fundamentals", "content": "Asyncio is a library to write concurrent code using the async/await syntax. It provides event loops, coroutines, and tasks for asynchronous programming in Python."},
    {"cluster": "PYTHON", "title": "Python Decorators Explained", "content": "Decorators are a powerful feature in Python that allow you to modify the behavior of functions or classes. They use the @ symbol and are commonly used for logging, timing, and access control."},
    {"cluster": "PYTHON", "title": "Python List Comprehensions", "content": "List comprehensions provide a concise way to create lists in Python. They consist of brackets containing an expression followed by a for clause, and can include optional if clauses."},
    {"cluster": "PYTHON", "title": "Python Context Managers", "content": "Context managers in Python use the with statement to ensure proper resource management. They implement __enter__ and __exit__ methods for setup and cleanup operations."},
    {"cluster": "PYTHON", "title": "Python Generators and Yield", "content": "Generators are functions that use yield instead of return to produce a sequence of values lazily. They are memory-efficient for handling large datasets and streams."},
    {"cluster": "PYTHON", "title": "Python Type Hints", "content": "Type hints in Python provide optional static typing using annotations. They improve code readability and enable better IDE support and static analysis tools like mypy."},
    {"cluster": "PYTHON", "title": "Python Virtual Environments", "content": "Virtual environments isolate Python project dependencies using venv or virtualenv. They prevent package conflicts and ensure reproducible development environments."},
    {"cluster": "PYTHON", "title": "Python Exception Handling", "content": "Exception handling in Python uses try-except blocks to catch and handle errors gracefully. Custom exceptions can be created by inheriting from the Exception class."},
    {"cluster": "PYTHON", "title": "Python Data Classes", "content": "Data classes introduced in Python 3.7 provide a decorator and functions for automatically adding special methods to classes. They reduce boilerplate code for simple data containers."},
    {"cluster": "PYTHON", "title": "Python Metaclasses", "content": "Metaclasses are classes of classes that define how classes behave. They are created by inheriting from type and are used for advanced metaprogramming techniques."},
    
    # DATABASE (10 resources)
    {"cluster": "DATABASE", "title": "SQL Indexing Strategies", "content": "Database indexes improve query performance by creating data structures that allow fast lookups. B-tree indexes are most common, while hash indexes work well for equality comparisons."},
    {"cluster": "DATABASE", "title": "Database Normalization", "content": "Normalization organizes database tables to reduce redundancy and improve data integrity. The process involves dividing tables and defining relationships through normal forms."},
    {"cluster": "DATABASE", "title": "ACID Properties", "content": "ACID stands for Atomicity, Consistency, Isolation, and Durability. These properties ensure reliable database transactions even in the face of errors or system failures."},
    {"cluster": "DATABASE", "title": "SQL Query Optimization", "content": "Query optimization involves analyzing execution plans, using appropriate indexes, avoiding N+1 queries, and writing efficient JOIN operations to improve database performance."},
    {"cluster": "DATABASE", "title": "Database Sharding", "content": "Sharding distributes data across multiple database instances to improve scalability. It involves partitioning data horizontally based on a shard key."},
    {"cluster": "DATABASE", "title": "NoSQL vs SQL", "content": "NoSQL databases like MongoDB offer flexible schemas and horizontal scaling, while SQL databases provide ACID guarantees and complex query capabilities through relational models."},
    {"cluster": "DATABASE", "title": "Database Replication", "content": "Replication creates copies of databases across multiple servers for high availability and load distribution. Master-slave and multi-master are common replication patterns."},
    {"cluster": "DATABASE", "title": "Database Transactions", "content": "Transactions group multiple database operations into a single unit of work. They ensure data consistency through commit and rollback mechanisms."},
    {"cluster": "DATABASE", "title": "Connection Pooling", "content": "Connection pooling maintains a cache of database connections that can be reused. This reduces the overhead of creating new connections for each database operation."},
    {"cluster": "DATABASE", "title": "Database Migrations", "content": "Database migrations are version-controlled changes to database schemas. Tools like Alembic and Flyway help manage schema evolution in production environments."},
    
    # WEB DEVELOPMENT (10 resources)
    {"cluster": "WEB", "title": "REST API Design", "content": "RESTful APIs use HTTP methods (GET, POST, PUT, DELETE) for CRUD operations. They follow stateless communication and use standard status codes for responses."},
    {"cluster": "WEB", "title": "GraphQL Fundamentals", "content": "GraphQL is a query language for APIs that allows clients to request exactly the data they need. It provides a type system and enables efficient data fetching."},
    {"cluster": "WEB", "title": "WebSocket Communication", "content": "WebSockets provide full-duplex communication channels over a single TCP connection. They enable real-time bidirectional data transfer between clients and servers."},
    {"cluster": "WEB", "title": "OAuth 2.0 Authentication", "content": "OAuth 2.0 is an authorization framework that enables applications to obtain limited access to user accounts. It uses access tokens and refresh tokens for secure authentication."},
    {"cluster": "WEB", "title": "CORS and Security", "content": "Cross-Origin Resource Sharing (CORS) is a security feature that controls how web pages can request resources from different domains. Proper CORS configuration prevents unauthorized access."},
    {"cluster": "WEB", "title": "HTTP Caching", "content": "HTTP caching stores copies of responses to reduce server load and improve performance. Cache-Control headers and ETags manage cache validation and expiration."},
    {"cluster": "WEB", "title": "API Rate Limiting", "content": "Rate limiting controls the number of API requests a client can make in a time period. It prevents abuse and ensures fair resource allocation across users."},
    {"cluster": "WEB", "title": "Microservices Architecture", "content": "Microservices decompose applications into small, independent services that communicate via APIs. Each service handles a specific business capability and can be deployed independently."},
    {"cluster": "WEB", "title": "API Versioning", "content": "API versioning manages changes to APIs while maintaining backward compatibility. Common strategies include URL versioning, header versioning, and content negotiation."},
    {"cluster": "WEB", "title": "Service Mesh", "content": "A service mesh is an infrastructure layer that handles service-to-service communication in microservices. It provides features like load balancing, service discovery, and observability."},
    
    # MACHINE LEARNING (10 resources)
    {"cluster": "ML", "title": "Neural Networks Basics", "content": "Neural networks are computing systems inspired by biological neural networks. They consist of layers of interconnected nodes that process information through weighted connections."},
    {"cluster": "ML", "title": "Gradient Descent", "content": "Gradient descent is an optimization algorithm that minimizes loss functions by iteratively moving in the direction of steepest descent. Learning rate controls the step size."},
    {"cluster": "ML", "title": "Overfitting and Regularization", "content": "Overfitting occurs when models learn training data too well and fail to generalize. Regularization techniques like L1, L2, and dropout prevent overfitting."},
    {"cluster": "ML", "title": "Transfer Learning", "content": "Transfer learning reuses pre-trained models on new tasks. It's especially effective when training data is limited, leveraging knowledge from related domains."},
    {"cluster": "ML", "title": "Attention Mechanisms", "content": "Attention mechanisms allow models to focus on relevant parts of input sequences. They are fundamental to transformer architectures and modern NLP models."},
    {"cluster": "ML", "title": "Batch Normalization", "content": "Batch normalization normalizes layer inputs to stabilize and accelerate training. It reduces internal covariate shift and allows higher learning rates."},
    {"cluster": "ML", "title": "Embeddings and Representations", "content": "Embeddings map discrete objects like words into continuous vector spaces. They capture semantic relationships and enable mathematical operations on categorical data."},
    {"cluster": "ML", "title": "Model Evaluation Metrics", "content": "Evaluation metrics like accuracy, precision, recall, and F1-score measure model performance. The choice depends on the problem type and class distribution."},
    {"cluster": "ML", "title": "Hyperparameter Tuning", "content": "Hyperparameter tuning optimizes model configuration parameters that aren't learned during training. Grid search, random search, and Bayesian optimization are common approaches."},
    {"cluster": "ML", "title": "Feature Engineering", "content": "Feature engineering creates new input variables from raw data to improve model performance. It includes scaling, encoding, and creating interaction terms."},
    
    # DEVOPS (10 resources)
    {"cluster": "DEVOPS", "title": "Docker Containers", "content": "Docker containers package applications with their dependencies into isolated units. They provide consistent environments across development, testing, and production."},
    {"cluster": "DEVOPS", "title": "Kubernetes Orchestration", "content": "Kubernetes orchestrates containerized applications across clusters. It handles deployment, scaling, load balancing, and self-healing of containerized workloads."},
    {"cluster": "DEVOPS", "title": "CI/CD Pipelines", "content": "Continuous Integration and Continuous Deployment automate software delivery. Pipelines run tests, build artifacts, and deploy code changes automatically."},
    {"cluster": "DEVOPS", "title": "Infrastructure as Code", "content": "Infrastructure as Code manages infrastructure through machine-readable files. Tools like Terraform and CloudFormation enable version-controlled infrastructure."},
    {"cluster": "DEVOPS", "title": "Monitoring and Observability", "content": "Monitoring tracks system metrics and logs to ensure reliability. Observability goes further by enabling understanding of system behavior through metrics, logs, and traces."},
    {"cluster": "DEVOPS", "title": "Load Balancing", "content": "Load balancers distribute network traffic across multiple servers to ensure high availability and reliability. They use algorithms like round-robin and least connections."},
    {"cluster": "DEVOPS", "title": "Blue-Green Deployment", "content": "Blue-green deployment maintains two identical production environments. Traffic switches between them to enable zero-downtime deployments and easy rollbacks."},
    {"cluster": "DEVOPS", "title": "Service Discovery", "content": "Service discovery automatically detects services in dynamic environments. It maintains a registry of available services and their network locations."},
    {"cluster": "DEVOPS", "title": "Secret Management", "content": "Secret management securely stores and accesses sensitive data like passwords and API keys. Tools like HashiCorp Vault provide encryption and access control."},
    {"cluster": "DEVOPS", "title": "Chaos Engineering", "content": "Chaos engineering deliberately introduces failures to test system resilience. It helps identify weaknesses before they cause production outages."},
]

# Generate 2 annotations per resource (100 total)
for item in DATASET:
    item["annotations"] = [
        f"Key concept: {item['title'].split()[-1]}",
        f"Related to {item['cluster']} domain"
    ]


def generate_large_dataset():
    print("=" * 60)
    print("LARGE DATASET SEEDER")
    print("=" * 60)
    
    engine = create_engine(DB_URL)
    print("--> Dropping and recreating tables...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("--> Loading Dense Model (Nomic)...")
    dense_model = SentenceTransformer(DENSE_MODEL_ID, trust_remote_code=True)
    
    print("--> Generating Data...")
    resources_created = 0
    annotations_created = 0
    
    for item in DATASET:
        # Generate embedding
        dense_vec = dense_model.encode(item["content"]).tolist()
        embedding_json = json.dumps(dense_vec)
        
        # Create resource
        res = Resource(
            title=item["title"],
            description=item["content"],
            embedding=embedding_json,
            subject=[item["cluster"]]
        )
        
        session.add(res)
        session.flush()
        
        # Add annotations
        for idx, note in enumerate(item["annotations"]):
            start = idx * 100
            end = start + len(note)
            ann = Annotation(
                resource_id=res.id,
                user_id="audit_system",
                start_offset=start,
                end_offset=end,
                highlighted_text=note,
                note=f"Annotation {idx+1} for {item['cluster']}"
            )
            session.add(ann)
            annotations_created += 1
        
        resources_created += 1
        if resources_created % 10 == 0:
            print(f"   Progress: {resources_created}/50 resources")
    
    session.commit()
    
    print("=" * 60)
    print(f"SUCCESS: Created {resources_created} Resources and {annotations_created} Annotations.")
    print("=" * 60)


if __name__ == "__main__":
    generate_large_dataset()
