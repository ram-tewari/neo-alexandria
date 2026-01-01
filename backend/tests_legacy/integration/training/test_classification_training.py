"""
Integration tests for classification model training pipeline.

These tests verify the end-to-end training workflow including:
- Dataset loading and label mapping
- Model training with small dataset
- Checkpoint saving and loading
- Model evaluation
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path

from backend.scripts.training.train_classification import (
    ClassificationTrainer,
    ArxivClassificationDataset
)


@pytest.fixture
def small_dataset():
    """Create a small synthetic dataset for testing."""
    # Create 100 samples across 3 classes
    samples = []
    categories = ["cs.AI", "cs.LG", "cs.CV"]
    
    for i in range(100):
        category = categories[i % 3]
        samples.append({
            "text": f"This is a test paper about {category} with some content. " * 10,
            "label": category,
            "arxiv_id": f"2301.{i:05d}",
            "title": f"Test Paper {i}",
            "authors": ["Test Author"],
            "published": "2023-01-01T00:00:00"
        })
    
    return samples


@pytest.fixture
def temp_data_dir(small_dataset):
    """Create temporary directory with train/val/test splits."""
    temp_dir = tempfile.mkdtemp()
    data_dir = Path(temp_dir) / "splits"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Split dataset: 70 train, 15 val, 15 test
    train_samples = small_dataset[:70]
    val_samples = small_dataset[70:85]
    test_samples = small_dataset[85:100]
    
    # Save splits
    with open(data_dir / "train.json", 'w') as f:
        json.dump(train_samples, f)
    with open(data_dir / "val.json", 'w') as f:
        json.dump(val_samples, f)
    with open(data_dir / "test.json", 'w') as f:
        json.dump(test_samples, f)
    
    yield str(data_dir)
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for model output."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir)


class TestClassificationTrainer:
    """Test suite for ClassificationTrainer."""
    
    def test_trainer_initialization(self, temp_output_dir):
        """Test that trainer initializes correctly."""
        trainer = ClassificationTrainer(
            model_name="distilbert-base-uncased",
            output_dir=temp_output_dir
        )
        
        assert trainer.model_name == "distilbert-base-uncased"
        assert trainer.checkpoint_dir.exists()
        assert trainer.tokenizer is None  # Lazy loading
        assert trainer.model is None  # Lazy loading
        assert len(trainer.label_to_id) == 0
        assert len(trainer.id_to_label) == 0
    
    def test_dataset_loading(self, temp_data_dir, temp_output_dir):
        """Test dataset loading and label mapping."""
        trainer = ClassificationTrainer(output_dir=temp_output_dir)
        
        train_samples, val_samples, test_samples = trainer.load_datasets(temp_data_dir)
        
        # Check sample counts
        assert len(train_samples) == 70
        assert len(val_samples) == 15
        assert len(test_samples) == 15
        
        # Check label mappings
        assert len(trainer.label_to_id) == 3
        assert "cs.AI" in trainer.label_to_id
        assert "cs.LG" in trainer.label_to_id
        assert "cs.CV" in trainer.label_to_id
        
        # Check bidirectional mapping
        for label, idx in trainer.label_to_id.items():
            assert trainer.id_to_label[idx] == label
    
    def test_pytorch_dataset(self, small_dataset, temp_output_dir):
        """Test PyTorch dataset creation."""
        from transformers import AutoTokenizer
        
        trainer = ClassificationTrainer(output_dir=temp_output_dir)
        trainer.label_to_id = {"cs.AI": 0, "cs.LG": 1, "cs.CV": 2}
        
        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        
        dataset = ArxivClassificationDataset(
            small_dataset[:10],
            tokenizer,
            trainer.label_to_id
        )
        
        # Check dataset length
        assert len(dataset) == 10
        
        # Check sample format
        sample = dataset[0]
        assert "input_ids" in sample
        assert "attention_mask" in sample
        assert "labels" in sample
        
        # Check tensor shapes
        assert sample["input_ids"].shape[0] == 512  # max_length
        assert sample["attention_mask"].shape[0] == 512
        assert sample["labels"].dim() == 0  # scalar
    
    @pytest.mark.slow
    def test_end_to_end_training(self, temp_data_dir, temp_output_dir):
        """
        Test end-to-end training pipeline with small dataset.
        
        This test:
        1. Loads a small dataset
        2. Trains for 1 epoch
        3. Saves checkpoint
        4. Evaluates on test set
        5. Verifies model can be loaded
        """
        # Initialize trainer
        trainer = ClassificationTrainer(
            model_name="distilbert-base-uncased",
            output_dir=temp_output_dir
        )
        
        # Load datasets
        train_samples, val_samples, test_samples = trainer.load_datasets(temp_data_dir)
        
        # Train model (1 epoch, small batch size for speed)
        train_metrics = trainer.train(
            train_samples,
            val_samples,
            epochs=1,
            batch_size=8,
            learning_rate=2e-5
        )
        
        # Check training completed
        assert "eval_accuracy" in train_metrics
        assert train_metrics["eval_accuracy"] > 0.0
        
        # Save checkpoint
        trainer.save_checkpoint()
        
        # Verify checkpoint files exist
        checkpoint_dir = Path(temp_output_dir)
        assert (checkpoint_dir / "pytorch_model.bin").exists()
        assert (checkpoint_dir / "config.json").exists()
        assert (checkpoint_dir / "label_map.json").exists()
        
        # Evaluate on test set
        test_metrics = trainer.evaluate(test_samples)
        
        # Check evaluation metrics
        assert "test_accuracy" in test_metrics
        assert "test_macro_f1" in test_metrics
        assert test_metrics["test_accuracy"] > 0.5  # Should achieve >50% on small dataset
        
        # Verify results file was created
        assert (checkpoint_dir / "test_results.json").exists()
        
        # Test model can be loaded from checkpoint
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        
        loaded_model = AutoModelForSequenceClassification.from_pretrained(temp_output_dir)
        loaded_tokenizer = AutoTokenizer.from_pretrained(temp_output_dir)
        
        assert loaded_model is not None
        assert loaded_tokenizer is not None
        
        # Verify label mapping was saved correctly
        with open(checkpoint_dir / "label_map.json", 'r') as f:
            label_map = json.load(f)
        
        assert "id_to_label" in label_map
        assert "label_to_id" in label_map
        assert len(label_map["label_to_id"]) == 3
    
    def test_checkpoint_saving(self, temp_data_dir, temp_output_dir):
        """Test that checkpoint saving creates all required files."""
        trainer = ClassificationTrainer(output_dir=temp_output_dir)
        
        # Load datasets first to build label mappings
        train_samples, val_samples, _ = trainer.load_datasets(temp_data_dir)
        
        # Train briefly with small subset
        trainer.train(
            train_samples[:20],  # Use only 20 samples for speed
            val_samples[:5],
            epochs=1,
            batch_size=4
        )
        
        # Save checkpoint
        trainer.save_checkpoint()
        
        # Verify all required files
        checkpoint_dir = Path(temp_output_dir)
        required_files = [
            "pytorch_model.bin",
            "config.json",
            "label_map.json",
            "tokenizer_config.json",
            "vocab.txt"
        ]
        
        for filename in required_files:
            assert (checkpoint_dir / filename).exists(), f"Missing file: {filename}"
        
        # Check model size is reasonable (<500MB)
        model_file = checkpoint_dir / "pytorch_model.bin"
        size_mb = model_file.stat().st_size / (1024 * 1024)
        assert size_mb < 500, f"Model too large: {size_mb:.2f} MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
