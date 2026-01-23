# Phase 19: Hybrid Edge-Cloud Orchestration & Neural Graph Learning

## Status
🚧 **Draft** - Specification complete, ready for implementation

## Overview

This specification defines a hybrid edge-cloud architecture that splits Neo Alexandria's backend into two complementary components:

1. **Cloud API (Control Plane)**: Lightweight FastAPI service on Render Free Tier that handles user requests and dispatches tasks
2. **Edge Worker (Compute Plane)**: GPU-accelerated Python worker on local hardware that performs heavy ML operations

The system implements PyTorch Geometric's Node2Vec algorithm to generate structural embeddings of code repositories based on dependency graphs, enabling code search by structural relationships rather than just text content.

## Key Features

- **Zero-Cost Cloud Infrastructure**: Runs on free tiers of Render, Neon, Qdrant, and Upstash
- **GPU-Accelerated Processing**: Leverages local RTX 4070 for graph neural network training
- **Asynchronous Task Queue**: HTTP-based Redis queue bridges cloud and edge
- **Graph Representation Learning**: Node2Vec embeddings capture code structure
- **Multi-Language Support**: Parses Python, JavaScript, TypeScript, Java, and Go
- **Fault Tolerant**: Retry logic, error recovery, and graceful degradation
- **Comprehensive Testing**: 15 property-based tests + extensive unit tests

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Cloud Layer (Render Free Tier - 512MB RAM)             │
│                                                         │
│  User → FastAPI → Upstash Redis Queue                  │
│           ↓              ↓                              │
│      Neon Postgres   Qdrant Cloud                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Edge Layer (Local Laptop - i9/RTX 4070/16GB)           │
│                                                         │
│  Worker → Clone Repo → Parse AST → Build Graph         │
│            ↓              ↓            ↓                │
│        Git Repo    Tree-sitter   PyTorch Geometric     │
│                                      ↓                  │
│                              Node2Vec Training          │
│                                      ↓                  │
│                          Upload to Qdrant Cloud         │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

### Cloud API
- FastAPI (web framework)
- Upstash Redis (task queue)
- Neon Postgres (metadata)
- Qdrant Cloud (vector search)
- Render (hosting)

### Edge Worker
- PyTorch + PyTorch Geometric (graph neural networks)
- Tree-sitter (code parsing)
- GitPython (repository cloning)
- CUDA (GPU acceleration)

## Cost Analysis

**Monthly Costs**:
- Render Free Tier: $0
- Neon Free Tier: $0 (3GB storage)
- Qdrant Cloud Free: $0 (1GB cluster)
- Upstash Redis Free: $0 (10K commands/day)
- Local electricity: ~$10-20/month

**Total: $10-20/month** (just electricity for local GPU)

## Documents

- **[requirements.md](./requirements.md)**: 12 requirements with EARS patterns covering infrastructure, processing, ML, security, and deployment
- **[design.md](./design.md)**: Complete technical design with architecture diagrams, component specifications, 15 correctness properties, error handling, and testing strategy
- **[tasks.md](./tasks.md)**: 13 main tasks with 40+ sub-tasks for incremental implementation

## Implementation Timeline

**Estimated Duration**: 8-13 days

1. **Days 1-3**: Core services (configuration, repository parser, neural graph service)
2. **Days 4-6**: API and worker (cloud endpoints, edge worker, job processing)
3. **Days 7-8**: Security and deployment (validation, credentials, configurations)
4. **Days 9-11**: Testing (integration, performance, stress tests)
5. **Days 12-13**: Documentation and final verification

## Success Criteria

- [ ] All unit tests pass
- [ ] All property tests pass (100+ iterations each)
- [ ] Integration tests pass end-to-end
- [ ] Cloud API deploys successfully to Render
- [ ] Edge worker runs successfully on local GPU
- [ ] Complete workflow: submit URL → process → embeddings in Qdrant
- [ ] Documentation complete and accurate
- [ ] Cost remains at $0/month for cloud infrastructure

## Getting Started

### Prerequisites

**Cloud**:
- GitHub account (for Render deployment)
- Neon account (serverless Postgres)
- Qdrant Cloud account (vector database)
- Upstash account (Redis queue)

**Edge**:
- Python 3.10+
- NVIDIA GPU with CUDA support (RTX 4070 or better)
- 16GB RAM minimum
- 50GB free disk space

### Quick Start

1. **Provision Infrastructure**:
   ```bash
   # Follow infrastructure setup guide in design.md
   # Get credentials for Neon, Qdrant, Upstash
   ```

2. **Deploy Cloud API**:
   ```bash
   # Push to GitHub
   # Connect Render to repository
   # Set environment variables
   # Deploy
   ```

3. **Start Edge Worker**:
   ```bash
   # Clone repository
   # Create .env.edge with credentials
   pip install -r requirements-edge.txt
   python worker.py
   ```

4. **Submit Test Job**:
   ```bash
   curl -X POST https://your-app.onrender.com/api/v1/ingestion/ingest/github.com/user/repo
   ```

## Related Phases

- **Phase 18**: Code Intelligence (AST parsing foundation)
- **Phase 17.5**: Advanced RAG Architecture (embedding infrastructure)
- **Phase 20**: Advanced Graph Features (future enhancements)

## Notes

- This phase introduces a fundamentally new architecture pattern for Neo Alexandria
- The hybrid approach enables both cost efficiency and compute power
- Graph embeddings complement existing text embeddings for multi-modal search
- The system is designed to scale horizontally (multiple edge workers) in the future

## Questions?

- Check the [design document](./design.md) for detailed technical specifications
- Check the [requirements document](./requirements.md) for acceptance criteria
- Check the [tasks document](./tasks.md) for implementation steps

---

**Created**: January 20, 2026
**Status**: Ready for implementation
**Estimated Effort**: 8-13 days
**Priority**: High (enables GPU-accelerated code analysis)
