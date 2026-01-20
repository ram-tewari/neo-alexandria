"""
Unit tests for training error handling and robustness features.

These tests verify:
- OOM error handling with batch size reduction
- Training divergence detection (NaN/Inf loss)
- Checkpoint validation and backup loading
- Data validation before training
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

import torch

from backend.scripts.training.train_classification import (
    ClassificationTrainer,
    TrainingDivergenceError,
    CheckpointValidationError,
    DataValidationError,
    check_training_health,
    load_checkpoint_with_validation,
    save_checkpoint_backup,
    validate_sample,
    validate_labels,
    validate_dataset,
)


class TestTrainingDivergenceDetection:
    """Test suite for training divergence detection."""

    def test_check_training_health_with_nan_loss(self):
        """Test that NaN loss raises TrainingDivergenceError."""
        with pytest.raises(TrainingDivergenceError) as exc_info:
            check_training_health(float("nan"), step=100)

        assert "Training diverged" in str(exc_info.value)
        assert "step 100" in str(exc_info.value)
        assert "Reduce learning rate" in str(exc_info.value)

    def test_check_training_health_with_inf_loss(self):
        """Test that Inf loss raises TrainingDivergenceError."""
        with pytest.raises(TrainingDivergenceError) as exc_info:
            check_training_health(float("inf"), step=250)

        assert "Training diverged" in str(exc_info.value)
        assert "step 250" in str(exc_info.value)

    def test_check_training_health_with_valid_loss(self):
        """Test that valid loss does not raise error."""
        # Should not raise any exception
        check_training_health(0.5, step=100)
        check_training_health(1.234, step=200)
        check_training_health(0.001, step=300)


class TestCheckpointValidation:
    """Test suite for checkpoint validation and backup."""

    @pytest.fixture
    def temp_checkpoint_dir(self):
        """Create temporary checkpoint directory."""
        temp_dir = tempfile.mkdtemp()
        checkpoint_dir = Path(temp_dir) / "checkpoint"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        yield checkpoint_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_checkpoint_validation_missing_directory(self):
        """Test that missing checkpoint directory raises error."""
        non_existent_path = Path("/non/existent/path")

        with pytest.raises(CheckpointValidationError) as exc_info:
            load_checkpoint_with_validation(non_existent_path)

        assert "not found" in str(exc_info.value)

    def test_checkpoint_validation_missing_files(self, temp_checkpoint_dir):
        """Test that missing required files raises error."""
        # Create checkpoint dir but don't add required files

        with pytest.raises(CheckpointValidationError) as exc_info:
            load_checkpoint_with_validation(temp_checkpoint_dir)

        assert "Missing files" in str(exc_info.value)
        assert "pytorch_model.bin" in str(exc_info.value)

    def test_checkpoint_validation_with_valid_checkpoint(self, temp_checkpoint_dir):
        """Test that valid checkpoint loads successfully."""
        # Create required files
        config_file = temp_checkpoint_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump({"model_type": "distilbert"}, f)

        # Create a simple state dict
        model_file = temp_checkpoint_dir / "pytorch_model.bin"
        state_dict = {"layer.weight": torch.randn(10, 10)}
        torch.save(state_dict, model_file)

        # Should load successfully
        result = load_checkpoint_with_validation(temp_checkpoint_dir)

        assert result is not None
        assert "checkpoint_path" in result
        assert "state_dict" in result

    def test_checkpoint_validation_with_corrupted_file(self, temp_checkpoint_dir):
        """Test that corrupted checkpoint file raises error."""
        # Create required files
        config_file = temp_checkpoint_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump({"model_type": "distilbert"}, f)

        # Create corrupted model file
        model_file = temp_checkpoint_dir / "pytorch_model.bin"
        with open(model_file, "wb") as f:
            f.write(b"corrupted data")

        with pytest.raises(CheckpointValidationError) as exc_info:
            load_checkpoint_with_validation(temp_checkpoint_dir)

        assert "loading failed" in str(exc_info.value).lower()

    def test_checkpoint_backup_loading(self, temp_checkpoint_dir):
        """Test that backup checkpoint is loaded when main checkpoint fails."""
        # Create backup directory with valid checkpoint
        backup_dir = temp_checkpoint_dir.parent / f"{temp_checkpoint_dir.name}.backup"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create valid backup checkpoint
        config_file = backup_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump({"model_type": "distilbert"}, f)

        model_file = backup_dir / "pytorch_model.bin"
        state_dict = {"layer.weight": torch.randn(10, 10)}
        torch.save(state_dict, model_file)

        # Main checkpoint has missing files
        # Should fall back to backup
        result = load_checkpoint_with_validation(temp_checkpoint_dir)

        assert result is not None
        assert "checkpoint_path" in result

    def test_save_checkpoint_backup(self, temp_checkpoint_dir):
        """Test that checkpoint backup is created correctly."""
        # Create some files in checkpoint
        config_file = temp_checkpoint_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump({"model_type": "distilbert"}, f)

        model_file = temp_checkpoint_dir / "pytorch_model.bin"
        state_dict = {"layer.weight": torch.randn(10, 10)}
        torch.save(state_dict, model_file)

        # Save backup
        save_checkpoint_backup(temp_checkpoint_dir)

        # Verify backup exists
        backup_dir = temp_checkpoint_dir.parent / f"{temp_checkpoint_dir.name}.backup"
        assert backup_dir.exists()
        assert (backup_dir / "config.json").exists()
        assert (backup_dir / "pytorch_model.bin").exists()


class TestDataValidation:
    """Test suite for data validation."""

    def test_validate_sample_with_valid_sample(self):
        """Test that valid sample passes validation."""
        sample = {
            "text": "This is a test paper with enough words to pass validation check.",
            "label": "cs.AI",
            "arxiv_id": "2301.12345",
        }

        is_valid, error_msg = validate_sample(sample, 0)

        assert is_valid is True
        assert error_msg is None

    def test_validate_sample_missing_field(self):
        """Test that sample with missing field fails validation."""
        sample = {
            "text": "This is a test paper.",
            "label": "cs.AI",
            # Missing arxiv_id
        }

        is_valid, error_msg = validate_sample(sample, 0)

        assert is_valid is False
        assert "Missing required field" in error_msg
        assert "arxiv_id" in error_msg

    def test_validate_sample_empty_text(self):
        """Test that sample with empty text fails validation."""
        sample = {"text": "", "label": "cs.AI", "arxiv_id": "2301.12345"}

        is_valid, error_msg = validate_sample(sample, 0)

        assert is_valid is False
        assert "empty" in error_msg.lower()

    def test_validate_sample_short_text(self):
        """Test that sample with too few words fails validation."""
        sample = {
            "text": "Too short",  # Only 2 words
            "label": "cs.AI",
            "arxiv_id": "2301.12345",
        }

        is_valid, error_msg = validate_sample(sample, 0)

        assert is_valid is False
        assert "too short" in error_msg.lower()
        assert "minimum 10" in error_msg.lower()

    def test_validate_labels_with_valid_labels(self):
        """Test that valid labels pass validation."""
        samples = [{"label": "cs.AI"}, {"label": "cs.LG"}, {"label": "cs.CV"}]

        is_valid, error_msg = validate_labels(samples)

        assert is_valid is True
        assert error_msg is None

    def test_validate_labels_with_expected_set(self):
        """Test label validation against expected set."""
        samples = [{"label": "cs.AI"}, {"label": "cs.LG"}]

        expected_labels = {"cs.AI", "cs.LG", "cs.CV"}

        is_valid, error_msg = validate_labels(samples, expected_labels)

        assert is_valid is True
        assert error_msg is None

    def test_validate_labels_with_unexpected_label(self):
        """Test that unexpected label fails validation."""
        samples = [
            {"label": "cs.AI"},
            {"label": "cs.INVALID"},  # Not in expected set
        ]

        expected_labels = {"cs.AI", "cs.LG", "cs.CV"}

        is_valid, error_msg = validate_labels(samples, expected_labels)

        assert is_valid is False
        assert "Unexpected labels" in error_msg
        assert "cs.INVALID" in error_msg

    def test_validate_dataset_with_valid_dataset(self):
        """Test that valid dataset passes validation."""
        samples = [
            {
                "text": "This is a test paper with enough words to pass validation check.",
                "label": "cs.AI",
                "arxiv_id": f"2301.{i:05d}",
            }
            for i in range(10)
        ]

        # Should not raise any exception
        validate_dataset(samples, "test_dataset")

    def test_validate_dataset_with_empty_dataset(self):
        """Test that empty dataset raises error."""
        samples = []

        with pytest.raises(DataValidationError) as exc_info:
            validate_dataset(samples, "test_dataset")

        assert "empty" in str(exc_info.value).lower()

    def test_validate_dataset_with_invalid_samples(self):
        """Test that dataset with invalid samples raises error."""
        samples = [
            {
                "text": "Valid sample with enough words to pass validation check.",
                "label": "cs.AI",
                "arxiv_id": "2301.00001",
            },
            {
                "text": "Short",  # Too short
                "label": "cs.AI",
                "arxiv_id": "2301.00002",
            },
        ]

        with pytest.raises(DataValidationError) as exc_info:
            validate_dataset(samples, "test_dataset")

        assert "validation failed" in str(exc_info.value).lower()
        assert "too short" in str(exc_info.value).lower()


class TestOOMErrorHandling:
    """Test suite for OOM error handling."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_dir = tempfile.mkdtemp()
        data_dir = Path(temp_dir) / "data"
        output_dir = Path(temp_dir) / "output"
        data_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create small dataset
        samples = [
            {
                "text": f"Test paper {i} with enough content to be valid. " * 10,
                "label": "cs.AI",
                "arxiv_id": f"2301.{i:05d}",
            }
            for i in range(20)
        ]

        # Save splits
        with open(data_dir / "train.json", "w") as f:
            json.dump(samples[:15], f)
        with open(data_dir / "val.json", "w") as f:
            json.dump(samples[15:18], f)
        with open(data_dir / "test.json", "w") as f:
            json.dump(samples[18:20], f)

        yield str(data_dir), str(output_dir)

        # Cleanup
        shutil.rmtree(temp_dir)

    @patch(
        "backend.scripts.training.train_classification.ClassificationTrainer._train_with_batch_size"
    )
    def test_oom_error_triggers_batch_size_reduction(self, mock_train, temp_dirs):
        """Test that OOM error triggers retry with reduced batch size."""
        data_dir, output_dir = temp_dirs

        # First call raises OOM error, second call succeeds
        mock_train.side_effect = [
            RuntimeError("CUDA out of memory"),
            {"eval_accuracy": 0.8, "train_loss": 0.5},
        ]

        trainer = ClassificationTrainer(output_dir=output_dir)
        train_samples, val_samples, _ = trainer.load_datasets(data_dir)

        # Train with batch size 16
        trainer.train(train_samples, val_samples, epochs=1, batch_size=16)

        # Verify _train_with_batch_size was called twice
        assert mock_train.call_count == 2

        # First call with original batch size
        first_call_batch_size = mock_train.call_args_list[0][0][3]
        assert first_call_batch_size == 16

        # Second call with reduced batch size
        second_call_batch_size = mock_train.call_args_list[1][0][3]
        assert second_call_batch_size == 8  # Half of original

    @patch(
        "backend.scripts.training.train_classification.ClassificationTrainer._train_with_batch_size"
    )
    @patch("torch.cuda.is_available")
    @patch("torch.cuda.empty_cache")
    def test_oom_error_clears_gpu_cache(
        self, mock_empty_cache, mock_cuda_available, mock_train, temp_dirs
    ):
        """Test that OOM error clears GPU cache before retry."""
        data_dir, output_dir = temp_dirs

        # Simulate GPU available
        mock_cuda_available.return_value = True

        # First call raises OOM error, second call succeeds
        mock_train.side_effect = [
            RuntimeError("CUDA out of memory"),
            {"eval_accuracy": 0.8, "train_loss": 0.5},
        ]

        trainer = ClassificationTrainer(output_dir=output_dir)
        train_samples, val_samples, _ = trainer.load_datasets(data_dir)

        # Train
        trainer.train(train_samples, val_samples, epochs=1, batch_size=16)

        # Verify GPU cache was cleared
        mock_empty_cache.assert_called_once()

    @patch(
        "backend.scripts.training.train_classification.ClassificationTrainer._train_with_batch_size"
    )
    def test_persistent_oom_error_provides_suggestions(self, mock_train, temp_dirs):
        """Test that persistent OOM error provides helpful suggestions."""
        data_dir, output_dir = temp_dirs

        # Both calls raise OOM error
        mock_train.side_effect = RuntimeError("CUDA out of memory")

        trainer = ClassificationTrainer(output_dir=output_dir)
        train_samples, val_samples, _ = trainer.load_datasets(data_dir)

        # Should raise RuntimeError with suggestions
        with pytest.raises(RuntimeError):
            trainer.train(train_samples, val_samples, epochs=1, batch_size=16)

        # Verify _train_with_batch_size was called twice
        assert mock_train.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
