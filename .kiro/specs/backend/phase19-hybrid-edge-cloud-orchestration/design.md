# Design Document: Phase 19 - Hybrid Edge-Cloud Orchestration & Neural Graph Learning

## Overview

This design implements a hybrid edge-cloud architecture that splits Neo Alexandria's backend into two complementary components:

1. **Cloud API (Control Plane)**: A lightweight FastAPI service deployed on Render Free Tier that handles user requests, dispatches tasks, and manages metadata
2. **Edge Worker (Compute Plane)**: A GPU-accelerated Python worker running locally that performs heavy ML operations including graph neural network training

The architecture leverages serverless infrastructure (Neon Postgres, Qdrant Cloud, Upstash Redis) to minimize costs while maximizing compute power through local GPU utilization. The system implements PyTorch Geometric's Node2Vec algorithm to generate structural embeddings of code repositories based on dependency graphs.

### Key Design Principles

- **Separation of Concerns**: Cloud handles orchestration, Edge handles computation
- **Resource Optimization**: Free-tier cloud for API, local GPU for ML
- **Asynchronous Processing**: Queue-based task distribution with status tracking
- **Fault Tolerance**: Retry logic, graceful degradation, and error recovery
- **Scalability**: Horizontal scaling of edge workers, vertical scaling of cloud API
- **Security First**: API authentication, queue caps, and TTL enforcement
- **Operational Resilience**: Zombie queue prevention, stale task handling, real-time status

### Critical Risk Mitigations

This design addresses three critical operational and security risks:

**Risk A: The "Open Door" Security Hole**
- **Problem**: POST /ingest on public internet without authentication allows anyone to bombard edge worker
- **Solution**: Bearer token authentication (PHAROS_ADMIN_TOKEN) required for all /ingest requests
- **Implementation**: HTTPBearer security with 401 rejection for invalid/missing tokens
- **Monitoring**: Log all authentication failures for security auditing

**Risk B: The "Zombie Queue" Problem**
- **Problem**: Queue fills with stale jobs when laptop offline, overwhelming system on restart
- **Solution**: Queue cap (10 pending tasks max) + TTL (24 hours) on all tasks
- **Implementation**: Check queue size before accepting tasks (429 if full), skip stale tasks on worker
- **Benefit**: Prevents system overload and GitHub API rate limit issues

**Risk C: The "Dependency Hell" Problem**
- **Problem**: Maintaining separate requirements.txt files leads to version mismatches between cloud/edge
- **Solution**: Base + extension strategy with requirements-base.txt inherited by both
- **Implementation**: Use "-r requirements-base.txt" in cloud and edge files
- **Benefit**: Update shared dependencies once, both environments inherit automatically

**Risk D: The "Silent Failure" Problem**
- **Problem**: Users don't know if worker is training, idle, or stuck
- **Solution**: Real-time status endpoint (GET /worker/status) with detailed state
- **Implementation**: Worker updates Redis status, UI polls for updates
- **Benefit**: Visual feedback ("Training... 40%") makes hybrid architecture transparent

## Architecture

### System Architecture Diagram

```mermaid
graph TD
    subgraph "Cloud Layer (Render Free Tier)"
        User[User/Client] -->|POST /ingest| CloudAPI[FastAPI Control Plane]
        CloudAPI -->|RPUSH Task| Redis[(Upstash Redis Queue)]
        CloudAPI <-->|Read/Write Metadata| Neon[(Neon Postgres)]
        CloudAPI <-->|Search Vectors| Qdrant[(Qdrant Cloud)]
    end
    
    subgraph "Edge Layer (Local Laptop - RTX 4070)"
        Worker[Python Edge Worker] -->|LPOP Task| Redis
        Worker -->|Clone & Parse| Repo[Git Repository]
        Worker -->|Build Graph| GraphBuilder[Dependency Graph Builder]
        GraphBuilder -->|Train| PyTorch[PyTorch Geometric Node2Vec]
        PyTorch -->|Generate| Embeddings[Structural Embeddings]
        Embeddings -->|Upload| Qdrant
        Worker -->|Update Status| Redis
    end
    
    Redis -.->|Poll Every 2s| Worker
```

### Component Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant CloudAPI
    participant Redis
    participant EdgeWorker
    participant PyTorch
    participant Qdrant
    
    User->>CloudAPI: POST /ingest/github.com/user/repo
    CloudAPI->>Redis: RPUSH ingest_queue
    CloudAPI-->>User: {job_id, queue_position}
    
    loop Every 2 seconds
        EdgeWorker->>Redis: LPOP ingest_queue
    end
    
    Redis-->>EdgeWorker: repo_url
    EdgeWorker->>Redis: SET worker_status "Training..."
    EdgeWorker->>EdgeWorker: Clone repository
    EdgeWorker->>EdgeWorker: Parse imports
    EdgeWorker->>EdgeWorker: Build dependency graph
    EdgeWorker->>PyTorch: Train Node2Vec
    PyTorch-->>EdgeWorker: Embeddings tensor
    EdgeWorker->>Qdrant: Batch upload embeddings
    EdgeWorker->>Redis: SET worker_status "Idle"
    
    User->>CloudAPI: GET /worker/status
    CloudAPI->>Redis: GET worker_status
    Redis-->>CloudAPI: "Idle"
    CloudAPI-->>User: {status: "Idle"}
```

## Components and Interfaces

### 1. Cloud API (Control Plane)

**Location**: `backend/app/main.py` (deployed to Render)

**Purpose**: Lightweight orchestration layer that dispatches tasks and serves metadata

**Key Responsibilities**:
- Accept repository ingestion requests
- Validate and queue tasks to Redis
- Provide worker status information
- Serve search and metadata queries
- Manage authentication and rate limiting

**Dependencies**:

The project uses a base + extension strategy to avoid dependency hell:

`requirements-base.txt` (shared dependencies):
```
fastapi==0.104.1
uvicorn==0.24.0
upstash-redis==0.15.0
pydantic==2.5.0
python-dotenv==1.0.0
gitpython==3.1.40
```

`requirements-cloud.txt` (extends base):
```
-r requirements-base.txt
psycopg2-binary==2.9.9
qdrant-client==1.7.0
```

`requirements-edge.txt` (extends base):
```
-r requirements-base.txt
torch==2.1.0
torch-geometric==2.4.0
tree-sitter==0.20.4
tree-sitter-python==0.20.4
tree-sitter-javascript==0.20.3
qdrant-client==1.7.0
numpy==1.24.3
psycopg2-binary==2.9.9
```

**Rationale**: Using `-r requirements-base.txt` ensures version consistency across deployments. When updating a shared dependency, update it once in base.txt and both cloud and edge inherit the change. This prevents the "dependency hell" problem where cloud and edge have different versions of the same package (e.g., "It works on my machine (Edge) but fails on Cloud because I forgot to upgrade Pydantic in the cloud file").

**Configuration**:
```python
# app/core/config.py
class Settings(BaseSettings):
    MODE: str = "CLOUD"  # or "EDGE"
    
    # Cloud-specific
    UPSTASH_REDIS_REST_URL: str
    UPSTASH_REDIS_REST_TOKEN: str
    NEON_DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: str
    
    # Conditional loading
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.MODE == "CLOUD":
            # Skip heavy imports
            pass
        elif self.MODE == "EDGE":
            # Verify CUDA, load torch
            import torch
            self.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
```

**API Endpoints**:

```python
# app/routers/ingestion.py
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from upstash_redis import Redis
from app.core.config import settings
from app.schemas.ingestion import IngestionRequest, IngestionResponse
import os

router = APIRouter(prefix="/api/v1/ingestion", tags=["ingestion"])
security = HTTPBearer()

# Maximum queue size to prevent zombie queue problem
MAX_QUEUE_SIZE = 10
# Task TTL in seconds (24 hours)
TASK_TTL = 86400

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify API admin token for ingestion endpoint.
    
    This prevents unauthorized users from bombarding the edge worker
    with git clone requests.
    """
    expected_token = os.getenv("PHAROS_ADMIN_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="Server misconfiguration: PHAROS_ADMIN_TOKEN not set"
        )
    
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing authentication token"
        )
    
    return credentials.credentials

@router.post("/ingest/{repo_url:path}", response_model=IngestionResponse)
async def trigger_remote_ingestion(
    repo_url: str,
    redis: Redis = Depends(get_redis_client),
    token: str = Depends(verify_admin_token)
):
    """
    Dispatch a repository ingestion task to the edge worker.
    
    **Security**: Requires Bearer token authentication via PHAROS_ADMIN_TOKEN.
    This prevents unauthorized users from submitting tasks.
    
    **Queue Management**: Rejects new tasks if queue has >10 pending jobs
    to prevent overwhelming the edge worker.
    
    Args:
        repo_url: Full repository URL (e.g., github.com/user/repo)
        
    Returns:
        Job ID and queue position
        
    Raises:
        401: Invalid or missing authentication token
        400: Invalid repository URL
        429: Queue is full (>10 pending tasks)
        503: Queue unavailable
    """
    # Validate URL
    if not is_valid_repo_url(repo_url):
        raise HTTPException(status_code=400, detail="Invalid repository URL")
    
    try:
        # Check queue size to prevent zombie queue problem
        queue_size = redis.llen("ingest_queue")
        if queue_size >= MAX_QUEUE_SIZE:
            raise HTTPException(
                status_code=429,
                detail=f"Queue is full ({queue_size} pending tasks). Please try again later."
            )
        
        # Create task with metadata
        task_data = {
            "repo_url": repo_url,
            "submitted_at": datetime.now().isoformat(),
            "ttl": TASK_TTL
        }
        
        # Push to queue with TTL
        job_id = redis.rpush("ingest_queue", json.dumps(task_data))
        
        # Set expiration on the queue key (refreshed on each push)
        redis.expire("ingest_queue", TASK_TTL)
        
        return IngestionResponse(
            status="dispatched",
            job_id=job_id,
            queue_position=queue_size + 1,
            target="RTX-4070-Node",
            queue_size=queue_size + 1,
            max_queue_size=MAX_QUEUE_SIZE
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Queue unavailable: {str(e)}")

@router.get("/worker/status")
async def get_worker_status(redis: Redis = Depends(get_redis_client)):
    """
    Get current edge worker status.
    
    **Critical for UI**: This endpoint enables real-time status updates
    in the frontend, showing users when the worker is training, idle,
    or encountering errors. The visual feedback ("Training... 40%") is
    what makes the hybrid architecture transparent to users.
    
    Returns:
        Worker status string or "Offline" if not available
    """
    try:
        status = redis.get("worker_status")
        return {"status": status or "Offline"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis unavailable: {str(e)}")

@router.get("/jobs/history")
async def get_job_history(
    limit: int = 10,
    redis: Redis = Depends(get_redis_client)
):
    """
    Get recent job history.
    
    Args:
        limit: Number of recent jobs to return (max 100)
        
    Returns:
        List of recent jobs with status and timing
    """
    limit = min(limit, 100)
    jobs = redis.lrange("job_history", 0, limit - 1)
    return {"jobs": [json.loads(job) for job in jobs]}
```

### 2. Edge Worker (Compute Plane)

**Location**: `backend/worker.py` (runs locally)

**Purpose**: GPU-accelerated worker that processes repositories and trains graph neural networks

**Key Responsibilities**:
- Poll task queue for new jobs
- Clone and parse code repositories
- Build dependency graphs from imports
- Train Node2Vec models on GPU
- Upload embeddings to Qdrant
- Update job status in Redis

**Dependencies**:

The project uses a base + extension strategy to avoid dependency hell:

`requirements-base.txt` (shared dependencies):
```
upstash-redis==0.15.0
gitpython==0.1.40
```

`requirements-edge.txt` (extends base):
```
-r requirements-base.txt
torch==2.1.0
torch-geometric==2.4.0
tree-sitter==0.20.4
tree-sitter-python==0.20.4
tree-sitter-javascript==0.20.3
qdrant-client==1.7.0
numpy==1.24.3
```

**Rationale**: Using `-r requirements-base.txt` ensures version consistency. When updating a shared dependency like upstash-redis, update it once in base.txt and edge inherits the change.

**Implementation**:

```python
# worker.py
import os
import time
import json
import torch
from datetime import datetime
from upstash_redis import Redis
from app.services.neural_graph import NeuralGraphService
from app.utils.repo_parser import RepositoryParser

# Configuration
redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🔥 Edge Worker Online")
print(f"   Hardware: {torch.cuda.get_device_name(0) if device == 'cuda' else 'CPU'}")
print(f"   Device: {device}")

def process_job(task_data: dict):
    """Process a single repository ingestion job."""
    job_start = datetime.now()
    
    # Extract task data
    repo_url = task_data.get("repo_url")
    submitted_at = task_data.get("submitted_at")
    ttl = task_data.get("ttl", 86400)
    
    # Check if task is stale (older than TTL)
    if submitted_at:
        submitted_time = datetime.fromisoformat(submitted_at)
        age_seconds = (job_start - submitted_time).total_seconds()
        
        if age_seconds > ttl:
            print(f"⏭️  Skipping stale task (age: {age_seconds:.0f}s, TTL: {ttl}s): {repo_url}")
            
            # Record as skipped
            job_record = {
                "repo_url": repo_url,
                "status": "skipped",
                "reason": "Task exceeded TTL",
                "age_seconds": age_seconds,
                "timestamp": job_start.isoformat()
            }
            redis.lpush("job_history", json.dumps(job_record))
            redis.ltrim("job_history", 0, 99)
            return
    
    try:
        # Update status
        redis.set("worker_status", f"Training Graph on {repo_url}")
        
        # Initialize services
        parser = RepositoryParser()
        neural_service = NeuralGraphService(device=device)
        
        # Clone and parse
        print(f"⚡ Received Job: {repo_url}")
        repo_path = parser.clone_repository(repo_url)
        
        # Build dependency graph
        print("📊 Building dependency graph...")
        dependency_graph = parser.build_dependency_graph(repo_path)
        
        # Train embeddings
        print("🧠 Training Node2Vec...")
        embeddings = neural_service.train_embeddings(
            edge_index=dependency_graph.edge_index,
            num_nodes=dependency_graph.num_nodes
        )
        
        # Upload to Qdrant
        print("☁️  Uploading embeddings to Qdrant...")
        neural_service.upload_embeddings(
            embeddings=embeddings,
            file_paths=dependency_graph.file_paths,
            repo_url=repo_url
        )
        
        # Record success
        job_end = datetime.now()
        duration = (job_end - job_start).total_seconds()
        
        job_record = {
            "repo_url": repo_url,
            "status": "complete",
            "duration_seconds": duration,
            "files_processed": dependency_graph.num_nodes,
            "embeddings_generated": len(embeddings),
            "timestamp": job_end.isoformat()
        }
        
        redis.lpush("job_history", json.dumps(job_record))
        redis.ltrim("job_history", 0, 99)  # Keep last 100 jobs
        
        print(f"✅ Job Complete ({duration:.2f}s)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        redis.set("worker_status", f"Error: {str(e)}")
        
        # Record failure
        job_record = {
            "repo_url": repo_url,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        redis.lpush("job_history", json.dumps(job_record))
        redis.ltrim("job_history", 0, 99)
    
    finally:
        # Cleanup
        if 'repo_path' in locals():
            parser.cleanup(repo_path)

def main():
    """Main worker loop."""
    redis.set("worker_status", "Idle")
    
    while True:
        try:
            # Poll for jobs
            job = redis.lpop("ingest_queue")
            
            if job:
                # Parse task data (handle both old string format and new JSON format)
                task_str = job.decode() if isinstance(job, bytes) else job
                
                try:
                    task_data = json.loads(task_str)
                except json.JSONDecodeError:
                    # Legacy format: plain URL string
                    task_data = {
                        "repo_url": task_str,
                        "submitted_at": None,
                        "ttl": 86400
                    }
                
                process_job(task_data)
                redis.set("worker_status", "Idle")
            else:
                # Sleep when idle
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down gracefully...")
            redis.set("worker_status", "Offline")
            break
            
        except Exception as e:
            print(f"❌ Worker Error: {e}")
            redis.set("worker_status", f"Error: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    main()
```

### 3. Neural Graph Service

**Location**: `backend/app/services/neural_graph.py`

**Purpose**: PyTorch Geometric service for graph representation learning

**Key Responsibilities**:
- Train Node2Vec models on dependency graphs
- Generate 64-dimensional structural embeddings
- Manage GPU memory and training loops
- Export embeddings for storage

**Implementation**:

```python
# app/services/neural_graph.py
import torch
from torch_geometric.nn import Node2Vec
from torch_geometric.data import Data
from typing import Tuple
import numpy as np

class NeuralGraphService:
    """
    Service for generating structural embeddings using PyTorch Geometric.
    
    Implements Node2Vec algorithm to create embeddings based on graph structure
    rather than text content. This captures code organization and dependencies.
    """
    
    def __init__(self, device: str = "cuda"):
        self.device = device
        
        # Hyperparameters (optimized for code graphs)
        self.embedding_dim = 64  # Matryoshka-style compact embeddings
        self.walk_length = 20    # Longer walks for deep dependencies
        self.context_size = 10   # Context window for skip-gram
        self.walks_per_node = 10 # Multiple walks per node
        self.num_epochs = 10     # Fast training
        self.batch_size = 128
        self.learning_rate = 0.01
        
    def train_embeddings(
        self,
        edge_index: torch.Tensor,
        num_nodes: int
    ) -> torch.Tensor:
        """
        Train Node2Vec model on dependency graph.
        
        Args:
            edge_index: Edge list tensor of shape [2, num_edges]
            num_nodes: Total number of nodes in graph
            
        Returns:
            Embedding tensor of shape [num_nodes, embedding_dim]
        """
        print(f"🧠 Training Node2Vec on {self.device}...")
        print(f"   Nodes: {num_nodes}, Edges: {edge_index.shape[1]}")
        
        # Initialize Node2Vec model
        model = Node2Vec(
            edge_index=edge_index,
            embedding_dim=self.embedding_dim,
            walk_length=self.walk_length,
            context_size=self.context_size,
            walks_per_node=self.walks_per_node,
            sparse=True  # Use sparse gradients for efficiency
        ).to(self.device)
        
        # Create data loader
        loader = model.loader(
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=0  # Single worker for GPU
        )
        
        # Optimizer (SparseAdam for sparse gradients)
        optimizer = torch.optim.SparseAdam(
            list(model.parameters()),
            lr=self.learning_rate
        )
        
        # Training loop
        model.train()
        for epoch in range(1, self.num_epochs + 1):
            total_loss = 0
            
            for pos_rw, neg_rw in loader:
                optimizer.zero_grad()
                
                # Compute loss
                loss = model.loss(
                    pos_rw.to(self.device),
                    neg_rw.to(self.device)
                )
                
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            
            # Log progress
            if epoch % 5 == 0:
                avg_loss = total_loss / len(loader)
                print(f"   Epoch {epoch:02d}: Loss = {avg_loss:.4f}")
        
        # Extract embeddings and move to CPU
        embeddings = model.embedding.weight.data.cpu()
        
        print(f"✅ Training complete. Generated {num_nodes} embeddings.")
        return embeddings
    
    def upload_embeddings(
        self,
        embeddings: torch.Tensor,
        file_paths: list[str],
        repo_url: str
    ):
        """
        Upload embeddings to Qdrant Cloud.
        
        Args:
            embeddings: Tensor of shape [num_files, embedding_dim]
            file_paths: List of file paths corresponding to embeddings
            repo_url: Repository URL for metadata
        """
        from qdrant_client import QdrantClient
        from qdrant_client.models import PointStruct, Distance, VectorParams
        import os
        
        # Initialize Qdrant client
        client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        
        collection_name = "code_structure_embeddings"
        
        # Create collection if it doesn't exist
        try:
            client.get_collection(collection_name)
        except:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
        
        # Prepare points for batch upload
        points = []
        for idx, (embedding, file_path) in enumerate(zip(embeddings, file_paths)):
            point = PointStruct(
                id=idx,
                vector=embedding.numpy().tolist(),
                payload={
                    "file_path": file_path,
                    "repo_url": repo_url,
                    "embedding_type": "structural",
                    "model": "node2vec"
                }
            )
            points.append(point)
        
        # Batch upload with retry logic
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            
            for attempt in range(3):
                try:
                    client.upsert(
                        collection_name=collection_name,
                        points=batch
                    )
                    break
                except Exception as e:
                    if attempt == 2:
                        raise
                    print(f"   Retry {attempt + 1}/3 for batch {i // batch_size + 1}")
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        print(f"☁️  Uploaded {len(points)} embeddings to Qdrant")
```

### 4. Repository Parser

**Location**: `backend/app/utils/repo_parser.py`

**Purpose**: Parse code repositories and extract dependency graphs

**Key Responsibilities**:
- Clone Git repositories
- Parse source files using Tree-sitter
- Extract import statements
- Build graph representations
- Clean up temporary files

**Implementation**:

```python
# app/utils/repo_parser.py
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import torch
from git import Repo
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript

class DependencyGraph:
    """Container for dependency graph data."""
    
    def __init__(self, edge_index: torch.Tensor, file_paths: List[str]):
        self.edge_index = edge_index
        self.file_paths = file_paths
        self.num_nodes = len(file_paths)

class RepositoryParser:
    """Parse code repositories and build dependency graphs."""
    
    def __init__(self):
        # Initialize Tree-sitter parsers
        self.parsers = {
            '.py': self._create_parser(tspython.language()),
            '.js': self._create_parser(tsjavascript.language()),
            '.ts': self._create_parser(tsjavascript.language()),
        }
        
    def _create_parser(self, language) -> Parser:
        """Create a Tree-sitter parser for a language."""
        parser = Parser()
        parser.set_language(language)
        return parser
    
    def clone_repository(self, repo_url: str) -> str:
        """
        Clone a Git repository to a temporary directory.
        
        Args:
            repo_url: Repository URL (e.g., github.com/user/repo)
            
        Returns:
            Path to cloned repository
        """
        # Ensure URL has protocol
        if not repo_url.startswith(('http://', 'https://', 'git@')):
            repo_url = f"https://{repo_url}"
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="neo_repo_")
        
        try:
            print(f"📥 Cloning {repo_url}...")
            Repo.clone_from(repo_url, temp_dir, depth=1)  # Shallow clone
            return temp_dir
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"Failed to clone repository: {e}")
    
    def build_dependency_graph(self, repo_path: str) -> DependencyGraph:
        """
        Build dependency graph from repository.
        
        Args:
            repo_path: Path to cloned repository
            
        Returns:
            DependencyGraph with edge_index and file_paths
        """
        # Find all source files
        file_paths = self._find_source_files(repo_path)
        
        # Create file index mapping
        file_to_idx = {path: idx for idx, path in enumerate(file_paths)}
        
        # Extract imports and build edges
        edges = []
        for file_path in file_paths:
            imports = self._extract_imports(file_path)
            
            # Resolve imports to file paths
            for import_path in imports:
                resolved = self._resolve_import(import_path, file_path, repo_path)
                if resolved and resolved in file_to_idx:
                    # Add edge: file -> imported_file
                    edges.append([file_to_idx[file_path], file_to_idx[resolved]])
        
        # Convert to PyTorch tensor
        if edges:
            edge_index = torch.tensor(edges, dtype=torch.long).t()
        else:
            # Empty graph - create self-loops
            edge_index = torch.tensor([[i, i] for i in range(len(file_paths))], dtype=torch.long).t()
        
        print(f"📊 Built graph: {len(file_paths)} nodes, {edge_index.shape[1]} edges")
        
        return DependencyGraph(edge_index=edge_index, file_paths=file_paths)
    
    def _find_source_files(self, repo_path: str) -> List[str]:
        """Find all source files in repository."""
        source_files = []
        
        for ext in self.parsers.keys():
            for file_path in Path(repo_path).rglob(f"*{ext}"):
                # Skip common non-source directories
                if any(skip in str(file_path) for skip in ['.git', 'node_modules', '__pycache__', 'venv', '.venv']):
                    continue
                source_files.append(str(file_path))
        
        return source_files
    
    def _extract_imports(self, file_path: str) -> List[str]:
        """Extract import statements from a source file."""
        ext = Path(file_path).suffix
        parser = self.parsers.get(ext)
        
        if not parser:
            return []
        
        try:
            with open(file_path, 'rb') as f:
                code = f.read()
            
            tree = parser.parse(code)
            imports = []
            
            # Language-specific import extraction
            if ext == '.py':
                imports = self._extract_python_imports(tree.root_node, code)
            elif ext in ['.js', '.ts']:
                imports = self._extract_javascript_imports(tree.root_node, code)
            
            return imports
            
        except Exception as e:
            print(f"⚠️  Failed to parse {file_path}: {e}")
            return []
    
    def _extract_python_imports(self, node, code: bytes) -> List[str]:
        """Extract Python import statements."""
        imports = []
        
        def traverse(node):
            if node.type == 'import_statement':
                # import module
                for child in node.children:
                    if child.type == 'dotted_name':
                        imports.append(code[child.start_byte:child.end_byte].decode())
            elif node.type == 'import_from_statement':
                # from module import ...
                for child in node.children:
                    if child.type == 'dotted_name':
                        imports.append(code[child.start_byte:child.end_byte].decode())
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
        return imports
    
    def _extract_javascript_imports(self, node, code: bytes) -> List[str]:
        """Extract JavaScript/TypeScript import statements."""
        imports = []
        
        def traverse(node):
            if node.type == 'import_statement':
                # import ... from 'module'
                for child in node.children:
                    if child.type == 'string':
                        # Remove quotes
                        import_path = code[child.start_byte:child.end_byte].decode().strip('"\'')
                        imports.append(import_path)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
        return imports
    
    def _resolve_import(self, import_path: str, current_file: str, repo_path: str) -> str:
        """Resolve import path to actual file path."""
        # Handle relative imports
        if import_path.startswith('.'):
            current_dir = Path(current_file).parent
            resolved = (current_dir / import_path).resolve()
            
            # Try with common extensions
            for ext in ['.py', '.js', '.ts', '/index.js', '/index.ts']:
                candidate = Path(str(resolved) + ext)
                if candidate.exists():
                    return str(candidate)
        
        # Handle absolute imports (simplified)
        # In production, would need more sophisticated module resolution
        
        return None
    
    def cleanup(self, repo_path: str):
        """Clean up temporary repository directory."""
        try:
            shutil.rmtree(repo_path, ignore_errors=True)
            print(f"🧹 Cleaned up {repo_path}")
        except Exception as e:
            print(f"⚠️  Cleanup failed: {e}")
```

## Data Models

### Task Queue Schema

**Redis Key**: `ingest_queue`
**Type**: List (FIFO queue)
**Value**: Repository URL string

```
Example:
"github.com/user/awesome-project"
"gitlab.com/org/internal-tool"
```

### Worker Status Schema

**Redis Key**: `worker_status`
**Type**: String
**Values**:
- `"Idle"` - Worker is waiting for tasks
- `"Training Graph on {repo_url}"` - Worker is processing
- `"Error: {error_message}"` - Worker encountered an error
- `"Offline"` - Worker is not running

### Job History Schema

**Redis Key**: `job_history`
**Type**: List (capped at 100 entries)
**Value**: JSON string

```json
{
  "repo_url": "github.com/user/repo",
  "status": "complete",
  "duration_seconds": 127.5,
  "files_processed": 342,
  "embeddings_generated": 342,
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### Qdrant Embedding Schema

**Collection**: `code_structure_embeddings`
**Vector Size**: 64
**Distance**: Cosine

```json
{
  "id": 12345,
  "vector": [0.123, -0.456, ...],  // 64 dimensions
  "payload": {
    "file_path": "src/utils/parser.py",
    "repo_url": "github.com/user/repo",
    "embedding_type": "structural",
    "model": "node2vec"
  }
}
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Task Queue Round Trip
*For any* valid repository URL, when submitted to the Cloud API, the task should appear in the Redis queue and the response should contain a valid job_id and queue_position.
**Validates: Requirements 2.1, 2.2**

### Property 2: Worker Status Consistency
*For any* job processed by the Edge Worker, the worker status in Redis should transition from "Idle" → "Training Graph on {repo}" → "Idle" (or "Error: {message}").
**Validates: Requirements 3.5, 6.5**

### Property 3: URL Validation Rejects Invalid Input
*For any* malformed or malicious repository URL, the Cloud API should reject it with a 400 status code before queuing.
**Validates: Requirements 2.4, 11.4**

### Property 4: Status Endpoint Reflects Redis State
*For any* worker status value stored in Redis, the GET /worker/status endpoint should return that exact value.
**Validates: Requirements 2.3**

### Property 5: Repository Processing Pipeline Completeness
*For any* successfully cloned repository, all source files should be parsed, a dependency graph should be built, and the graph should have at least as many nodes as there are source files.
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 6: Embedding Dimensionality Invariant
*For any* dependency graph with N nodes, the Neural Graph Service should generate exactly N embeddings, each with exactly 64 dimensions.
**Validates: Requirements 5.2**

### Property 7: Embedding Device Location
*For any* completed training run, all returned embeddings should be CPU tensors (not GPU tensors).
**Validates: Requirements 5.6**

### Property 8: Embedding Upload Completeness
*For any* set of generated embeddings, all embeddings should be uploaded to Qdrant with payloads containing file_path and repo_url fields.
**Validates: Requirements 6.1, 6.2**

### Property 9: Job History Record Completeness
*For any* completed job, the job history record should contain repo_url, status, duration_seconds, files_processed, embeddings_generated, and timestamp fields.
**Validates: Requirements 9.3, 9.4**

### Property 10: Job History Size Cap
*For any* sequence of more than 100 jobs, the job_history list in Redis should contain exactly 100 entries (the most recent ones).
**Validates: Requirements 9.6**

### Property 11: Status Format Validation
*For any* worker status update, the status string should match one of the patterns: "Idle", "Training Graph on {repo_url}", or "Error: {error_message}".
**Validates: Requirements 9.1**

### Property 12: HTTPS Protocol Enforcement
*For any* external API call to Neon, Qdrant, or Upstash, the URL should use the HTTPS protocol.
**Validates: Requirements 11.3**

### Property 13: Temporary Directory Isolation
*For any* two concurrent repository clones, they should use different temporary directory paths.
**Validates: Requirements 11.5**

### Property 14: Cleanup Removes Temporary Files
*For any* completed or failed job, the temporary repository directory should be removed from the filesystem.
**Validates: Requirements 11.6**

### Property 15: Error Status Codes
*For any* error condition (invalid input, service unavailable, etc.), the Cloud API should return an appropriate HTTP status code (400, 503, etc.) and not 200.
**Validates: Requirements 8.5**

### Property 16: Queue Cap Enforcement
*For any* Cloud API request when the queue has 10 or more pending tasks, the API should reject the request with status code 429.
**Validates: Requirements 2.6**

### Property 17: Authentication Required
*For any* POST /ingest request without a valid Bearer token, the Cloud API should return status code 401.
**Validates: Requirements 2.8**

### Property 18: Stale Task Handling
*For any* task in the queue older than its TTL, the Edge Worker should skip it and record it as "skipped" in job history.
**Validates: Requirements 3.7**

## Error Handling

### Cloud API Error Handling

**Invalid Repository URL**:
- Validate URL format before queuing
- Return 400 Bad Request with descriptive error message
- Log validation failures for monitoring

**Redis Unavailable**:
- Catch connection exceptions
- Return 503 Service Unavailable
- Log error and attempt reconnection on next request

**Qdrant Unavailable**:
- Catch connection exceptions for search operations
- Return 503 Service Unavailable
- Maintain degraded service (queue still works)

**Database Unavailable**:
- Catch connection exceptions
- Return 503 Service Unavailable
- Implement connection pooling with retry logic

### Edge Worker Error Handling

**Repository Clone Failure**:
- Log error with repository URL
- Mark job as failed in history
- Update status to "Error: Clone failed"
- Continue to next job (don't crash)

**Parse Failure**:
- Log error with file path
- Skip problematic file
- Continue parsing remaining files
- Complete job with partial results

**Training Failure**:
- Log error with stack trace
- Mark job as failed
- Clean up GPU memory
- Continue to next job

**Qdrant Upload Failure**:
- Retry up to 3 times with exponential backoff (2^attempt seconds)
- If all retries fail, mark job as failed
- Log error for manual investigation
- Clean up resources and continue

**Redis Connection Loss**:
- Log error
- Attempt reconnection every 5 seconds
- Buffer status updates locally if possible
- Resume normal operation when connection restored

**GPU Out of Memory**:
- Catch CUDA OOM exceptions
- Reduce batch size and retry
- If still fails, fall back to CPU
- Log warning about performance degradation

### Graceful Shutdown

**Cloud API**:
- Handle SIGTERM signal
- Complete in-flight requests
- Close database connections
- Shutdown within 30 seconds

**Edge Worker**:
- Handle SIGINT (Ctrl+C) signal
- Complete current job if possible
- Update status to "Offline"
- Clean up temporary files
- Shutdown within 60 seconds

## Testing Strategy

### Dual Testing Approach

This system requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests**: Verify specific examples, edge cases, and error conditions
**Property Tests**: Verify universal properties across all inputs

Together, these provide comprehensive coverage where unit tests catch concrete bugs and property tests verify general correctness.

### Property-Based Testing Configuration

We will use **Hypothesis** for Python property-based testing:

```python
# Install
pip install hypothesis

# Configuration
# - Minimum 100 iterations per property test
# - Each test tagged with feature name and property number
# - Tests reference design document properties
```

**Test Tagging Format**:
```python
@pytest.mark.property
@pytest.mark.feature("phase19-hybrid-edge-cloud-orchestration")
def test_property_1_task_queue_round_trip():
    """
    Property 1: Task Queue Round Trip
    For any valid repository URL, when submitted to the Cloud API,
    the task should appear in the Redis queue and the response should
    contain a valid job_id and queue_position.
    """
    # Test implementation
```

### Unit Test Coverage

**Cloud API Tests** (`tests/test_cloud_api.py`):
- Test MODE=CLOUD doesn't load torch (1.2)
- Test database connection (1.3)
- Test Qdrant connection (1.4)
- Test Redis connection (1.5)
- Test 503 when Redis unavailable (2.5)
- Test health check endpoint (12.6)

**Edge Worker Tests** (`tests/test_edge_worker.py`):
- Test CUDA detection (3.1)
- Test CPU fallback (3.2)
- Test hardware logging (3.4)
- Test error continuation (3.6)
- Test parse error handling (4.4)
- Test multi-language support (4.5)
- Test training loss logging (5.5)
- Test batch upload (6.3)
- Test retry logic (6.4)

**Configuration Tests** (`tests/test_configuration.py`):
- Test MODE environment variable (7.1)
- Test CLOUD mode excludes torch (7.2)
- Test EDGE mode verifies CUDA (7.3)
- Test environment variable validation (7.6)

**Error Handling Tests** (`tests/test_error_handling.py`):
- Test network retry logic (8.1)
- Test clone failure handling (8.2)
- Test Redis reconnection (8.6)

**Security Tests** (`tests/test_security.py`):
- Test credential validation (11.1, 11.2)
- Test worker startup command (12.2)

### Property Test Coverage

**Queue Properties** (`tests/properties/test_queue_properties.py`):
- Property 1: Task queue round trip
- Property 3: URL validation rejects invalid input
- Property 4: Status endpoint reflects Redis state

**Processing Properties** (`tests/properties/test_processing_properties.py`):
- Property 2: Worker status consistency
- Property 5: Repository processing pipeline completeness

**Embedding Properties** (`tests/properties/test_embedding_properties.py`):
- Property 6: Embedding dimensionality invariant
- Property 7: Embedding device location
- Property 8: Embedding upload completeness

**Monitoring Properties** (`tests/properties/test_monitoring_properties.py`):
- Property 9: Job history record completeness
- Property 10: Job history size cap
- Property 11: Status format validation

**Security Properties** (`tests/properties/test_security_properties.py`):
- Property 12: HTTPS protocol enforcement
- Property 13: Temporary directory isolation
- Property 14: Cleanup removes temporary files
- Property 15: Error status codes

### Integration Tests

**End-to-End Workflow** (`tests/integration/test_e2e_workflow.py`):
1. Start Cloud API (mocked Render environment)
2. Start Edge Worker (mocked or real GPU)
3. Submit repository URL via API
4. Verify task appears in queue
5. Verify worker picks up task
6. Verify embeddings uploaded to Qdrant
7. Verify job history updated
8. Verify worker returns to idle

**Multi-Repository Processing** (`tests/integration/test_multi_repo.py`):
1. Queue multiple repositories
2. Verify sequential processing
3. Verify status updates for each
4. Verify all embeddings uploaded
5. Verify job history contains all jobs

### Performance Tests

**Benchmarks** (`tests/performance/test_benchmarks.py`):
- Measure API dispatch latency (target: <100ms)
- Measure embedding generation time (target: <5min for 100 files)
- Measure GPU utilization (target: >70%)
- Measure throughput (target: >10 repos/hour)

**Stress Tests** (`tests/performance/test_stress.py`):
- Test with 10,000 file repository
- Test with 100 concurrent API requests
- Test with queue of 1000 repositories
- Test with limited GPU memory

### Test Infrastructure

**Fixtures** (`tests/conftest.py`):
```python
@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    return MockRedis()

@pytest.fixture
def mock_qdrant():
    """Mock Qdrant client for testing."""
    return MockQdrant()

@pytest.fixture
def sample_repository():
    """Create a sample repository for testing."""
    return create_test_repo(num_files=10)

@pytest.fixture
def cloud_api_client():
    """FastAPI test client in CLOUD mode."""
    os.environ["MODE"] = "CLOUD"
    return TestClient(app)

@pytest.fixture
def edge_worker():
    """Edge worker instance for testing."""
    os.environ["MODE"] = "EDGE"
    return EdgeWorker(device="cpu")  # Use CPU for tests
```

**Test Utilities** (`tests/utils.py`):
```python
def create_test_repo(num_files: int, language: str = "python") -> str:
    """Create a temporary test repository."""
    
def generate_valid_repo_urls(n: int) -> List[str]:
    """Generate valid repository URLs for property testing."""
    
def generate_invalid_repo_urls(n: int) -> List[str]:
    """Generate invalid repository URLs for property testing."""
    
def assert_embedding_shape(embeddings: torch.Tensor, expected_nodes: int):
    """Assert embedding tensor has correct shape."""
    
def assert_job_record_complete(record: dict):
    """Assert job record contains all required fields."""
```

### Continuous Integration

**GitHub Actions Workflow** (`.github/workflows/phase19-tests.yml`):
```yaml
name: Phase 19 Tests

on: [push, pull_request]

jobs:
  test-cloud-api:
    runs-on: ubuntu-latest
    env:
      MODE: CLOUD
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements-cloud.txt
      - name: Run unit tests
        run: pytest tests/test_cloud_api.py -v
      - name: Run property tests
        run: pytest tests/properties/test_queue_properties.py -v
  
  test-edge-worker:
    runs-on: ubuntu-latest
    env:
      MODE: EDGE
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements-edge.txt
      - name: Run unit tests (CPU only)
        run: pytest tests/test_edge_worker.py -v --device=cpu
      - name: Run property tests
        run: pytest tests/properties/ -v --device=cpu
```

### Test Execution Commands

```bash
# Run all tests
pytest tests/ -v

# Run only unit tests
pytest tests/test_*.py -v

# Run only property tests
pytest tests/properties/ -v --hypothesis-profile=ci

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific property test
pytest tests/properties/test_queue_properties.py::test_property_1 -v

# Run integration tests
pytest tests/integration/ -v

# Run performance tests
pytest tests/performance/ -v --benchmark-only
```

## Deployment Architecture

### Cloud Deployment (Render)

**Service Configuration**:
```yaml
# render.yaml
services:
  - type: web
    name: neo-alexandria-cloud-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements-cloud.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: MODE
        value: CLOUD
      - key: UPSTASH_REDIS_REST_URL
        sync: false
      - key: UPSTASH_REDIS_REST_TOKEN
        sync: false
      - key: NEON_DATABASE_URL
        sync: false
      - key: QDRANT_URL
        sync: false
      - key: QDRANT_API_KEY
        sync: false
    healthCheckPath: /health
```

**Resource Limits**:
- Memory: 512MB (Free Tier)
- CPU: Shared
- Disk: 1GB
- Bandwidth: 100GB/month

**Scaling Strategy**:
- Horizontal: Not available on Free Tier
- Vertical: Upgrade to Starter ($7/month) for 512MB guaranteed
- Auto-sleep: After 15 minutes of inactivity

### Edge Deployment (Local Laptop)

**System Requirements**:
- OS: Windows 10/11, Linux, or macOS
- CPU: Intel i9 or equivalent (8+ cores recommended)
- GPU: NVIDIA RTX 4070 or better (16GB VRAM)
- RAM: 16GB minimum, 32GB recommended
- Storage: 50GB free space for repositories and models
- Network: Stable internet connection for Redis/Qdrant

**Setup Script** (`setup_edge.sh`):
```bash
#!/bin/bash

# Install Python dependencies
pip install -r requirements-edge.txt

# Verify CUDA installation
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"

# Create .env.edge from template
cp .env.edge.template .env.edge
echo "Please edit .env.edge with your credentials"

# Test worker startup
python worker.py --test
```

**Systemd Service** (Linux) (`neo-alexandria-worker.service`):
```ini
[Unit]
Description=Neo Alexandria Edge Worker
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/neo-alexandria-2.0/backend
Environment="MODE=EDGE"
EnvironmentFile=/path/to/.env.edge
ExecStart=/usr/bin/python3 worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Windows Service** (using NSSM):
```powershell
# Install NSSM
choco install nssm

# Create service
nssm install NeoAlexandriaWorker "C:\Python310\python.exe" "C:\path\to\worker.py"
nssm set NeoAlexandriaWorker AppDirectory "C:\path\to\backend"
nssm set NeoAlexandriaWorker AppEnvironmentExtra MODE=EDGE
nssm start NeoAlexandriaWorker
```

### Infrastructure Setup Guide

**Step 1: Provision Neon Database**
```bash
# 1. Go to https://neon.tech
# 2. Create new project
# 3. Copy connection string
# 4. Add to .env.cloud and .env.edge:
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb
```

**Step 2: Provision Qdrant Cloud**
```bash
# 1. Go to https://cloud.qdrant.io
# 2. Create 1GB free cluster
# 3. Copy URL and API key
# 4. Add to .env.cloud and .env.edge:
QDRANT_URL=https://xxx.qdrant.io
QDRANT_API_KEY=your-api-key
```

**Step 3: Provision Upstash Redis**
```bash
# 1. Go to https://upstash.com
# 2. Create Redis database
# 3. Copy REST URL and token
# 4. Add to .env.cloud and .env.edge:
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-token
```

**Step 4: Deploy Cloud API**
```bash
# 1. Push code to GitHub
# 2. Connect Render to repository
# 3. Create Web Service
# 4. Set environment variables
# 5. Deploy
```

**Step 5: Start Edge Worker**
```bash
# 1. Clone repository locally
# 2. Create .env.edge with credentials
# 3. Install dependencies: pip install -r requirements-edge.txt
# 4. Run worker: python worker.py
```

### Monitoring and Observability

**Cloud API Monitoring**:
- Render built-in metrics (CPU, memory, requests)
- Custom health check endpoint: `/health`
- Log aggregation via Render dashboard
- Uptime monitoring via Render

**Edge Worker Monitoring**:
- Worker status via Redis: `GET worker_status`
- Job history via Redis: `LRANGE job_history 0 -1`
- GPU utilization: `nvidia-smi` command
- System logs: stdout/stderr or systemd journal

**Alerting**:
- Render email alerts for service downtime
- Custom alerts via Redis status monitoring
- GPU temperature monitoring (local)
- Disk space monitoring (local)

### Cost Analysis

**Monthly Costs**:
- Render Free Tier: $0
- Neon Free Tier: $0 (3GB storage, scales to zero)
- Qdrant Cloud Free: $0 (1GB cluster)
- Upstash Redis Free: $0 (10K commands/day)
- **Total Cloud Cost: $0/month**

**Local Costs**:
- Electricity for laptop: ~$10-20/month (varies by usage)
- Internet: Existing connection
- **Total Edge Cost: $10-20/month**

**Scaling Costs** (if needed):
- Render Starter: $7/month (512MB guaranteed)
- Neon Pro: $19/month (unlimited storage)
- Qdrant Cloud: $25/month (4GB cluster)
- Upstash Redis: $10/month (100K commands/day)
- **Total Scaled Cost: $61/month**

### Security Considerations

**API Security**:
- HTTPS only (enforced by Render)
- Input validation on all endpoints
- Rate limiting (future enhancement)
- API key authentication (future enhancement)

**Credential Management**:
- Environment variables for secrets
- No credentials in code or logs
- Separate .env files for cloud/edge
- .gitignore for .env files

**Network Security**:
- Upstash Redis uses HTTPS (no port forwarding needed)
- Qdrant Cloud uses HTTPS with API key
- Neon uses SSL/TLS for database connections
- No inbound ports required on edge worker

**Code Security**:
- Repository cloning in isolated temp directories
- Cleanup after processing
- No arbitrary code execution
- Sandboxed parsing with Tree-sitter

## Future Enhancements

### Phase 19.5: Multi-Worker Support
- Support multiple edge workers
- Load balancing across workers
- Worker registration and discovery
- Distributed task queue

### Phase 20: Advanced Graph Features
- Graph-based code search
- Dependency analysis and visualization
- Breaking change detection
- Code similarity search

### Phase 21: Hybrid Embeddings
- Combine structural and text embeddings
- Multi-modal search (structure + semantics)
- Weighted fusion strategies
- A/B testing framework

### Phase 22: Real-time Processing
- WebSocket support for live updates
- Streaming embeddings
- Progressive results
- Real-time status dashboard

### Phase 23: Enterprise Features
- Multi-tenancy support
- Team collaboration
- Access control and permissions
- Audit logging
- SLA monitoring
