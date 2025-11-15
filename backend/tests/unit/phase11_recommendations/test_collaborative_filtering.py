"""
Unit tests for Collaborative Filtering Service (Phase 11).

Tests NCF model initialization, training, and prediction functionality.
Uses mocked PyTorch models to avoid loading actual weights.
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import numpy as np
import pytest
import torch

from backend.app.database.models import User, UserInteraction, Resource
from backend.app.services.collaborative_filtering_service import (
    CollaborativeFilteringService,
    NCFModel
)


class TestNCFModel:
    """Test NCF model architecture."""
    
    def test_model_initialization(self):
        """Test NCF model initialization with correct dimensions."""
        num_users = 100
        num_items = 500
        embedding_dim = 64
        
        model = NCFModel(num_users, num_items, embedding_dim)
        
        assert model.num_users == num_users
        assert model.num_items == num_items
        assert model.embedding_dim == embedding_dim
        
        # Check embedding layers
        assert model.user_embedding.num_embeddings == num_users
        assert model.user_embedding.embedding_dim == embedding_dim
        assert model.item_embedding.num_embeddings == num_items
        assert model.item_embedding.embedding_dim == embedding_dim
        
        # Check MLP layers
        assert model.fc1.in_features == embedding_dim * 2
        assert model.fc1.out_features == 128
        assert model.fc2.in_features == 128
        assert model.fc2.out_features == 64
        assert model.fc3.in_features == 64
        assert model.fc3.out_features == 32
        assert model.fc4.in_features == 32
        assert model.fc4.out_features == 1
    
    def test_model_forward_pass(self):
        """Test forward pass produces correct output shape."""
        model = NCFModel(num_users=10, num_items=20, embedding_dim=64)
        model.eval()
        
        # Create sample input
        user_ids = torch.LongTensor([0, 1, 2])
        item_ids = torch.LongTensor([5, 10, 15])
        
        with torch.no_grad():
            output = model(user_ids, item_ids)
        
        # Check output shape and range
        assert output.shape == (3,)
        assert torch.all(output >= 0.0)
        assert torch.all(output <= 1.0)
    
    def test_model_cuda_vs_cpu(self):
        """Test model works on both CUDA and CPU."""
        model = NCFModel(num_users=10, num_items=20, embedding_dim=64)
        
        # Test CPU
        device = torch.device("cpu")
        model.to(device)
        user_ids = torch.LongTensor([0, 1]).to(device)
        item_ids = torch.LongTensor([5, 10]).to(device)
        
        with torch.no_grad():
            output = model(user_ids, item_ids)
        
        assert output.device.type == "cpu"
        
        # Test CUDA if available
        if torch.cuda.is_available():
            device = torch.device("cuda")
            model.to(device)
            user_ids = user_ids.to(device)
            item_ids = item_ids.to(device)
            
            with torch.no_grad():
                output = model(user_ids, item_ids)
            
            assert output.device.type == "cuda"


class TestCollaborativeFilteringService:
    """Test Collaborative Filtering Service."""
    
    @pytest.fixture
    def temp_model_path(self):
        """Create temporary model path for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield os.path.join(tmpdir, "test_model.pt")
    
    @pytest.fixture
    def service(self, db_session, temp_model_path):
        """Create CollaborativeFilteringService instance."""
        return CollaborativeFilteringService(db_session, model_path=temp_model_path)
    
    @pytest.fixture
    def sample_users(self, db_session):
        """Create sample users."""
        users = []
        for i in range(5):
            user = User(
                id=uuid4(),
                email=f"user{i}@test.com",
                username=f"user{i}"
            )
            db_session.add(user)
            users.append(user)
        
        db_session.commit()
        return users
    
    @pytest.fixture
    def sample_resources(self, db_session):
        """Create sample resources."""
        resources = []
        for i in range(10):
            resource = Resource(
                id=uuid4(),
                title=f"Resource {i}",
                embedding=json.dumps([0.1] * 768)
            )
            db_session.add(resource)
            resources.append(resource)
        
        db_session.commit()
        return resources
    
    @pytest.fixture
    def sample_interactions(self, db_session, sample_users, sample_resources):
        """Create sample interactions."""
        interactions = []
        
        # Create positive interactions
        for i, user in enumerate(sample_users):
            for j in range(3):
                resource = sample_resources[(i * 3 + j) % len(sample_resources)]
                interaction = UserInteraction(
                    id=uuid4(),
                    user_id=user.id,
                    resource_id=resource.id,
                    interaction_type="view",
                    interaction_strength=0.6 + j * 0.1,
                    is_positive=1,
                    confidence=0.7
                )
                db_session.add(interaction)
                interactions.append(interaction)
        
        db_session.commit()
        return interactions
    
    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service.db is not None
        assert service.device is not None
        assert service.model_path is not None
        assert isinstance(service.user_id_to_idx, dict)
        assert isinstance(service.item_id_to_idx, dict)
    
    def test_device_selection(self, service):
        """Test CUDA vs CPU device selection."""
        if torch.cuda.is_available():
            assert service.device.type == "cuda"
        else:
            assert service.device.type == "cpu"
    
    def test_train_model_insufficient_data(self, service):
        """Test training with insufficient data."""
        result = service.train_model(epochs=2, batch_size=32)
        
        assert "error" in result or "num_interactions" in result
        if "num_interactions" in result:
            assert result["num_interactions"] < 10
    
    def test_train_model_success(self, service, sample_interactions):
        """Test successful model training."""
        result = service.train_model(epochs=2, batch_size=32, learning_rate=0.001)
        
        assert result.get("success") is True
        assert "final_loss" in result
        assert "loss_history" in result
        assert "num_users" in result
        assert "num_items" in result
        assert result["epochs"] == 2
        assert len(result["loss_history"]) == 2
        
        # Check model was created
        assert service.model is not None
        assert len(service.user_id_to_idx) > 0
        assert len(service.item_id_to_idx) > 0
    
    def test_save_and_load_model(self, service, sample_interactions, temp_model_path):
        """Test model checkpoint save and load."""
        # Train model
        result = service.train_model(epochs=2, batch_size=32)
        assert result.get("success") is True
        
        # Check model file was created
        assert os.path.exists(temp_model_path)
        
        # Create new service and load model
        new_service = CollaborativeFilteringService(service.db, model_path=temp_model_path)
        
        # Check model was loaded
        assert new_service.model is not None
        assert len(new_service.user_id_to_idx) == len(service.user_id_to_idx)
        assert len(new_service.item_id_to_idx) == len(service.item_id_to_idx)
    
    def test_predict_score_no_model(self, service):
        """Test prediction without trained model."""
        user_id = str(uuid4())
        resource_id = str(uuid4())
        
        score = service.predict_score(user_id, resource_id)
        
        assert score is None
    
    def test_predict_score_unknown_user(self, service, sample_interactions, sample_resources):
        """Test prediction for unknown user."""
        # Train model
        service.train_model(epochs=2, batch_size=32)
        
        # Try to predict for unknown user
        unknown_user_id = str(uuid4())
        resource_id = str(sample_resources[0].id)
        
        score = service.predict_score(unknown_user_id, resource_id)
        
        assert score is None
    
    def test_predict_score_unknown_resource(self, service, sample_interactions, sample_users):
        """Test prediction for unknown resource."""
        # Train model
        service.train_model(epochs=2, batch_size=32)
        
        # Try to predict for unknown resource
        user_id = str(sample_users[0].id)
        unknown_resource_id = str(uuid4())
        
        score = service.predict_score(user_id, unknown_resource_id)
        
        assert score is None
    
    def test_predict_score_success(self, service, sample_interactions, sample_users, sample_resources):
        """Test successful score prediction."""
        # Train model
        service.train_model(epochs=2, batch_size=32)
        
        # Predict score
        user_id = str(sample_users[0].id)
        resource_id = str(sample_resources[0].id)
        
        score = service.predict_score(user_id, resource_id)
        
        assert score is not None
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_get_top_recommendations_no_model(self, service):
        """Test recommendations without trained model."""
        user_id = str(uuid4())
        candidate_ids = [str(uuid4()) for _ in range(5)]
        
        recommendations = service.get_top_recommendations(user_id, candidate_ids, limit=3)
        
        assert recommendations == []
    
    def test_get_top_recommendations_unknown_user(self, service, sample_interactions, sample_resources):
        """Test recommendations for unknown user."""
        # Train model
        service.train_model(epochs=2, batch_size=32)
        
        # Try to get recommendations for unknown user
        unknown_user_id = str(uuid4())
        candidate_ids = [str(r.id) for r in sample_resources[:5]]
        
        recommendations = service.get_top_recommendations(unknown_user_id, candidate_ids, limit=3)
        
        assert recommendations == []
    
    def test_get_top_recommendations_no_valid_candidates(self, service, sample_interactions, sample_users):
        """Test recommendations with no valid candidates."""
        # Train model
        service.train_model(epochs=2, batch_size=32)
        
        # Try with unknown candidates
        user_id = str(sample_users[0].id)
        candidate_ids = [str(uuid4()) for _ in range(5)]
        
        recommendations = service.get_top_recommendations(user_id, candidate_ids, limit=3)
        
        assert recommendations == []
    
    def test_get_top_recommendations_success(self, service, sample_interactions, sample_users, sample_resources):
        """Test successful batch recommendations."""
        # Train model
        service.train_model(epochs=2, batch_size=32)
        
        # Get recommendations
        user_id = str(sample_users[0].id)
        candidate_ids = [str(r.id) for r in sample_resources[:7]]
        
        recommendations = service.get_top_recommendations(user_id, candidate_ids, limit=3)
        
        assert len(recommendations) <= 3
        assert len(recommendations) > 0
        
        # Check structure
        for rec in recommendations:
            assert "resource_id" in rec
            assert "score" in rec
            assert isinstance(rec["score"], float)
            assert 0.0 <= rec["score"] <= 1.0
        
        # Check sorted by score descending
        scores = [rec["score"] for rec in recommendations]
        assert scores == sorted(scores, reverse=True)
    
    def test_get_top_recommendations_respects_limit(self, service, sample_interactions, sample_users, sample_resources):
        """Test that recommendations respect the limit parameter."""
        # Train model
        service.train_model(epochs=2, batch_size=32)
        
        # Get recommendations with different limits
        user_id = str(sample_users[0].id)
        candidate_ids = [str(r.id) for r in sample_resources]
        
        recommendations_5 = service.get_top_recommendations(user_id, candidate_ids, limit=5)
        recommendations_3 = service.get_top_recommendations(user_id, candidate_ids, limit=3)
        
        assert len(recommendations_5) <= 5
        assert len(recommendations_3) <= 3
        assert len(recommendations_3) <= len(recommendations_5)
    
    @patch('torch.save')
    def test_save_model_error_handling(self, mock_save, service, sample_interactions):
        """Test error handling during model save."""
        # Train model
        service.train_model(epochs=1, batch_size=32)
        
        # Mock save to raise exception
        mock_save.side_effect = Exception("Save failed")
        
        # Try to save
        result = service._save_model()
        
        assert result is False
    
    @patch('torch.load')
    def test_load_model_error_handling(self, mock_load, db_session, temp_model_path):
        """Test error handling during model load."""
        # Create a dummy file
        with open(temp_model_path, 'w') as f:
            f.write("dummy")
        
        # Mock load to raise exception
        mock_load.side_effect = Exception("Load failed")
        
        # Try to load
        service = CollaborativeFilteringService(db_session, model_path=temp_model_path)
        
        # Model should not be loaded
        assert service.model is None
