# Phase 6.5 Usage Examples: Scholarly Metadata Extraction

This document provides practical examples for using the Phase 6.5 scholarly metadata extraction features.

## Table of Contents

1. [Basic Metadata Extraction](#basic-metadata-extraction)
2. [Accessing Equations](#accessing-equations)
3. [Working with Tables](#working-with-tables)
4. [Manual Extraction Triggers](#manual-extraction-triggers)
5. [Analytics and Statistics](#analytics-and-statistics)
6. [Python SDK Examples](#python-sdk-examples)

---

## Basic Metadata Extraction

### Get Complete Scholarly Metadata

Retrieve all scholarly metadata for a resource:

```bash
curl http://localhost:8000/scholarly/resources/123e4567-e89b-12d3-a456-426614174000/metadata
```

**Response:**

```json
{
  "resource_id": "123e4567-e89b-12d3-a456-426614174000",
  "authors": [
    {
      "name": "John Doe",
      "affiliation": "MIT",
      "orcid": "0000-0001-2345-6789"
    },
    {
      "name": "Jane Smith",
      "affiliation": "Stanford University",
      "orcid": null
    }
  ],
  "doi": "10.1234/example.2024.001",
  "arxiv_id": "2024.12345",
  "journal": "Journal of Example Research",
  "publication_year": 2024,
  "volume": "42",
  "issue": "3",
  "pages": "123-145",
  "equation_count": 15,
  "table_count": 4,
  "figure_count": 8,
  "metadata_completeness_score": 0.87,
  "extraction_confidence": 0.92,
  "requires_manual_review": false
}
```

---

## Accessing Equations

### Get All Equations (LaTeX Format)

```bash
curl http://localhost:8000/scholarly/resources/123e4567-e89b-12d3-a456-426614174000/equations?format=latex
```

**Response:**

```json
[
  {
    "position": 0,
    "latex": "E = mc^2",
    "context": "Einstein's famous equation E = mc^2 relates energy and mass.",
    "confidence": 0.95
  },
  {
    "position": 1,
    "latex": "\\frac{d}{dx}(x^2) = 2x",
    "context": "The derivative of x squared is \\frac{d}{dx}(x^2) = 2x as shown.",
    "confidence": 0.88
  },
  {
    "position": 2,
    "latex": "\\int_0^\\infty e^{-x} dx = 1",
    "context": "The integral \\int_0^\\infty e^{-x} dx = 1 converges.",
    "confidence": 0.91
  }
]
```

### Get Equations in MathML Format

```bash
curl http://localhost:8000/scholarly/resources/123e4567-e89b-12d3-a456-426614174000/equations?format=mathml
```

**Response:**

```json
[
  {
    "position": 0,
    "latex": "<math><mi>E</mi><mo>=</mo><mi>m</mi><msup><mi>c</mi><mn>2</mn></msup></math>",
    "context": "Einstein's famous equation E = mc^2 relates energy and mass.",
    "confidence": 0.95
  }
]
```

---

## Working with Tables

### Get All Tables with Full Data

```bash
curl http://localhost:8000/scholarly/resources/123e4567-e89b-12d3-a456-426614174000/tables?include_data=true
```

**Response:**

```json
[
  {
    "position": 0,
    "caption": "Table 1: Experimental Results",
    "headers": ["Method", "Accuracy", "F1-Score", "Runtime (ms)"],
    "rows": [
      ["Baseline", "0.85", "0.82", "120"],
      ["Proposed", "0.92", "0.90", "95"],
      ["State-of-art", "0.89", "0.87", "150"]
    ],
    "format": "html",
    "confidence": 0.94
  },
  {
    "position": 1,
    "caption": "Table 2: Dataset Statistics",
    "headers": ["Dataset", "Size", "Classes"],
    "rows": [
      ["Train", "10000", "10"],
      ["Val", "2000", "10"],
      ["Test", "3000", "10"]
    ],
    "format": "camelot",
    "confidence": 0.88
  }
]
```

### Get Table Metadata Only (Faster)

```bash
curl http://localhost:8000/scholarly/resources/123e4567-e89b-12d3-a456-426614174000/tables?include_data=false
```

**Response:**

```json
[
  {
    "position": 0,
    "caption": "Table 1: Experimental Results",
    "headers": ["Method", "Accuracy", "F1-Score", "Runtime (ms)"],
    "rows": [],
    "format": "html",
    "confidence": 0.94
  },
  {
    "position": 1,
    "caption": "Table 2: Dataset Statistics",
    "headers": ["Dataset", "Size", "Classes"],
    "rows": [],
    "format": "camelot",
    "confidence": 0.88
  }
]
```

---

## Manual Extraction Triggers

### Trigger Metadata Extraction

Manually trigger scholarly metadata extraction for a resource:

```bash
curl -X POST http://localhost:8000/scholarly/resources/123e4567-e89b-12d3-a456-426614174000/metadata/extract \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

**Response:**

```json
{
  "status": "queued",
  "resource_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Metadata extraction queued for processing"
}
```

### Force Re-extraction

Re-extract metadata even if already processed:

```bash
curl -X POST http://localhost:8000/scholarly/resources/123e4567-e89b-12d3-a456-426614174000/metadata/extract \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

---

## Analytics and Statistics

### Get System-Wide Metadata Statistics

```bash
curl http://localhost:8000/scholarly/metadata/completeness-stats
```

**Response:**

```json
{
  "total_resources": 1250,
  "with_doi": 450,
  "with_authors": 520,
  "with_publication_year": 680,
  "avg_completeness_score": 0.72,
  "requires_review_count": 85,
  "by_content_type": {
    "application/pdf": 800,
    "text/html": 350,
    "text/markdown": 100
  }
}
```

---

## Python SDK Examples

### Extract Metadata Programmatically

```python
from backend.app.services.metadata_extractor import MetadataExtractor
from backend.app.database.base import SessionLocal

# Create database session
db = SessionLocal()

# Initialize extractor
extractor = MetadataExtractor(db)

# Extract metadata for a resource
resource_id = "123e4567-e89b-12d3-a456-426614174000"
metadata = extractor.extract_scholarly_metadata(resource_id)

print(f"DOI: {metadata.get('doi')}")
print(f"Publication Year: {metadata.get('publication_year')}")
print(f"Equation Count: {metadata.get('equation_count')}")
print(f"Completeness Score: {metadata.get('metadata_completeness_score')}")

db.close()
```

### Parse Equations from Text

```python
from backend.app.utils.equation_parser import EquationParser

parser = EquationParser()

text = """
The famous equation $E = mc^2$ relates energy and mass.
The quadratic formula is: $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$
"""

equations = parser.extract_latex_from_text(text)

for eq in equations:
    print(f"Position {eq['position']}: {eq['latex']} ({eq['type']})")
    
    # Validate LaTeX
    valid, error = parser.validate_latex(eq['latex'])
    if valid:
        print("  ✓ Valid LaTeX")
    else:
        print(f"  ✗ Invalid: {error}")
```

### Extract Tables from HTML

```python
from backend.app.utils.table_extractor import TableExtractor

extractor = TableExtractor()

html = """
<table>
    <caption>Table 1: Results</caption>
    <thead>
        <tr><th>Method</th><th>Score</th></tr>
    </thead>
    <tbody>
        <tr><td>A</td><td>0.85</td></tr>
        <tr><td>B</td><td>0.92</td></tr>
    </tbody>
</table>
"""

tables = extractor.extract_from_html(html)

for table in tables:
    print(f"Caption: {table['caption']}")
    print(f"Headers: {table['headers']}")
    print(f"Rows: {len(table['rows'])}")
    
    # Validate structure
    confidence = extractor.validate_table_structure(table)
    print(f"Confidence: {confidence:.2f}")
```

### Query Resources by Scholarly Metadata

```python
from backend.app.database import models as db_models
from backend.app.database.base import SessionLocal

db = SessionLocal()

# Find all papers with DOI
papers_with_doi = db.query(db_models.Resource).filter(
    db_models.Resource.doi.isnot(None)
).all()

print(f"Found {len(papers_with_doi)} papers with DOI")

# Find papers from specific year
papers_2024 = db.query(db_models.Resource).filter(
    db_models.Resource.publication_year == 2024
).all()

print(f"Found {len(papers_2024)} papers from 2024")

# Find papers with high metadata completeness
high_quality = db.query(db_models.Resource).filter(
    db_models.Resource.metadata_completeness_score >= 0.8
).all()

print(f"Found {len(high_quality)} papers with >80% metadata completeness")

db.close()
```

### Batch Process Multiple Resources

```python
from backend.app.services.metadata_extractor import MetadataExtractor
from backend.app.database import models as db_models
from backend.app.database.base import SessionLocal

db = SessionLocal()
extractor = MetadataExtractor(db)

# Get all resources without scholarly metadata
resources = db.query(db_models.Resource).filter(
    db_models.Resource.doi.is_(None),
    db_models.Resource.format.in_(['application/pdf', 'text/html'])
).limit(100).all()

print(f"Processing {len(resources)} resources...")

for resource in resources:
    try:
        metadata = extractor.extract_scholarly_metadata(str(resource.id))
        print(f"✓ Processed {resource.title[:50]}...")
    except Exception as e:
        print(f"✗ Failed {resource.title[:50]}: {e}")

db.close()
```

---

## Integration with Ingestion Pipeline

### Automatic Extraction During Ingestion

The scholarly metadata extraction can be integrated into the ingestion pipeline:

```python
# In backend/app/services/resource_service.py

def process_ingestion(resource_id: str, ...):
    # ... existing ingestion logic ...
    
    # After content extraction and before quality scoring:
    if _is_scholarly_resource(resource):
        from backend.app.services.metadata_extractor import MetadataExtractor
        extractor = MetadataExtractor(session)
        extractor.extract_scholarly_metadata(resource_id)
    
    # ... continue with quality scoring ...
```

### Check if Resource is Scholarly

```python
def _is_scholarly_resource(resource: db_models.Resource) -> bool:
    """Determine if resource is scholarly/academic content."""
    scholarly_domains = [
        "arxiv.org", "doi.org", "pubmed", "scholar.google",
        "ieee.org", "acm.org", "springer.com", "sciencedirect.com"
    ]
    
    # Check URL
    if any(domain in resource.source for domain in scholarly_domains):
        return True
    
    # Check content type
    if resource.format == "application/pdf":
        # Check for scholarly indicators in content
        if resource.description:
            keywords = ["abstract", "references", "doi:", "arxiv:"]
            count = sum(1 for kw in keywords if kw in resource.description.lower())
            if count >= 2:
                return True
    
    return False
```

---

## Error Handling

### Handle Missing Metadata

```python
from backend.app.routers.scholarly import get_scholarly_metadata
from fastapi import HTTPException

try:
    metadata = await get_scholarly_metadata(resource_id, db)
    print(f"DOI: {metadata.doi or 'Not available'}")
except HTTPException as e:
    if e.status_code == 404:
        print("Resource not found")
    elif e.status_code == 400:
        print("Invalid resource ID")
```

### Check Extraction Status

```python
resource = db.query(db_models.Resource).filter(
    db_models.Resource.id == resource_uuid
).first()

if resource.requires_manual_review:
    print("⚠️ Extraction confidence low - manual review recommended")
    print(f"Confidence: {resource.extraction_confidence:.2f}")
    print(f"Completeness: {resource.metadata_completeness_score:.2f}")
else:
    print("✓ Extraction successful")
```

---

## Best Practices

1. **Check Completeness Score**: Always check `metadata_completeness_score` to assess data quality
2. **Handle Missing Fields**: All scholarly fields are optional - always check for None
3. **Use Background Tasks**: For batch processing, use background tasks to avoid timeouts
4. **Validate Extracted Data**: Cross-reference DOIs with external APIs when critical
5. **Monitor Review Queue**: Regularly check resources with `requires_manual_review=True`
6. **Cache Results**: Metadata extraction is expensive - cache results when possible
7. **Graceful Degradation**: Handle missing optional dependencies (camelot, tabula) gracefully

---

## Troubleshooting

### No Equations Extracted

- Check if content contains LaTeX markup ($...$, $$...$$)
- Verify content is properly stored in database
- Check extraction confidence score

### Tables Not Detected

- Ensure PDF has actual tables (not images of tables)
- Try different extraction methods (camelot vs tabula)
- Check if HTML tables have proper structure

### Low Completeness Score

- Content may not be scholarly/academic
- Source document may lack metadata
- Consider manual metadata entry for important resources

### Extraction Takes Too Long

- Large PDFs can be slow (especially with camelot)
- Use background tasks for batch processing
- Consider setting limits on equation/table counts

---

## Next Steps

- Explore [API Documentation](API_DOCUMENTATION.md) for complete endpoint reference
- Review [CHANGELOG](CHANGELOG.md) for latest updates
- Check [PHASE6_5_IMPLEMENTATION_SUMMARY](../PHASE6_5_IMPLEMENTATION_SUMMARY.md) for technical details
