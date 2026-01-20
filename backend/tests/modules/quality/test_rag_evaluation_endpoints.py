"""
Tests for RAG Evaluation API Endpoints (Phase 17.5 - Advanced RAG)

Tests the three RAG evaluation endpoints:
- POST /evaluation/submit - Submit evaluation data
- GET /evaluation/metrics - Get aggregated metrics
- GET /evaluation/history - Get paginated history

Requirements: 4.1-4.13
"""

import json
import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import status

from app.database.models import RAGEvaluation


def generate_uuid() -> str:
    """Helper to generate valid UUID strings for tests."""
    return str(uuid.uuid4())


class TestSubmitEvaluation:
    """Tests for POST /evaluation/submit endpoint."""

    def test_submit_evaluation_success(self, client, db_session):
        """Test successful evaluation submission with all fields."""
        # Arrange
        evaluation_data = {
            "query": "What is machine learning?",
            "expected_answer": "Machine learning is a subset of AI...",
            "generated_answer": "Machine learning is a method of data analysis...",
            "retrieved_chunk_ids": [generate_uuid(), generate_uuid(), generate_uuid()],
            "faithfulness_score": 0.85,
            "answer_relevance_score": 0.90,
            "context_precision_score": 0.75,
        }

        # Act
        response = client.post("/evaluation/submit", json=evaluation_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert "id" in data
        assert data["query"] == evaluation_data["query"]
        assert data["expected_answer"] == evaluation_data["expected_answer"]
        assert data["generated_answer"] == evaluation_data["generated_answer"]
        assert data["retrieved_chunk_ids"] == evaluation_data["retrieved_chunk_ids"]
        assert data["faithfulness_score"] == evaluation_data["faithfulness_score"]
        assert (
            data["answer_relevance_score"] == evaluation_data["answer_relevance_score"]
        )
        assert (
            data["context_precision_score"]
            == evaluation_data["context_precision_score"]
        )
        assert "created_at" in data

        # Verify database record
        eval_record = (
            db_session.query(RAGEvaluation)
            .filter(RAGEvaluation.id == data["id"])
            .first()
        )
        assert eval_record is not None
        assert eval_record.query == evaluation_data["query"]

    def test_submit_evaluation_minimal_fields(self, client, db_session):
        """Test evaluation submission with only required fields."""
        # Arrange
        evaluation_data = {
            "query": "What is deep learning?",
            "retrieved_chunk_ids": [generate_uuid()],
        }

        # Act
        response = client.post("/evaluation/submit", json=evaluation_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["query"] == evaluation_data["query"]
        assert data["retrieved_chunk_ids"] == evaluation_data["retrieved_chunk_ids"]
        assert data["expected_answer"] is None
        assert data["generated_answer"] is None
        assert data["faithfulness_score"] is None
        assert data["answer_relevance_score"] is None
        assert data["context_precision_score"] is None

    def test_submit_evaluation_empty_chunk_ids(self, client):
        """Test validation fails with empty chunk IDs list."""
        # Arrange
        evaluation_data = {
            "query": "What is AI?",
            "retrieved_chunk_ids": [],
        }

        # Act
        response = client.post("/evaluation/submit", json=evaluation_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_submit_evaluation_invalid_score_range(self, client):
        """Test validation fails with score outside 0.0-1.0 range."""
        # Arrange
        evaluation_data = {
            "query": "What is neural networks?",
            "retrieved_chunk_ids": [generate_uuid()],
            "faithfulness_score": 1.5,  # Invalid: > 1.0
        }

        # Act
        response = client.post("/evaluation/submit", json=evaluation_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_submit_evaluation_negative_score(self, client):
        """Test validation fails with negative score."""
        # Arrange
        evaluation_data = {
            "query": "What is NLP?",
            "retrieved_chunk_ids": [generate_uuid()],
            "answer_relevance_score": -0.1,  # Invalid: < 0.0
        }

        # Act
        response = client.post("/evaluation/submit", json=evaluation_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_submit_evaluation_missing_query(self, client):
        """Test validation fails without query field."""
        # Arrange
        evaluation_data = {
            "retrieved_chunk_ids": [generate_uuid()],
        }

        # Act
        response = client.post("/evaluation/submit", json=evaluation_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetEvaluationMetrics:
    """Tests for GET /evaluation/metrics endpoint."""

    def test_get_metrics_with_data(self, client, db_session):
        """Test metrics aggregation with existing evaluation data."""
        # Arrange - Create test evaluations
        now = datetime.utcnow()
        evaluations = [
            RAGEvaluation(
                id=generate_uuid(),
                query=f"Query {i}",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                faithfulness_score=0.8 + (i * 0.05),
                answer_relevance_score=0.7 + (i * 0.05),
                context_precision_score=0.6 + (i * 0.05),
                created_at=now - timedelta(days=i),
            )
            for i in range(5)
        ]

        for eval_record in evaluations:
            db_session.add(eval_record)
        db_session.commit()

        # Act
        response = client.get("/evaluation/metrics")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total_evaluations"] == 5
        assert "date_range" in data
        assert "metrics" in data

        # Check faithfulness metrics
        faithfulness = data["metrics"]["faithfulness"]
        assert faithfulness["count"] == 5
        assert faithfulness["avg"] is not None
        assert faithfulness["min"] is not None
        assert faithfulness["max"] is not None
        assert 0.0 <= faithfulness["avg"] <= 1.0

        # Check answer relevance metrics
        answer_relevance = data["metrics"]["answer_relevance"]
        assert answer_relevance["count"] == 5
        assert answer_relevance["avg"] is not None

        # Check context precision metrics
        context_precision = data["metrics"]["context_precision"]
        assert context_precision["count"] == 5
        assert context_precision["avg"] is not None

    def test_get_metrics_empty_database(self, client, db_session):
        """Test metrics endpoint with no evaluation data."""
        # Act
        response = client.get("/evaluation/metrics")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total_evaluations"] == 0
        assert data["metrics"]["faithfulness"]["avg"] is None
        assert data["metrics"]["answer_relevance"]["avg"] is None
        assert data["metrics"]["context_precision"]["avg"] is None

    def test_get_metrics_with_date_range(self, client, db_session):
        """Test metrics filtering by date range."""
        # Arrange - Create evaluations across different dates
        now = datetime.utcnow()

        # Recent evaluations (within range)
        for i in range(3):
            eval_record = RAGEvaluation(
                id=generate_uuid(),
                query=f"Recent query {i}",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                faithfulness_score=0.9,
                created_at=now - timedelta(days=i),
            )
            db_session.add(eval_record)

        # Old evaluations (outside range)
        for i in range(2):
            eval_record = RAGEvaluation(
                id=generate_uuid(),
                query=f"Old query {i}",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                faithfulness_score=0.5,
                created_at=now - timedelta(days=60 + i),
            )
            db_session.add(eval_record)

        db_session.commit()

        # Act - Query last 30 days (use wider range to ensure all recent evals are included)
        start_date = (now - timedelta(days=31)).strftime("%Y-%m-%d")
        end_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")  # Include today
        response = client.get(
            f"/evaluation/metrics?start_date={start_date}&end_date={end_date}"
        )

        # Assert - Should only include recent evaluations
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total_evaluations"] == 3
        assert data["metrics"]["faithfulness"]["count"] == 3
        # Average should be 0.9 (recent) not affected by 0.5 (old)
        assert data["metrics"]["faithfulness"]["avg"] == pytest.approx(0.9, abs=0.01)

    def test_get_metrics_invalid_date_format(self, client):
        """Test error handling for invalid date format."""
        # Act
        response = client.get("/evaluation/metrics?start_date=invalid-date")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid start_date format" in response.json()["detail"]

    def test_get_metrics_partial_scores(self, client, db_session):
        """Test metrics with some null scores."""
        # Arrange - Create evaluations with partial scores
        evaluations = [
            RAGEvaluation(
                id=generate_uuid(),
                query="Query 1",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                faithfulness_score=0.8,
                answer_relevance_score=None,  # Missing
                context_precision_score=0.7,
                created_at=datetime.utcnow(),
            ),
            RAGEvaluation(
                id=generate_uuid(),
                query="Query 2",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                faithfulness_score=0.9,
                answer_relevance_score=0.85,
                context_precision_score=None,  # Missing
                created_at=datetime.utcnow(),
            ),
        ]

        for eval_record in evaluations:
            db_session.add(eval_record)
        db_session.commit()

        # Act
        response = client.get("/evaluation/metrics")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Faithfulness: 2 values
        assert data["metrics"]["faithfulness"]["count"] == 2
        assert data["metrics"]["faithfulness"]["avg"] == pytest.approx(0.85, abs=0.01)

        # Answer relevance: 1 value
        assert data["metrics"]["answer_relevance"]["count"] == 1
        assert data["metrics"]["answer_relevance"]["avg"] == pytest.approx(
            0.85, abs=0.01
        )

        # Context precision: 1 value
        assert data["metrics"]["context_precision"]["count"] == 1
        assert data["metrics"]["context_precision"]["avg"] == pytest.approx(
            0.7, abs=0.01
        )


class TestGetEvaluationHistory:
    """Tests for GET /evaluation/history endpoint."""

    def test_get_history_success(self, client, db_session):
        """Test retrieving evaluation history with pagination."""
        # Arrange - Create test evaluations
        now = datetime.utcnow()
        for i in range(10):
            eval_record = RAGEvaluation(
                id=generate_uuid(),
                query=f"Query {i}",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                faithfulness_score=0.8,
                created_at=now - timedelta(minutes=i),
            )
            db_session.add(eval_record)
        db_session.commit()

        # Act
        response = client.get("/evaluation/history?page=1&limit=5")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total"] == 10
        assert data["page"] == 1
        assert data["limit"] == 5
        assert len(data["evaluations"]) == 5

        # Verify first evaluation (most recent)
        first_eval = data["evaluations"][0]
        assert "id" in first_eval
        assert "query" in first_eval
        assert "retrieved_chunk_ids" in first_eval
        assert "created_at" in first_eval

    def test_get_history_pagination(self, client, db_session):
        """Test pagination across multiple pages."""
        # Arrange - Create 25 evaluations
        now = datetime.utcnow()
        for i in range(25):
            eval_record = RAGEvaluation(
                id=generate_uuid(),
                query=f"Query {i}",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                created_at=now - timedelta(minutes=i),
            )
            db_session.add(eval_record)
        db_session.commit()

        # Act - Get page 2
        response = client.get("/evaluation/history?page=2&limit=10")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total"] == 25
        assert data["page"] == 2
        assert data["limit"] == 10
        assert len(data["evaluations"]) == 10

    def test_get_history_filter_by_faithfulness(self, client, db_session):
        """Test filtering by minimum faithfulness score."""
        # Arrange - Create evaluations with varying scores
        eval_high_id = generate_uuid()
        eval_low_id = generate_uuid()

        evaluations = [
            RAGEvaluation(
                id=eval_high_id,
                query="High score query",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                faithfulness_score=0.9,
                created_at=datetime.utcnow(),
            ),
            RAGEvaluation(
                id=eval_low_id,
                query="Low score query",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                faithfulness_score=0.5,
                created_at=datetime.utcnow(),
            ),
        ]

        for eval_record in evaluations:
            db_session.add(eval_record)
        db_session.commit()

        # Act - Filter for faithfulness >= 0.8
        response = client.get("/evaluation/history?min_faithfulness=0.8")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total"] == 1
        assert data["evaluations"][0]["id"] == eval_high_id
        assert data["evaluations"][0]["faithfulness_score"] >= 0.8

    def test_get_history_filter_by_answer_relevance(self, client, db_session):
        """Test filtering by minimum answer relevance score."""
        # Arrange
        eval_relevant_id = generate_uuid()
        eval_irrelevant_id = generate_uuid()

        evaluations = [
            RAGEvaluation(
                id=eval_relevant_id,
                query="Relevant query",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                answer_relevance_score=0.95,
                created_at=datetime.utcnow(),
            ),
            RAGEvaluation(
                id=eval_irrelevant_id,
                query="Irrelevant query",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                answer_relevance_score=0.4,
                created_at=datetime.utcnow(),
            ),
        ]

        for eval_record in evaluations:
            db_session.add(eval_record)
        db_session.commit()

        # Act
        response = client.get("/evaluation/history?min_answer_relevance=0.9")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total"] == 1
        assert data["evaluations"][0]["id"] == eval_relevant_id

    def test_get_history_filter_by_context_precision(self, client, db_session):
        """Test filtering by minimum context precision score."""
        # Arrange
        eval_precise_id = generate_uuid()
        eval_imprecise_id = generate_uuid()

        evaluations = [
            RAGEvaluation(
                id=eval_precise_id,
                query="Precise context query",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                context_precision_score=0.85,
                created_at=datetime.utcnow(),
            ),
            RAGEvaluation(
                id=eval_imprecise_id,
                query="Imprecise context query",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                context_precision_score=0.3,
                created_at=datetime.utcnow(),
            ),
        ]

        for eval_record in evaluations:
            db_session.add(eval_record)
        db_session.commit()

        # Act
        response = client.get("/evaluation/history?min_context_precision=0.8")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total"] == 1
        assert data["evaluations"][0]["id"] == eval_precise_id

    def test_get_history_multiple_filters(self, client, db_session):
        """Test combining multiple score filters."""
        # Arrange
        eval_all_high_id = generate_uuid()
        eval_mixed_id = generate_uuid()

        evaluations = [
            RAGEvaluation(
                id=eval_all_high_id,
                query="All high scores",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                faithfulness_score=0.9,
                answer_relevance_score=0.85,
                context_precision_score=0.8,
                created_at=datetime.utcnow(),
            ),
            RAGEvaluation(
                id=eval_mixed_id,
                query="Mixed scores",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                faithfulness_score=0.9,
                answer_relevance_score=0.5,  # Too low
                context_precision_score=0.8,
                created_at=datetime.utcnow(),
            ),
        ]

        for eval_record in evaluations:
            db_session.add(eval_record)
        db_session.commit()

        # Act - Apply all three filters
        response = client.get(
            "/evaluation/history"
            "?min_faithfulness=0.8"
            "&min_answer_relevance=0.8"
            "&min_context_precision=0.7"
        )

        # Assert - Only eval-all-high should pass all filters
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total"] == 1
        assert data["evaluations"][0]["id"] == eval_all_high_id

    def test_get_history_empty_results(self, client, db_session):
        """Test history endpoint with no matching evaluations."""
        # Act
        response = client.get("/evaluation/history")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total"] == 0
        assert data["evaluations"] == []

    def test_get_history_invalid_page(self, client):
        """Test validation for invalid page number."""
        # Act
        response = client.get("/evaluation/history?page=0")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_history_invalid_limit(self, client):
        """Test validation for invalid limit."""
        # Act
        response = client.get("/evaluation/history?limit=200")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_history_ordered_by_date(self, client, db_session):
        """Test that history is ordered by created_at descending."""
        # Arrange - Create evaluations with different timestamps
        now = datetime.utcnow()
        eval_oldest_id = generate_uuid()
        eval_newest_id = generate_uuid()
        eval_middle_id = generate_uuid()

        evaluations = [
            RAGEvaluation(
                id=eval_oldest_id,
                query="Oldest",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                created_at=now - timedelta(days=3),
            ),
            RAGEvaluation(
                id=eval_newest_id,
                query="Newest",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                created_at=now,
            ),
            RAGEvaluation(
                id=eval_middle_id,
                query="Middle",
                retrieved_chunk_ids=json.dumps([generate_uuid()]),
                created_at=now - timedelta(days=1),
            ),
        ]

        for eval_record in evaluations:
            db_session.add(eval_record)
        db_session.commit()

        # Act
        response = client.get("/evaluation/history")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should be ordered newest to oldest
        assert data["evaluations"][0]["id"] == eval_newest_id
        assert data["evaluations"][1]["id"] == eval_middle_id
        assert data["evaluations"][2]["id"] == eval_oldest_id
