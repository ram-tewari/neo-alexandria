# Requirements Document: Phase 7 Collection Management

## Introduction

Phase 7 introduces a comprehensive collection management system for Neo Alexandria, enabling users to organize, curate, and share groups of resources. Collections support hierarchical organization, collaborative editing, intelligent recommendations based on aggregate embeddings, and seamless integration with the existing search and recommendation infrastructure. This feature empowers researchers to build thematic resource libraries, share curated reading lists, and discover related materials through collection-level semantic similarity.

## Glossary

- **Collection System**: The Neo Alexandria subsystem responsible for managing user-created collections of resources
- **Collection**: A user-curated group of resources with metadata, ownership, visibility controls, and an aggregate embedding
- **Resource**: An existing Neo Alexandria entity representing a document, paper, or other scholarly material (defined in Phase 1-6)
- **Owner**: The user who created a collection and has full control over its properties and membership
- **Member Resource**: A resource that belongs to a collection
- **Aggregate Embedding**: A computed vector representation of a collection derived from the embeddings of its member resources
- **Visibility Level**: The access control setting for a collection (private, shared, or public)
- **Nested Collection**: A collection that exists as a child of another collection, enabling hierarchical organization
- **Parent Collection**: A collection that contains one or more nested collections as children
- **Collection Membership**: The many-to-many relationship between collections and resources
- **Collaborative Editing**: The ability for multiple users to modify a shared collection
- **Embedding Service**: The existing Neo Alexandria service that computes and manages vector embeddings for semantic search
- **Recommendation Engine**: The system component that suggests related resources and collections based on embedding similarity

## Requirements

### Requirement 1: Collection Creation and Ownership

**User Story:** As a researcher, I want to create named collections with descriptions so that I can organize my resources into thematic groups.

#### Acceptance Criteria

1. WHEN a user submits a collection creation request with a name, THE Collection System SHALL create a new collection with a unique identifier and set the requesting user as the owner
2. THE Collection System SHALL store the collection name as a required text field with a maximum length of 255 characters
3. THE Collection System SHALL store an optional description field with a maximum length of 2000 characters
4. THE Collection System SHALL set the default visibility level to private for newly created collections
5. THE Collection System SHALL record creation and update timestamps for each collection

### Requirement 2: Collection Metadata Management

**User Story:** As a collection owner, I want to update my collection's name, description, and visibility settings so that I can refine how my collection is presented and shared.

#### Acceptance Criteria

1. WHEN the owner requests to update collection metadata, THE Collection System SHALL modify the specified fields and update the modification timestamp
2. THE Collection System SHALL reject update requests from users who are not the collection owner with an authorization error
3. THE Collection System SHALL validate that the new name is not empty and does not exceed 255 characters
4. THE Collection System SHALL validate that visibility values are one of: private, shared, or public
5. THE Collection System SHALL allow the description field to be set to null or empty

### Requirement 3: Resource Membership Management

**User Story:** As a collection owner, I want to add and remove resources from my collection so that I can curate the collection's contents.

#### Acceptance Criteria

1. WHEN the owner requests to add resources by providing resource identifiers, THE Collection System SHALL create membership associations for all valid resource identifiers
2. WHEN the owner requests to remove resources by providing resource identifiers, THE Collection System SHALL delete the membership associations for those resources
3. THE Collection System SHALL reject membership modification requests from non-owners with an authorization error
4. THE Collection System SHALL validate that all provided resource identifiers exist in the Resource table before creating associations
5. THE Collection System SHALL support batch operations for adding or removing up to 100 resources in a single request

### Requirement 4: Collection Deletion

**User Story:** As a collection owner, I want to delete my collections so that I can remove collections I no longer need.

#### Acceptance Criteria

1. WHEN the owner requests to delete a collection, THE Collection System SHALL remove the collection record and all associated membership records
2. THE Collection System SHALL reject deletion requests from non-owners with an authorization error
3. WHEN a collection with nested subcollections is deleted, THE Collection System SHALL delete all descendant collections recursively
4. THE Collection System SHALL not delete the member resources themselves when a collection is deleted
5. THE Collection System SHALL complete the deletion operation within 2 seconds for collections with up to 1000 resources

### Requirement 5: Collection Retrieval and Listing

**User Story:** As a user, I want to view collections I own or have access to so that I can browse and select collections to work with.

#### Acceptance Criteria

1. WHEN a user requests a specific collection by identifier, THE Collection System SHALL return the collection metadata and summary of member resources if the user has access
2. WHEN a user requests a list of collections, THE Collection System SHALL return all collections where the user is the owner or the visibility is public
3. THE Collection System SHALL support filtering collection lists by owner identifier
4. THE Collection System SHALL support pagination for collection lists with configurable page size up to 100 items
5. THE Collection System SHALL include the count of member resources in collection list responses

### Requirement 6: Visibility and Access Control

**User Story:** As a collection owner, I want to control who can view my collection so that I can share collections publicly or keep them private.

#### Acceptance Criteria

1. WHEN a collection visibility is set to private, THE Collection System SHALL allow access only to the owner
2. WHEN a collection visibility is set to public, THE Collection System SHALL allow read access to all authenticated users
3. WHEN a collection visibility is set to shared, THE Collection System SHALL allow read access to users with explicit sharing permissions
4. THE Collection System SHALL enforce visibility rules for all collection retrieval operations
5. THE Collection System SHALL return an access denied error when a user attempts to access a collection without proper permissions

### Requirement 7: Aggregate Embedding Computation

**User Story:** As a researcher, I want my collections to have semantic representations so that I can discover related resources and collections through similarity search.

#### Acceptance Criteria

1. WHEN resources are added to or removed from a collection, THE Collection System SHALL recompute the aggregate embedding from member resource embeddings
2. THE Collection System SHALL compute the aggregate embedding as the mean vector of all member resource embeddings
3. WHEN a collection has no member resources with embeddings, THE Collection System SHALL set the aggregate embedding to null
4. THE Collection System SHALL complete embedding computation within 1 second for collections with up to 1000 member resources
5. THE Collection System SHALL store the aggregate embedding in the same vector format as resource embeddings

### Requirement 8: Collection-Based Recommendations

**User Story:** As a researcher, I want to receive recommendations for resources and collections similar to my collection so that I can discover related materials.

#### Acceptance Criteria

1. WHEN a user requests recommendations for a collection with an aggregate embedding, THE Collection System SHALL return the top N most similar resources based on embedding cosine similarity
2. WHEN a user requests recommendations for a collection with an aggregate embedding, THE Collection System SHALL return the top N most similar collections based on embedding cosine similarity
3. THE Collection System SHALL exclude resources already in the collection from resource recommendations
4. THE Collection System SHALL exclude the source collection itself from collection recommendations
5. THE Collection System SHALL support configurable recommendation limits between 1 and 50 items

### Requirement 9: Hierarchical Collection Organization

**User Story:** As a researcher, I want to organize collections within other collections so that I can create hierarchical structures for complex research topics.

#### Acceptance Criteria

1. WHEN creating or updating a collection, THE Collection System SHALL accept an optional parent collection identifier to establish a hierarchical relationship
2. THE Collection System SHALL validate that the parent collection exists and the user is the owner before creating the relationship
3. THE Collection System SHALL prevent circular references by rejecting parent assignments that would create a cycle
4. WHEN a parent collection is deleted, THE Collection System SHALL delete all child collections recursively
5. THE Collection System SHALL support retrieval of all subcollections for a given parent collection

### Requirement 10: Resource Deletion Consistency

**User Story:** As a system administrator, I want collections to remain consistent when resources are deleted so that collections do not reference non-existent resources.

#### Acceptance Criteria

1. WHEN a resource is deleted from the Resource table, THE Collection System SHALL automatically remove that resource from all collection memberships
2. WHEN a resource is removed from a collection due to deletion, THE Collection System SHALL recompute the collection's aggregate embedding
3. THE Collection System SHALL complete resource deletion cleanup within 2 seconds for resources belonging to up to 100 collections
4. THE Collection System SHALL log resource deletion events that affect collection memberships
5. THE Collection System SHALL not fail resource deletion operations due to collection membership cleanup errors

### Requirement 11: Performance and Scalability

**User Story:** As a researcher with large collections, I want collection operations to complete quickly so that I can work efficiently with my curated resources.

#### Acceptance Criteria

1. THE Collection System SHALL support collections with up to 1000 member resources
2. THE Collection System SHALL complete collection retrieval operations within 500 milliseconds for collections with 1000 resources
3. THE Collection System SHALL complete aggregate embedding computation within 1 second for collections with 1000 resources
4. THE Collection System SHALL use database indexes on owner_id and visibility fields to optimize query performance
5. THE Collection System SHALL use batch database operations to minimize query overhead for membership updates

### Requirement 12: API Integration

**User Story:** As a frontend developer, I want RESTful API endpoints for collection operations so that I can build user interfaces for collection management.

#### Acceptance Criteria

1. THE Collection System SHALL expose a POST endpoint at /collections for creating collections
2. THE Collection System SHALL expose a GET endpoint at /collections/{id} for retrieving individual collections
3. THE Collection System SHALL expose a PUT endpoint at /collections/{id} for updating collection metadata
4. THE Collection System SHALL expose a DELETE endpoint at /collections/{id} for deleting collections
5. THE Collection System SHALL expose POST and DELETE endpoints at /collections/{id}/resources for managing resource membership
6. THE Collection System SHALL expose a GET endpoint at /collections/{id}/recommendations for retrieving similar resources and collections
7. THE Collection System SHALL return appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500) for all operations
8. THE Collection System SHALL validate all request payloads against defined schemas and return detailed error messages for validation failures
