# Scholarly Module

## Purpose

The Scholarly module handles academic metadata extraction for research papers and scholarly content. It extracts authors, DOIs, publication details, equations, tables, and other academic metadata.

## Architecture

This module follows the vertical slice architecture pattern:

```
scholarly/
├── __init__.py       # Public interface
├── router.py         # API endpoints (5 endpoints)
├── extractor.py      # Metadata extraction service
├── schema.py         # Pydantic schemas
├── model.py          # Database models (none - uses Resource model)
├── handlers.py       # Event handlers
└── README.md         # This file
```

## Public Interface

### Router Endpoints

1. **GET /scholarly/resources/{resource_id}/metadata**
   - Get complete scholarly metadata for a resource
   - Returns: ScholarlyMetadataResponse

2. **GET /scholarly/resources/{resource_id}/equations**
   - Get all equations from a resource
   - Query params: format (latex|mathml)
   - Returns: List[Equation]

3. **GET /scholarly/resources/{resource_id}/tables**
   - Get all tables from a resource
   - Query params: include_data (bool)
   - Returns: List[TableData]

4. **POST /scholarly/resources/{resource_id}/metadata/extract**
   - Manually trigger metadata extraction
   - Body: MetadataExtractionRequest
   - Returns: MetadataExtractionResponse

5. **GET /scholarly/metadata/completeness-stats**
   - Get aggregate statistics on metadata completeness
   - Returns: MetadataCompletenessStats

### Service Classes

**MetadataExtractor**
- `extract_scholarly_metadata(resource_id: str) -> Dict`
- `extract_paper_metadata(content: str, content_type: str) -> Dict`
- `emit_authors_extracted_event(resource_id: str, authors: List[Dict]) -> None`

### Schema Classes

- `Author`: Author information with affiliation and ORCID
- `Equation`: Mathematical equation with LaTeX representation
- `TableData`: Structured table data
- `Figure`: Figure/image metadata
- `ScholarlyMetadataResponse`: Complete scholarly metadata
- `MetadataExtractionRequest`: Request to trigger extraction
- `MetadataExtractionResponse`: Response from extraction trigger
- `MetadataCompletenessStats`: Aggregate statistics

## Event-Driven Communication

### Events Emitted

1. **metadata.extracted**
   - When: Metadata is successfully extracted
   - Payload: `{resource_id, metadata_fields, completeness_score}`
   - Priority: LOW

2. **equations.parsed**
   - When: Equations are found and parsed
   - Payload: `{resource_id, equation_count, equations}`
   - Priority: LOW

3. **tables.extracted**
   - When: Tables are extracted
   - Payload: `{resource_id, table_count, tables}`
   - Priority: LOW

4. **authors.extracted**
   - When: Authors are successfully extracted
   - Payload: `{resource_id, authors, author_count}`
   - Priority: LOW

### Events Subscribed

1. **resource.created**
   - Handler: `handle_resource_created(payload)`
   - Action: Trigger metadata extraction for new resources
   - Priority: LOW

## Dependencies

### Shared Kernel
- `shared.database`: Database session management
- `shared.event_bus`: Event emission and subscription

### External Services
- None (self-contained)

### Utilities
- `utils.equation_parser`: LaTeX equation parsing
- `utils.table_extractor`: Table structure extraction

## Data Storage

Scholarly metadata is stored directly on the Resource model:

**Resource Model Fields:**
- `authors`: JSON array of author objects
- `affiliations`: JSON array of affiliations
- `doi`: DOI identifier
- `pmid`: PubMed ID
- `arxiv_id`: arXiv identifier
- `isbn`: ISBN for books
- `journal`: Journal name
- `conference`: Conference name
- `volume`: Volume number
- `issue`: Issue number
- `pages`: Page range
- `publication_year`: Year of publication
- `funding_sources`: JSON array of funding sources
- `acknowledgments`: Acknowledgments text
- `equation_count`: Number of equations
- `table_count`: Number of tables
- `figure_count`: Number of figures
- `reference_count`: Number of references
- `equations`: JSON array of equation objects
- `tables`: JSON array of table objects
- `metadata_completeness_score`: Completeness score (0-1)
- `extraction_confidence`: Confidence score (0-1)
- `requires_manual_review`: Boolean flag
- `is_ocr_processed`: Boolean flag
- `ocr_confidence`: OCR confidence score
- `ocr_corrections_applied`: Number of OCR corrections

## Usage Examples

### Extract Metadata

```python
from app.modules.scholarly import MetadataExtractor

extractor = MetadataExtractor(db)
metadata = extractor.extract_scholarly_metadata(resource_id)
```

### Get Equations

```python
from app.modules.scholarly import scholarly_router

# GET /scholarly/resources/{resource_id}/equations?format=latex
```

### Subscribe to Events

```python
from app.modules.scholarly.handlers import register_handlers

# Register all event handlers
register_handlers()
```

## Testing

Tests are located in `tests/modules/scholarly/`:

- `test_extractor.py`: Metadata extraction tests
- `test_router.py`: API endpoint tests
- `test_handlers.py`: Event handler tests

## Migration Notes

This module was extracted from:
- `routers/scholarly.py` → `modules/scholarly/router.py`
- `services/metadata_extractor.py` → `modules/scholarly/extractor.py`
- `schemas/scholarly.py` → `modules/scholarly/schema.py`

No database models were extracted (uses Resource model directly).

## Future Enhancements

- Advanced NER for author extraction
- Citation parsing and linking
- Full-text equation search
- Table data extraction and querying
- Figure caption analysis
- Reference extraction and linking
