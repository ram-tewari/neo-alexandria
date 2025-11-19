"""
Integration tests for automated retraining pipeline.

Tests the complete retraining workflow including data detection, trigger logic,
dataset augmentation, model training, evaluation, and promotion.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.training.retrain_pipeline import RetrainingPipeline


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create directory structure
        data_dir = tmpdir / "data"
        raw_dir = data_dir / "raw" / "arxiv"
        processed_dir = data_dir / "processed"
        splits_dir = data_dir / "splits" / "arxiv_classification"
        model_dir = tmpdir / "models" / "classification"
        
        raw_dir.mkdir(parents=True)
        processed_dir.mkdir(parents=True)
        splits_dir.mkdir(parents=True)
        model_dir.mkdir(parents=True)
        
        # Create config file
        config = {
            "data_dir": str(data_dir),
            "model_base_dir": str(model_dir),
            "data_growth_threshold": 0.10,
            "promotion_threshold": 0.02,
            "default_start_date": "2020-01-01",
            "model_name": "distilbert-base-uncased",
            "epochs": 1,
            "batch_size": 8,
            "learning_rate": 2e-5
        }
        
        config_file = tmpdir / "retraining_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        # Create version registry
        registry = {
            "versions": [
                {
                    "version": "v1.0.0",
                    "path": str(model_dir / "arxiv_v1.0.0"),
                    "created_at": "2025-01-01T00:00:00",
                    "status": "production"
                }
            ],
            "production_version": "v1.0.0",
            "latest_version": "v1.0.0"
        }
        
        registry_file = model_dir / "version_registry.json"
        with open(registry_file, 'w') as f:
            json.dump(registry, f)
        
        # Create existing training data
        existing_data = [
            {
                "text": f"Sample paper {i} about machine learning",
                "label": "cs.LG",
                "arxiv_id": f"2301.{i:05d}",
                "title": f"Paper {i}",
                "authors": ["Author A"],
                "published": "2023-01-01T00:00:00"
            }
            for i in range(100)
        ]
        
        with open(splits_dir / "train.json", 'w') as f:
            json.dump(existing_data, f)
        
        yield {
            "tmpdir": tmpdir,
            "config_file": config_file,
            "data_dir": data_dir,
            "splits_dir": splits_dir,
            "model_dir": model_dir,
            "existing_data": existing_data
        }


def test_pipeline_detects_new_data_correctly(temp_dirs):
    """Test that pipeline correctly detects new data from arXiv."""
    pipeline = RetrainingPipeline(config_path=str(temp_dirs["config_file"]))
    
    # Mock arXiv collector to return new papers
    new_papers = [
        {
            "arxiv_id": f"2025.{i:05d}",
            "title": f"New Paper {i}",
            "abstract": "This is a new paper about AI",
            "authors": ["New Author"],
            "categories": ["cs.AI"],
            "primary_category": "cs.AI",
            "published": "2025-11-01T00:00:00"
        }
        for i in range(15)
    ]
    
    with patch.object(
        pipeline.arxiv_collector,
        'collect_papers_by_category',
        return_value=new_papers
    ):
        result = pipeline.check_for_new_data()
    
    # Verify results
    assert result["new_data_count"] == 150  # 15 papers * 10 categories
    assert len(result["new_papers"]) == 150
    assert "last_training_date" in result
    assert "categories" in result


def test_retraining_trigger_logic_works(temp_dirs):
    """Test that retraining trigger logic correctly evaluates growth rate."""
    pipeline = RetrainingPipeline(config_path=str(temp_dirs["config_file"]))
    
    # Test case 1: Growth above threshold (should trigger)
    should_retrain = pipeline.should_retrain(
        new_data_count=15,
        current_dataset_size=100
    )
    assert should_retrain is True  # 15/100 = 15% > 10% threshold
    
    # Test case 2: Growth below threshold (should not trigger)
    should_retrain = pipeline.should_retrain(
        new_data_count=5,
        current_dataset_size=100
    )
    assert should_retrain is False  # 5/100 = 5% < 10% threshold
    
    # Test case 3: Growth exactly at threshold (should not trigger)
    should_retrain = pipeline.should_retrain(
        new_data_count=10,
        current_dataset_size=100
    )
    assert should_retrain is False  # 10/100 = 10% = threshold (not >)


def test_dataset_augmentation_combines_data_correctly(temp_dirs):
    """Test that dataset augmentation correctly combines existing and new data."""
    pipeline = RetrainingPipeline(config_path=str(temp_dirs["config_file"]))
    
    existing_data = temp_dirs["existing_data"]
    
    # Create new papers with longer abstracts to pass quality filter (50+ words)
    new_papers = [
        {
            "arxiv_id": f"2025.{i:05d}",
            "title": f"New Paper {i}",
            "abstract": (
                "This is a new paper about artificial intelligence and machine learning "
                "that explores novel approaches to deep neural networks and their applications "
                "in natural language processing computer vision and reinforcement learning domains "
                "with significant improvements over baseline methods and state of the art results "
                "demonstrating the effectiveness of the proposed techniques and methodologies"
            ),
            "authors": ["New Author"],
            "categories": ["cs.AI"],
            "primary_category": "cs.AI",
            "published": "2025-11-01T00:00:00"
        }
        for i in range(20)
    ]
    
    train, val, test = pipeline.augment_dataset(
        existing_data=existing_data,
        new_data=new_papers
    )
    
    # Verify augmentation
    total_samples = len(train) + len(val) + len(test)
    assert total_samples <= len(existing_data) + len(new_papers)  # May be less due to filtering
    assert total_samples > len(existing_data)  # Should have more than before
    
    # Verify splits maintain ratios (approximately)
    assert len(train) > len(val)
    assert len(train) > len(test)
    assert abs(len(val) - len(test)) < 5  # Val and test should be similar


def test_new_version_training_works(temp_dirs):
    """Test that new version training creates a model."""
    pipeline = RetrainingPipeline(config_path=str(temp_dirs["config_file"]))
    
    # Create minimal training data
    train_samples = [
        {
            "text": f"Sample paper {i} about machine learning and neural networks",
            "label": "cs.LG",
            "arxiv_id": f"2301.{i:05d}",
            "title": f"Paper {i}",
            "authors": ["Author A"],
            "published": "2023-01-01T00:00:00"
        }
        for i in range(50)
    ]
    
    val_samples = train_samples[:10]
    
    # Mock the trainer to avoid actual training
    with patch('scripts.training.retrain_pipeline.ClassificationTrainer') as MockTrainer:
        mock_trainer = MockTrainer.return_value
        mock_trainer.train.return_value = {
            "accuracy": 0.85,
            "f1": 0.83,
            "training_time_seconds": 100
        }
        
        new_version, metrics = pipeline.train_new_version(
            train_samples=train_samples,
            val_samples=val_samples,
            current_version="v1.0.0"
        )
    
    # Verify version increment
    assert new_version == "v1.1.0"  # Minor version incremented
    
    # Verify metrics
    assert "accuracy" in metrics
    assert "f1" in metrics
    assert "training_time_seconds" in metrics


def test_improvement_evaluation_compares_models_correctly(temp_dirs):
    """Test that improvement evaluation correctly compares models."""
    pipeline = RetrainingPipeline(config_path=str(temp_dirs["config_file"]))
    
    test_samples = [
        {
            "text": f"Test paper {i} about AI",
            "label": "cs.AI",
            "arxiv_id": f"2301.{i:05d}",
            "title": f"Test Paper {i}",
            "authors": ["Author A"],
            "published": "2023-01-01T00:00:00"
        }
        for i in range(20)
    ]
    
    # Mock the trainers
    with patch('scripts.training.retrain_pipeline.ClassificationTrainer') as MockTrainer:
        # Production model
        prod_trainer = MagicMock()
        prod_trainer.evaluate.return_value = {
            "accuracy": 0.90,
            "f1": 0.88
        }
        
        # New model
        new_trainer = MagicMock()
        new_trainer.evaluate.return_value = {
            "accuracy": 0.93,
            "f1": 0.91
        }
        
        # Configure mock to return different instances
        MockTrainer.side_effect = [prod_trainer, new_trainer]
        
        comparison = pipeline.evaluate_improvement(
            new_version="v1.1.0",
            production_version="v1.0.0",
            test_samples=test_samples
        )
    
    # Verify comparison
    assert comparison["production_version"] == "v1.0.0"
    assert comparison["new_version"] == "v1.1.0"
    assert comparison["production_metrics"]["accuracy"] == 0.90
    assert comparison["new_metrics"]["accuracy"] == 0.93
    assert abs(comparison["improvement"]["accuracy"] - 0.03) < 0.001  # Allow for floating point precision
    assert abs(comparison["improvement"]["accuracy_percent"] - 3.0) < 0.1


def test_promotion_logic_works_when_improvement_exceeds_threshold(temp_dirs):
    """Test that promotion logic promotes model when improvement exceeds threshold."""
    pipeline = RetrainingPipeline(config_path=str(temp_dirs["config_file"]))
    
    # Create comparison with improvement above threshold (2%)
    comparison = {
        "production_version": "v1.0.0",
        "new_version": "v1.1.0",
        "production_metrics": {"accuracy": 0.90, "f1": 0.88},
        "new_metrics": {"accuracy": 0.93, "f1": 0.91},
        "improvement": {
            "accuracy": 0.03,
            "accuracy_percent": 3.0,
            "f1": 0.03,
            "f1_percent": 3.0
        }
    }
    
    # Mock versioning.promote_to_production
    with patch.object(pipeline.versioning, 'promote_to_production'):
        promoted = pipeline.promote_if_better(
            new_version="v1.1.0",
            comparison=comparison
        )
    
    # Should promote (3% > 2% threshold)
    assert promoted is True


def test_promotion_logic_does_not_promote_when_below_threshold(temp_dirs):
    """Test that promotion logic does not promote when improvement is below threshold."""
    pipeline = RetrainingPipeline(config_path=str(temp_dirs["config_file"]))
    
    # Create comparison with improvement below threshold (2%)
    comparison = {
        "production_version": "v1.0.0",
        "new_version": "v1.1.0",
        "production_metrics": {"accuracy": 0.90, "f1": 0.88},
        "new_metrics": {"accuracy": 0.91, "f1": 0.89},
        "improvement": {
            "accuracy": 0.01,
            "accuracy_percent": 1.0,
            "f1": 0.01,
            "f1_percent": 1.0
        }
    }
    
    # Mock versioning.promote_to_production
    with patch.object(pipeline.versioning, 'promote_to_production'):
        promoted = pipeline.promote_if_better(
            new_version="v1.1.0",
            comparison=comparison
        )
    
    # Should not promote (1% < 2% threshold)
    assert promoted is False


def test_version_increment_logic(temp_dirs):
    """Test that version increment logic works correctly."""
    pipeline = RetrainingPipeline(config_path=str(temp_dirs["config_file"]))
    
    # Test minor increment
    assert pipeline._increment_version("v1.0.0", "minor") == "v1.1.0"
    assert pipeline._increment_version("v1.5.3", "minor") == "v1.6.0"
    
    # Test major increment
    assert pipeline._increment_version("v1.0.0", "major") == "v2.0.0"
    assert pipeline._increment_version("v1.5.3", "major") == "v2.0.0"
    
    # Test patch increment
    assert pipeline._increment_version("v1.0.0", "patch") == "v1.0.1"
    assert pipeline._increment_version("v1.5.3", "patch") == "v1.5.4"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
