# Field Mapping Reference

This document provides a comprehensive mapping of legacy field names to current field names in the Neo Alexandria 2.0 database models. This reference is essential for updating test fixtures and ensuring tests use the correct field names.

## Resource Model Field Mappings

### Current Model Location
- **Primary Definition**: `backend/app/modules/resources/model.py`
- **Legacy Definition**: `backend/app/database/models.py` (same structure)

### Dublin Core Field Mappings

The Resource model implements the Dublin Core metadata standard. Tests using legacy field names must be updated to use the correct Dublin Core field names.

| Legacy Field Name | Current Field Name | Type | Dublin Core Element | Notes |
|-------------------|-------------------|------|---------------------|-------|
| `url` | `source` | `String` | `dc:source` | URL or source location of the resource |
| `resource_type` | `type` | `String` | `dc:type` | Resource type (article, book, etc.) |
| `resource_id` | `identifier` | `String` | `dc:identifier` | Unique identifier for the resource |
| `title` | `title` | `String` | `dc:title` | **UNCHANGED** - Title of the resource |
| `description` | `description` | `Text` | `dc:description` | **UNCHANGED** - Description of the resource |
| `creator` | `creator` | `String` | `dc:creator` | **UNCHANGED** - Creator/author |
| `publisher` | `publisher` | `String` | `dc:publisher` | **UNCHANGED** - Publisher |
| `contributor` | `contributor` | `String` | `dc:contributor` | **UNCHANGED** - Contributor |
| `date_created` | `date_created` | `DateTime` | `dc:date` | **UNCHANGED** - Creation date |
| `date_modified` | `date_modified` | `DateTime` | `dc:date` | **UNCHANGED** - Modification date |
| `format` | `format` | `String` | `dc:format` | **UNCHANGED** - File format |
| `language` | `language` | `String(16)` | `dc:language` | **UNCHANGED** - Language code |
| `coverage` | `coverage` | `String` | `dc:coverage` | **UNCHANGED** - Spatial/temporal coverage |
| `rights` | `rights` | `String` | `dc:rights` | **UNCHANGED** - Rights statement |
| `subject` | `subject` | `JSON (List[str])` | `dc:subject` | **UNCHANGED** - Subject keywords (multi-valued) |
| `relation` | `relation` | `JSON (List[str])` | `dc:relation` | **UNCHANGED** - Related resources (multi-valued) |

### Complete Resource Model Fields

All fields in the current Resource model (as of Phase 13):

#### Core Dublin Core Fields
- `id`: UUID (primary key)
- `title`: String (required)
- `description`: Text (optional)
- `creator`: String (optional)
- `publisher`: String (optional)
- `contributor`: String (optional)
- `date_created`: DateTime (optional)
- `date_modified`: DateTime (optional)
- `type`: String (optional) - **formerly `resource_type`**
- `format`: String (optional)
- `identifier`: String (optional) - **formerly `resource_id`**
- `source`: String (optional) - **formerly `url`**
- `language`: String(16) (optional)
- `coverage`: String (optional)
- `rights`: String (optional)
- `subject`: JSON List[str] (multi-valued)
- `relation`: JSON List[str] (multi-valued)

#### Custom Application Fields
- `classification_code`: String (optional)
- `read_status`: String (default: "unread")
- `quality_score`: Float (default: 0.0)

#### Ingestion Workflow Fields
- `ingestion_status`: String (default: "pending")
- `ingestion_error`: Text (optional)
- `ingestion_started_at`: DateTime (optional)
- `ingestion_completed_at`: DateTime (optional)

#### Vector Embeddings (Phase 4 & 8)
- `embedding`: JSON List[float] (dense vector)
- `sparse_embedding`: Text (JSON string of token weights)
- `sparse_embedding_model`: String(100) (model name)
- `sparse_embedding_updated_at`: DateTime (optional)

#### Full-Text Search (Phase 13)
- `search_vector`: Text (PostgreSQL TSVector, NULL in SQLite)

#### Scholarly Metadata (Phase 6.5)
- `authors`: Text (JSON array of author objects)
- `affiliations`: Text (JSON array of institutions)
- `doi`: String(255) (indexed)
- `pmid`: String(50) (indexed)
- `arxiv_id`: String(50) (indexed)
- `isbn`: String(20)
- `journal`: String
- `conference`: String
- `volume`: String(50)
- `issue`: String(50)
- `pages`: String(50)
- `publication_year`: Integer (indexed)
- `funding_sources`: Text (JSON array)
- `acknowledgments`: Text

#### Content Structure
- `equation_count`: Integer (default: 0)
- `table_count`: Integer (default: 0)
- `figure_count`: Integer (default: 0)
- `reference_count`: Integer (optional)
- `equations`: Text (JSON array)
- `tables`: Text (JSON array)
- `figures`: Text (JSON array)

#### Metadata Quality
- `metadata_completeness_score`: Float (optional)
- `extraction_confidence`: Float (optional)
- `requires_manual_review`: Boolean (default: False)

#### Enhanced Quality Control (Phase 9)
- `quality_accuracy`: Float (optional)
- `quality_completeness`: Float (optional)
- `quality_consistency`: Float (optional)
- `quality_timeliness`: Float (optional)
- `quality_relevance`: Float (optional)
- `quality_overall`: Float (optional)
- `quality_weights`: Text (JSON)
- `quality_last_computed`: DateTime (optional)
- `quality_computation_version`: String(50) (optional)
- `is_quality_outlier`: Boolean (default: False)
- `outlier_score`: Float (optional)
- `outlier_reasons`: Text (JSON)
- `needs_quality_review`: Boolean (default: False)
- `summary_coherence`: Float (optional)
- `summary_consistency`: Float (optional)
- `summary_fluency`: Float (optional)
- `summary_relevance`: Float (optional)

#### OCR Metadata
- `is_ocr_processed`: Boolean (default: False)
- `ocr_confidence`: Float (optional)
- `ocr_corrections_applied`: Integer (optional)

#### Audit Fields
- `created_at`: DateTime (auto-generated)
- `updated_at`: DateTime (auto-updated)

#### Relationships
- `collections`: Many-to-many with Collection (via collection_resources)
- `annotations`: One-to-many with Annotation

## User Model Field Mappings

### Current Model Location
- **Definition**: `backend/app/database/models.py` (lines 1007-1060)

### User Model Fields

The User model in Neo Alexandria 2.0 is a **simplified model** without authentication fields. It is used primarily for the Phase 11 recommendation system.

| Field Name | Type | Notes |
|------------|------|-------|
| `id` | UUID | Primary key |
| `email` | String(255) | Unique, indexed |
| `username` | String(255) | Unique, indexed |
| `created_at` | DateTime | Auto-generated |

### Important Note: No Password Field

**The User model does NOT contain any password-related fields** (no `password`, `hashed_password`, or `password_hash`).

If tests are attempting to create User instances with password fields, they are likely:
1. Using an outdated User model definition
2. Confusing the User model with an authentication model from a different system
3. Need to be updated to remove password-related code

### User Relationships
- `profile`: One-to-one with UserProfile
- `interactions`: One-to-many with UserInteraction
- `recommendation_feedback`: One-to-many with RecommendationFeedback

## Other Core Models

### Collection Model
**Location**: `backend/app/database/models.py` (lines 600-700)

Key fields:
- `id`: UUID (primary key)
- `name`: String(255) (required)
- `description`: Text (optional)
- `owner_id`: String(255) (required, indexed)
- `visibility`: String(20) (default: "private", indexed)
- `parent_id`: UUID (optional, self-referential)
- `embedding`: JSON List[float] (optional)
- `created_at`: DateTime
- `updated_at`: DateTime

### TaxonomyNode Model
**Location**: `backend/app/database/models.py` (lines 700-800)

Key fields:
- `id`: UUID (primary key)
- `name`: String(255) (required)
- `slug`: String(255) (unique)
- `parent_id`: UUID (optional, self-referential)
- `level`: Integer (default: 0)
- `path`: String(1000) (materialized path)
- `description`: Text (optional)
- `keywords`: JSON List[str] (optional)

### Annotation Model
**Location**: `backend/app/database/models.py` (lines 800-900)

Key fields:
- `id`: UUID (primary key)
- `resource_id`: UUID (foreign key to resources)
- `user_id`: String(255) (indexed)
- `start_offset`: Integer (required)
- `end_offset`: Integer (required)
- `highlighted_text`: Text (required)
- `note`: Text (optional)
- `tags`: Text (JSON array)
- `color`: String(7) (default: "#FFFF00")

## Test Fixture Update Patterns

### Pattern 1: Resource Creation with Legacy Fields

**INCORRECT (Legacy)**:
```python
resource = Resource(
    url="https://example.com/paper.pdf",
    resource_type="article",
    title="Sample Paper"
)
```

**CORRECT (Current)**:
```python
resource = Resource(
    source="https://example.com/paper.pdf",
    type="article",
    title="Sample Paper"
)
```

### Pattern 2: Resource Creation with Identifier

**INCORRECT (Legacy)**:
```python
resource = Resource(
    resource_id="doi:10.1234/example",
    title="Sample Paper"
)
```

**CORRECT (Current)**:
```python
resource = Resource(
    identifier="doi:10.1234/example",
    title="Sample Paper"
)
```

### Pattern 3: User Creation (No Password)

**INCORRECT (Outdated)**:
```python
user = User(
    email="user@example.com",
    username="testuser",
    hashed_password="$2b$12$..."  # WRONG - field doesn't exist
)
```

**CORRECT (Current)**:
```python
user = User(
    email="user@example.com",
    username="testuser"
    # No password field needed
)
```

## Files Requiring Updates

Based on the design document, the following files need field name updates:

### Test Fixture Files (conftest.py)
1. `backend/tests/conftest.py` - Root test fixtures
2. `backend/tests/integration/conftest.py` - Integration test fixtures
3. `backend/tests/unit/phase7_collections/conftest.py` - Collection fixtures
4. `backend/tests/integration/workflows/conftest.py` - Workflow fixtures
5. `backend/tests/integration/phase8_classification/conftest.py` - Classification fixtures
6. `backend/tests/integration/phase9_quality/conftest.py` - Quality fixtures
7. `backend/tests/integration/phase11_recommendations/conftest.py` - Recommendation fixtures
8. `backend/tests/integration/phase3_search/conftest.py` - Search fixtures

### Test Files with Direct Model Instantiation
Approximately 80 test files across:
- `backend/tests/unit/phase8_classification/`
- `backend/tests/unit/phase9_quality/`
- `backend/tests/integration/workflows/`
- `backend/tests/integration/phase8_classification/`
- `backend/tests/integration/phase9_quality/`
- `backend/tests/integration/phase11_recommendations/`

## Search and Replace Patterns

To update test files efficiently, use these search patterns:

### Resource Field Updates
```bash
# Find all instances of url= in Resource creation
grep -r "Resource(.*url=" backend/tests/

# Find all instances of resource_type= in Resource creation
grep -r "Resource(.*resource_type=" backend/tests/

# Find all instances of resource_id= in Resource creation
grep -r "Resource(.*resource_id=" backend/tests/
```

### Replacement Strategy
1. Search for `Resource(url=` → Replace with `Resource(source=`
2. Search for `Resource(resource_type=` → Replace with `Resource(type=`
3. Search for `resource_id=` → Replace with `identifier=`
4. Search for User password fields → Remove entirely

## Verification Commands

After updating field names, verify fixes with:

```bash
# Test Resource fixtures
pytest backend/tests/integration/workflows/ -v -k "resource"

# Test Collection fixtures
pytest backend/tests/unit/phase7_collections/ -v

# Test Classification fixtures
pytest backend/tests/unit/phase8_classification/ -v

# Test Quality fixtures
pytest backend/tests/unit/phase9_quality/ -v

# Check for "unexpected keyword argument" errors
pytest backend/tests/ -v 2>&1 | grep "unexpected keyword argument"
```

## Summary

### Critical Changes
1. **`url` → `source`** (Dublin Core dc:source)
2. **`resource_type` → `type`** (Dublin Core dc:type)
3. **`resource_id` → `identifier`** (Dublin Core dc:identifier)
4. **User model has NO password field** (remove all password-related code)

### Impact
- Approximately **80 test files** need updates
- Approximately **8 conftest.py files** need fixture updates
- All direct Resource instantiation in tests must use correct field names

### Priority
This is a **P0 (Critical)** fix as it affects the foundation of the test suite. Database model field mismatches cause immediate test failures and must be fixed before other service-level fixes can be validated.
