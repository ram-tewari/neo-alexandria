# Requirements Document - Phase 7.5: Annotation & Active Reading System

## Introduction

This specification defines a comprehensive annotation and active reading system for Neo Alexandria that enables researchers to highlight text, add notes, tag annotations, search semantically across their annotations, and export research notes. The system transforms passive content consumption into active knowledge building by allowing users to create a personal knowledge base on top of ingested resources.

## Glossary

- **Annotation System**: The complete subsystem managing user highlights, notes, and tags on resource content
- **Highlight**: A selected text range within a resource marked by start and end character offsets
- **Note**: User-written commentary or observation attached to a highlight
- **Text Offset**: Zero-indexed character position within resource content (start_offset, end_offset)
- **Annotation Embedding**: Vector representation of annotation note content for semantic search
- **Context Window**: 50 characters before and after a highlight for preview purposes
- **Shared Annotation**: An annotation marked as publicly visible to other users
- **Tag**: User-defined label for categorizing and organizing annotations
- **Export Format**: Structured output format (Markdown or JSON) for annotation data

## Requirements

### Requirement 1: Annotation Creation and Management

**User Story:** As a researcher, I want to highlight text passages and add my own notes, so that I can capture important insights while reading.

#### Acceptance Criteria

1. WHEN a user selects a text range and creates an annotation, THE Annotation System SHALL store the start_offset, end_offset, highlighted_text, and optional note
2. WHEN a user creates an annotation, THE Annotation System SHALL validate that start_offset is less than end_offset
3. WHEN a user creates an annotation, THE Annotation System SHALL validate that both offsets are non-negative integers
4. WHEN a user creates an annotation with a note, THE Annotation System SHALL generate a semantic embedding within 500 milliseconds
5. THE Annotation System SHALL extract and store 50 characters of context before and after each highlight

### Requirement 2: Annotation Ownership and Access Control

**User Story:** As a researcher, I want my annotations to be private by default, so that I can control who sees my research notes.

#### Acceptance Criteria

1. WHEN a user creates an annotation, THE Annotation System SHALL set is_shared to False by default
2. WHEN a user attempts to update an annotation, THE Annotation System SHALL verify the user owns the annotation
3. WHEN a user attempts to delete an annotation, THE Annotation System SHALL verify the user owns the annotation
4. IF a user attempts to modify another user's annotation, THEN THE Annotation System SHALL raise a PermissionError
5. WHEN a user retrieves annotations for a resource, THE Annotation System SHALL return only annotations owned by the user or marked as shared

### Requirement 3: Annotation Organization and Tagging

**User Story:** As a researcher, I want to tag my annotations with custom labels, so that I can organize highlights by theme or topic.

#### Acceptance Criteria

1. THE Annotation System SHALL support storing multiple tags per annotation as a JSON array
2. WHEN a user searches annotations by tags, THE Annotation System SHALL support matching ANY tag or ALL tags
3. WHEN a user retrieves annotations for a resource, THE Annotation System SHALL support filtering by tag list
4. THE Annotation System SHALL support color-coding annotations with hex color values
5. THE Annotation System SHALL default annotation color to "#FFFF00" (yellow) when not specified

### Requirement 4: Full-Text Annotation Search

**User Story:** As a researcher, I want to search across all my annotation notes and highlights, so that I can quickly find specific passages I've marked.

#### Acceptance Criteria

1. WHEN a user performs a full-text search, THE Annotation System SHALL search both note content and highlighted_text fields
2. WHEN a user performs a full-text search with 10,000 annotations, THE Annotation System SHALL return results within 100 milliseconds
3. THE Annotation System SHALL return search results ordered by relevance
4. THE Annotation System SHALL limit full-text search results to annotations owned by the requesting user
5. THE Annotation System SHALL support pagination of search results with configurable limit

### Requirement 5: Semantic Annotation Search

**User Story:** As a researcher, I want to search my annotations by meaning rather than exact keywords, so that I can find conceptually related notes.

#### Acceptance Criteria

1. WHEN a user performs a semantic search, THE Annotation System SHALL generate an embedding for the query text
2. WHEN a user performs a semantic search, THE Annotation System SHALL compute cosine similarity between query embedding and annotation embeddings
3. THE Annotation System SHALL return semantic search results ordered by similarity score descending
4. THE Annotation System SHALL include similarity scores in semantic search responses
5. WHEN a user performs a semantic search, THE Annotation System SHALL only search annotations that have embeddings

### Requirement 6: Annotation Retrieval and Filtering

**User Story:** As a researcher, I want to view all my annotations for a specific document in reading order, so that I can review my notes sequentially.

#### Acceptance Criteria

1. WHEN a user retrieves annotations for a resource, THE Annotation System SHALL return annotations ordered by start_offset ascending
2. THE Annotation System SHALL support retrieving all annotations for a user across all resources
3. WHEN retrieving user annotations, THE Annotation System SHALL support sorting by "recent" or "oldest" based on created_at
4. THE Annotation System SHALL support pagination with configurable limit and offset parameters
5. THE Annotation System SHALL eagerly load resource relationships to prevent N+1 query problems

### Requirement 7: Annotation Export

**User Story:** As a researcher, I want to export my annotations to Markdown format, so that I can use them in my note-taking applications.

#### Acceptance Criteria

1. WHEN a user exports annotations to Markdown, THE Annotation System SHALL format each annotation with highlighted text, note, tags, and timestamp
2. WHEN a user exports 1,000 annotations, THE Annotation System SHALL complete the export within 2 seconds
3. THE Annotation System SHALL support exporting annotations for a specific resource or all resources
4. THE Annotation System SHALL support exporting annotations to JSON format with complete annotation metadata
5. WHEN exporting to Markdown, THE Annotation System SHALL group annotations by resource with resource title headers

### Requirement 8: Collection Integration

**User Story:** As a researcher, I want to associate my annotations with research collections, so that I can organize notes within project contexts.

#### Acceptance Criteria

1. THE Annotation System SHALL support storing multiple collection IDs per annotation as a JSON array
2. WHEN a user creates an annotation, THE Annotation System SHALL accept optional collection_ids parameter
3. THE Annotation System SHALL support filtering annotations by collection membership
4. WHEN retrieving collection details, THE Annotation System SHALL include annotation count for that collection
5. THE Annotation System SHALL maintain collection associations when annotations are updated

### Requirement 9: Resource Lifecycle Integration

**User Story:** As a system administrator, I want annotations to be automatically deleted when their parent resource is deleted, so that orphaned data does not accumulate.

#### Acceptance Criteria

1. WHEN a resource is deleted, THE Annotation System SHALL cascade delete all associated annotations
2. THE Annotation System SHALL verify resource existence before creating annotations
3. IF a user attempts to create an annotation on a non-existent resource, THEN THE Annotation System SHALL raise a ResourceNotFoundError
4. THE Annotation System SHALL maintain referential integrity between annotations and resources
5. THE Annotation System SHALL maintain referential integrity between annotations and users

### Requirement 10: Search Integration

**User Story:** As a researcher, I want global search results to include my annotations, so that I can find resources through my own notes.

#### Acceptance Criteria

1. WHEN a user performs a global search, THE Annotation System SHALL optionally include annotation matches
2. THE Annotation System SHALL return a mapping of resources to matching annotation IDs
3. THE Annotation System SHALL indicate which resources have annotation matches in search results
4. THE Annotation System SHALL integrate annotation search with existing resource search functionality
5. THE Annotation System SHALL support disabling annotation inclusion in global search

### Requirement 11: Recommendation Integration

**User Story:** As a researcher, I want the system to recommend resources based on what I actively annotate, so that I discover content aligned with my research interests.

#### Acceptance Criteria

1. THE Annotation System SHALL analyze user annotation patterns to identify research interests
2. WHEN generating recommendations, THE Annotation System SHALL extract frequent tags from recent annotations
3. WHEN generating recommendations, THE Annotation System SHALL aggregate note content for semantic similarity
4. THE Annotation System SHALL exclude already-annotated resources from recommendations
5. THE Annotation System SHALL combine tag-based and embedding-based recommendations

### Requirement 12: Performance and Scalability

**User Story:** As a researcher with heavily annotated papers, I want the system to handle thousands of annotations per document without performance degradation.

#### Acceptance Criteria

1. THE Annotation System SHALL support storing at least 10,000 annotations per resource
2. WHEN creating an annotation, THE Annotation System SHALL complete the operation within 50 milliseconds excluding embedding generation
3. THE Annotation System SHALL generate annotation embeddings asynchronously without blocking creation
4. THE Annotation System SHALL use composite database indexes on (user_id, resource_id) for efficient filtering
5. THE Annotation System SHALL use database indexes on resource_id, user_id, and created_at fields

### Requirement 13: Data Validation and Error Handling

**User Story:** As a system, I want to validate annotation data to prevent invalid text offsets and ensure data integrity.

#### Acceptance Criteria

1. IF start_offset is greater than or equal to end_offset, THEN THE Annotation System SHALL raise a ValidationError
2. IF either offset is negative, THEN THE Annotation System SHALL raise a ValidationError
3. THE Annotation System SHALL enforce database check constraints for offset validation
4. WHEN annotation creation fails, THE Annotation System SHALL provide descriptive error messages
5. THE Annotation System SHALL handle concurrent annotation creation without data corruption

### Requirement 14: Context Extraction

**User Story:** As a researcher, I want to see surrounding text when viewing annotation lists, so that I can understand the context of each highlight.

#### Acceptance Criteria

1. WHEN creating an annotation, THE Annotation System SHALL extract 50 characters before the highlight as context_before
2. WHEN creating an annotation, THE Annotation System SHALL extract 50 characters after the highlight as context_after
3. THE Annotation System SHALL handle edge cases where offsets are near document boundaries
4. THE Annotation System SHALL store context fields for display in annotation lists
5. THE Annotation System SHALL complete context extraction within 10 milliseconds

### Requirement 15: Annotation Updates

**User Story:** As a researcher, I want to edit my annotation notes and tags after creation, so that I can refine my thoughts over time.

#### Acceptance Criteria

1. WHEN a user updates an annotation note, THE Annotation System SHALL regenerate the embedding
2. THE Annotation System SHALL support updating note, tags, color, and is_shared fields
3. THE Annotation System SHALL prevent updating start_offset, end_offset, and highlighted_text after creation
4. WHEN an annotation is updated, THE Annotation System SHALL update the updated_at timestamp
5. THE Annotation System SHALL return the updated annotation object after successful modification
