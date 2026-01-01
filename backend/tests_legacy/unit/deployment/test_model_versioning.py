"""
Unit tests for model versioning system.

Tests cover:
- Version creation with valid and invalid formats
- Version listing
- Version loading
- Production promotion
- Version registry management
"""

import json
import pytest
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.deployment.model_versioning import ModelVersioning


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_model_dir(temp_dir):
    """Create a mock model directory with required files."""
    model_dir = temp_dir / "mock_model"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Create mock model files
    (model_dir / "pytorch_model.bin").write_text("mock model weights")
    (model_dir / "config.json").write_text('{"model_type": "distilbert"}')
    (model_dir / "tokenizer_config.json").write_text('{"do_lower_case": true}')
    (model_dir / "vocab.txt").write_text("mock vocab")
    
    # Create label map
    label_map = {
        "id_to_label": {"0": "cs.AI", "1": "cs.LG"},
        "label_to_id": {"cs.AI": 0, "cs.LG": 1}
    }
    with open(model_dir / "label_map.json", 'w') as f:
        json.dump(label_map, f)
    
    return model_dir


@pytest.fixture
def versioning(temp_dir):
    """Create a ModelVersioning instance with temporary directory."""
    return ModelVersioning(base_dir=str(temp_dir / "models"))


class TestModelVersioningInitialization:
    """Test ModelVersioning class initialization."""
    
    def test_initialization_creates_base_directory(self, temp_dir):
        """Test that initialization creates base directory."""
        base_dir = temp_dir / "models"
        versioning = ModelVersioning(base_dir=str(base_dir))
        
        assert base_dir.exists()
        assert versioning.base_dir == base_dir
    
    def test_initialization_creates_registry_file(self, temp_dir):
        """Test that initialization creates version registry file."""
        base_dir = temp_dir / "models"
        ModelVersioning(base_dir=str(base_dir))
        
        registry_file = base_dir / "version_registry.json"
        assert registry_file.exists()
        
        # Check registry structure
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        assert "versions" in registry
        assert "production_version" in registry
        assert "latest_version" in registry
        assert registry["versions"] == []
        assert registry["production_version"] is None
    
    def test_initialization_loads_existing_registry(self, temp_dir):
        """Test that initialization loads existing registry."""
        base_dir = temp_dir / "models"
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create existing registry
        registry_file = base_dir / "version_registry.json"
        existing_registry = {
            "versions": [{"version": "v1.0.0", "path": "test"}],
            "production_version": "v1.0.0",
            "latest_version": "v1.0.0"
        }
        with open(registry_file, 'w') as f:
            json.dump(existing_registry, f)
        
        # Initialize versioning
        versioning = ModelVersioning(base_dir=str(base_dir))
        
        assert len(versioning.registry["versions"]) == 1
        assert versioning.registry["production_version"] == "v1.0.0"


class TestVersionCreation:
    """Test version creation functionality."""
    
    def test_create_version_with_valid_format(self, versioning, mock_model_dir):
        """Test creating a version with valid format."""
        version = "v1.0.0"
        metadata = {
            "model_name": "distilbert-base-uncased",
            "dataset": {"source": "arXiv", "size": 10000},
            "hyperparameters": {"epochs": 3, "batch_size": 16},
            "metrics": {"accuracy": 0.91, "f1": 0.90}
        }
        
        version_path = versioning.create_version(
            model_path=str(mock_model_dir),
            version=version,
            metadata=metadata
        )
        
        # Check version directory created
        assert Path(version_path).exists()
        assert "arxiv_v1.0.0" in version_path
        
        # Check metadata file created
        metadata_file = Path(version_path) / "metadata.json"
        assert metadata_file.exists()
        
        with open(metadata_file, 'r') as f:
            saved_metadata = json.load(f)
        
        assert saved_metadata["version"] == version
        assert "created_at" in saved_metadata
        assert saved_metadata["model_name"] == "distilbert-base-uncased"
        
        # Check registry updated
        assert len(versioning.registry["versions"]) == 1
        assert versioning.registry["latest_version"] == version
    
    def test_create_version_rejects_invalid_format(self, versioning, mock_model_dir):
        """Test that invalid version formats are rejected."""
        invalid_versions = [
            "1.0.0",      # Missing 'v' prefix
            "v1.0",       # Missing patch version
            "v1",         # Missing minor and patch
            "version1",   # Invalid format
            "v1.0.0.0",   # Too many parts
        ]
        
        for invalid_version in invalid_versions:
            with pytest.raises(ValueError, match="Invalid version format"):
                versioning.create_version(
                    model_path=str(mock_model_dir),
                    version=invalid_version,
                    metadata={}
                )
    
    def test_create_version_rejects_duplicate_versions(self, versioning, mock_model_dir):
        """Test that duplicate versions are rejected."""
        version = "v1.0.0"
        metadata = {"model_name": "test"}
        
        # Create first version
        versioning.create_version(
            model_path=str(mock_model_dir),
            version=version,
            metadata=metadata
        )
        
        # Try to create duplicate
        with pytest.raises(ValueError, match="already exists"):
            versioning.create_version(
                model_path=str(mock_model_dir),
                version=version,
                metadata=metadata
            )
    
    def test_create_version_copies_model_files(self, versioning, mock_model_dir):
        """Test that model files are copied to version directory."""
        version = "v1.0.0"
        
        version_path = versioning.create_version(
            model_path=str(mock_model_dir),
            version=version,
            metadata={}
        )
        
        version_dir = Path(version_path)
        
        # Check all model files copied
        assert (version_dir / "pytorch_model.bin").exists()
        assert (version_dir / "config.json").exists()
        assert (version_dir / "tokenizer_config.json").exists()
        assert (version_dir / "vocab.txt").exists()
        assert (version_dir / "label_map.json").exists()
    
    def test_create_version_calculates_model_size(self, versioning, mock_model_dir):
        """Test that model size is calculated and stored."""
        version = "v1.0.0"
        
        # Add some content to make files larger
        (mock_model_dir / "pytorch_model.bin").write_text("x" * 1024 * 100)  # 100KB
        
        version_path = versioning.create_version(
            model_path=str(mock_model_dir),
            version=version,
            metadata={}
        )
        
        metadata_file = Path(version_path) / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        assert "model_size_mb" in metadata
        assert metadata["model_size_mb"] > 0


class TestVersionListing:
    """Test version listing functionality."""
    
    def test_list_versions_returns_all_versions(self, versioning, mock_model_dir):
        """Test that list_versions returns all versions."""
        # Create multiple versions
        versions = ["v1.0.0", "v1.1.0", "v2.0.0"]
        for version in versions:
            versioning.create_version(
                model_path=str(mock_model_dir),
                version=version,
                metadata={}
            )
        
        # List versions
        listed_versions = versioning.list_versions()
        
        assert len(listed_versions) == 3
        listed_version_strings = [v["version"] for v in listed_versions]
        assert set(listed_version_strings) == set(versions)
    
    def test_list_versions_returns_empty_for_new_registry(self, versioning):
        """Test that list_versions returns empty list for new registry."""
        versions = versioning.list_versions()
        assert versions == []


class TestVersionLoading:
    """Test version loading functionality."""
    
    def test_load_version_returns_model_and_metadata(
        self,
        versioning,
        mock_model_dir
    ):
        """Test that load_version returns model and metadata."""
        # Create version
        version = "v1.0.0"
        metadata = {"model_name": "test", "accuracy": 0.91}
        versioning.create_version(
            model_path=str(mock_model_dir),
            version=version,
            metadata=metadata
        )
        
        # Mock transformers imports inside the load_version method
        with patch('transformers.AutoModelForSequenceClassification') as mock_model_class, \
             patch('transformers.AutoTokenizer') as mock_tokenizer_class:
            
            mock_model = MagicMock()
            mock_tokenizer = MagicMock()
            mock_model_class.from_pretrained.return_value = mock_model
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
            
            # Load version
            model_data, loaded_metadata = versioning.load_version(version)
            
            assert model_data is not None
            assert 'model' in model_data
            assert 'tokenizer' in model_data
            assert loaded_metadata["version"] == version
            assert loaded_metadata["accuracy"] == 0.91
    
    def test_load_version_raises_error_for_missing_version(self, versioning):
        """Test that load_version raises error for missing version."""
        with pytest.raises(ValueError, match="not found"):
            versioning.load_version("v99.99.99")


class TestProductionPromotion:
    """Test production promotion functionality."""
    
    def test_promote_to_production_updates_registry(self, versioning, mock_model_dir):
        """Test that promotion updates registry correctly."""
        # Create version
        version = "v1.0.0"
        versioning.create_version(
            model_path=str(mock_model_dir),
            version=version,
            metadata={}
        )
        
        # Promote to production
        versioning.promote_to_production(version)
        
        # Check registry updated
        assert versioning.registry["production_version"] == version
        
        # Check version status updated
        version_entry = next(
            v for v in versioning.registry["versions"]
            if v["version"] == version
        )
        assert version_entry["status"] == "production"
    
    def test_promote_to_production_archives_previous(self, versioning, mock_model_dir):
        """Test that promotion archives previous production version."""
        # Create two versions
        v1 = "v1.0.0"
        v2 = "v1.1.0"
        
        versioning.create_version(str(mock_model_dir), v1, {})
        versioning.create_version(str(mock_model_dir), v2, {})
        
        # Promote v1
        versioning.promote_to_production(v1)
        
        # Promote v2
        versioning.promote_to_production(v2)
        
        # Check v1 is archived
        v1_entry = next(
            v for v in versioning.registry["versions"]
            if v["version"] == v1
        )
        assert v1_entry["status"] == "archived"
        
        # Check v2 is production
        assert versioning.registry["production_version"] == v2
    
    def test_promote_to_production_raises_error_for_missing_version(self, versioning):
        """Test that promotion raises error for missing version."""
        with pytest.raises(ValueError, match="not found"):
            versioning.promote_to_production("v99.99.99")


class TestVersionComparison:
    """Test version comparison functionality."""
    
    def test_compare_versions_returns_metrics(
        self,
        versioning,
        mock_model_dir
    ):
        """Test that compare_versions returns comparison metrics."""
        # Create two versions
        v1 = "v1.0.0"
        v2 = "v1.1.0"
        
        versioning.create_version(str(mock_model_dir), v1, {})
        versioning.create_version(str(mock_model_dir), v2, {})
        
        # Test data
        test_data = [
            {"text": "Machine learning paper", "label": "cs.AI"},
            {"text": "Deep learning research", "label": "cs.LG"}
        ]
        
        # Mock all the imports and model behavior
        with patch('transformers.AutoModelForSequenceClassification') as mock_model_class, \
             patch('transformers.AutoTokenizer') as mock_tokenizer_class, \
             patch('torch.cuda.is_available', return_value=False), \
             patch('torch.no_grad'), \
             patch('torch.argmax') as mock_argmax:
            
            # Setup model mocks
            mock_model1 = MagicMock()
            mock_model2 = MagicMock()
            mock_tokenizer = MagicMock()
            
            # Mock tokenizer output
            mock_tokenizer.return_value = {
                'input_ids': MagicMock(),
                'attention_mask': MagicMock()
            }
            
            # Mock model outputs with logits
            mock_output = MagicMock()
            mock_output.logits = MagicMock()
            mock_model1.return_value = mock_output
            mock_model2.return_value = mock_output
            
            # Mock argmax to return predictions
            mock_argmax.return_value.item.return_value = 0
            
            # Setup from_pretrained to return different models
            mock_model_class.from_pretrained.side_effect = [mock_model1, mock_model2]
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
            
            # Compare versions
            comparison = versioning.compare_versions(v1, v2, test_data)
            
            # Check comparison structure
            assert "version1" in comparison
            assert "version2" in comparison
            assert "version1_metrics" in comparison
            assert "version2_metrics" in comparison
            assert "improvement" in comparison
            assert "recommendation" in comparison
            
            # Check metrics structure
            assert "accuracy" in comparison["version1_metrics"]
            assert "f1_score" in comparison["version1_metrics"]
            assert "latency_p95_ms" in comparison["version1_metrics"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
