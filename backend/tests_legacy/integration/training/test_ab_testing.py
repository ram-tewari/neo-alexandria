"""
Integration tests for A/B Testing Framework

Tests the complete A/B testing workflow including experiment creation,
prediction routing, logging, analysis, and winner promotion.
"""

import pytest
import uuid

from backend.app.database.base import SessionLocal
from backend.app.database.models import ModelVersion, ABTestExperiment, PredictionLog
from backend.scripts.deployment.ab_testing import ABTestingFramework


@pytest.fixture
def db_session():
    """Create a database session for testing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def ab_testing(db_session):
    """Create ABTestingFramework instance."""
    return ABTestingFramework(db_session)


@pytest.fixture
def model_versions(db_session):
    """Create test model versions."""
    # Create control version
    control = ModelVersion(
        version="v1.0.0",
        model_type="classification",
        model_path="models/classification/arxiv_v1.0.0",
        status="production",
        model_metadata={"dataset_size": 10000, "num_categories": 10},
        model_metrics={"accuracy": 0.90, "f1_score": 0.88},
    )

    # Create treatment version
    treatment = ModelVersion(
        version="v1.1.0",
        model_type="classification",
        model_path="models/classification/arxiv_v1.1.0",
        status="testing",
        model_metadata={"dataset_size": 11500, "num_categories": 10},
        model_metrics={"accuracy": 0.93, "f1_score": 0.91},
    )

    db_session.add(control)
    db_session.add(treatment)
    db_session.commit()
    db_session.refresh(control)
    db_session.refresh(treatment)

    yield {"control": control, "treatment": treatment}

    # Cleanup
    db_session.query(PredictionLog).delete()
    db_session.query(ABTestExperiment).delete()
    db_session.query(ModelVersion).delete()
    db_session.commit()


class TestABTestingFramework:
    """Test suite for A/B Testing Framework."""

    def test_experiment_creation(self, ab_testing, model_versions):
        """Test creating an A/B test experiment."""
        # Create experiment
        experiment_id = ab_testing.create_experiment(
            name="test_experiment",
            control_version="v1.0.0",
            treatment_version="v1.1.0",
            traffic_split=0.1,
        )

        # Verify experiment was created
        assert experiment_id is not None
        assert isinstance(uuid.UUID(experiment_id), uuid.UUID)

        # Verify experiment in database
        experiment = (
            ab_testing.db.query(ABTestExperiment)
            .filter(ABTestExperiment.id == uuid.UUID(experiment_id))
            .first()
        )

        assert experiment is not None
        assert experiment.name == "test_experiment"
        assert experiment.control_version.version == "v1.0.0"
        assert experiment.treatment_version.version == "v1.1.0"
        assert experiment.traffic_split == 0.1
        assert experiment.status == "running"

    def test_experiment_creation_validation(self, ab_testing, model_versions):
        """Test experiment creation validation."""
        # Test invalid traffic_split
        with pytest.raises(ValueError, match="traffic_split must be between"):
            ab_testing.create_experiment(
                name="invalid_split",
                control_version="v1.0.0",
                treatment_version="v1.1.0",
                traffic_split=1.5,
            )

        # Test non-existent control version
        with pytest.raises(ValueError, match="Control version.*not found"):
            ab_testing.create_experiment(
                name="invalid_control",
                control_version="v9.9.9",
                treatment_version="v1.1.0",
                traffic_split=0.1,
            )

        # Test non-existent treatment version
        with pytest.raises(ValueError, match="Treatment version.*not found"):
            ab_testing.create_experiment(
                name="invalid_treatment",
                control_version="v1.0.0",
                treatment_version="v9.9.9",
                traffic_split=0.1,
            )

    def test_prediction_routing_consistency(self, ab_testing, model_versions):
        """Test that prediction routing is consistent for same user."""
        # Create experiment
        experiment_id = ab_testing.create_experiment(
            name="routing_test",
            control_version="v1.0.0",
            treatment_version="v1.1.0",
            traffic_split=0.1,
        )

        # Test routing for multiple users
        user_ids = [f"user_{i}" for i in range(100)]

        # First routing
        first_routing = {}
        for user_id in user_ids:
            version = ab_testing.route_prediction(experiment_id, user_id)
            first_routing[user_id] = version

        # Second routing (should be identical)
        for user_id in user_ids:
            version = ab_testing.route_prediction(experiment_id, user_id)
            assert version == first_routing[user_id], (
                f"Routing changed for {user_id}: {first_routing[user_id]} -> {version}"
            )

        # Verify traffic split is approximately correct
        treatment_count = sum(1 for v in first_routing.values() if v == "treatment")
        treatment_ratio = treatment_count / len(user_ids)

        # Allow 5% tolerance
        assert abs(treatment_ratio - 0.1) < 0.05, (
            f"Traffic split {treatment_ratio:.2%} not close to target 10%"
        )

    def test_prediction_logging(self, ab_testing, model_versions):
        """Test prediction logging works correctly."""
        # Create experiment
        experiment_id = ab_testing.create_experiment(
            name="logging_test",
            control_version="v1.0.0",
            treatment_version="v1.1.0",
            traffic_split=0.5,
        )

        # Log predictions
        for i in range(50):
            ab_testing.log_prediction(
                experiment_id=experiment_id,
                version="v1.0.0",
                input_text=f"Test paper {i}",
                predictions={"cs.AI": 0.85, "cs.LG": 0.15},
                latency_ms=95.5,
                user_id=f"user_{i}",
            )

        # Flush buffer
        ab_testing._flush_prediction_buffer()

        # Verify predictions were logged
        logs = (
            ab_testing.db.query(PredictionLog)
            .filter(PredictionLog.experiment_id == uuid.UUID(experiment_id))
            .all()
        )

        assert len(logs) == 50
        assert all(log.latency_ms == 95.5 for log in logs)
        assert all("cs.AI" in log.predictions for log in logs)

    def test_experiment_analysis(self, ab_testing, model_versions):
        """Test experiment analysis calculates metrics correctly."""
        # Create experiment
        experiment_id = ab_testing.create_experiment(
            name="analysis_test",
            control_version="v1.0.0",
            treatment_version="v1.1.0",
            traffic_split=0.5,
        )

        # Log predictions for control (lower confidence)
        for i in range(50):
            ab_testing.log_prediction(
                experiment_id=experiment_id,
                version="v1.0.0",
                input_text=f"Test paper {i}",
                predictions={"cs.AI": 0.80, "cs.LG": 0.20},
                latency_ms=100.0,
                user_id=f"user_{i}",
            )

        # Log predictions for treatment (higher confidence)
        for i in range(50):
            ab_testing.log_prediction(
                experiment_id=experiment_id,
                version="v1.1.0",
                input_text=f"Test paper {i}",
                predictions={"cs.AI": 0.95, "cs.LG": 0.05},
                latency_ms=95.0,
                user_id=f"user_{i + 50}",
            )

        # Flush buffer
        ab_testing._flush_prediction_buffer()

        # Analyze experiment
        results = ab_testing.analyze_experiment(experiment_id)

        # Verify results structure
        assert "control" in results
        assert "treatment" in results
        assert "statistical_significance" in results
        assert "recommendation" in results

        # Verify metrics
        assert results["control"]["predictions"] == 50
        assert results["treatment"]["predictions"] == 50
        assert (
            results["control"]["avg_confidence"]
            < results["treatment"]["avg_confidence"]
        )
        assert results["treatment"]["latency_p95"] < results["control"]["latency_p95"]

        # Verify statistical test
        assert "p_value" in results["statistical_significance"]
        assert "confidence_improvement" in results["statistical_significance"]

    def test_promotion_logic_when_treatment_better(self, ab_testing, model_versions):
        """Test promotion logic works when treatment is significantly better."""
        # Create experiment
        experiment_id = ab_testing.create_experiment(
            name="promotion_test",
            control_version="v1.0.0",
            treatment_version="v1.1.0",
            traffic_split=0.5,
        )

        # Log predictions showing treatment is significantly better
        for i in range(50):
            # Control: lower confidence
            ab_testing.log_prediction(
                experiment_id=experiment_id,
                version="v1.0.0",
                input_text=f"Test paper {i}",
                predictions={"cs.AI": 0.75, "cs.LG": 0.25},
                latency_ms=100.0,
                user_id=f"user_{i}",
            )

            # Treatment: much higher confidence (>2% improvement)
            ab_testing.log_prediction(
                experiment_id=experiment_id,
                version="v1.1.0",
                input_text=f"Test paper {i}",
                predictions={"cs.AI": 0.95, "cs.LG": 0.05},
                latency_ms=95.0,
                user_id=f"user_{i + 50}",
            )

        # Flush buffer
        ab_testing._flush_prediction_buffer()

        # Analyze experiment
        results = ab_testing.analyze_experiment(experiment_id)

        # Verify recommendation is PROMOTE
        assert results["recommendation"] == "PROMOTE"

        # Note: We can't actually test promotion without ModelVersioning
        # being fully implemented, but we can verify the analysis logic
        assert results["statistical_significance"]["confidence_improvement"] > 0.02
        assert results["statistical_significance"]["p_value"] < 0.05

    def test_insufficient_data_error(self, ab_testing, model_versions):
        """Test that analysis fails with insufficient data."""
        # Create experiment
        experiment_id = ab_testing.create_experiment(
            name="insufficient_data_test",
            control_version="v1.0.0",
            treatment_version="v1.1.0",
            traffic_split=0.5,
        )

        # Log only a few predictions (< 30)
        for i in range(10):
            ab_testing.log_prediction(
                experiment_id=experiment_id,
                version="v1.0.0",
                input_text=f"Test paper {i}",
                predictions={"cs.AI": 0.85},
                latency_ms=100.0,
            )

        ab_testing._flush_prediction_buffer()

        # Attempt analysis should fail
        with pytest.raises(ValueError, match="Insufficient data"):
            ab_testing.analyze_experiment(experiment_id)

    def test_batch_prediction_logging(self, ab_testing, model_versions):
        """Test that prediction logging batches correctly."""
        # Create experiment
        experiment_id = ab_testing.create_experiment(
            name="batch_test",
            control_version="v1.0.0",
            treatment_version="v1.1.0",
            traffic_split=0.5,
        )

        # Log exactly buffer_size predictions
        buffer_size = ab_testing.buffer_size
        for i in range(buffer_size):
            ab_testing.log_prediction(
                experiment_id=experiment_id,
                version="v1.0.0",
                input_text=f"Test paper {i}",
                predictions={"cs.AI": 0.85},
                latency_ms=100.0,
            )

        # Buffer should be empty after automatic flush
        assert len(ab_testing.prediction_buffer) == 0

        # Verify predictions were saved
        logs = (
            ab_testing.db.query(PredictionLog)
            .filter(PredictionLog.experiment_id == uuid.UUID(experiment_id))
            .all()
        )

        assert len(logs) == buffer_size


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
