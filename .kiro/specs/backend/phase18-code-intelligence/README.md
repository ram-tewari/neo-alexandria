# Phase 18: Code Intelligence Pipeline

## Status
**Phase**: Planning Complete
**Started**: January 4, 2026
**Completed**: Not yet started

## Overview

Phase 18 transforms Neo Alexandria from a "File Library" to a "Code-Aware Context Server" by implementing intelligent code repository ingestion, AST-based chunking, and static analysis capabilities.

## Key Features

1. **Repository Ingestion**: Ingest entire code repositories (local directories or Git URLs)
2. **Smart Chunking**: AST-based chunking by logical units (functions, classes) instead of character count
3. **Static Analysis**: Extract code relationships (IMPORTS, DEFINES, CALLS) without executing code
4. **Multi-Language Support**: Python, JavaScript/TypeScript, Rust, Go, Java
5. **Async Processing**: Handle large repositories via Celery task queue
6. **API Endpoints**: REST API for triggering ingestion and tracking progress

## Architecture

### Modules Affected
- **Resources Module**: Repository ingestion, AST chunking, file classification
- **Graph Module**: Static analysis, code relationship extraction
- **Tasks Module**: Async ingestion via Celery

### New Components
- `RepoIngestionService`: Directory crawling and Git cloning
- `CodeChunkingStrategy`: Tree-Sitter-based AST chunking
- `StaticAnalysisService`: Code relationship extraction
- `ingest_repo_task`: Celery task for async processing

### Technology Stack
- **Tree-Sitter**: Fast, incremental parser for AST generation
- **GitPython**: Git repository cloning and metadata extraction
- **Pathspec**: .gitignore pattern matching
- **Celery**: Async task processing

## Documents

- [requirements.md](./requirements.md) - User stories and acceptance criteria
- [design.md](./design.md) - Technical architecture and design decisions
- [tasks.md](./tasks.md) - Implementation checklist

## Dependencies

### New Python Packages
```
tree-sitter==0.20.4
tree-sitter-languages==1.10.2
gitpython==3.1.40
pathspec==0.12.1
```

### Existing Infrastructure
- PostgreSQL/SQLite database (DocumentChunk, GraphRelationship tables)
- Celery task queue
- Event bus (resource.created events)

## Success Criteria

- [ ] Can ingest local directory with 100+ files
- [ ] Can ingest Git repository from URL
- [ ] Code files chunked by functions/classes with metadata
- [ ] Graph relationships extracted for imports/definitions/calls
- [ ] API endpoints work with authentication and rate limiting
- [ ] All tests pass with >90% coverage
- [ ] Documentation complete and accurate
- [ ] Performance requirements met (P95 < 2s parsing, < 1s extraction)

## Testing Strategy

### Property-Based Tests (13 properties)
- Directory crawling completeness
- Gitignore compliance
- Binary file exclusion
- File classification correctness
- AST logical unit extraction
- Code chunk metadata completeness
- Parsing fallback safety
- Static analysis relationship extraction
- Static analysis safety (no code execution)
- Task state transitions
- Repository metadata preservation
- Graceful error handling
- Performance bounds

### Integration Tests
- End-to-end repository ingestion
- AST chunking → Graph extraction pipeline
- Event-driven processing
- API endpoints with Celery tasks

### Performance Tests
- AST parsing speed benchmarks
- Static analysis speed benchmarks
- Repository ingestion throughput

## Related Documentation

- [API Documentation](../../../backend/docs/api/resources.md) - Resources API
- [API Documentation](../../../backend/docs/api/graph.md) - Graph API
- [Architecture](../../../backend/docs/architecture/modules.md) - Module architecture
- [Code Ingestion Guide](../../../backend/docs/guides/code-ingestion.md) - User guide (to be created)

## Migration Notes

- **Backward Compatible**: All existing endpoints continue to work unchanged
- **Additive Only**: New endpoints and strategies added, no breaking changes
- **Graceful Fallback**: If Tree-Sitter unavailable, falls back to character-based chunking
- **No Schema Changes**: Uses existing DocumentChunk and GraphRelationship tables

## Security Considerations

- **No Code Execution**: Static analysis only, never executes ingested code
- **Input Validation**: Validates file paths to prevent directory traversal
- **Git Safety**: Only allows https:// URLs, rejects file:// and git://
- **Rate Limiting**: Limits ingestion requests to prevent abuse
- **Authentication**: All endpoints require authentication

## Performance Targets

- **AST Parsing**: < 2 seconds per file (P95)
- **Static Analysis**: < 1 second per file (P95)
- **Repository Ingestion**: < 30 minutes for 1000 files
- **Concurrent Tasks**: Limit to 3 per user
- **Batch Size**: Process 50 files per batch

## Future Enhancements (Phase 18.1+)

- Full symbol resolution (not just pattern matching)
- Cross-file call graph
- Type inference for dynamic languages
- Semantic code search
- Code similarity detection
- Additional languages (PHP, Ruby, Swift, Kotlin)
- Incremental updates (only process changed files)
- Branch comparison and commit history analysis
