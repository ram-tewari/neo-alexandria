# Requirements Document: Phase 18 - Code Intelligence Pipeline

## Introduction

This specification defines the Code Intelligence Pipeline for Neo Alexandria 2.0, transforming the system from a "File Library" to a "Code-Aware Context Server." The pipeline enables intelligent ingestion, analysis, and retrieval of code repositories through AST-based chunking and static analysis.

## Glossary

- **Repository**: A collection of source code files organized in a directory structure
- **AST (Abstract Syntax Tree)**: A tree representation of the syntactic structure of source code
- **Tree-Sitter**: A parser generator tool for building fast, incremental parsers
- **Static Analysis**: Code analysis performed without executing the code
- **Logical Unit**: A semantically meaningful code block (function, class, method)
- **Code Chunk**: A DocumentChunk containing a logical unit of code with AST metadata
- **Graph Triple**: A subject-predicate-object relationship extracted from code structure

## Requirements

### Requirement 1: Repository Ingestion

**User Story:** As a developer, I want to ingest entire code repositories into Neo Alexandria, so that I can search and analyze codebases at scale.

#### Acceptance Criteria

1. WHEN a user provides a local directory path, THE System SHALL recursively crawl all files and create Resource entries
2. WHEN a user provides a Git repository URL, THE System SHALL clone the repository and ingest its contents
3. WHEN crawling a repository, THE System SHALL respect .gitignore rules and exclude ignored files
4. WHEN crawling a repository, THE System SHALL filter out binary files and build artifacts
5. WHEN ingesting files, THE System SHALL preserve the directory structure in Resource metadata
6. WHEN ingesting files, THE System SHALL auto-classify resources into THEORY, PRACTICE, or GOVERNANCE categories
7. WHEN ingestion is long-running, THE System SHALL process it asynchronously via Celery task queue

### Requirement 2: File Classification

**User Story:** As a system architect, I want automatic classification of ingested files, so that I can organize code, documentation, and governance files separately.

#### Acceptance Criteria

1. WHEN a file has extension .py, .js, .ts, .rs, .go, .java, .cpp, .c, .rb, THE System SHALL classify it as PRACTICE
2. WHEN a file has extension .pdf, .md, .rst, .tex AND contains academic content, THE System SHALL classify it as THEORY
3. WHEN a file matches patterns like CONTRIBUTING.md, CODE_OF_CONDUCT.md, .eslintrc, THE System SHALL classify it as GOVERNANCE
4. WHEN a file does not match classification rules, THE System SHALL classify it as PRACTICE by default
5. WHEN classification occurs, THE System SHALL store the classification in Resource metadata

### Requirement 3: AST-Based Smart Chunking

**User Story:** As a developer, I want code files chunked by logical units (functions, classes), so that search results return semantically meaningful code blocks rather than arbitrary character ranges.

#### Acceptance Criteria

1. WHEN chunking a code file, THE System SHALL use Tree-Sitter to parse the Abstract Syntax Tree
2. WHEN parsing the AST, THE System SHALL identify function definitions as logical units
3. WHEN parsing the AST, THE System SHALL identify class definitions as logical units
4. WHEN creating a code chunk, THE System SHALL store function_name, class_name, start_line, end_line in chunk_metadata
5. WHEN creating a code chunk, THE System SHALL store the programming language in chunk_metadata
6. WHEN a logical unit is too large (>2000 tokens), THE System SHALL split it at natural boundaries (methods within classes)
7. WHEN Tree-Sitter parsing fails, THE System SHALL fall back to character-based chunking with a warning

### Requirement 4: Static Graph Extraction

**User Story:** As a developer, I want automatic extraction of code relationships (imports, function calls, class definitions), so that I can navigate and understand code structure through the knowledge graph.

#### Acceptance Criteria

1. WHEN analyzing a code chunk, THE System SHALL extract import statements and create IMPORTS relationships
2. WHEN analyzing a code chunk, THE System SHALL extract class definitions and create DEFINES relationships
3. WHEN analyzing a code chunk, THE System SHALL extract function call patterns and create CALLS relationships
4. WHEN creating a graph relationship, THE System SHALL use the code-specific relationship types (IMPORTS, DEFINES, CALLS)
5. WHEN creating a graph relationship, THE System SHALL store source file path, target symbol, and line numbers in metadata
6. WHEN static analysis encounters ambiguous symbols, THE System SHALL create relationships with confidence scores
7. WHEN static analysis is performed, THE System SHALL not execute any code (security constraint)

### Requirement 5: Async Processing Pipeline

**User Story:** As a system administrator, I want repository ingestion to run asynchronously, so that large repositories don't block the API or timeout.

#### Acceptance Criteria

1. WHEN a repository ingestion is triggered, THE System SHALL create a Celery task and return a task ID immediately
2. WHEN the Celery task runs, THE System SHALL update task status (PENDING, PROCESSING, COMPLETED, FAILED)
3. WHEN ingestion completes, THE System SHALL emit resource.created events for each file
4. WHEN ingestion fails, THE System SHALL log detailed error information and mark the task as FAILED
5. WHEN a user queries task status, THE System SHALL return progress information (files processed, total files)

### Requirement 6: API Endpoints

**User Story:** As a frontend developer, I want REST API endpoints for repository ingestion and status tracking, so that I can build UI for code repository management.

#### Acceptance Criteria

1. THE System SHALL provide POST /resources/ingest-repo endpoint accepting path or git_url
2. THE System SHALL provide GET /resources/ingest-repo/{task_id}/status endpoint for progress tracking
3. WHEN calling ingest-repo, THE System SHALL validate that the path exists or URL is valid
4. WHEN calling ingest-repo, THE System SHALL require authentication
5. WHEN calling ingest-repo, THE System SHALL apply rate limiting to prevent abuse
6. WHEN returning task status, THE System SHALL include files_processed, total_files, and current_file fields

### Requirement 7: Metadata Preservation

**User Story:** As a developer, I want file paths and repository structure preserved, so that I can understand the context and location of code snippets in search results.

#### Acceptance Criteria

1. WHEN creating a Resource from a repository file, THE System SHALL store the relative file path in metadata
2. WHEN creating a Resource from a repository file, THE System SHALL store the repository root path in metadata
3. WHEN creating a Resource from a Git repository, THE System SHALL store the commit hash in metadata
4. WHEN creating a Resource from a Git repository, THE System SHALL store the branch name in metadata
5. WHEN displaying search results, THE System SHALL include file path and line numbers in the response

### Requirement 8: Language Support

**User Story:** As a polyglot developer, I want support for multiple programming languages, so that I can ingest repositories written in different languages.

#### Acceptance Criteria

1. THE System SHALL support Python (.py) files with Tree-Sitter
2. THE System SHALL support JavaScript/TypeScript (.js, .ts, .jsx, .tsx) files with Tree-Sitter
3. THE System SHALL support Rust (.rs) files with Tree-Sitter
4. THE System SHALL support Go (.go) files with Tree-Sitter
5. THE System SHALL support Java (.java) files with Tree-Sitter
6. WHEN a language is not supported by Tree-Sitter, THE System SHALL fall back to character-based chunking
7. WHEN adding a new language, THE System SHALL require only adding the Tree-Sitter grammar to the configuration

### Requirement 9: Error Handling

**User Story:** As a system administrator, I want robust error handling during repository ingestion, so that partial failures don't corrupt the database or leave the system in an inconsistent state.

#### Acceptance Criteria

1. WHEN a file cannot be read, THE System SHALL log the error and continue processing other files
2. WHEN Tree-Sitter parsing fails, THE System SHALL fall back to character-based chunking
3. WHEN static analysis fails, THE System SHALL log the error and skip graph extraction for that file
4. WHEN a repository clone fails, THE System SHALL return a clear error message to the user
5. WHEN ingestion is interrupted, THE System SHALL mark the task as FAILED and allow retry
6. WHEN database errors occur, THE System SHALL rollback the transaction and preserve data integrity

### Requirement 10: Performance Requirements

**User Story:** As a system architect, I want efficient processing of large repositories, so that ingestion completes in reasonable time without overwhelming system resources.

#### Acceptance Criteria

1. WHEN ingesting a repository, THE System SHALL process files in batches of 50 to avoid memory exhaustion
2. WHEN parsing AST, THE System SHALL complete parsing within 2 seconds per file (P95)
3. WHEN extracting graph relationships, THE System SHALL complete extraction within 1 second per file (P95)
4. WHEN ingesting a 1000-file repository, THE System SHALL complete within 30 minutes
5. WHEN multiple ingestion tasks run concurrently, THE System SHALL limit concurrent tasks to 3 to prevent resource exhaustion
