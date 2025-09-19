# Neo Alexandria 2.0 Examples and Tutorials

This document provides comprehensive examples and tutorials for using the Neo Alexandria 2.0 API. It includes practical code samples in multiple programming languages, common use cases, and step-by-step tutorials for key features.

## Table of Contents

- [Quick Start Tutorial](#quick-start-tutorial)
- [Content Ingestion Examples](#content-ingestion-examples)
- [Search and Discovery Examples](#search-and-discovery-examples)
- [Knowledge Graph Examples](#knowledge-graph-examples)
- [Recommendation System Examples](#recommendation-system-examples)
- [Python SDK Examples](#python-sdk-examples)
- [JavaScript Examples](#javascript-examples)
- [cURL Examples](#curl-examples)
- [Advanced Use Cases](#advanced-use-cases)
- [Error Handling Examples](#error-handling-examples)

## Quick Start Tutorial

### Step 1: Start the API Server

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run database migrations
cd backend && alembic upgrade head

# Start the server
uvicorn backend.app.main:app --reload
```

### Step 2: Ingest Your First Resource

```bash
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

### Step 3: Monitor Processing Status

```bash
# Get the resource ID from the previous response
RESOURCE_ID="your-resource-id-here"

# Check processing status

curl "http://127.0.0.1:8000/resources/$RESOURCE_ID/status"
```

### Step 4: Retrieve Processed Content

```bash
# Get the full resource after processing
curl "http://127.0.0.1:8000/resources/$RESOURCE_ID"
```

### Step 5: Search Your Content

```bash
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{"text": "your search query", "limit": 10}'
```

## Content Ingestion Examples

### Basic URL Ingestion

```bash
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

**Response (202 Accepted):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending"
}
```

**Note**: The full resource data is available after background processing completes. Use the status endpoint to monitor progress.

### Monitoring Ingestion Status

```bash
# Check ingestion status
curl http://127.0.0.1:8000/resources/123e4567-e89b-12d3-a456-426614174000/status
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "ingestion_status": "completed",
  "ingestion_error": null,
  "ingestion_started_at": "2024-01-15T12:00:00Z",
  "ingestion_completed_at": "2024-01-15T12:00:05Z"
}
```

### Retrieving Processed Resource

```bash
# Get full resource after processing completes
curl http://127.0.0.1:8000/resources/123e4567-e89b-12d3-a456-426614174000
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Example Article",
  "description": "AI-generated summary of the article content...",
  "subject": ["Machine Learning", "Artificial Intelligence", "Technology"],
  "classification_code": "004",
  "quality_score": 0.85,
  "read_status": "unread",
  "ingestion_status": "completed",
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:05Z"
}
```

## Recommendation System Examples

### Get Personalized Recommendations

**Python:**
```python
import requests

def get_recommendations(limit=10):
    """Get personalized content recommendations."""
    response = requests.get(
        "http://127.0.0.1:8000/recommendations",
        params={"limit": limit}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get recommendations: {response.json()}")

# Usage
recommendations = get_recommendations(limit=5)
print(f"Found {len(recommendations['items'])} recommendations")

for rec in recommendations['items']:
    print(f"- {rec['title']}")
    print(f"  URL: {rec['url']}")
    print(f"  Relevance: {rec['relevance_score']}")
    print(f"  Reasoning: {', '.join(rec['reasoning'])}")
    print()
```

**JavaScript:**
```javascript
async function getRecommendations(limit = 10) {
    const response = await fetch(
        `http://127.0.0.1:8000/recommendations?limit=${limit}`
    );
    
    if (response.status === 200) {
        return await response.json();
    } else {
        throw new Error(`Failed to get recommendations: ${await response.text()}`);
    }
}

// Usage
getRecommendations(5)
    .then(recommendations => {
        console.log(`Found ${recommendations.items.length} recommendations`);
        recommendations.items.forEach(rec => {
            console.log(`- ${rec.title}`);
            console.log(`  URL: ${rec.url}`);
            console.log(`  Relevance: ${rec.relevance_score}`);
            console.log(`  Reasoning: ${rec.reasoning.join(', ')}`);
        });
    })
    .catch(console.error);
```

**cURL:**
```bash
# Get recommendations
curl "http://127.0.0.1:8000/recommendations?limit=5"
```

## Python Examples

### Complete Python Client

```python
import requests
import json
import time

def ingest_url_async(url, **kwargs):
    """Ingest a URL asynchronously and wait for completion."""
    # Submit ingestion request
    response = requests.post(
        "http://127.0.0.1:8000/resources",
        json={"url": url, **kwargs}
    )
    
    if response.status_code != 202:
        raise Exception(f"Error: {response.json()['detail']}")
    
    resource_id = response.json()["id"]
    print(f"Submitted for processing: {resource_id}")
    
    # Poll for completion
    while True:
        status_response = requests.get(
            f"http://127.0.0.1:8000/resources/{resource_id}/status"
        )
        status_data = status_response.json()
        
        if status_data["ingestion_status"] == "completed":
            # Get full resource
            resource_response = requests.get(
                f"http://127.0.0.1:8000/resources/{resource_id}"
            )
            return resource_response.json()
        elif status_data["ingestion_status"] == "failed":
            raise Exception(f"Ingestion failed: {status_data['ingestion_error']}")
        
        time.sleep(1)  # Wait 1 second before checking again

# Basic usage
resource = ingest_url_async("https://example.com/article")
print(f"Created: {resource['title']}")
print(f"AI Summary: {resource['description']}")
print(f"AI Tags: {', '.join(resource['subject'])}")
print(f"Quality: {resource['quality_score']}")
```

### Python Client with Error Handling

```python
import requests
import json
from typing import Optional, Dict, Any

class NeoAlexandriaClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
    
    def ingest_url(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Ingest a URL with comprehensive error handling."""
        try:
            response = requests.post(
                f"{self.base_url}/resources",
                json={"url": url, **kwargs},
                timeout=30
            )
            
            if response.status_code == 201:
                return response.json()
            elif response.status_code == 400:
                error_detail = response.json().get('detail', 'Bad request')
                print(f"Bad Request: {error_detail}")
            elif response.status_code == 422:
                validation_errors = response.json().get('detail', [])
                print(f"Validation Error: {validation_errors}")
            elif response.status_code == 500:
                error_detail = response.json().get('detail', 'Internal server error')
                print(f"Server Error: {error_detail}")
            else:
                print(f"Unexpected status code: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("Request timed out")
        except requests.exceptions.ConnectionError:
            print("Connection error - is the server running?")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except json.JSONDecodeError:
            print("Invalid JSON response")
        
        return None

# Usage
client = NeoAlexandriaClient()

# Basic ingestion
resource = client.ingest_url("https://example.com/article")
if resource:
    print(f"Success: {resource['title']}")

# With overrides
resource = client.ingest_url(
    "https://example.com/ml-guide",
    title="Machine Learning Guide",
    language="en",
    type="tutorial"
)
if resource:
    print(f"Success: {resource['title']} (Quality: {resource['quality_score']})")
```

### Batch Processing in Python

```python
import requests
import time
from typing import List, Dict, Any

def batch_ingest_urls(urls: List[str], delay: float = 1.0) -> List[Dict[str, Any]]:
    """Ingest multiple URLs with rate limiting."""
    results = []
    
    for i, url in enumerate(urls):
        print(f"Processing {i+1}/{len(urls)}: {url}")
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/resources",
                json={"url": url},
                timeout=30
            )
            
            if response.status_code == 201:
                resource = response.json()
                results.append({
                    "url": url,
                    "success": True,
                    "resource": resource
                })
                print(f"  ✓ Created: {resource['title']}")
            else:
                error = response.json().get('detail', 'Unknown error')
                results.append({
                    "url": url,
                    "success": False,
                    "error": error
                })
                print(f"  ✗ Failed: {error}")
                
        except Exception as e:
            results.append({
                "url": url,
                "success": False,
                "error": str(e)
            })
            print(f"  ✗ Exception: {e}")
        
        # Rate limiting
        if i < len(urls) - 1:
            time.sleep(delay)
    
    return results

# Usage
urls = [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3"
]

results = batch_ingest_urls(urls, delay=2.0)

# Summary
successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]

print(f"\nSummary:")
print(f"Successful: {len(successful)}")
print(f"Failed: {len(failed)}")

if failed:
    print("\nFailed URLs:")
    for result in failed:
        print(f"  {result['url']}: {result['error']}")
```

## JavaScript/Node.js Examples

### Basic Node.js Client

```javascript
const fetch = require('node-fetch');

async function ingestUrl(url, options = {}) {
    try {
        const response = await fetch('http://127.0.0.1:8000/resources', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, ...options })
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(`HTTP ${response.status}: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error ingesting URL:', error.message);
        throw error;
    }
}

// Usage
async function main() {
    try {
        const resource = await ingestUrl('https://example.com/article');
        console.log('Created:', resource.title);
        console.log('Quality:', resource.quality_score);
        console.log('Subjects:', resource.subject.join(', '));
    } catch (error) {
        console.error('Failed:', error.message);
    }
}

main();
```

### Advanced Node.js Client with Retry Logic

```javascript
const fetch = require('node-fetch');

class NeoAlexandriaClient {
    constructor(baseUrl = 'http://127.0.0.1:8000') {
        this.baseUrl = baseUrl;
    }

    async ingestUrl(url, options = {}, maxRetries = 3) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                const response = await fetch(`${this.baseUrl}/resources`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url, ...options }),
                    timeout: 30000
                });

                if (response.ok) {
                    return await response.json();
                } else {
                    const error = await response.json();
                    if (response.status >= 500 && attempt < maxRetries) {
                        console.log(`Attempt ${attempt} failed, retrying...`);
                        await this.delay(1000 * attempt); // Exponential backoff
                        continue;
                    }
                    throw new Error(`HTTP ${response.status}: ${error.detail}`);
                }
            } catch (error) {
                if (attempt === maxRetries) {
                    throw error;
                }
                console.log(`Attempt ${attempt} failed: ${error.message}`);
                await this.delay(1000 * attempt);
            }
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Usage
const client = new NeoAlexandriaClient();

async function main() {
    try {
        const resource = await client.ingestUrl('https://example.com/article');
        console.log('Success:', resource.title);
    } catch (error) {
        console.error('Failed after retries:', error.message);
    }
}

main();
```

## cURL Examples

### Basic cURL Commands

```bash
# Basic ingestion
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'

# With title override
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "title": "Custom Title"
  }'

# With multiple overrides
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/ml-guide",
    "title": "Machine Learning Guide",
    "description": "A comprehensive guide to ML",
    "language": "en",
    "type": "tutorial"
  }'
```

### cURL with Error Handling

```bash
#!/bin/bash

# Function to ingest URL with error handling
ingest_url() {
    local url="$1"
    local title="$2"
    
    echo "Ingesting: $url"
    
    response=$(curl -s -w "\n%{http_code}" -X POST http://127.0.0.1:8000/resources \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"$url\", \"title\": \"$title\"}")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    case $http_code in
        201)
            echo "✓ Success: $(echo "$body" | jq -r '.title')"
            echo "  Quality: $(echo "$body" | jq -r '.quality_score')"
            echo "  Subjects: $(echo "$body" | jq -r '.subject | join(", ")')"
            ;;
        400)
            echo "✗ Bad Request: $(echo "$body" | jq -r '.detail')"
            ;;
        422)
            echo "✗ Validation Error: $(echo "$body" | jq -r '.detail')"
            ;;
        500)
            echo "✗ Server Error: $(echo "$body" | jq -r '.detail')"
            ;;
        *)
            echo "✗ Unexpected status: $http_code"
            ;;
    esac
}

# Usage
ingest_url "https://example.com/article" "Example Article"
ingest_url "https://example.com/ml-guide" "ML Guide"
```

## Advanced Usage

### Content Type Detection

```python
import requests
import mimetypes
from urllib.parse import urlparse

def get_content_type(url):
    """Get content type from URL extension."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    if path.endswith('.pdf'):
        return 'application/pdf'
    elif path.endswith('.html') or path.endswith('.htm'):
        return 'text/html'
    elif path.endswith('.txt'):
        return 'text/plain'
    else:
        return 'text/html'  # Default assumption

def ingest_with_type_detection(url):
    """Ingest URL with automatic type detection."""
    content_type = get_content_type(url)
    
    return requests.post(
        "http://127.0.0.1:8000/resources",
        json={
            "url": url,
            "type": content_type
        }
    ).json()

# Usage
resource = ingest_with_type_detection("https://example.com/document.pdf")
print(f"Type: {resource['type']}")
```

### Language Detection

```python
import requests
import langdetect
from langdetect import detect

def ingest_with_language_detection(url):
    """Ingest URL with automatic language detection."""
    try:
        # First, get the content to detect language
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Simple language detection (you might want to use the extracted text)
            detected_lang = detect(response.text[:1000])  # First 1000 chars
        else:
            detected_lang = 'en'  # Default
    except:
        detected_lang = 'en'  # Default
    
    return requests.post(
        "http://127.0.0.1:8000/resources",
        json={
            "url": url,
            "language": detected_lang
        }
    ).json()

# Usage
resource = ingest_with_language_detection("https://example.com/spanish-article")
print(f"Language: {resource['language']}")
```

## Error Handling

### Common Error Scenarios

```python
import requests

def handle_ingestion_errors(url):
    """Demonstrate various error handling scenarios."""
    try:
        response = requests.post(
            "http://127.0.0.1:8000/resources",
            json={"url": url}
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            error_data = response.json()
            error_detail = error_data.get('detail', 'Unknown error')
            
            if response.status_code == 400:
                if "HTTP 404" in error_detail:
                    print("URL not found (404)")
                elif "timeout" in error_detail:
                    print("Request timeout")
                elif "HTTP 403" in error_detail:
                    print("Access forbidden (403)")
                else:
                    print(f"Bad request: {error_detail}")
                    
            elif response.status_code == 422:
                print("Validation error - check your request format")
                print(f"Details: {error_detail}")
                
            elif response.status_code == 500:
                print("Server error - try again later")
                print(f"Details: {error_detail}")
                
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server - is it running?")
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except ValueError as e:
        print(f"JSON decode error: {e}")

# Test various error scenarios
test_urls = [
    "https://httpstat.us/404",  # 404 error
    "https://httpstat.us/403",  # 403 error
    "https://httpstat.us/500",  # 500 error
    "not-a-url",               # Invalid URL
    "https://example.com/valid" # Valid URL
]

for url in test_urls:
    print(f"\nTesting: {url}")
    handle_ingestion_errors(url)
```

## Batch Processing

### Parallel Processing

```python
import requests
import asyncio
import aiohttp
from typing import List, Dict, Any

async def ingest_url_async(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    """Async URL ingestion."""
    try:
        async with session.post(
            "http://127.0.0.1:8000/resources",
            json={"url": url}
        ) as response:
            if response.status == 201:
                data = await response.json()
                return {"url": url, "success": True, "resource": data}
            else:
                error = await response.json()
                return {"url": url, "success": False, "error": error.get('detail')}
    except Exception as e:
        return {"url": url, "success": False, "error": str(e)}

async def batch_ingest_async(urls: List[str], max_concurrent: int = 5) -> List[Dict[str, Any]]:
    """Batch ingest URLs with concurrency control."""
    connector = aiohttp.TCPConnector(limit=max_concurrent)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [ingest_url_async(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "url": urls[i],
                    "success": False,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results

# Usage
async def main():
    urls = [
        "https://example.com/article1",
        "https://example.com/article2",
        "https://example.com/article3",
        "https://example.com/article4",
        "https://example.com/article5"
    ]
    
    results = await batch_ingest_async(urls, max_concurrent=3)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    for result in successful:
        print(f"✓ {result['url']}: {result['resource']['title']}")

# Run the async function
asyncio.run(main())
```

### Progress Tracking

```python
import requests
from tqdm import tqdm
import time

def batch_ingest_with_progress(urls: List[str], delay: float = 1.0):
    """Batch ingest with progress bar."""
    results = []
    
    with tqdm(total=len(urls), desc="Ingesting URLs") as pbar:
        for url in urls:
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/resources",
                    json={"url": url},
                    timeout=30
                )
                
                if response.status_code == 201:
                    resource = response.json()
                    results.append({
                        "url": url,
                        "success": True,
                        "resource": resource
                    })
                    pbar.set_postfix(status="✓ Success")
                else:
                    error = response.json().get('detail', 'Unknown error')
                    results.append({
                        "url": url,
                        "success": False,
                        "error": error
                    })
                    pbar.set_postfix(status="✗ Failed")
                    
            except Exception as e:
                results.append({
                    "url": url,
                    "success": False,
                    "error": str(e)
                })
                pbar.set_postfix(status="✗ Error")
            
            pbar.update(1)
            time.sleep(delay)
    
    return results

# Usage
urls = [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3"
]

results = batch_ingest_with_progress(urls, delay=2.0)
```

## CRUD and Curation

- `GET /resources`, `GET /resources/{id}`, `PUT /resources/{id}`, `DELETE /resources/{id}`
- `GET /curation/review-queue`, `POST /curation/batch-update`

## Search and Facets

- `POST /search` supports text, filters, pagination, sorting, and returns facets.

## Phase 4: Vector & Hybrid Search

### Hybrid Search Examples

**Pure Keyword Search (hybrid_weight=0.0):**
```bash
curl -X POST http://127.0.0.1:8000/search \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "machine learning algorithms",
    "hybrid_weight": 0.0,
    "limit": 10
  }'
```

**Pure Semantic Search (hybrid_weight=1.0):**
```bash
curl -X POST http://127.0.0.1:8000/search \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "artificial intelligence techniques",
    "hybrid_weight": 1.0,
    "limit": 10
  }'
```

**Balanced Hybrid Search (hybrid_weight=0.5):**
```bash
curl -X POST http://127.0.0.1:8000/search \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "data science methods",
    "hybrid_weight": 0.5,
    "limit": 10
  }'
```

**Semantic Discovery (hybrid_weight=0.8):**
```bash
# Find content about "cars" by searching for "vehicles"
curl -X POST http://127.0.0.1:8000/search \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "automotive vehicles",
    "hybrid_weight": 0.8,
    "limit": 10
  }'
```

### Python Examples for Phase 4

**Hybrid Search Client:**
```python
import requests
import time

class HybridSearchClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
    
    def search(self, text, hybrid_weight=0.5, limit=25, **filters):
        """Perform hybrid search with configurable weight."""
        payload = {
            "text": text,
            "hybrid_weight": hybrid_weight,
            "limit": limit,
            "filters": filters
        }
        
        response = requests.post(f"{self.base_url}/search", json=payload)
        response.raise_for_status()
        return response.json()
    
    def semantic_discovery(self, concept, limit=25):
        """Find content by semantic similarity."""
        return self.search(concept, hybrid_weight=0.8, limit=limit)
    
    def exact_match_search(self, terms, limit=25):
        """Find exact keyword matches."""
        return self.search(terms, hybrid_weight=0.0, limit=limit)

# Usage examples
client = HybridSearchClient()

# Semantic discovery - find ML content through various terms
results = client.semantic_discovery("machine learning")
print(f"Found {results['total']} ML-related resources")

# Exact keyword search
results = client.exact_match_search("Python programming")
print(f"Found {results['total']} exact matches for 'Python programming'")

# Balanced hybrid search
results = client.search("data analysis", hybrid_weight=0.5)
print(f"Found {results['total']} data analysis resources")
```

### JavaScript Examples for Phase 4

**Hybrid Search Client:**
```javascript
class HybridSearchClient {
    constructor(baseUrl = 'http://127.0.0.1:8000') {
        this.baseUrl = baseUrl;
    }
    
    async search(text, hybridWeight = 0.5, limit = 25, filters = {}) {
        const payload = {
            text,
            hybrid_weight: hybridWeight,
            limit,
            filters
        };
        
        const response = await fetch(`${this.baseUrl}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`Search failed: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async semanticDiscovery(concept, limit = 25) {
        return this.search(concept, 0.8, limit);
    }
    
    async exactMatchSearch(terms, limit = 25) {
        return this.search(terms, 0.0, limit);
    }
}

// Usage examples
const client = new HybridSearchClient();

// Semantic discovery
client.semanticDiscovery('artificial intelligence')
    .then(results => console.log(`Found ${results.total} AI-related resources`))
    .catch(error => console.error('Search failed:', error));

// Hybrid search with different weights
const searchPromises = [
    client.search('data science', 0.0), // Pure keyword
    client.search('data science', 0.5), // Balanced
    client.search('data science', 1.0)  // Pure semantic
];

Promise.all(searchPromises)
    .then(results => {
        console.log('Keyword results:', results[0].total);
        console.log('Hybrid results:', results[1].total);
        console.log('Semantic results:', results[2].total);
    });
```

### Advanced Hybrid Search Examples

**Search with Filters and Hybrid Weight:**
```bash
curl -X POST http://127.0.0.1:8000/search \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "machine learning",
    "hybrid_weight": 0.7,
    "filters": {
      "classification_code": ["006"],
      "language": ["en"],
      "min_quality": 0.6
    },
    "limit": 20,
    "sort_by": "relevance",
    "sort_dir": "desc"
  }'
```

**Semantic Search Across Multiple Concepts:**
```python
# Find resources related to "automation" by searching for related terms
related_terms = ["automation", "robotics", "artificial intelligence", "machine learning"]

for term in related_terms:
    results = client.search(term, hybrid_weight=0.8, limit=5)
    print(f"'{term}' found {results['total']} related resources")
    for item in results['items']:
        print(f"  - {item['title']} (quality: {item['quality_score']:.2f})")
```

## Phase 5: Hybrid Knowledge Graph

### Mind-Map Neighbor Discovery

#### cURL Examples

**Get neighbors for a specific resource:**
```bash
# Get default 7 neighbors for a resource
curl "http://127.0.0.1:8000/graph/resource/550e8400-e29b-41d4-a716-446655440000/neighbors"

# Get custom number of neighbors
curl "http://127.0.0.1:8000/graph/resource/550e8400-e29b-41d4-a716-446655440000/neighbors?limit=10"
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "type": "article",
      "classification_code": "004"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Deep Learning with Python",
      "type": "book",
      "classification_code": "004"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "title": "Neural Networks Explained",
      "type": "article",
      "classification_code": "004"
    }
  ],
  "edges": [
    {
      "source": "550e8400-e29b-41d4-a716-446655440000",
      "target": "550e8400-e29b-41d4-a716-446655440001",
      "weight": 0.76,
      "details": {
        "connection_type": "classification",
        "vector_similarity": 0.8,
        "shared_subjects": ["python", "programming"]
      }
    },
    {
      "source": "550e8400-e29b-41d4-a716-446655440000",
      "target": "550e8400-e29b-41d4-a716-446655440002",
      "weight": 0.68,
      "details": {
        "connection_type": "topical",
        "vector_similarity": 0.65,
        "shared_subjects": ["neural networks", "deep learning"]
      }
    }
  ]
}
```

#### Global Overview Analysis

**Get system-wide strongest connections:**
```bash
# Get default global overview (50 edges, 0.85 threshold)
curl "http://127.0.0.1:8000/graph/overview"

# Get custom overview with different parameters
curl "http://127.0.0.1:8000/graph/overview?limit=20&vector_threshold=0.9"
```

### Python Examples

#### Graph Analysis Client

```python
import requests
from typing import Dict, List, Optional

class GraphClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
    
    def get_neighbors(self, resource_id: str, limit: int = 7) -> Dict:
        """Get neighbors for a specific resource."""
        response = requests.get(
            f"{self.base_url}/graph/resource/{resource_id}/neighbors",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_global_overview(self, limit: int = 50, vector_threshold: float = 0.85) -> Dict:
        """Get global overview of strongest connections."""
        response = requests.get(
            f"{self.base_url}/graph/overview",
            params={"limit": limit, "vector_threshold": vector_threshold}
        )
        response.raise_for_status()
        return response.json()
    
    def analyze_connections(self, resource_id: str) -> Dict:
        """Analyze connection types for a resource."""
        graph = self.get_neighbors(resource_id)
        
        connection_types = {}
        for edge in graph["edges"]:
            conn_type = edge["details"]["connection_type"]
            if conn_type not in connection_types:
                connection_types[conn_type] = []
            connection_types[conn_type].append({
                "target": edge["target"],
                "weight": edge["weight"],
                "shared_subjects": edge["details"]["shared_subjects"]
            })
        
        return connection_types

# Usage
client = GraphClient()

# Get neighbors for a resource
resource_id = "550e8400-e29b-41d4-a716-446655440000"
neighbors = client.get_neighbors(resource_id, limit=10)

print(f"Found {len(neighbors['edges'])} connections:")
for edge in neighbors["edges"]:
    details = edge["details"]
    print(f"  - {details['connection_type']}: weight={edge['weight']:.2f}, "
          f"shared_subjects={details['shared_subjects']}")

# Analyze connection types
connections = client.analyze_connections(resource_id)
for conn_type, edges in connections.items():
    print(f"\n{conn_type.title()} connections: {len(edges)}")
    for edge in edges:
        print(f"  - Weight: {edge['weight']:.2f}, Subjects: {edge['shared_subjects']}")
```

## Error Handling

- Standard error format: `{ "detail": "..." }`

## Batch Processing

- See earlier batch examples and apply to CRUD/listing as needed.

---

## Tips and Best Practices

1. **Rate Limiting**: Add delays between requests to avoid overwhelming the server
2. **Error Handling**: Always handle network errors and HTTP status codes
3. **Timeout Configuration**: Set appropriate timeouts for your use case
4. **Retry Logic**: Implement exponential backoff for transient failures
5. **Batch Processing**: Use async/parallel processing for multiple URLs
6. **Progress Tracking**: Show progress for long-running batch operations
7. **Validation**: Validate URLs before sending requests
8. **Logging**: Log successful and failed operations for debugging

For more examples and advanced usage patterns, see the [API Documentation](API_DOCUMENTATION.md) and [Developer Guide](DEVELOPER_GUIDE.md).
