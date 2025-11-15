# Requirements Document

## Introduction

This document specifies requirements for Phase 11 of Neo Alexandria: a state-of-the-art hybrid recommendation engine that combines Neural Collaborative Filtering (NCF), graph-based recommendations, and content similarity with sophisticated ranking, diversity optimization, and personalized user profiles. The system will transform the basic content-based recommendation system into an intelligent, multi-strategy engine that learns from user behavior and provides highly relevant, diverse, and novel recommendations.

## Glossary

- **Recommendation Engine**: The system component that suggests relevant resources to users based on multiple signals
- **NCF (Neural Collaborative Filtering)**: A deep learning approach to collaborative filtering that learns user-item interactions
- **User Profile**: A persistent record of user preferences, interaction history, and recommendation settings
- **User Interaction**: Any user action with a resource (view, annotation, collection add, export, rating)
- **Interaction Strength**: A normalized score (0.0-1.0) representing the intensity of user engagement with a resource
- **Hybrid Strategy**: A recommendation approach combining multiple algorithms (collaborative, content-based, graph-based)
- **Diversity Optimization**: Techniques to ensure recommendations cover varied topics and perspectives
- **Novelty Score**: A metric measuring how different a recommendation is from popular or previously seen items
- **Cold Start**: The challenge of providing recommendations for new users with minimal interaction history
- **MMR (Maximal Marginal Relevance)**: An algorithm that balances relevance and diversity in result ranking
- **Gini Coefficient**: A statistical measure of diversity (0 = perfect diversity, 1 = no diversity)
- **User Embedding**: A vector representation of user preferences learned from interaction history
- **Candidate Generation**: The first stage of recommendation that produces a broad set of potential items
- **Ranking Stage**: The second stage that scores and orders candidates by predicted relevance

## Requirements

### Requirement 1: User Profile Management

**User Story:** As a researcher, I want the system to learn my preferences over time, so that recommendations become increasingly personalized to my research interests.

#### Acceptance Criteria

1. WHEN a user first accesses the recommendation system, THE Recommendation Engine SHALL create a UserProfile with default preference settings (diversity=0.5, novelty=0.3, recency=0.5)
2. THE Recommendation Engine SHALL store user research domains, active domain, preferred taxonomy categories, preferred authors, and excluded sources in the UserProfile
3. WHEN a user completes 10 interactions, THE Recommendation Engine SHALL update learned preferences by analyzing interaction history from the previous 90 days
4. THE Recommendation Engine SHALL maintain interaction metrics including total_interactions count, average_session_duration, and last_active_at timestamp
5. WHERE a user explicitly updates preference settings, THE Recommendation Engine SHALL validate that diversity_preference, novelty_preference, and recency_bias values are between 0.0 and 1.0

### Requirement 2: Interaction Tracking

**User Story:** As a system, I want to capture detailed user-resource interactions, so that I can learn patterns and improve recommendation quality.

#### Acceptance Criteria

1. WHEN a user views a resource, THE Recommendation Engine SHALL create a UserInteraction record with interaction_type "view" and compute interaction_strength based on dwell_time and scroll_depth
2. WHEN a user annotates a resource, THE Recommendation Engine SHALL record interaction_type "annotation" with interaction_strength of 0.7
3. WHEN a user adds a resource to a collection, THE Recommendation Engine SHALL record interaction_type "collection_add" with interaction_strength of 0.8
4. WHEN a user exports a resource, THE Recommendation Engine SHALL record interaction_type "export" with interaction_strength of 0.9
5. IF a user interacts with the same resource multiple times, THEN THE Recommendation Engine SHALL increment return_visits and update interaction_strength to the maximum observed value
6. THE Recommendation Engine SHALL mark interactions as is_positive when interaction_strength exceeds 0.4
7. THE Recommendation Engine SHALL compute confidence scores between 0.0 and 1.0 for each interaction signal

### Requirement 3: User Embedding Generation

**User Story:** As a recommendation algorithm, I want to represent users as vectors in embedding space, so that I can compute similarity between users and resources efficiently.

#### Acceptance Criteria

1. WHEN computing a user embedding, THE Recommendation Engine SHALL retrieve the user's positive interactions (is_positive=true) limited to the most recent 100 interactions
2. THE Recommendation Engine SHALL compute a weighted average of resource embeddings where weights are interaction_strength values
3. IF a user has no positive interactions, THEN THE Recommendation Engine SHALL return a zero vector of dimension 768 for cold start handling
4. THE Recommendation Engine SHALL validate that all resource embeddings have consistent dimensions before averaging
5. THE Recommendation Engine SHALL handle JSON parsing errors gracefully and skip resources with invalid embeddings

### Requirement 4: Neural Collaborative Filtering

**User Story:** As a researcher, I want recommendations based on what similar users found valuable, so that I can discover resources through collaborative intelligence.

#### Acceptance Criteria

1. THE Recommendation Engine SHALL implement a Neural Collaborative Filtering model with user embeddings, item embeddings, and multi-layer perceptron architecture
2. THE Recommendation Engine SHALL train the NCF model on positive user-resource interactions with interaction_strength as implicit feedback
3. WHEN generating collaborative recommendations, THE Recommendation Engine SHALL compute predicted scores for candidate resources using the trained NCF model
4. THE Recommendation Engine SHALL handle CUDA unavailability by falling back to CPU computation
5. THE Recommendation Engine SHALL save model checkpoints periodically and load them with error handling for corrupted files
6. IF the NCF model is not trained or unavailable, THEN THE Recommendation Engine SHALL fall back to content-based recommendations

### Requirement 5: Hybrid Recommendation Strategy

**User Story:** As a researcher, I want recommendations that combine multiple signals (collaborative, content, graph), so that I receive comprehensive and accurate suggestions.

#### Acceptance Criteria

1. THE Recommendation Engine SHALL implement a two-stage pipeline with candidate generation followed by ranking
2. WHEN generating candidates, THE Recommendation Engine SHALL retrieve candidates from collaborative filtering, content similarity, and graph-based algorithms
3. THE Recommendation Engine SHALL combine candidate lists and remove duplicates while preserving source strategy metadata
4. WHEN ranking candidates, THE Recommendation Engine SHALL compute a hybrid score combining collaborative_score, content_score, graph_score, quality_score, and recency_score
5. THE Recommendation Engine SHALL apply user-specific weights to score components based on UserProfile preferences
6. THE Recommendation Engine SHALL validate that all candidate lists are non-empty before ranking and handle empty lists gracefully
7. THE Recommendation Engine SHALL cap recommendation lists at 100 items to prevent memory issues

### Requirement 6: Diversity Optimization

**User Story:** As a researcher, I want diverse recommendations covering different topics and perspectives, so that I don't get stuck in a filter bubble.

#### Acceptance Criteria

1. THE Recommendation Engine SHALL implement Maximal Marginal Relevance (MMR) algorithm for diversity optimization
2. WHEN applying MMR, THE Recommendation Engine SHALL balance relevance scores with dissimilarity to already-selected items using the formula: MMR = λ * relevance - (1-λ) * max_similarity
3. THE Recommendation Engine SHALL use the user's diversity_preference value as the λ parameter in MMR
4. THE Recommendation Engine SHALL compute the Gini coefficient for final recommendation lists to measure diversity
5. THE Recommendation Engine SHALL achieve a Gini coefficient below 0.3 for diverse recommendation sets
6. THE Recommendation Engine SHALL handle empty candidate lists gracefully without raising exceptions
7. THE Recommendation Engine SHALL validate that similarity scores are finite numbers before MMR computation

### Requirement 7: Novelty Promotion

**User Story:** As a researcher, I want to discover lesser-known but relevant resources, so that I can find hidden gems beyond popular items.

#### Acceptance Criteria

1. THE Recommendation Engine SHALL compute novelty scores for resources based on view counts and recency
2. THE Recommendation Engine SHALL boost scores for resources with novelty_score above the user's novelty_preference threshold
3. THE Recommendation Engine SHALL ensure at least 20% of recommendations come from outside the top-viewed resources
4. WHEN a user sets novelty_preference to 0.0, THE Recommendation Engine SHALL prioritize popular resources
5. WHEN a user sets novelty_preference to 1.0, THE Recommendation Engine SHALL maximize novel resource discovery

### Requirement 8: Cold Start Handling

**User Story:** As a new user with no interaction history, I want to receive relevant recommendations immediately, so that I can start exploring the system productively.

#### Acceptance Criteria

1. WHEN a user has fewer than 5 interactions, THE Recommendation Engine SHALL use content-based and graph-based strategies exclusively
2. THE Recommendation Engine SHALL provide relevant recommendations within 5 user interactions for cold start users
3. IF a user specifies research_domains in their profile, THEN THE Recommendation Engine SHALL filter recommendations to match those domains
4. THE Recommendation Engine SHALL use default preference weights for cold start users until sufficient interaction data is collected

### Requirement 9: Recommendation Feedback Loop

**User Story:** As a system, I want to track which recommendations users find useful, so that I can continuously improve recommendation quality.

#### Acceptance Criteria

1. WHEN a recommendation is presented to a user, THE Recommendation Engine SHALL create a RecommendationFeedback record with recommendation_strategy, recommendation_score, and rank_position
2. WHEN a user clicks a recommended resource, THE Recommendation Engine SHALL update the RecommendationFeedback record with was_clicked=true
3. WHERE a user provides explicit feedback, THE Recommendation Engine SHALL record was_useful and feedback_notes
4. THE Recommendation Engine SHALL use feedback data to compute click-through rates (CTR) for each recommendation strategy
5. THE Recommendation Engine SHALL achieve a 40% improvement in CTR compared to baseline content-only recommendations

### Requirement 10: Performance Requirements

**User Story:** As a researcher, I want recommendations to load quickly, so that my workflow is not interrupted by slow system responses.

#### Acceptance Criteria

1. THE Recommendation Engine SHALL generate 20 recommendations in less than 200 milliseconds
2. THE Recommendation Engine SHALL limit database queries to prevent N+1 query problems using batch loading
3. THE Recommendation Engine SHALL cache user embeddings for 5 minutes to reduce computation overhead
4. THE Recommendation Engine SHALL use database indexes on user_id, resource_id, and interaction_timestamp fields
5. THE Recommendation Engine SHALL limit interaction history queries to the most recent 1000 records

### Requirement 11: API Endpoints

**User Story:** As a frontend developer, I want RESTful API endpoints for recommendations, so that I can integrate the recommendation engine into the user interface.

#### Acceptance Criteria

1. THE Recommendation Engine SHALL provide a GET /api/recommendations endpoint that returns personalized recommendations for the authenticated user
2. THE Recommendation Engine SHALL accept query parameters: limit (default=20, max=100), strategy (collaborative|content|graph|hybrid), and diversity (0.0-1.0)
3. THE Recommendation Engine SHALL provide a POST /api/interactions endpoint to track user-resource interactions
4. THE Recommendation Engine SHALL provide a GET /api/profile endpoint to retrieve user profile settings
5. THE Recommendation Engine SHALL provide a PUT /api/profile endpoint to update user preference settings
6. THE Recommendation Engine SHALL convert all UUID objects to strings in JSON responses
7. THE Recommendation Engine SHALL validate request bodies using Pydantic schemas
8. THE Recommendation Engine SHALL wrap all service calls in try-except blocks and return appropriate HTTP error codes

### Requirement 12: Data Validation and Security

**User Story:** As a system administrator, I want all user inputs validated and sanitized, so that the system is protected from malicious data and injection attacks.

#### Acceptance Criteria

1. THE Recommendation Engine SHALL validate that all preference values (diversity, novelty, recency) are between 0.0 and 1.0
2. THE Recommendation Engine SHALL validate that interaction_type values are in the allowed set: ["view", "annotation", "collection_add", "export", "rating"]
3. THE Recommendation Engine SHALL use SQLAlchemy ORM for all database queries to prevent SQL injection
4. THE Recommendation Engine SHALL validate JSON data before parsing and handle JSONDecodeError exceptions
5. THE Recommendation Engine SHALL sanitize user-provided lists (excluded_sources, research_domains) before storage
6. THE Recommendation Engine SHALL log all validation errors with user_id and error details
7. THE Recommendation Engine SHALL roll back database transactions on any error

### Requirement 13: Testing and Quality Assurance

**User Story:** As a developer, I want comprehensive tests for the recommendation engine, so that I can ensure reliability and catch regressions early.

#### Acceptance Criteria

1. THE Recommendation Engine SHALL have unit tests for UserProfileService covering profile creation, updates, and preference learning
2. THE Recommendation Engine SHALL have unit tests for interaction tracking with various interaction types and edge cases
3. THE Recommendation Engine SHALL have unit tests for user embedding generation including cold start scenarios
4. THE Recommendation Engine SHALL have integration tests for the complete recommendation pipeline
5. THE Recommendation Engine SHALL have tests that mock all ML models to avoid loading actual model weights
6. THE Recommendation Engine SHALL have tests that use pytest fixtures as function parameters only
7. THE Recommendation Engine SHALL have tests that validate only fields present in models.py
8. THE Recommendation Engine SHALL achieve 80% code coverage for all recommendation service modules

### Requirement 14: Documentation

**User Story:** As a developer joining the project, I want clear documentation of the recommendation system, so that I can understand and extend it effectively.

#### Acceptance Criteria

1. THE Recommendation Engine SHALL have API documentation describing all endpoints, request/response schemas, and example usage
2. THE Recommendation Engine SHALL have architecture documentation explaining the hybrid strategy, NCF model, and ranking algorithm
3. THE Recommendation Engine SHALL have inline code comments explaining complex algorithms (MMR, NCF, embedding generation)
4. THE Recommendation Engine SHALL have a CHANGELOG entry documenting Phase 11 features and breaking changes
5. THE Recommendation Engine SHALL have a README section explaining how to train and deploy the NCF model
