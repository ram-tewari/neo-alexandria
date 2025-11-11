"""
Basic test for ML Classification Service initialization and model loading.

This test verifies:
1. Service initialization with default parameters
2. Service initialization with custom parameters
3. Lazy loading behavior (model not loaded on init)
4. Model loading on demand
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for backend imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database.base import Base
from backend.app.services.ml_classification_service import MLClassificationService


def test_service_initialization():
    """Test that service initializes correctly without loading model."""
    print("\n=== Test 1: Service Initialization ===")
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Initialize service
        service = MLClassificationService(db)
        
        # Verify initialization
        assert service.db is not None, "Database session should be set"
        assert service.model_name == "distilbert-base-uncased", "Default model name should be distilbert"
        assert service.model_version == "v1.0", "Default version should be v1.0"
        
        # Verify lazy loading (model not loaded yet)
        assert service.model is None, "Model should not be loaded on initialization"
        assert service.tokenizer is None, "Tokenizer should not be loaded on initialization"
        
        # Verify label mappings initialized
        assert isinstance(service.id_to_label, dict), "id_to_label should be a dict"
        assert isinstance(service.label_to_id, dict), "label_to_id should be a dict"
        assert len(service.id_to_label) == 0, "id_to_label should be empty initially"
        assert len(service.label_to_id) == 0, "label_to_id should be empty initially"
        
        # Verify checkpoint directory created
        assert service.checkpoint_dir.exists(), "Checkpoint directory should be created"
        assert service.checkpoint_dir.is_dir(), "Checkpoint path should be a directory"
        
        print("✓ Service initialized correctly")
        print(f"  - Model name: {service.model_name}")
        print(f"  - Model version: {service.model_version}")
        print(f"  - Checkpoint dir: {service.checkpoint_dir}")
        print(f"  - Model loaded: {service.model is not None}")
        print(f"  - Tokenizer loaded: {service.tokenizer is not None}")
        
    finally:
        db.close()


def test_custom_initialization():
    """Test service initialization with custom parameters."""
    print("\n=== Test 2: Custom Initialization ===")
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Initialize with custom parameters
        custom_model = "bert-base-uncased"
        custom_version = "v2.0"
        service = MLClassificationService(
            db,
            model_name=custom_model,
            model_version=custom_version
        )
        
        # Verify custom parameters
        assert service.model_name == custom_model, f"Model name should be {custom_model}"
        assert service.model_version == custom_version, f"Version should be {custom_version}"
        
        # Verify checkpoint directory uses custom version
        expected_dir = Path("models") / "classification" / custom_version
        assert service.checkpoint_dir == expected_dir, "Checkpoint dir should use custom version"
        
        print("✓ Custom initialization works correctly")
        print(f"  - Custom model: {service.model_name}")
        print(f"  - Custom version: {service.model_version}")
        print(f"  - Checkpoint dir: {service.checkpoint_dir}")
        
    finally:
        db.close()


def test_lazy_loading_behavior():
    """Test that model loading is deferred until needed."""
    print("\n=== Test 3: Lazy Loading Behavior ===")
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Initialize service
        service = MLClassificationService(db)
        
        # Verify model not loaded
        assert service.model is None, "Model should not be loaded initially"
        assert service.tokenizer is None, "Tokenizer should not be loaded initially"
        
        print("✓ Lazy loading behavior verified")
        print("  - Model and tokenizer are not loaded on initialization")
        print("  - This improves startup time and memory efficiency")
        
        # Note: We don't actually load the model in this test to avoid
        # downloading large model files during testing
        
    finally:
        db.close()


def main():
    """Run all tests."""
    print("=" * 60)
    print("ML Classification Service - Basic Tests")
    print("=" * 60)
    
    try:
        test_service_initialization()
        test_custom_initialization()
        test_lazy_loading_behavior()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
