# Design Document: Phase 18 - Code Intelligence Pipeline

## Overview

The Code Intelligence Pipeline transforms Neo Alexandria from a document-centric system into a code-aware context server. This design introduces AST-based chunking, static analysis, and repository ingestion capabilities while maintaining the vertical slice architecture and event-driven communication patterns.

## Architecture

### High-Level Flow

```
User Request → API Endpoint → Celery Task → Repository Crawler
                                              ↓
                                         File Discovery
                                              ↓
                                    Resource Creation (per file)
                                              ↓
                                    Event: resource.created
                                              ↓
                        ┌────────────────────┴────────────────────┐
                        ↓                                          ↓
                AST Chunking Service                    Graph Extraction Service
                        ↓                                          ↓
                DocumentChunk (with metadata)          GraphRelationship (IMPORTS, DEFINES, CALLS)
```

### Module Responsibilities

**Resources Module** (`app/modules/resources`):
- Repository ingestion and file discovery
- AST-based chunking strategy
- File classification logic
- Resource metadata management

**Graph Module** (`app/modules/graph`):
- Static analysis of code structure
- Relationship extraction (imports, definitions, calls)
- Graph triple storage

**Tasks Module** (`app/tasks`):
- Async repository ingestion via Celery
- Progress tracking and status updates
- Error handling and retry logic

**Shared Kernel** (`app/shared`):
- No new shared services required
- Existing database and event bus used

## Components and Interfaces

### 1. Code Chunking Strategy (IMPLEMENTED)

**Location**: `app/modules/resources/logic/chunking.py`

**Supported Languages**:
- **Python**: functions, classes, methods (with parent class tracking)
- **JavaScript**: functions, classes, methods (with class body traversal)
- **TypeScript**: functions, classes, methods, interfaces
- **Rust**: functions, structs, impl blocks, traits, methods within impl/trait
- **Go**: functions, methods (with receiver), structs, interfaces
- **Java**: classes, interfaces, methods, constructors (with visibility)

**Key Classes**:
- `LogicalUnit`: Dataclass representing extracted code units
- `ChunkMetadata`: Dataclass for chunk metadata serialization
- `CodeChunkingStrategy`: Main chunking class with AST parsing

**Key Methods**:
- `chunk()`: Main entry point, falls back to character-based if AST fails
- `_parse_ast()`: Parse content using Tree-Sitter
- `_extract_logical_units()`: Dispatch to language-specific extractors
- `_extract_python_units()`: Python AST extraction
- `_extract_javascript_units()`: JavaScript AST extraction
- `_extract_typescript_units()`: TypeScript AST extraction
- `_extract_rust_units()`: Rust AST extraction
- `_extract_go_units()`: Go AST extraction
- `_extract_java_units()`: Java AST extraction
- `_chunk_with_ast()`: Create DocumentChunks from logical units
- `_chunk_character_based()`: Fallback chunking strategy

**Utility Functions**:
- `detect_language()`: Detect language from file extension
- `is_code_file()`: Check if file is a recognized code file
- `get_chunking_strategy()`: Factory function for chunking strategy

### 2. Repository Ingestion Service

**Location**: `app/modules/resources/service.py`

**New Methods**:
```python
class ResourceService:
    async def ingest_repository(
        self,
        path: Optional[str] = None,
        git_url: Optional[str] = None,
        user_id: UUID,
        db: AsyncSession
    ) -> str:
        """
        Trigger async repository ingestion.
        Returns: Celery task ID
        """
        
    async def get_ingestion_status(
        self,
        task_id: str,
        db: AsyncSession
    ) -> IngestionStatus:
        """
        Get status of repository ingestion task.
        """
```

**New Helper Class**: `RepoIngestionService`

**Location**: `app/modules/resources/logic/repo_ingestion.py`

```python
class RepoIngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def crawl_directory(
        self,
        root_path: Path,
        user_id: UUID
    ) -> List[Resource]:
        """
        Recursively crawl directory and create Resources.
        Respects .gitignore rules.
        """
        
    async def clone_and_ingest(
        self,
        git_url: str,
        user_id: UUID
    ) -> List[Resource]:
        """
        Clone Git repository and ingest contents.
        """
        
    def should_ignore_file(self, file_path: Path, gitignore_spec) -> bool:
        """
        Check if file should be ignored based on .gitignore.
        """
        
    def classify_file(self, file_path: Path, content: str) -> str:
        """
        Classify file as THEORY, PRACTICE, or GOVERNANCE.
        """
```

### 2. Code Chunking Strategy

**Location**: `app/modules/resources/logic/chunking.py`

**New Class**: `CodeChunkingStrategy`

```python
class CodeChunkingStrategy:
    def __init__(self, language: str):
        self.language = language
        self.parser = self._get_parser(language)
        
    def chunk(self, content: str, resource_id: UUID) -> List[DocumentChunk]:
        """
        Chunk code by logical units (functions, classes).
        Returns chunks with AST metadata.
        """
        
    def _parse_ast(self, content: str) -> Tree:
        """
        Parse content into AST using Tree-Sitter.
        """
        
    def _extract_logical_units(self, tree: Tree) -> List[LogicalUnit]:
        """
        Extract functions and classes from AST.
        """
        
    def _create_chunk_from_unit(
        self,
        unit: LogicalUnit,
        content: str,
        resource_id: UUID
    ) -> DocumentChunk:
        """
        Create DocumentChunk with metadata:
        {
            "function_name": "...",
            "class_name": "...",
            "start_line": 10,
            "end_line": 25,
            "language": "python",
            "type": "function" | "class" | "method"
        }
        """
```

**Integration Point**: Update `ChunkingService` factory

```python
class ChunkingService:
    def get_strategy(self, resource: Resource) -> ChunkingStrategy:
        """
        Select chunking strategy based on file type.
        """
        if self._is_code_file(resource):
            language = self._detect_language(resource)
            return CodeChunkingStrategy(language)
        else:
            # Existing text strategies
            return self._get_text_strategy(resource)
```

### 3. Static Analysis Service

**Location**: `app/modules/graph/logic/static_analysis.py`

**New Class**: `StaticAnalysisService`

```python
class StaticAnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def analyze_code_chunk(
        self,
        chunk: DocumentChunk,
        resource: Resource
    ) -> List[GraphRelationship]:
        """
        Extract code relationships from chunk.
        Returns IMPORTS, DEFINES, CALLS relationships.
        """
        
    def _extract_imports(
        self,
        tree: Tree,
        file_path: str
    ) -> List[ImportRelationship]:
        """
        Extract import statements.
        Example: import os → (file.py, IMPORTS, os)
        """
        
    def _extract_definitions(
        self,
        tree: Tree,
        file_path: str
    ) -> List[DefinitionRelationship]:
        """
        Extract class/function definitions.
        Example: class Foo → (file.py, DEFINES, Foo)
        """
        
    def _extract_calls(
        self,
        tree: Tree,
        file_path: str
    ) -> List[CallRelationship]:
        """
        Extract function calls (best-effort).
        Example: foo() → (current_func, CALLS, foo)
        """
```

**Integration Point**: Update `GraphExtractionService`

```python
class GraphExtractionService:
    async def extract_from_resource(
        self,
        resource: Resource,
        db: AsyncSession
    ) -> List[GraphRelationship]:
        """
        Extract relationships based on resource type.
        """
        if self._is_code_resource(resource):
            return await self._extract_code_relationships(resource, db)
        else:
            # Existing semantic extraction
            return await self._extract_semantic_relationships(resource, db)
```

### 4. Celery Task

**Location**: `app/tasks/celery_tasks.py`

**New Task**: `ingest_repo_task`

```python
@celery_app.task(bind=True, name="tasks.ingest_repo")
def ingest_repo_task(
    self,
    path: Optional[str],
    git_url: Optional[str],
    user_id: str
) -> Dict[str, Any]:
    """
    Async task for repository ingestion.
    Updates task state with progress.
    """
    try:
        # Create async session
        async with get_async_session() as db:
            service = RepoIngestionService(db)
            
            # Crawl or clone
            if path:
                resources = await service.crawl_directory(Path(path), UUID(user_id))
            else:
                resources = await service.clone_and_ingest(git_url, UUID(user_id))
            
            # Update progress
            total = len(resources)
            for i, resource in enumerate(resources):
                self.update_state(
                    state='PROCESSING',
                    meta={
                        'current': i + 1,
                        'total': total,
                        'current_file': resource.metadata.get('path')
                    }
                )
                
                # Emit event for downstream processing
                await event_bus.emit(ResourceCreatedEvent(resource_id=resource.id))
            
            return {
                'status': 'COMPLETED',
                'files_processed': total
            }
            
    except Exception as e:
        self.update_state(
            state='FAILED',
            meta={'error': str(e)}
        )
        raise
```

### 5. API Endpoints

**Location**: `app/modules/resources/router.py`

**New Endpoints**:

```python
@router.post("/ingest-repo", response_model=IngestionTaskResponse)
async def ingest_repository(
    request: RepoIngestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger async repository ingestion.
    
    Request:
    {
        "path": "/path/to/repo",  // Optional
        "git_url": "https://...",  // Optional
    }
    
    Response:
    {
        "task_id": "abc-123",
        "status": "PENDING"
    }
    """
    
@router.get("/ingest-repo/{task_id}/status", response_model=IngestionStatusResponse)
async def get_ingestion_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of repository ingestion task.
    
    Response:
    {
        "task_id": "abc-123",
        "status": "PROCESSING",
        "files_processed": 45,
        "total_files": 100,
        "current_file": "app/main.py"
    }
    """
```

## Data Models

### Resource Metadata Extensions

Existing `Resource.metadata` JSON field will store:

```json
{
    "path": "app/modules/auth/service.py",
    "repo_root": "/path/to/repo",
    "commit_hash": "abc123",
    "branch": "main",
    "classification": "PRACTICE",
    "language": "python"
}
```

### DocumentChunk Metadata Extensions

Existing `DocumentChunk.chunk_metadata` JSON field will store:

```json
{
    "function_name": "authenticate_user",
    "class_name": "AuthService",
    "start_line": 45,
    "end_line": 67,
    "language": "python",
    "type": "method"
}
```

### GraphRelationship Extensions

Existing `GraphRelationship.metadata` JSON field will store:

```json
{
    "source_file": "app/main.py",
    "target_symbol": "FastAPI",
    "line_number": 10,
    "confidence": 1.0
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Acceptance Criteria Testing Prework

**1.1** WHEN a user provides a local directory path, THE System SHALL recursively crawl all files and create Resource entries
- Thoughts: This is a property about all directories. We can generate random directory structures, ingest them, and verify that the count of Resources matches the count of non-ignored files.
- Testable: yes - property

**1.2** WHEN a user provides a Git repository URL, THE System SHALL clone the repository and ingest its contents
- Thoughts: This is testing a specific workflow with external dependencies (Git). We can test with a known small repository.
- Testable: yes - example

**1.3** WHEN crawling a repository, THE System SHALL respect .gitignore rules and exclude ignored files
- Thoughts: This is a property about all .gitignore patterns. We can generate random .gitignore rules and verify that matching files are excluded.
- Testable: yes - property

**1.4** WHEN crawling a repository, THE System SHALL filter out binary files and build artifacts
- Thoughts: This is a property about all binary files. We can generate random file sets with binary files and verify they're excluded.
- Testable: yes - property

**1.5** WHEN ingesting files, THE System SHALL preserve the directory structure in Resource metadata
- Thoughts: This is a property about all file paths. We can generate random directory structures and verify the path is preserved in metadata.
- Testable: yes - property

**1.6** WHEN ingesting files, THE System SHALL auto-classify resources into THEORY, PRACTICE, or GOVERNANCE categories
- Thoughts: This is a property about all file types. We can generate files with different extensions and verify classification.
- Testable: yes - property

**2.1-2.4** File classification rules
- Thoughts: These are specific classification rules that should hold for all files of given types.
- Testable: yes - property (can be combined)

**3.1** WHEN chunking a code file, THE System SHALL use Tree-Sitter to parse the Abstract Syntax Tree
- Thoughts: This is a property about all code files. We can generate random valid code and verify Tree-Sitter is used.
- Testable: yes - property

**3.2-3.3** AST parsing for functions and classes
- Thoughts: These are properties about all functions and classes. We can generate random code with functions/classes and verify they're identified.
- Testable: yes - property (can be combined)

**3.4** WHEN creating a code chunk, THE System SHALL store function_name, class_name, start_line, end_line in chunk_metadata
- Thoughts: This is a property about all code chunks. We can generate random code chunks and verify metadata is present.
- Testable: yes - property

**3.7** WHEN Tree-Sitter parsing fails, THE System SHALL fall back to character-based chunking with a warning
- Thoughts: This is testing error handling behavior. We can provide invalid syntax and verify fallback.
- Testable: yes - example

**4.1-4.3** Static analysis extraction
- Thoughts: These are properties about all code with imports/definitions/calls. We can generate random code and verify relationships are extracted.
- Testable: yes - property (can be combined)

**4.7** WHEN static analysis is performed, THE System SHALL not execute any code (security constraint)
- Thoughts: This is a security property. We can provide code with side effects and verify it's not executed.
- Testable: yes - property

**5.1-5.5** Async processing
- Thoughts: These are properties about task lifecycle. We can test task state transitions.
- Testable: yes - property

**7.1-7.4** Metadata preservation
- Thoughts: These are properties about all repository files. We can verify metadata is preserved.
- Testable: yes - property (can be combined)

**9.1-9.6** Error handling
- Thoughts: These are properties about error conditions. We can generate error scenarios and verify handling.
- Testable: yes - property (can be combined)

**10.1-10.5** Performance requirements
- Thoughts: These are performance properties. We can measure timing and verify constraints.
- Testable: yes - property

### Property Reflection

After reviewing all properties, I identify the following consolidation opportunities:

- Properties 2.1-2.4 (file classification) can be combined into one comprehensive property
- Properties 3.2-3.3 (AST parsing) can be combined into one property about logical unit extraction
- Properties 4.1-4.3 (static analysis) can be combined into one property about relationship extraction
- Properties 7.1-7.4 (metadata preservation) can be combined into one property about metadata completeness
- Properties 9.1-9.6 (error handling) can be combined into one property about graceful degradation

### Correctness Properties

**Property 1: Directory Crawling Completeness**
*For any* directory structure with N non-ignored files, ingesting the directory should create exactly N Resource entries with preserved file paths.
**Validates: Requirements 1.1, 1.5**

**Property 2: Gitignore Compliance**
*For any* .gitignore pattern and file set, files matching the pattern should be excluded from ingestion.
**Validates: Requirements 1.3**

**Property 3: Binary File Exclusion**
*For any* file set containing binary files, binary files should be excluded from ingestion.
**Validates: Requirements 1.4**

**Property 4: File Classification Correctness**
*For any* file with a known extension, the classification should match the expected category (PRACTICE for .py/.js, THEORY for .pdf/.md with academic content, GOVERNANCE for CONTRIBUTING.md).
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

**Property 5: AST Logical Unit Extraction**
*For any* valid code file, all function and class definitions should be identified as separate chunks with correct line numbers.
**Validates: Requirements 3.2, 3.3**

**Property 6: Code Chunk Metadata Completeness**
*For any* code chunk created from a logical unit, the chunk_metadata should contain function_name/class_name, start_line, end_line, and language.
**Validates: Requirements 3.4, 3.5**

**Property 7: Parsing Fallback Safety**
*For any* code file where Tree-Sitter parsing fails, the system should fall back to character-based chunking without crashing.
**Validates: Requirements 3.7**

**Property 8: Static Analysis Relationship Extraction**
*For any* code chunk containing imports, definitions, or calls, the corresponding graph relationships (IMPORTS, DEFINES, CALLS) should be created.
**Validates: Requirements 4.1, 4.2, 4.3**

**Property 9: Static Analysis Safety**
*For any* code file analyzed, no code execution should occur (verified by absence of side effects).
**Validates: Requirements 4.7**

**Property 10: Task State Transitions**
*For any* repository ingestion task, the task state should transition from PENDING → PROCESSING → COMPLETED (or FAILED), never skipping states.
**Validates: Requirements 5.1, 5.2, 5.4**

**Property 11: Repository Metadata Preservation**
*For any* file ingested from a repository, the Resource metadata should contain path, repo_root, and (if from Git) commit_hash and branch.
**Validates: Requirements 7.1, 7.2, 7.3, 7.4**

**Property 12: Graceful Error Handling**
*For any* file that cannot be processed (read error, parse error, analysis error), the system should log the error and continue processing other files without data corruption.
**Validates: Requirements 9.1, 9.2, 9.3, 9.5, 9.6**

**Property 13: Performance Bounds**
*For any* repository with N files, AST parsing should complete within 2 seconds per file (P95) and graph extraction within 1 second per file (P95).
**Validates: Requirements 10.2, 10.3**

## Error Handling

### File System Errors
- **File not found**: Log error, skip file, continue processing
- **Permission denied**: Log error, skip file, continue processing
- **Binary file detected**: Skip file silently (expected behavior)

### Parsing Errors
- **Tree-Sitter parse failure**: Fall back to character-based chunking, log warning
- **Invalid syntax**: Fall back to character-based chunking, log warning
- **Unsupported language**: Fall back to character-based chunking, log info

### Git Errors
- **Clone failure**: Return error to user, do not create task
- **Invalid URL**: Return validation error immediately
- **Authentication required**: Return error with instructions

### Database Errors
- **Transaction failure**: Rollback, mark task as FAILED, allow retry
- **Constraint violation**: Log error, skip problematic file, continue
- **Connection loss**: Retry with exponential backoff

### Task Errors
- **Task timeout**: Mark as FAILED, log partial progress
- **Worker crash**: Celery will retry automatically
- **Out of memory**: Process files in smaller batches, log warning

## Testing Strategy

### Unit Tests

**Test File**: `tests/modules/resources/test_repo_ingestion.py`
- Test directory crawling with mock file system
- Test .gitignore pattern matching
- Test file classification logic
- Test binary file detection

**Test File**: `tests/modules/resources/test_code_chunking.py`
- Test Tree-Sitter parsing for each supported language
- Test logical unit extraction (functions, classes)
- Test chunk metadata creation
- Test fallback to character-based chunking

**Test File**: `tests/modules/graph/test_static_analysis.py`
- Test import extraction
- Test definition extraction
- Test call extraction (best-effort)
- Test relationship metadata

**Test File**: `tests/tasks/test_ingestion_tasks.py`
- Test task state transitions
- Test progress updates
- Test error handling
- Test event emission

### Property-Based Tests

**Test File**: `tests/properties/test_code_intelligence_properties.py`

All property tests should run with minimum 100 iterations.

**Property 1 Test**: Generate random directory structures, verify Resource count matches file count
**Property 2 Test**: Generate random .gitignore patterns, verify exclusion
**Property 3 Test**: Generate file sets with binary files, verify exclusion
**Property 4 Test**: Generate files with various extensions, verify classification
**Property 5 Test**: Generate random valid code, verify all functions/classes extracted
**Property 6 Test**: Generate random code chunks, verify metadata completeness
**Property 7 Test**: Generate invalid syntax, verify fallback behavior
**Property 8 Test**: Generate code with imports/defs/calls, verify relationships
**Property 9 Test**: Generate code with side effects, verify no execution
**Property 10 Test**: Trigger tasks, verify state transitions
**Property 11 Test**: Ingest repository files, verify metadata preservation
**Property 12 Test**: Generate error conditions, verify graceful handling
**Property 13 Test**: Measure parsing/extraction time, verify performance bounds

### Integration Tests

**Test File**: `tests/integration/test_code_pipeline.py`
- Test end-to-end repository ingestion
- Test AST chunking → Graph extraction pipeline
- Test event-driven processing (resource.created → chunking → graph)
- Test API endpoints with real Celery tasks

### Performance Tests

**Test File**: `tests/performance/test_code_intelligence_performance.py`
- Benchmark AST parsing speed
- Benchmark static analysis speed
- Benchmark repository ingestion throughput
- Verify P95 latency requirements

## Dependencies

### New Python Packages

Add to `requirements.txt`:
```
tree-sitter==0.20.4
tree-sitter-languages==1.10.2
gitpython==3.1.40
pathspec==0.12.1  # For .gitignore parsing
```

### Tree-Sitter Language Grammars

The `tree-sitter-languages` package includes pre-built parsers for:
- Python
- JavaScript/TypeScript
- Rust
- Go
- Java
- C/C++
- Ruby

No additional installation required.

## Migration Strategy

### Phase 1: Core Infrastructure (No Breaking Changes)
1. Add new dependencies
2. Create `RepoIngestionService` (new code, no changes to existing)
3. Create `CodeChunkingStrategy` (new code, extends existing factory)
4. Create `StaticAnalysisService` (new code, extends existing service)

### Phase 2: API Integration (Additive Only)
1. Add new API endpoints (no changes to existing endpoints)
2. Add Celery task (new task, no changes to existing tasks)
3. Update `ChunkingService` factory to support code files (backward compatible)

### Phase 3: Testing & Documentation
1. Add unit tests
2. Add property-based tests
3. Add integration tests
4. Update API documentation
5. Update architecture documentation

### Backward Compatibility

- All existing endpoints continue to work unchanged
- Existing text chunking strategies unaffected
- Existing graph extraction for semantic content unaffected
- New code paths only activated for code files
- Graceful fallback if Tree-Sitter unavailable

## Security Considerations

### Code Execution Prevention
- **Static analysis only**: Never execute ingested code
- **Sandboxing**: Tree-Sitter parsing is safe (no eval/exec)
- **Input validation**: Validate file paths to prevent directory traversal

### Git Repository Safety
- **URL validation**: Only allow https:// URLs (no file:// or git://)
- **Clone isolation**: Clone to temporary directory with restricted permissions
- **Size limits**: Reject repositories larger than 1GB
- **Timeout**: Abort clone operations after 5 minutes

### Rate Limiting
- **Ingestion endpoint**: Limit to 5 requests per hour per user
- **Concurrent tasks**: Limit to 3 concurrent ingestion tasks per user
- **File count**: Reject repositories with more than 10,000 files

### Authentication
- **Required**: All ingestion endpoints require authentication
- **Authorization**: Users can only ingest to their own resources
- **Audit logging**: Log all ingestion attempts with user ID and timestamp

## Performance Optimization

### Batch Processing
- Process files in batches of 50 to avoid memory exhaustion
- Commit database transactions per batch
- Emit events per batch (not per file)

### Caching
- Cache Tree-Sitter parsers (one per language)
- Cache .gitignore patterns per repository
- Cache file classification rules

### Parallel Processing
- Use Celery worker pool for concurrent file processing
- Limit concurrent workers to prevent resource exhaustion
- Use async I/O for file reading

### Memory Management
- Stream large files instead of loading entirely into memory
- Release AST trees after processing each file
- Use generators for directory traversal

## Monitoring & Observability

### Metrics to Track
- Repository ingestion success/failure rate
- Average files processed per repository
- AST parsing success rate per language
- Static analysis relationship extraction rate
- Task queue depth and processing time

### Logging
- Log each repository ingestion start/completion
- Log parsing failures with file path and error
- Log static analysis warnings
- Log performance metrics (parsing time, extraction time)

### Alerts
- Alert if ingestion failure rate > 10%
- Alert if task queue depth > 100
- Alert if parsing time P95 > 5 seconds
- Alert if worker crashes

## Future Enhancements

### Phase 18.1: Advanced Static Analysis
- Full symbol resolution (not just pattern matching)
- Cross-file call graph
- Type inference for dynamic languages
- Dependency graph visualization

### Phase 18.2: Code Search Enhancements
- Semantic code search (search by functionality, not just keywords)
- Code similarity detection
- Duplicate code detection
- Code quality metrics

### Phase 18.3: Additional Languages
- PHP, Ruby, Swift, Kotlin
- Shell scripts (bash, zsh)
- Configuration languages (YAML, TOML, JSON)

### Phase 18.4: Git Integration
- Incremental updates (only process changed files)
- Branch comparison
- Commit history analysis
- Blame information
