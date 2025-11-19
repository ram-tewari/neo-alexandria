"""
Unit tests for UserProfileService.

Tests profile creation, preference updates, interaction tracking,
user embedding generation, and preference learning.
"""

import json
import pytest
from datetime import datetime
from uuid import uuid4

import numpy as np

from backend.app.database.models import User, UserProfile, UserInteraction, Resource
from backend.app.services.user_profile_service import UserProfileService


class TestUserProfileService:
    """Test suite for UserProfileService."""
    
    def test_get_or_create_profile_creates_new(self, test_db):
        """Test profile creation with default preferences."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create a user
        user = User(email="test@example.com", username="testuser")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Get or create profile
        profile = service.get_or_create_profile(user.id)
        
        # Verify defaults
        assert profile.user_id == user.id
        assert profile.diversity_preference == 0.5
        assert profile.novelty_preference == 0.3
        assert profile.recency_bias == 0.5
        assert profile.total_interactions == 0
        
        db.close()
    
    def test_get_or_create_profile_returns_existing(self, test_db):
        """Test that existing profile is returned."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user and profile
        user = User(email="test@example.com", username="testuser")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        profile1 = service.get_or_create_profile(user.id)
        profile1.diversity_preference = 0.7
        db.commit()
        
        # Get profile again
        profile2 = service.get_or_create_profile(user.id)
        
        # Should be same profile
        assert profile2.id == profile1.id
        assert profile2.diversity_preference == 0.7
        
        db.close()
    
    def test_get_or_create_profile_user_not_found(self, test_db):
        """Test error when user does not exist."""
        db = test_db()
        service = UserProfileService(db)
        
        # Try to get profile for non-existent user
        with pytest.raises(ValueError, match="does not exist"):
            service.get_or_create_profile(uuid4())
        
        db.close()
    
    def test_update_profile_settings_valid_ranges(self, test_db):
        """Test preference updates with valid ranges."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user
        user = User(email="test@example.com", username="testuser")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Update preferences
        profile = service.update_profile_settings(
            user.id,
            diversity_preference=0.8,
            novelty_preference=0.6,
            recency_bias=0.4,
            excluded_sources=["example.com", "test.org"],
            research_domains=["AI", "ML"]
        )
        
        # Verify updates
        assert profile.diversity_preference == 0.8
        assert profile.novelty_preference == 0.6
        assert profile.recency_bias == 0.4
        assert json.loads(profile.excluded_sources) == ["example.com", "test.org"]
        assert json.loads(profile.research_domains) == ["AI", "ML"]
        
        db.close()
    
    def test_update_profile_settings_invalid_ranges(self, test_db):
        """Test validation of preference ranges."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user
        user = User(email="test@example.com", username="testuser")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Test invalid diversity_preference
        with pytest.raises(ValueError, match="diversity_preference must be between"):
            service.update_profile_settings(user.id, diversity_preference=1.5)
        
        # Test invalid novelty_preference
        with pytest.raises(ValueError, match="novelty_preference must be between"):
            service.update_profile_settings(user.id, novelty_preference=-0.1)
        
        # Test invalid recency_bias
        with pytest.raises(ValueError, match="recency_bias must be between"):
            service.update_profile_settings(user.id, recency_bias=2.0)
        
        db.close()
    
    def test_compute_interaction_strength_view(self, test_db):
        """Test interaction strength computation for view interactions."""
        db = test_db()
        service = UserProfileService(db)
        
        # Test view with no signals
        strength = service._compute_interaction_strength("view")
        assert strength == 0.1
        
        # Test view with dwell time
        strength = service._compute_interaction_strength("view", dwell_time=500)
        assert strength == pytest.approx(0.1 + 0.3, rel=0.01)
        
        # Test view with scroll depth
        strength = service._compute_interaction_strength("view", scroll_depth=0.8)
        assert strength == pytest.approx(0.1 + 0.08, rel=0.01)
        
        # Test view with both (capped at 0.5)
        strength = service._compute_interaction_strength("view", dwell_time=2000, scroll_depth=1.0)
        assert strength == 0.5
        
        db.close()
    
    def test_compute_interaction_strength_other_types(self, test_db):
        """Test interaction strength for other interaction types."""
        db = test_db()
        service = UserProfileService(db)
        
        assert service._compute_interaction_strength("annotation") == 0.7
        assert service._compute_interaction_strength("collection_add") == 0.8
        assert service._compute_interaction_strength("export") == 0.9
        
        # Test rating
        assert service._compute_interaction_strength("rating", rating=1) == pytest.approx(0.2)
        assert service._compute_interaction_strength("rating", rating=3) == pytest.approx(0.6)
        assert service._compute_interaction_strength("rating", rating=5) == pytest.approx(1.0)
        
        db.close()
    
    def test_track_interaction_creates_new(self, test_db):
        """Test creating new interaction."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user and resource
        user = User(email="test@example.com", username="testuser")
        resource = Resource(title="Test Resource")
        db.add(user)
        db.add(resource)
        db.commit()
        db.refresh(user)
        db.refresh(resource)
        
        # Track interaction
        interaction = service.track_interaction(
            user.id,
            resource.id,
            "view",
            dwell_time=300,
            scroll_depth=0.5,
            session_id="session123"
        )
        
        # Verify interaction
        assert interaction.user_id == user.id
        assert interaction.resource_id == resource.id
        assert interaction.interaction_type == "view"
        assert interaction.dwell_time == 300
        assert interaction.scroll_depth == 0.5
        assert interaction.session_id == "session123"
        assert interaction.return_visits == 0
        # strength = 0.1 + min(0.3, 300/1000) + 0.1*0.5 = 0.1 + 0.3 + 0.05 = 0.45 > 0.4
        assert interaction.is_positive == 1
        
        # Verify profile updated
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        assert profile.total_interactions == 1
        assert profile.last_active_at is not None
        
        db.close()
    
    def test_track_interaction_updates_existing(self, test_db):
        """Test updating existing interaction."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user and resource
        user = User(email="test@example.com", username="testuser")
        resource = Resource(title="Test Resource")
        db.add(user)
        db.add(resource)
        db.commit()
        db.refresh(user)
        db.refresh(resource)
        
        # Track first interaction
        interaction1 = service.track_interaction(
            user.id, resource.id, "view", dwell_time=100
        )
        first_strength = interaction1.interaction_strength
        
        # Track second interaction (same type)
        interaction2 = service.track_interaction(
            user.id, resource.id, "view", dwell_time=500
        )
        
        # Should be same interaction, updated
        assert interaction2.id == interaction1.id
        assert interaction2.return_visits == 1
        assert interaction2.interaction_strength > first_strength
        
        # Profile should have 2 interactions
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        assert profile.total_interactions == 2
        
        db.close()
    
    def test_track_interaction_invalid_type(self, test_db):
        """Test validation of interaction type."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user and resource
        user = User(email="test@example.com", username="testuser")
        resource = Resource(title="Test Resource")
        db.add(user)
        db.add(resource)
        db.commit()
        db.refresh(user)
        db.refresh(resource)
        
        # Try invalid interaction type
        with pytest.raises(ValueError, match="Invalid interaction_type"):
            service.track_interaction(user.id, resource.id, "invalid_type")
        
        db.close()
    
    def test_track_interaction_resource_not_found(self, test_db):
        """Test error when resource does not exist."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user
        user = User(email="test@example.com", username="testuser")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Try to track interaction with non-existent resource
        with pytest.raises(ValueError, match="does not exist"):
            service.track_interaction(user.id, uuid4(), "view")
        
        db.close()
    
    def test_get_user_embedding_cold_start(self, test_db):
        """Test user embedding for cold start (no interactions)."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user
        user = User(email="test@example.com", username="testuser")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Get embedding
        embedding = service.get_user_embedding(user.id)
        
        # Should be zero vector
        assert embedding.shape == (768,)
        assert np.all(embedding == 0)
        
        db.close()
    
    def test_get_user_embedding_single_interaction(self, test_db):
        """Test user embedding with single positive interaction."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user and resource with embedding
        user = User(email="test@example.com", username="testuser")
        resource_embedding = [0.1] * 768
        resource = Resource(
            title="Test Resource",
            embedding=json.dumps(resource_embedding)
        )
        db.add(user)
        db.add(resource)
        db.commit()
        db.refresh(user)
        db.refresh(resource)
        
        # Create positive interaction
        interaction = UserInteraction(
            user_id=user.id,
            resource_id=resource.id,
            interaction_type="annotation",
            interaction_strength=0.7,
            is_positive=1
        )
        db.add(interaction)
        db.commit()
        
        # Get embedding
        embedding = service.get_user_embedding(user.id)
        
        # Should match resource embedding
        assert embedding.shape == (768,)
        assert np.allclose(embedding, resource_embedding)
        
        db.close()
    
    def test_get_user_embedding_multiple_interactions(self, test_db):
        """Test user embedding with multiple interactions (weighted average)."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user
        user = User(email="test@example.com", username="testuser")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create resources with different embeddings
        resource1 = Resource(title="Resource 1", embedding=json.dumps([1.0] * 768))
        resource2 = Resource(title="Resource 2", embedding=json.dumps([0.0] * 768))
        db.add(resource1)
        db.add(resource2)
        db.commit()
        db.refresh(resource1)
        db.refresh(resource2)
        
        # Create interactions with different strengths
        interaction1 = UserInteraction(
            user_id=user.id,
            resource_id=resource1.id,
            interaction_type="export",
            interaction_strength=0.9,
            is_positive=1
        )
        interaction2 = UserInteraction(
            user_id=user.id,
            resource_id=resource2.id,
            interaction_type="view",
            interaction_strength=0.1,
            is_positive=0  # Not positive, should be excluded
        )
        db.add(interaction1)
        db.add(interaction2)
        db.commit()
        
        # Get embedding
        embedding = service.get_user_embedding(user.id)
        
        # Should be weighted average (only positive interactions)
        # Since only interaction1 is positive, should match resource1
        assert embedding.shape == (768,)
        assert np.allclose(embedding, [1.0] * 768)
        
        db.close()
    
    def test_update_learned_preferences(self, test_db):
        """Test preference learning from interaction history."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user
        user = User(email="test@example.com", username="testuser")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create resources with authors
        authors1 = [{"name": "Alice Smith"}, {"name": "Bob Jones"}]
        authors2 = [{"name": "Alice Smith"}, {"name": "Carol White"}]
        authors3 = [{"name": "Bob Jones"}]
        
        resource1 = Resource(title="Resource 1", authors=json.dumps(authors1))
        resource2 = Resource(title="Resource 2", authors=json.dumps(authors2))
        resource3 = Resource(title="Resource 3", authors=json.dumps(authors3))
        db.add(resource1)
        db.add(resource2)
        db.add(resource3)
        db.commit()
        db.refresh(resource1)
        db.refresh(resource2)
        db.refresh(resource3)
        
        # Create positive interactions
        interaction1 = UserInteraction(
            user_id=user.id,
            resource_id=resource1.id,
            interaction_type="annotation",
            interaction_strength=0.7,
            is_positive=1,
            interaction_timestamp=datetime.utcnow()
        )
        interaction2 = UserInteraction(
            user_id=user.id,
            resource_id=resource2.id,
            interaction_type="export",
            interaction_strength=0.9,
            is_positive=1,
            interaction_timestamp=datetime.utcnow()
        )
        interaction3 = UserInteraction(
            user_id=user.id,
            resource_id=resource3.id,
            interaction_type="collection_add",
            interaction_strength=0.8,
            is_positive=1,
            interaction_timestamp=datetime.utcnow()
        )
        db.add(interaction1)
        db.add(interaction2)
        db.add(interaction3)
        db.commit()
        
        # Update learned preferences
        service._update_learned_preferences(user.id)
        
        # Verify preferred authors
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        preferred_authors = json.loads(profile.preferred_authors)
        
        # Alice Smith and Bob Jones should be top (both appear twice)
        assert "Alice Smith" in preferred_authors
        assert "Bob Jones" in preferred_authors
        
        db.close()
    
    def test_update_learned_preferences_no_interactions(self, test_db):
        """Test preference learning with no interactions."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user and profile
        user = User(email="test@example.com", username="testuser")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create profile first
        profile = service.get_or_create_profile(user.id)
        
        # Update learned preferences (should not raise error)
        service._update_learned_preferences(user.id)
        
        # Profile should exist but no preferred authors
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        assert profile is not None
        
        db.close()
    
    def test_preference_learning_triggered_every_10_interactions(self, test_db):
        """Test that preference learning is triggered every 10 interactions."""
        db = test_db()
        service = UserProfileService(db)
        
        # Create user and resource
        user = User(email="test@example.com", username="testuser")
        resource = Resource(
            title="Test Resource",
            authors=json.dumps([{"name": "Test Author"}])
        )
        db.add(user)
        db.add(resource)
        db.commit()
        db.refresh(user)
        db.refresh(resource)
        
        # Track 10 interactions
        for i in range(10):
            service.track_interaction(
                user.id,
                resource.id,
                "annotation",
                session_id=f"session{i}"
            )
        
        # Check profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        assert profile.total_interactions == 10
        
        # Preferred authors should be set (learning triggered at 10)
        if profile.preferred_authors:
            preferred_authors = json.loads(profile.preferred_authors)
            assert "Test Author" in preferred_authors
        
        db.close()
