# Phase 7.5: Annotation & Active Reading System Examples

This document provides practical examples for using the Annotation and Active Reading features in Neo Alexandria 2.0.

## Table of Contents
- [Basic Annotation Operations](#basic-annotation-operations)
- [Search and Discovery](#search-and-discovery)
- [Export and Integration](#export-and-integration)
- [Advanced Use Cases](#advanced-use-cases)
- [Python SDK Examples](#python-sdk-examples)
- [Integration with Collections](#integration-with-collections)

## Basic Annotation Operations

### Create an Annotation

```bash
# Create a simple annotation with a note
curl -X POST http://127.0.0.1:8000/resources/660e8400-e29b-41d4-a716-446655440001/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "start_offset": 150,
    "end_offset": 200,
    "highlighted_text": "This is the key finding of the paper",
    "note": "Important result - contradicts previous assumptions",
    "tags": ["key-finding", "methodology"],
    "color": "#FFD700"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "resource_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "user123",
  "start_offset": 150,
  "end_offset": 200,
  "highlighted_text": "This is the key finding of the paper",
  "note": "Important result - contradicts previous assumptions",
  "tags": ["key-finding", "methodology"],
  "color": "#FFD700",
  "context_before": "...previous text leading up to...",
  "context_after": "...text following the highlight...",
  "is_shared": false,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### Create Annotation Without Note

```bash
# Create a simple highlight without a note
curl -X POST http://127.0.0.1:8000/resources/660e8400-e29b-41d4-a716-446655440001/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "start_offset": 500,
    "end_offset": 550,
    "highlighted_text": "Another important passage",
    "color": "#00FF00"
  }'
```

### Get Annotation Details

```bash
# Retrieve a specific annotation
curl "http://127.0.0.1:8000/annotations/550e8400-e29b-41d4-a716-446655440000"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "resource_id": "660e8400-e29b-41d4-a716-446655440001",
  "resource_title": "Deep Learning Fundamentals",
  "user_id": "user123",
  "start_offset": 150,
  "end_offset": 200,
  "highlighted_text": "This is the key finding",
  "note": "Important result",
  "tags": ["key-finding"],
  "color": "#FFD700",
  "context_before": "...previous text...",
  "context_after": "...following text...",
  "is_shared": false,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### Update Annotation

```bash
# Update annotation note and tags
curl -X PUT http://127.0.0.1:8000/annotations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "note": "Updated note with new insights after further reading",
    "tags": ["key-finding", "methodology", "revised"],
    "color": "#00FF00",
    "is_shared": true
  }'
```

### Delete Annotation

```bash
# Delete an annotation
curl -X DELETE http://127.0.0.1:8000/annotations/550e8400-e29b-41d4-a716-446655440000
```

### List Annotations for a Resource

```bash
# Get all annotations for a specific resource (in document order)
curl "http://127.0.0.1:8000/resources/660e8400-e29b-41d4-a716-446655440001/annotations"

# Include shared annotations from other users
curl "http://127.0.0.1:8000/resources/660e8400-e29b-41d4-a716-446655440001/annotations?include_shared=true"

# Filter by tags
curl "http://127.0.0.1:8000/resources/660e8400-e29b-41d4-a716-446655440001/annotations?tags=key-finding,methodology"
```

### List All User Annotations

```bash
# Get recent annotations across all resources
curl "http://127.0.0.1:8000/annotations?limit=20&sort_by=recent"

# Get oldest annotations with pagination
curl "http://127.0.0.1:8000/annotations?limit=50&offset=50&sort_by=oldest"
```

## Search and Discovery

### Full-Text Search

```bash
# Search annotations by keyword
curl "http://127.0.0.1:8000/annotations/search/fulltext?query=machine+learning&limit=10"

# Search for specific phrases
curl "http://127.0.0.1:8000/annotations/search/fulltext?query=neural+network+architecture&limit=25"
```

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_title": "Deep Learning Fundamentals",
      "highlighted_text": "machine learning algorithms",
      "note": "Key discussion of ML algorithms and their applications",
      "tags": ["algorithms", "ml"],
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

### Semantic Search

```bash
# Find conceptually related annotations
curl "http://127.0.0.1:8000/annotations/search/semantic?query=deep+learning+architectures&limit=10"

# Search by concept rather than exact keywords
curl "http://127.0.0.1:8000/annotations/search/semantic?query=convolutional+neural+networks&limit=5"
```

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_title": "Deep Learning Fundamentals",
      "highlighted_text": "neural network architectures",
      "note": "Discussion of CNN and RNN structures for image and sequence processing",
      "tags": ["architecture", "cnn", "rnn"],
      "similarity": 0.92,
      "created_at": "2024-01-01T10:00:00Z"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "resource_id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_title": "Deep Learning Fundamentals",
      "highlighted_text": "layer-wise feature extraction",
      "note": "How CNNs build hierarchical representations",
      "tags": ["cnn", "features"],
      "similarity": 0.87,
      "created_at": "2024-01-01T11:00:00Z"
    }
  ],
  "total": 2
}
```

### Tag-Based Search

```bash
# Find annotations with any of these tags
curl "http://127.0.0.1:8000/annotations/search/tags?tags=key-finding,methodology&match_all=false&limit=50"

# Find annotations with all of these tags
curl "http://127.0.0.1:8000/annotations/search/tags?tags=key-finding,methodology&match_all=true&limit=50"

# Search by single tag
curl "http://127.0.0.1:8000/annotations/search/tags?tags=important&limit=100"
```

## Export and Integration

### Export to Markdown

```bash
# Export all annotations to Markdown
curl "http://127.0.0.1:8000/annotations/export/markdown" > my_annotations.md

# Export annotations for a specific resource
curl "http://127.0.0.1:8000/annotations/export/markdown?resource_id=660e8400-e29b-41d4-a716-446655440001" > paper_notes.md
```

**Markdown Output:**
```markdown
# Annotations Export

## Deep Learning Fundamentals

### Annotation 1
**Highlighted Text:**
> This is the key finding of the paper

**Note:** Important result - contradicts previous assumptions

**Tags:** key-finding, methodology

**Created:** 2024-01-01 10:00:00

---

### Annotation 2
**Highlighted Text:**
> Convolutional layers extract spatial features

**Note:** Core concept for image processing with CNNs

**Tags:** architecture, cnn

**Created:** 2024-01-01 11:00:00

---

## Neural Network Architectures

### Annotation 3
**Highlighted Text:**
> Backpropagation algorithm

**Note:** Fundamental training method for neural networks

**Tags:** training, algorithms

**Created:** 2024-01-01 12:00:00

---
```

### Export to JSON

```bash
# Export all annotations to JSON
curl "http://127.0.0.1:8000/annotations/export/json" > annotations.json

# Export annotations for a specific resource
curl "http://127.0.0.1:8000/annotations/export/json?resource_id=660e8400-e29b-41d4-a716-446655440001" > paper_annotations.json
```

**JSON Output:**
```json
{
  "annotations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_title": "Deep Learning Fundamentals",
      "start_offset": 150,
      "end_offset": 200,
      "highlighted_text": "This is the key finding",
      "note": "Important result",
      "tags": ["key-finding", "methodology"],
      "color": "#FFD700",
      "is_shared": false,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1,
  "exported_at": "2024-01-01T12:00:00Z"
}
```

## Advanced Use Cases

### Annotating Research Papers

```bash
# 1. Ingest a research paper
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://arxiv.org/pdf/1234.5678.pdf"}'

# 2. Wait for ingestion to complete
# Check status: GET /resources/{resource_id}/status

# 3. Create annotations for key sections
curl -X POST http://127.0.0.1:8000/resources/{resource_id}/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "start_offset": 1500,
    "end_offset": 1650,
    "highlighted_text": "Our method achieves 95% accuracy on the benchmark",
    "note": "Main result - compare with baseline of 87%",
    "tags": ["results", "benchmark", "important"],
    "color": "#FF0000"
  }'

# 4. Annotate methodology section
curl -X POST http://127.0.0.1:8000/resources/{resource_id}/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "start_offset": 3200,
    "end_offset": 3450,
    "highlighted_text": "We use a transformer-based architecture with 12 layers",
    "note": "Architecture details - similar to BERT",
    "tags": ["methodology", "architecture", "transformer"],
    "color": "#00FF00"
  }'

# 5. Export annotations for literature review
curl "http://127.0.0.1:8000/annotations/export/markdown?resource_id={resource_id}" > paper_review.md
```

### Building a Personal Knowledge Base

```bash
# 1. Create annotations across multiple papers
# (Repeat annotation creation for different resources)

# 2. Search your knowledge base semantically
curl "http://127.0.0.1:8000/annotations/search/semantic?query=attention+mechanisms&limit=20"

# 3. Find all annotations on a specific topic
curl "http://127.0.0.1:8000/annotations/search/tags?tags=attention,transformer&match_all=false&limit=50"

# 4. Export your entire knowledge base
curl "http://127.0.0.1:8000/annotations/export/markdown" > knowledge_base.md
```

### Collaborative Reading (Shared Annotations)

```bash
# 1. Create a public annotation
curl -X POST http://127.0.0.1:8000/resources/{resource_id}/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "start_offset": 500,
    "end_offset": 600,
    "highlighted_text": "Critical limitation of the approach",
    "note": "This assumption may not hold in real-world scenarios",
    "tags": ["limitation", "discussion"],
    "color": "#FFA500",
    "is_shared": true
  }'

# 2. Other users can view shared annotations
curl "http://127.0.0.1:8000/resources/{resource_id}/annotations?include_shared=true"
```

### Tracking Reading Progress

```bash
# 1. Create annotations as you read
# Mark important passages with different colors

# 2. Review your reading history
curl "http://127.0.0.1:8000/annotations?sort_by=recent&limit=100"

# 3. Find what you read on a specific topic
curl "http://127.0.0.1:8000/annotations/search/fulltext?query=gradient+descent&limit=50"
```

## Python SDK Examples

### Basic Annotation Workflow

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

class AnnotationClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def create_annotation(
        self,
        resource_id: str,
        start_offset: int,
        end_offset: int,
        highlighted_text: str,
        note: str = None,
        tags: list = None,
        color: str = "#FFFF00"
    ):
        """Create a new annotation."""
        response = requests.post(
            f"{self.base_url}/resources/{resource_id}/annotations",
            json={
                "start_offset": start_offset,
                "end_offset": end_offset,
                "highlighted_text": highlighted_text,
                "note": note,
                "tags": tags or [],
                "color": color
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_resource_annotations(self, resource_id: str, include_shared: bool = False):
        """Get all annotations for a resource."""
        params = {"include_shared": include_shared}
        response = requests.get(
            f"{self.base_url}/resources/{resource_id}/annotations",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def search_semantic(self, query: str, limit: int = 10):
        """Search annotations semantically."""
        params = {"query": query, "limit": limit}
        response = requests.get(
            f"{self.base_url}/annotations/search/semantic",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def export_markdown(self, resource_id: str = None):
        """Export annotations to Markdown."""
        params = {}
        if resource_id:
            params["resource_id"] = resource_id
        
        response = requests.get(
            f"{self.base_url}/annotations/export/markdown",
            params=params
        )
        response.raise_for_status()
        return response.text

# Usage example
client = AnnotationClient(BASE_URL)

# Create annotation
annotation = client.create_annotation(
    resource_id="660e8400-e29b-41d4-a716-446655440001",
    start_offset=150,
    end_offset=200,
    highlighted_text="This is important",
    note="Key finding from the paper",
    tags=["important", "key-finding"],
    color="#FFD700"
)

print(f"Created annotation: {annotation['id']}")

# Search annotations
results = client.search_semantic("machine learning algorithms", limit=5)
for item in results["items"]:
    print(f"- {item['highlighted_text']} (similarity: {item['similarity']:.2f})")

# Export to Markdown
markdown = client.export_markdown()
with open("annotations.md", "w") as f:
    f.write(markdown)
```

### Batch Annotation Creation

```python
def annotate_paper_sections(client, resource_id: str, sections: list):
    """
    Annotate multiple sections of a paper.
    
    Args:
        client: AnnotationClient instance
        resource_id: UUID of the resource
        sections: List of dicts with section info
    """
    annotations = []
    
    for section in sections:
        annotation = client.create_annotation(
            resource_id=resource_id,
            start_offset=section["start"],
            end_offset=section["end"],
            highlighted_text=section["text"],
            note=section.get("note"),
            tags=section.get("tags", []),
            color=section.get("color", "#FFFF00")
        )
        annotations.append(annotation)
        print(f"Created annotation: {annotation['id']}")
    
    return annotations

# Example usage
sections = [
    {
        "start": 150,
        "end": 200,
        "text": "Main hypothesis of the paper",
        "note": "Central claim - needs verification",
        "tags": ["hypothesis", "main-claim"],
        "color": "#FF0000"
    },
    {
        "start": 500,
        "end": 650,
        "text": "Experimental methodology",
        "note": "Dataset: ImageNet, Model: ResNet-50",
        "tags": ["methodology", "experiments"],
        "color": "#00FF00"
    },
    {
        "start": 1200,
        "end": 1350,
        "text": "Results show 95% accuracy",
        "note": "Best result in the paper",
        "tags": ["results", "accuracy"],
        "color": "#0000FF"
    }
]

annotations = annotate_paper_sections(client, resource_id, sections)
```

### Building a Research Assistant

```python
class ResearchAssistant:
    def __init__(self, client: AnnotationClient):
        self.client = client
    
    def find_related_notes(self, query: str, limit: int = 10):
        """Find annotations related to a research query."""
        results = self.client.search_semantic(query, limit=limit)
        
        print(f"\nFound {results['total']} related annotations:\n")
        for item in results["items"]:
            print(f"Resource: {item['resource_title']}")
            print(f"Highlight: {item['highlighted_text']}")
            print(f"Note: {item.get('note', 'No note')}")
            print(f"Similarity: {item['similarity']:.2f}")
            print(f"Tags: {', '.join(item.get('tags', []))}")
            print("-" * 80)
        
        return results
    
    def summarize_topic(self, topic: str):
        """Summarize all annotations on a specific topic."""
        # Search by tags
        tag_results = requests.get(
            f"{self.client.base_url}/annotations/search/tags",
            params={"tags": topic, "limit": 100}
        ).json()
        
        print(f"\nSummary of annotations on '{topic}':\n")
        print(f"Total annotations: {tag_results['total']}")
        
        # Group by resource
        by_resource = {}
        for item in tag_results["items"]:
            resource_title = item["resource_title"]
            if resource_title not in by_resource:
                by_resource[resource_title] = []
            by_resource[resource_title].append(item)
        
        for resource_title, annotations in by_resource.items():
            print(f"\n{resource_title} ({len(annotations)} annotations)")
            for ann in annotations:
                print(f"  - {ann['highlighted_text'][:50]}...")
        
        return by_resource
    
    def export_research_notes(self, output_file: str):
        """Export all research notes to a file."""
        markdown = self.client.export_markdown()
        
        with open(output_file, "w") as f:
            f.write(markdown)
        
        print(f"Exported annotations to {output_file}")

# Usage
assistant = ResearchAssistant(client)

# Find related notes
assistant.find_related_notes("attention mechanisms in transformers")

# Summarize a topic
assistant.summarize_topic("methodology")

# Export all notes
assistant.export_research_notes("research_notes.md")
```

## Integration with Collections

### Organize Annotations by Project

```bash
# 1. Create a collection for your research project
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Transformer Research",
    "description": "Papers and notes on transformer architectures",
    "visibility": "private"
  }'

# 2. Add resources to the collection
curl -X POST http://127.0.0.1:8000/collections/{collection_id}/resources \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": [
      "660e8400-e29b-41d4-a716-446655440001",
      "770e8400-e29b-41d4-a716-446655440002"
    ]
  }'

# 3. Create annotations with collection association
curl -X POST http://127.0.0.1:8000/resources/{resource_id}/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "start_offset": 150,
    "end_offset": 200,
    "highlighted_text": "Self-attention mechanism",
    "note": "Core innovation of transformers",
    "tags": ["attention", "transformer"],
    "collection_ids": ["{collection_id}"]
  }'

# 4. Get collection details with annotations
curl "http://127.0.0.1:8000/collections/{collection_id}"
```

### Cross-Reference Annotations

```python
def find_cross_references(client, annotation_id: str):
    """Find related annotations across resources."""
    # Get the annotation
    annotation = requests.get(
        f"{client.base_url}/annotations/{annotation_id}"
    ).json()
    
    # Search for similar annotations
    if annotation.get("note"):
        similar = client.search_semantic(annotation["note"], limit=10)
        
        print(f"Annotations related to: {annotation['highlighted_text']}\n")
        for item in similar["items"]:
            if item["id"] != annotation_id:
                print(f"- {item['resource_title']}")
                print(f"  {item['highlighted_text']}")
                print(f"  Similarity: {item['similarity']:.2f}\n")
```

## Best Practices

### Effective Annotation Strategies

1. **Use Consistent Tags**: Develop a tagging system for your research area
2. **Write Detailed Notes**: Include context and connections to other work
3. **Color-Code by Type**: Use colors to distinguish different types of annotations
4. **Regular Export**: Backup your annotations regularly
5. **Semantic Search**: Use semantic search to discover connections

### Performance Tips

1. **Batch Operations**: Create multiple annotations in sequence for better performance
2. **Limit Search Results**: Use appropriate limits for search queries
3. **Export Periodically**: Export large annotation sets in smaller batches
4. **Use Tags**: Tag-based search is faster than full-text for large datasets

### Integration Patterns

1. **With Collections**: Associate annotations with research projects
2. **With Search**: Use annotations to enhance resource discovery
3. **With Recommendations**: Leverage annotation patterns for better recommendations
4. **With External Tools**: Export to Markdown for use in Obsidian, Notion, etc.
