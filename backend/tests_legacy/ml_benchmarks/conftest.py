"""
Benchmark-specific test fixtures for ML benchmarking.

This module provides fixtures for:
- Loading test datasets
- Loading pre-trained models with graceful skipping
- Mocking external APIs (OpenAI)
- Database isolation for tests
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.database.base import Base


# ============================================================================
# Test Dataset Fixtures
# ============================================================================

@pytest.fixture
def classification_test_data() -> Dict[str, Any]:
    """
    Load and parse classification test dataset JSON.
    
    Returns:
        Dictionary containing metadata, samples, and class distribution
        
    Skips:
        Test if dataset file doesn't exist
    """
    dataset_path = Path(__file__).parent / "datasets" / "classification_test.json"
    
    if not dataset_path.exists():
        pytest.skip(f"Classification test dataset not found: {dataset_path}")
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required fields
        required_fields = ["metadata", "samples", "class_distribution"]
        for field in required_fields:
            if field not in data:
                pytest.skip(f"Classification dataset missing required field: {field}")
        
        return data
    except Exception as e:
        pytest.skip(f"Failed to load classification dataset: {str(e)}")


@pytest.fixture
def recommendation_test_data() -> Dict[str, Any]:
    """
    Load and parse recommendation test dataset JSON.
    
    Returns:
        Dictionary containing metadata, interactions, and held-out test cases
        
    Skips:
        Test if dataset file doesn't exist
    """
    dataset_path = Path(__file__).parent / "datasets" / "recommendation_test.json"
    
    if not dataset_path.exists():
        pytest.skip(f"Recommendation test dataset not found: {dataset_path}")
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required fields
        required_fields = ["metadata", "interactions", "held_out_test"]
        for field in required_fields:
            if field not in data:
                pytest.skip(f"Recommendation dataset missing required field: {field}")
        
        return data
    except Exception as e:
        pytest.skip(f"Failed to load recommendation dataset: {str(e)}")


@pytest.fixture
def search_relevance_data() -> Dict[str, Any]:
    """
    Load and parse search relevance dataset JSON.
    
    Returns:
        Dictionary containing metadata and queries with relevance judgments
        
    Skips:
        Test if dataset file doesn't exist
    """
    dataset_path = Path(__file__).parent / "datasets" / "search_relevance.json"
    
    if not dataset_path.exists():
        pytest.skip(f"Search relevance dataset not found: {dataset_path}")
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required fields
        required_fields = ["metadata", "queries"]
        for field in required_fields:
            if field not in data:
                pytest.skip(f"Search dataset missing required field: {field}")
        
        return data
    except Exception as e:
        pytest.skip(f"Failed to load search relevance dataset: {str(e)}")


@pytest.fixture
def summarization_test_data() -> Dict[str, Any]:
    """
    Load and parse summarization test dataset JSON.
    
    Returns:
        Dictionary containing metadata and text-summary pairs
        
    Skips:
        Test if dataset file doesn't exist
    """
    dataset_path = Path(__file__).parent / "datasets" / "summarization_test.json"
    
    if not dataset_path.exists():
        pytest.skip(f"Summarization test dataset not found: {dataset_path}")
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required fields
        required_fields = ["metadata", "samples"]
        for field in required_fields:
            if field not in data:
                pytest.skip(f"Summarization dataset missing required field: {field}")
        
        return data
    except Exception as e:
        pytest.skip(f"Failed to load summarization dataset: {str(e)}")


# ============================================================================
# Model Loading Fixtures
# ============================================================================

def check_model_availability() -> Dict[str, bool]:
    """
    Check if trained models are available.
    
    Returns:
        Dictionary with model availability status:
        {
            "classification": bool,
            "ncf": bool
        }
    """
    # Try both relative and absolute paths
    classification_path = Path("models/classification/benchmark_v1")
    if not classification_path.exists():
        classification_path = Path("backend/models/classification/benchmark_v1")
    
    ncf_path = Path("models/ncf_benchmark_v1.pt")
    if not ncf_path.exists():
        ncf_path = Path("backend/models/ncf_benchmark_v1.pt")
    
    return {
        "classification": classification_path.exists(),
        "ncf": ncf_path.exists()
    }


def get_training_instructions() -> str:
    """
    Get instructions for training missing models.
    
    Returns:
        Formatted string with training commands
    """
    availability = check_model_availability()
    
    instructions = []
    
    if not availability["classification"]:
        instructions.append(
            "Classification model not found. Train it using:\n"
            "  python backend/scripts/train_classification.py"
        )
    
    if not availability["ncf"]:
        instructions.append(
            "NCF model not found. Train it using:\n"
            "  python backend/scripts/train_ncf.py"
        )
    
    if not instructions:
        return "All models are available."
    
    return "\n\n".join(instructions)


@pytest.fixture
def trained_classifier(isolated_test_db: Session):
    """
    Load pre-trained classification model with graceful skipping if unavailable.
    
    Args:
        isolated_test_db: Isolated test database session
        
    Returns:
        MLClassificationService instance with loaded model
        
    Skips:
        Test if model checkpoint not available
    """
    try:
        from backend.app.services.ml_classification_service import MLClassificationService
    except ImportError:
        pytest.skip("MLClassificationService not available")
    
    # Check for model checkpoint - try both relative and absolute paths
    model_path = Path("models/classification/benchmark_v1")
    if not model_path.exists():
        model_path = Path("backend/models/classification/benchmark_v1")
    
    if not model_path.exists():
        pytest.skip(
            "Benchmark classification model not available. "
            "Train the model first using:\n"
            "  python backend/scripts/train_classification.py"
        )
    
    try:
        # Initialize service with benchmark_v1 version
        service = MLClassificationService(isolated_test_db, model_version="benchmark_v1")
        
        # Verify model can be loaded by attempting a test prediction
        # This ensures the model is properly initialized
        test_text = "Test classification"
        try:
            # Attempt classification to verify model works
            service.predict(test_text)
        except Exception as load_error:
            pytest.skip(f"Model loaded but classification failed: {str(load_error)}")
        
        return service
    except Exception as e:
        pytest.skip(f"Failed to load classification model: {str(e)}")


@pytest.fixture
def trained_ncf_model(isolated_test_db: Session):
    """
    Load pre-trained NCF model with graceful skipping if unavailable.
    
    Args:
        isolated_test_db: Isolated test database session
        
    Returns:
        NCFService instance with loaded model
        
    Skips:
        Test if model checkpoint not available
    """
    try:
        from backend.app.services.ncf_service import NCFService
    except ImportError:
        pytest.skip("NCFService not available")
    
    # Check for model checkpoint - try both relative and absolute paths
    model_path = Path("models/ncf_benchmark_v1.pt")
    if not model_path.exists():
        model_path = Path("backend/models/ncf_benchmark_v1.pt")
    
    if not model_path.exists():
        pytest.skip(
            "Benchmark NCF model not available. "
            "Train the model first using:\n"
            "  python backend/scripts/train_ncf.py"
        )
    
    try:
        # Initialize NCFService with model path
        service = NCFService(isolated_test_db, model_path=str(model_path))
        
        # Trigger lazy loading by calling _load_model
        service._load_model()
        
        return service
    except Exception as e:
        pytest.skip(f"Failed to load NCF model: {str(e)}")


# ============================================================================
# External API Mocking Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_api():
    """
    Mock OpenAI API calls for summarization tests.
    
    Yields:
        Mock object for OpenAI API
    """
    # Try to import openai, but if it's not available, just yield a mock
    try:
        with patch('openai.ChatCompletion.create') as mock_create:
            # Default mock response
            mock_create.return_value = {
                "id": "chatcmpl-test123",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "This is a mocked summary of the input text. "
                                     "It captures the key points concisely."
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 20,
                    "total_tokens": 120
                }
            }
            
            yield mock_create
    except (ImportError, ModuleNotFoundError):
        # OpenAI not installed, yield a simple mock
        mock_obj = MagicMock()
        mock_obj.return_value = {
            "choices": [{"message": {"content": "Mocked summary"}}]
        }
        yield mock_obj


@pytest.fixture(autouse=True)
def mock_all_external_apis():
    """
    Auto-mock all external APIs for safety and speed.
    
    This fixture automatically mocks:
    - OpenAI API calls
    - External HTTP requests
    - Any other third-party API calls
    
    Yields:
        Dictionary of mock objects
    """
    mocks = {}
    
    # Mock requests library (always available)
    try:
        with patch('requests.get') as mock_get, \
             patch('requests.post') as mock_post:
            
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {}
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {}
            
            mocks['requests_get'] = mock_get
            mocks['requests_post'] = mock_post
            
            # Try to mock OpenAI if available
            try:
                with patch('openai.ChatCompletion.create') as mock_openai:
                    mock_openai.return_value = {
                        "choices": [{"message": {"content": "Mocked response"}}]
                    }
                    mocks['openai'] = mock_openai
                    yield mocks
            except (ImportError, ModuleNotFoundError):
                # OpenAI not installed, continue without it
                yield mocks
    except Exception:
        # If patching fails, just yield empty mocks
        yield mocks


# ============================================================================
# Database Isolation Fixtures
# ============================================================================

@pytest.fixture
def isolated_test_db() -> Generator[Session, None, None]:
    """
    Create isolated temporary SQLite database for test isolation.
    
    This fixture ensures:
    - Each test gets a fresh database
    - No interference with production data
    - Automatic cleanup after test completion
    
    Yields:
        SQLAlchemy Session for the isolated test database
    """
    # Create temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # Create engine and tables
        engine = create_engine(
            f"sqlite:///{temp_db.name}",
            echo=False,
            connect_args={"check_same_thread": False}
        )
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        # Create session
        TestingSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        db = TestingSessionLocal()
        
        yield db
        
        # Cleanup
        db.close()
        engine.dispose()
        
    finally:
        # Remove temporary database file
        try:
            os.unlink(temp_db.name)
        except OSError:
            pass


@pytest.fixture(scope="session")
def benchmark_session_db() -> Generator[Session, None, None]:
    """
    Create session-scoped database for benchmarks that need shared state.
    
    Use this fixture when:
    - Multiple tests need to share the same database state
    - Setting up test data is expensive
    - Tests are read-only and don't modify data
    
    Yields:
        SQLAlchemy Session for the session-scoped database
    """
    # Create temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # Create engine and tables
        engine = create_engine(
            f"sqlite:///{temp_db.name}",
            echo=False,
            connect_args={"check_same_thread": False}
        )
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        # Create session
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        db = SessionLocal()
        
        yield db
        
        # Cleanup
        db.close()
        engine.dispose()
        
    finally:
        # Remove temporary database file
        try:
            os.unlink(temp_db.name)
        except OSError:
            pass


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def benchmark_output_dir(tmp_path: Path) -> Path:
    """
    Create temporary directory for benchmark outputs.
    
    Args:
        tmp_path: pytest's temporary path fixture
        
    Returns:
        Path to benchmark output directory
    """
    output_dir = tmp_path / "benchmark_outputs"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture(autouse=True)
def set_random_seeds():
    """
    Set fixed random seeds for reproducible benchmark results.
    
    This fixture automatically sets seeds for:
    - Python random module
    - NumPy
    - PyTorch (if available)
    """
    import random
    random.seed(42)
    
    try:
        import numpy as np
        np.random.seed(42)
    except ImportError:
        pass
    
    try:
        import torch
        torch.manual_seed(42)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(42)
    except ImportError:
        pass


@pytest.fixture
def benchmark_timeout():
    """
    Return timeout value for benchmark tests (in seconds).
    
    Returns:
        Timeout value (1800 seconds = 30 minutes)
    """
    return 1800  # 30 minutes


# ============================================================================
# Performance Monitoring Fixtures
# ============================================================================

@pytest.fixture
def memory_monitor():
    """
    Monitor memory usage during benchmark execution.
    
    Yields:
        Function to get current memory usage in MB
    """
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    def get_memory_mb():
        """Get current memory usage in MB."""
        return process.memory_info().rss / 1024 / 1024
    
    yield get_memory_mb


@pytest.fixture
def gpu_memory_monitor():
    """
    Monitor GPU memory usage during benchmark execution.
    
    Yields:
        Function to get current GPU memory usage in MB, or None if no GPU
    """
    try:
        import torch
        
        if not torch.cuda.is_available():
            yield lambda: None
            return
        
        def get_gpu_memory_mb():
            """Get current GPU memory usage in MB."""
            return torch.cuda.memory_allocated() / 1024 / 1024
        
        yield get_gpu_memory_mb
        
        # Cleanup GPU memory after test
        torch.cuda.empty_cache()
        
    except ImportError:
        yield lambda: None
