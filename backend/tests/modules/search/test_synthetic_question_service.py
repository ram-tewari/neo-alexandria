"""
Unit tests for SyntheticQuestionService.

Tests question generation from chunks, question quality and relevance,
embedding generation for questions, and configuration toggle.
"""

import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session

from app.modules.search.service import SyntheticQuestionService


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def mock_ai_service():
    """Create a mock AI service."""
    return Mock()


@pytest.fixture
def mock_embedding_service():
    """Create a mock embedding service."""
    service = Mock()
    service.generate_embedding.return_value = [0.1] * 384  # Mock embedding vector
    return service


@pytest.fixture
def question_service(mock_db, mock_ai_service, mock_embedding_service):
    """Create a SyntheticQuestionService instance."""
    return SyntheticQuestionService(
        db=mock_db, ai_service=mock_ai_service, embedding_service=mock_embedding_service
    )


class TestSyntheticQuestionService:
    """Test suite for SyntheticQuestionService."""

    def test_initialization(self, mock_db, mock_ai_service, mock_embedding_service):
        """Test service initialization."""
        service = SyntheticQuestionService(
            mock_db, mock_ai_service, mock_embedding_service
        )

        assert service.db == mock_db
        assert service.ai_service == mock_ai_service
        assert service.embedding_service == mock_embedding_service
        assert service.enabled is True
        assert service.questions_per_chunk == 2

    def test_generate_questions_empty_content(self, question_service):
        """Test question generation with empty content."""
        # Empty string
        questions = question_service.generate_questions("", "chunk_123")
        assert questions == []

        # Whitespace only
        questions = question_service.generate_questions("   ", "chunk_123")
        assert questions == []

    def test_generate_questions_disabled(
        self, mock_db, mock_ai_service, mock_embedding_service
    ):
        """Test that question generation is skipped when disabled."""
        service = SyntheticQuestionService(
            mock_db, mock_ai_service, mock_embedding_service
        )
        service.enabled = False

        text = "Machine Learning is a subset of Artificial Intelligence."
        questions = service.generate_questions(text, "chunk_123")

        assert questions == []

    def test_generate_questions_basic(self, question_service):
        """Test basic question generation from chunk."""
        text = "Machine Learning is a subset of Artificial Intelligence that enables computers to learn from data."

        questions = question_service.generate_questions(text, "chunk_123")

        # Should generate questions
        assert len(questions) > 0
        assert len(questions) <= question_service.questions_per_chunk

        # Check question structure
        for question in questions:
            assert "question_text" in question
            assert "chunk_id" in question
            assert question["chunk_id"] == "chunk_123"
            assert isinstance(question["question_text"], str)
            assert len(question["question_text"]) > 0

    def test_generate_questions_definition_pattern(self, question_service):
        """Test question generation for definition patterns."""
        text = "Neural Networks is a computational model inspired by biological neural networks."

        questions = question_service.generate_questions(text, "chunk_123")

        # Should generate "What is X?" type question
        assert len(questions) > 0
        question_texts = [q["question_text"] for q in questions]
        assert any("what is" in q.lower() for q in question_texts)

    def test_generate_questions_process_pattern(self, question_service):
        """Test question generation for process descriptions."""
        text = "The training process involves feeding data through the network and adjusting weights."

        questions = question_service.generate_questions(text, "chunk_123")

        # Should generate "How does X work?" type question
        assert len(questions) > 0
        question_texts = [q["question_text"] for q in questions]
        assert any("how" in q.lower() for q in question_texts)

    def test_generate_questions_benefits_pattern(self, question_service):
        """Test question generation for benefit descriptions."""
        text = "This approach improves accuracy and provides better generalization to unseen data."

        questions = question_service.generate_questions(text, "chunk_123")

        # Should generate "What are the benefits?" type question
        assert len(questions) > 0
        question_texts = [q["question_text"] for q in questions]
        assert any("benefit" in q.lower() for q in question_texts)

    def test_generate_questions_respects_limit(self, question_service):
        """Test that question generation respects the configured limit."""
        # Set limit to 1
        question_service.questions_per_chunk = 1

        text = "Machine Learning is a process that improves with benefits for many applications."
        questions = question_service.generate_questions(text, "chunk_123")

        # Should generate exactly 1 question
        assert len(questions) == 1

    def test_generate_questions_with_embeddings(self, question_service):
        """Test that embeddings are generated for questions."""
        text = "Deep Learning is a subset of Machine Learning."

        questions = question_service.generate_questions(text, "chunk_123")

        # Should have embedding IDs
        assert len(questions) > 0
        for question in questions:
            assert "embedding_id" in question
            assert question["embedding_id"] is not None

        # Verify embedding service was called
        assert question_service.embedding_service.generate_embedding.called

    def test_generate_questions_without_embedding_service(
        self, mock_db, mock_ai_service
    ):
        """Test question generation without embedding service."""
        service = SyntheticQuestionService(
            mock_db, mock_ai_service, embedding_service=None
        )

        text = "Machine Learning is a subset of Artificial Intelligence."
        questions = service.generate_questions(text, "chunk_123")

        # Should still generate questions
        assert len(questions) > 0

        # But no embedding IDs
        for question in questions:
            assert (
                "embedding_id" not in question or question.get("embedding_id") is None
            )

    def test_generate_questions_embedding_error_handling(self, question_service):
        """Test that embedding errors don't prevent question generation."""
        # Make embedding service raise an error
        question_service.embedding_service.generate_embedding.side_effect = Exception(
            "Embedding error"
        )

        text = "Machine Learning is a subset of Artificial Intelligence."
        questions = question_service.generate_questions(text, "chunk_123")

        # Should still generate questions despite embedding error
        assert len(questions) > 0

    def test_heuristic_question_generation(self, question_service):
        """Test heuristic-based question generation."""
        text = "Convolutional Neural Networks is a deep learning architecture used for image recognition."

        questions = question_service._generate_questions_heuristic(text)

        # Should generate at least one question
        assert len(questions) > 0
        assert all(isinstance(q, str) for q in questions)
        assert all(len(q) > 0 for q in questions)

    def test_question_quality(self, question_service):
        """Test that generated questions are grammatically correct."""
        text = "Transformers is a neural network architecture that uses self-attention mechanisms."

        questions = question_service.generate_questions(text, "chunk_123")

        # Check basic quality criteria
        for question in questions:
            question_text = question["question_text"]

            # Should be a question (ends with ?)
            assert question_text.endswith("?")

            # Should not be empty
            assert len(question_text) > 5

            # Should contain question words
            question_lower = question_text.lower()
            assert any(
                word in question_lower
                for word in ["what", "how", "why", "when", "where", "who"]
            )

    def test_question_relevance(self, question_service):
        """Test that questions are relevant to chunk content."""
        text = "Gradient descent is an optimization algorithm used to minimize the loss function."

        questions = question_service.generate_questions(text, "chunk_123")

        # Questions should reference concepts from the text
        text.lower()
        for question in questions:
            question_lower = question["question_text"].lower()

            # At least one key term from text should appear in question
            # or question should be generic enough to apply to the text
            key_terms = ["gradient", "descent", "optimization", "algorithm", "loss"]
            is_relevant = any(term in question_lower for term in key_terms) or any(
                word in question_lower
                for word in ["this", "approach", "process", "method"]
            )
            assert is_relevant, (
                f"Question '{question['question_text']}' not relevant to text"
            )

    def test_configuration_toggle(
        self, mock_db, mock_ai_service, mock_embedding_service
    ):
        """Test that configuration toggle works."""
        # Test with enabled=True
        service_enabled = SyntheticQuestionService(
            mock_db, mock_ai_service, mock_embedding_service
        )
        service_enabled.enabled = True

        text = "Machine Learning is a subset of AI."
        questions_enabled = service_enabled.generate_questions(text, "chunk_123")
        assert len(questions_enabled) > 0

        # Test with enabled=False
        service_disabled = SyntheticQuestionService(
            mock_db, mock_ai_service, mock_embedding_service
        )
        service_disabled.enabled = False

        questions_disabled = service_disabled.generate_questions(text, "chunk_123")
        assert len(questions_disabled) == 0

    def test_store_embedding(self, question_service):
        """Test embedding storage."""
        embedding = [0.1, 0.2, 0.3] * 128  # 384-dimensional vector

        embedding_id = question_service._store_embedding(embedding)

        # Should return a valid ID
        assert embedding_id is not None
        assert isinstance(embedding_id, str)
        assert len(embedding_id) > 0
