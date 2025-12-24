# Development Setup Guide

Installation and environment configuration for Neo Alexandria 2.0.

## Prerequisites

- Python 3.8 or higher
- Git
- SQLite (included with Python)
- 4GB RAM minimum (8GB recommended for AI features)
- 2GB free disk space

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Database Configuration
DATABASE_URL=sqlite:///backend.db
TEST_DATABASE_URL=sqlite:///:memory:

# AI Model Configuration
EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1
SUMMARIZER_MODEL=facebook/bart-large-cnn
TAGGER_MODEL=facebook/bart-large-mnli

# Search Configuration
DEFAULT_HYBRID_SEARCH_WEIGHT=0.5
EMBEDDING_CACHE_SIZE=1000

# Graph Configuration
GRAPH_WEIGHT_VECTOR=0.6
GRAPH_WEIGHT_TAGS=0.3
GRAPH_WEIGHT_CLASSIFICATION=0.1

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Start Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## Verify Installation

### Check API Documentation

Open in browser:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Test Health Endpoint

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2024-01-01T10:00:00Z"}
```

### Run Tests

```bash
pytest tests/ -v
```

## Database Configuration

### SQLite (Default)

No additional setup required. Database file created automatically.

```bash
DATABASE_URL=sqlite:///backend.db
```

### PostgreSQL (Production)

1. Install PostgreSQL 15+
2. Create database:
```bash
createdb neo_alexandria
```
3. Update `.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/neo_alexandria
```
4. Run migrations:
```bash
alembic upgrade head
```

## AI Model Setup

Models are downloaded automatically on first use. To pre-download:

```python
from transformers import AutoModel, AutoTokenizer

# Embedding model
AutoModel.from_pretrained("nomic-ai/nomic-embed-text-v1")
AutoTokenizer.from_pretrained("nomic-ai/nomic-embed-text-v1")

# Summarization model
AutoModel.from_pretrained("facebook/bart-large-cnn")
AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- Black Formatter
- isort

Settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

### PyCharm

1. Set interpreter to `.venv/bin/python`
2. Enable Black formatter
3. Configure pytest as test runner

## Common Issues

### Import Errors

Ensure virtual environment is activated:
```bash
source .venv/bin/activate
which python  # Should show .venv path
```

### Database Locked (SQLite)

SQLite doesn't support concurrent writes. For development:
- Use single process
- Or switch to PostgreSQL

### Model Download Fails

Check internet connection and disk space. Models require ~2GB.

### Memory Errors

AI models require significant RAM. Options:
- Increase system RAM to 8GB+
- Use smaller models
- Disable AI features for testing

## Next Steps

- [Development Workflows](workflows.md) - Common tasks
- [Testing Guide](testing.md) - Running tests
- [API Documentation](../api/) - API reference

## Related Documentation

- [Architecture Overview](../architecture/overview.md)
- [Database Configuration](../architecture/database.md)
- [Troubleshooting](troubleshooting.md)
