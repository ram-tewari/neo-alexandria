"""
User Profile Service for Phase 11 Hybrid Recommendation Engine.

This service manages user profiles, tracks interactions, generates user embeddings,
and learns user preferences from interaction history.

Related files:
- app/database/models.py: UserProfile, UserInteraction, User models
- app/services/hybrid_recommendation_service.py: Uses user profiles for recommendations
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import numpy as np
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..database.models import User, UserProfile, UserInteraction, Resource
from ..utils.performance_monitoring import timing_decorator, metrics
from ..shared.event_bus import event_bus, EventPriority
from ..events.event_types import SystemEvent

logger = logging.getLogger(__name__)


class UserProfileService:
    """
    Service for managing user profiles and interaction tracking.
    
    Provides methods for:
    - Profile creation and management
    - Interaction tracking with implicit feedback
    - User embedding generation
    - Preference learning from interaction history
    """
    
    def __init__(self, db: Session):
        """
        Initialize the UserProfileService.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        
        # In-memory cache for user embeddings with 5-minute TTL
        # Cache structure: {user_id: (embedding, timestamp)}
        self._embedding_cache: Dict[UUID, Tuple[np.ndarray, float]] = {}
        self._cache_ttl = 300  # 5 minutes in seconds
    
    def get_or_create_profile(self, user_id: UUID) -> UserProfile:
        """
        Get existing user profile or create with default preferences.
        
        Creates profile with default settings:
        - diversity_preference: 0.5
        - novelty_preference: 0.3
        - recency_bias: 0.5
        
        Args:
            user_id: User UUID
            
        Returns:
            UserProfile instance
            
        Raises:
            ValueError: If user does not exist
        """
        try:
            # Check if user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User not found: {user_id}")
                raise ValueError(f"User with id {user_id} does not exist")
            
            # Try to get existing profile
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if profile:
                logger.info(f"Retrieved existing profile for user {user_id}")
                return profile
            
            # Create new profile with defaults
            profile = UserProfile(
                user_id=user_id,
                diversity_preference=0.5,
                novelty_preference=0.3,
                recency_bias=0.5,
                total_interactions=0
            )
            
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            
            logger.info(f"Created new profile for user {user_id} with default preferences")
            return profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error in get_or_create_profile for user {user_id}: {str(e)}", exc_info=True)
            raise
    
    def update_profile_settings(
        self,
        user_id: UUID,
        diversity_preference: Optional[float] = None,
        novelty_preference: Optional[float] = None,
        recency_bias: Optional[float] = None,
        excluded_sources: Optional[List[str]] = None,
        research_domains: Optional[List[str]] = None,
        active_domain: Optional[str] = None
    ) -> UserProfile:
        """
        Update user profile settings with input validation.
        
        Validates that preference values are in range [0.0, 1.0].
        
        Args:
            user_id: User UUID
            diversity_preference: Diversity preference (0.0-1.0), optional
            novelty_preference: Novelty preference (0.0-1.0), optional
            recency_bias: Recency bias (0.0-1.0), optional
            excluded_sources: List of excluded source domains, optional
            research_domains: List of research domains, optional
            active_domain: Currently active research domain, optional
            
        Returns:
            Updated UserProfile instance
            
        Raises:
            ValueError: If preference values are out of range [0.0, 1.0]
        """
        try:
            # Validate preference ranges
            if diversity_preference is not None:
                if not 0.0 <= diversity_preference <= 1.0:
                    raise ValueError(f"diversity_preference must be between 0.0 and 1.0, got {diversity_preference}")
            
            if novelty_preference is not None:
                if not 0.0 <= novelty_preference <= 1.0:
                    raise ValueError(f"novelty_preference must be between 0.0 and 1.0, got {novelty_preference}")
            
            if recency_bias is not None:
                if not 0.0 <= recency_bias <= 1.0:
                    raise ValueError(f"recency_bias must be between 0.0 and 1.0, got {recency_bias}")
            
            # Get or create profile
            profile = self.get_or_create_profile(user_id)
            
            # Update preferences
            if diversity_preference is not None:
                profile.diversity_preference = diversity_preference
            if novelty_preference is not None:
                profile.novelty_preference = novelty_preference
            if recency_bias is not None:
                profile.recency_bias = recency_bias
            
            # Update JSON fields
            if excluded_sources is not None:
                profile.excluded_sources = json.dumps(excluded_sources)
            if research_domains is not None:
                profile.research_domains = json.dumps(research_domains)
            if active_domain is not None:
                profile.active_domain = active_domain
            
            self.db.commit()
            self.db.refresh(profile)
            
            logger.info(f"Updated profile settings for user {user_id}")
            return profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error in update_profile_settings for user {user_id}: {str(e)}", exc_info=True)
            raise

    def _compute_interaction_strength(
        self,
        interaction_type: str,
        dwell_time: Optional[int] = None,
        scroll_depth: Optional[float] = None,
        rating: Optional[int] = None
    ) -> float:
        """
        Compute interaction strength score based on interaction type and signals.
        
        Scoring formula:
        - view: 0.1 + min(0.3, dwell_time/1000) + 0.1*scroll_depth (max 0.5)
        - annotation: 0.7
        - collection_add: 0.8
        - export: 0.9
        - rating: 0.5 baseline, adjusted by rating value
        
        Args:
            interaction_type: Type of interaction
            dwell_time: Time spent on resource in seconds
            scroll_depth: Scroll depth (0.0-1.0)
            rating: Rating value (1-5 stars)
            
        Returns:
            Interaction strength score (0.0-1.0)
        """
        if interaction_type == "view":
            strength = 0.1
            if dwell_time is not None:
                strength += min(0.3, dwell_time / 1000.0)
            if scroll_depth is not None:
                strength += 0.1 * scroll_depth
            return min(strength, 0.5)
        
        elif interaction_type == "annotation":
            return 0.7
        
        elif interaction_type == "collection_add":
            return 0.8
        
        elif interaction_type == "export":
            return 0.9
        
        elif interaction_type == "rating":
            if rating is not None:
                # Scale rating (1-5) to strength (0.2-1.0)
                return 0.2 + (rating - 1) * 0.2
            return 0.5
        
        else:
            logger.warning(f"Unknown interaction type: {interaction_type}, defaulting to 0.1")
            return 0.1
    
    @timing_decorator(target_ms=50.0)
    def track_interaction(
        self,
        user_id: UUID,
        resource_id: UUID,
        interaction_type: str,
        dwell_time: Optional[int] = None,
        scroll_depth: Optional[float] = None,
        session_id: Optional[str] = None,
        rating: Optional[int] = None
    ) -> UserInteraction:
        """
        Track user-resource interaction with implicit feedback signals.
        
        Handles duplicate interactions by updating return_visits and max interaction_strength.
        Updates UserProfile.total_interactions and last_active_at.
        
        Args:
            user_id: User UUID
            resource_id: Resource UUID
            interaction_type: Type of interaction (view, annotation, collection_add, export, rating)
            dwell_time: Time spent on resource in seconds, optional
            scroll_depth: Scroll depth (0.0-1.0), optional
            session_id: Session identifier, optional
            rating: Rating value (1-5 stars), optional
            
        Returns:
            UserInteraction instance
            
        Raises:
            ValueError: If interaction_type is invalid or resource does not exist
        """
        try:
            # Validate interaction type
            allowed_types = ["view", "annotation", "collection_add", "export", "rating"]
            if interaction_type not in allowed_types:
                raise ValueError(f"Invalid interaction_type: {interaction_type}. Must be one of {allowed_types}")
            
            # Check if resource exists
            resource = self.db.query(Resource).filter(Resource.id == resource_id).first()
            if not resource:
                raise ValueError(f"Resource with id {resource_id} does not exist")
            
            # Compute interaction strength
            interaction_strength = self._compute_interaction_strength(
                interaction_type, dwell_time, scroll_depth, rating
            )
            
            # Check for existing interaction
            existing = self.db.query(UserInteraction).filter(
                UserInteraction.user_id == user_id,
                UserInteraction.resource_id == resource_id,
                UserInteraction.interaction_type == interaction_type
            ).first()
            
            if existing:
                # Update existing interaction
                existing.return_visits += 1
                existing.interaction_strength = max(existing.interaction_strength, interaction_strength)
                existing.interaction_timestamp = datetime.utcnow()
                
                # Update optional fields if provided
                if dwell_time is not None:
                    existing.dwell_time = dwell_time
                if scroll_depth is not None:
                    existing.scroll_depth = scroll_depth
                if rating is not None:
                    existing.rating = rating
                if session_id is not None:
                    existing.session_id = session_id
                
                # Update derived fields
                existing.is_positive = 1 if existing.interaction_strength > 0.4 else 0
                existing.confidence = min(1.0, existing.return_visits * 0.2 + existing.interaction_strength * 0.5)
                
                interaction = existing
                logger.info(f"Updated existing interaction for user {user_id}, resource {resource_id}, type {interaction_type}")
            else:
                # Create new interaction
                interaction = UserInteraction(
                    user_id=user_id,
                    resource_id=resource_id,
                    interaction_type=interaction_type,
                    interaction_strength=interaction_strength,
                    dwell_time=dwell_time,
                    scroll_depth=scroll_depth,
                    session_id=session_id,
                    rating=rating,
                    return_visits=0,
                    is_positive=1 if interaction_strength > 0.4 else 0,
                    confidence=interaction_strength * 0.5,
                    interaction_timestamp=datetime.utcnow()
                )
                self.db.add(interaction)
                logger.info(f"Created new interaction for user {user_id}, resource {resource_id}, type {interaction_type}")
            
            # Update user profile
            profile = self.get_or_create_profile(user_id)
            profile.total_interactions += 1
            profile.last_active_at = datetime.utcnow()
            
            # Invalidate cached embedding for this user (new interaction changes embedding)
            if user_id in self._embedding_cache:
                del self._embedding_cache[user_id]
                logger.debug(f"Invalidated embedding cache for user {user_id} due to new interaction")
            
            # Trigger preference learning every 10 interactions
            if profile.total_interactions % 10 == 0:
                self._update_learned_preferences(user_id)
            
            # Periodically clear expired cache entries (every 50 interactions)
            if profile.total_interactions % 50 == 0:
                self._clear_expired_cache_entries()
            
            self.db.commit()
            self.db.refresh(interaction)
            
            # Emit user.interaction_tracked event
            event_bus.emit(
                SystemEvent.USER_INTERACTION_TRACKED.value,
                {
                    "user_id": str(user_id),
                    "resource_id": str(resource_id),
                    "interaction_type": interaction_type,
                    "total_interactions": profile.total_interactions,
                    "interaction_strength": interaction_strength
                },
                priority=EventPriority.LOW
            )
            
            return interaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error in track_interaction for user {user_id}, resource {resource_id}: {str(e)}", exc_info=True)
            raise

    @timing_decorator(target_ms=10.0)
    def get_user_embedding(self, user_id: UUID) -> np.ndarray:
        """
        Compute user embedding as weighted average of resource embeddings.
        
        Queries positive interactions (is_positive=True) limited to 100 most recent.
        Returns zero vector (768-dim) for cold start users with no interactions.
        Uses in-memory cache with 5-minute TTL for performance.
        
        Args:
            user_id: User UUID
            
        Returns:
            User embedding as numpy array (768-dimensional)
        """
        try:
            # Check cache first
            cache_key = user_id
            current_time = time.time()
            
            if cache_key in self._embedding_cache:
                cached_embedding, cached_time = self._embedding_cache[cache_key]
                
                # Check if cache entry is still valid (within TTL)
                if current_time - cached_time < self._cache_ttl:
                    logger.debug(f"Cache hit for user embedding: {user_id}")
                    metrics.record_cache_hit()
                    return cached_embedding
                else:
                    # Cache expired, remove entry
                    logger.debug(f"Cache expired for user embedding: {user_id}")
                    del self._embedding_cache[cache_key]
            
            logger.debug(f"Cache miss for user embedding: {user_id}, computing...")
            metrics.record_cache_miss()
            # Query positive interactions, most recent first, limit to 100
            interactions = self.db.query(UserInteraction).filter(
                UserInteraction.user_id == user_id,
                UserInteraction.is_positive == 1
            ).order_by(
                desc(UserInteraction.interaction_timestamp)
            ).limit(100).all()
            
            # Cold start: no positive interactions
            if not interactions:
                logger.info(f"Cold start: user {user_id} has no positive interactions, returning zero vector")
                return np.zeros(768)
            
            # Collect embeddings and weights
            embeddings = []
            weights = []
            
            # Batch query resources to avoid N+1 problem
            resource_ids = [interaction.resource_id for interaction in interactions]
            resources = self.db.query(Resource).filter(
                Resource.id.in_(resource_ids)
            ).limit(100).all()
            
            # Create resource lookup dict
            resource_dict = {resource.id: resource for resource in resources}
            
            for interaction in interactions:
                resource = resource_dict.get(interaction.resource_id)
                
                if not resource or not resource.embedding:
                    continue
                
                try:
                    # Parse embedding JSON
                    if isinstance(resource.embedding, str):
                        embedding = json.loads(resource.embedding)
                    else:
                        embedding = resource.embedding
                    
                    # Validate dimensions
                    if len(embedding) != 768:
                        logger.warning(f"Invalid embedding dimension for resource {resource.id}: {len(embedding)}, expected 768")
                        continue
                    
                    embeddings.append(np.array(embedding))
                    weights.append(interaction.interaction_strength)
                    
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    logger.warning(f"Error parsing embedding for resource {resource.id}: {str(e)}")
                    continue
            
            # If no valid embeddings found, return zero vector
            if not embeddings:
                logger.info(f"No valid embeddings found for user {user_id}, returning zero vector")
                return np.zeros(768)
            
            # Compute weighted average
            embeddings_array = np.array(embeddings)
            weights_array = np.array(weights)
            
            # Normalize weights
            weights_array = weights_array / weights_array.sum()
            
            # Weighted average
            user_embedding = np.average(embeddings_array, axis=0, weights=weights_array)
            
            # Store in cache with current timestamp
            self._embedding_cache[cache_key] = (user_embedding, current_time)
            
            logger.info(f"Computed user embedding for user {user_id} from {len(embeddings)} interactions")
            return user_embedding
            
        except Exception as e:
            logger.error(f"Error in get_user_embedding for user {user_id}: {str(e)}", exc_info=True)
            # Return zero vector on error
            return np.zeros(768)
    
    def _clear_expired_cache_entries(self) -> None:
        """
        Clear expired entries from the embedding cache.
        
        Removes cache entries older than TTL (5 minutes).
        Called periodically to prevent memory bloat.
        """
        try:
            current_time = time.time()
            expired_keys = []
            
            for user_id, (embedding, cached_time) in self._embedding_cache.items():
                if current_time - cached_time >= self._cache_ttl:
                    expired_keys.append(user_id)
            
            for key in expired_keys:
                del self._embedding_cache[key]
            
            if expired_keys:
                logger.debug(f"Cleared {len(expired_keys)} expired cache entries")
        
        except Exception as e:
            logger.warning(f"Error clearing expired cache entries: {str(e)}")

    def _update_learned_preferences(self, user_id: UUID) -> None:
        """
        Analyze interaction history and update learned preferences.
        
        Queries positive interactions from last 90 days, limited to 1000 records.
        Extracts and counts preferred authors from resource.authors JSON field.
        Updates UserProfile with top 10 preferred authors.
        
        Triggered every 10 interactions (total_interactions % 10 == 0).
        
        Args:
            user_id: User UUID
        """
        try:
            # Calculate date 90 days ago
            ninety_days_ago = datetime.utcnow() - timedelta(days=90)
            
            # Query positive interactions from last 90 days
            interactions = self.db.query(UserInteraction).filter(
                UserInteraction.user_id == user_id,
                UserInteraction.is_positive == 1,
                UserInteraction.interaction_timestamp >= ninety_days_ago
            ).order_by(
                desc(UserInteraction.interaction_timestamp)
            ).limit(1000).all()
            
            if not interactions:
                logger.info(f"No positive interactions in last 90 days for user {user_id}")
                return
            
            # Extract preferred authors
            author_counts = {}
            
            # Batch query resources to avoid N+1 problem
            resource_ids = [interaction.resource_id for interaction in interactions]
            resources = self.db.query(Resource).filter(
                Resource.id.in_(resource_ids)
            ).limit(1000).all()
            
            # Create resource lookup dict
            resource_dict = {resource.id: resource for resource in resources}
            
            for interaction in interactions:
                resource = resource_dict.get(interaction.resource_id)
                
                if not resource or not resource.authors:
                    continue
                
                try:
                    # Parse authors JSON
                    if isinstance(resource.authors, str):
                        authors = json.loads(resource.authors)
                    else:
                        authors = resource.authors
                    
                    # Handle different author formats
                    if isinstance(authors, list):
                        for author in authors:
                            if isinstance(author, dict) and 'name' in author:
                                author_name = author['name']
                            elif isinstance(author, str):
                                author_name = author
                            else:
                                continue
                            
                            # Count author occurrences
                            author_counts[author_name] = author_counts.get(author_name, 0) + 1
                    
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    logger.warning(f"Error parsing authors for resource {resource.id}: {str(e)}")
                    continue
            
            # Get top 10 preferred authors
            if author_counts:
                top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                preferred_authors = [author for author, count in top_authors]
                
                # Update profile
                profile = self.get_or_create_profile(user_id)
                profile.preferred_authors = json.dumps(preferred_authors)
                
                self.db.commit()
                
                logger.info(f"Updated learned preferences for user {user_id}: {len(preferred_authors)} preferred authors")
            else:
                logger.info(f"No authors found in interactions for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error in _update_learned_preferences for user {user_id}: {str(e)}", exc_info=True)
            # Don't raise - this is a background operation
