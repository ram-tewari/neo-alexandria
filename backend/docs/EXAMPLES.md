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

## Phase 8: Three-Way Hybrid Search with Sparse Vectors & Reranking

### Three-Way Hybrid Search Examples

#### cURL Examples

**Basic three-way hybrid search:**
```bash
# Three-way search with reranking and adaptive weighting (default)
curl "http://127.0.0.1:8000/search/three-way-hybrid?query=machine+learning&limit=20"

# Three-way search without reranking (faster)
curl "http://127.0.0.1:8000/search/three-way-hybrid?query=neural+networks&limit=10&enable_reranking=false"

# Three-way search with fixed weights (no adaptation)
curl "http://127.0.0.1:8000/search/three-way-hybrid?query=data+science&adaptive_weighting=false"

# Three-way search with pagination
curl "http://127.0.0.1:8000/search/three-way-hybrid?query=artificial+intelligence&limit=20&offset=20"
```

**Response:**
```json
{
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "description": "Comprehensive guide to ML concepts",
      "subject": ["Machine Learning", "Artificial Intelligence"],
      "quality_score": 0.85,
      "relevance_score": 0.92
    }
  ],
  "total": 42,
  "latency_ms": 145.3,
  "method_contributions": {
    "fts5": 45,
    "dense": 38,
    "sparse": 42
  },
  "weights_used": [0.35, 0.35, 0.30],
  "facets": {
    "classification_code": [{"key": "004", "count": 30}]
  }
}
```

#### Compare Search Methods

**Compare all search methods side-by-side:**
```bash
curl "http://127.0.0.1:8000/search/compare-methods?query=deep+learning&limit=10"
```

**Response:**
```json
{
  "query": "deep learning",
  "methods": {
    "fts5_only": {
      "results": [...],
      "latency_ms": 25.3,
      "count": 10
    },
    "dense_only": {
      "results": [...],
      "latency_ms": 42.1,
      "count": 10
    },
    "sparse_only": {
      "results": [...],
      "latency_ms": 38.7,
      "count": 10
    },
    "two_way_hybrid": {
      "results": [...],
      "latency_ms": 67.4,
      "count": 10
    },
    "three_way_hybrid": {
      "results": [...],
      "latency_ms": 106.1,
      "count": 10
    },
    "three_way_reranked": {
      "results": [...],
      "latency_ms": 856.8,
      "count": 10
    }
  }
}
```

#### Evaluate Search Quality

**Evaluate search quality with relevance judgments:**
```bash
curl -X POST http://127.0.0.1:8000/search/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "relevance_judgments": {
      "550e8400-e29b-41d4-a716-446655440000": 3,
      "660e8400-e29b-41d4-a716-446655440001": 2,
      "770e8400-e29b-41d4-a716-446655440002": 1,
      "880e8400-e29b-41d4-a716-446655440003": 0
    }
  }'
```

**Response:**
```json
{
  "query": "machine learning algorithms",
  "metrics": {
    "ndcg@20": 0.847,
    "recall@20": 0.923,
    "precision@20": 0.650,
    "mrr": 0.833
  },
  "baseline_comparison": {
    "two_way_ndcg": 0.651,
    "improvement": 0.301
  }
}
```

#### Batch Generate Sparse Embeddings

**Generate sparse embeddings for all resources:**
```bash
curl -X POST http://127.0.0.1:8000/admin/sparse-embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 32}'
```

**Generate for specific resources:**
```bash
curl -X POST http://127.0.0.1:8000/admin/sparse-embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": [
      "550e8400-e29b-41d4-a716-446655440000",
      "660e8400-e29b-41d4-a716-446655440001"
    ],
    "batch_size": 16
  }'
```

**Response:**
```json
{
  "status": "queued",
  "job_id": "job_uuid",
  "estimated_duration_minutes": 45,
  "resources_to_process": 10000
}
```

### Python Examples

#### Three-Way Hybrid Search Client

```python
import requests
from typing import Dict, List, Optional

class ThreeWaySearchClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
    
    def search_three_way(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        enable_reranking: bool = True,
        adaptive_weighting: bool = True
    ) -> Dict:
        """Execute three-way hybrid search."""
        response = requests.get(
            f"{self.base_url}/search/three-way-hybrid",
            params={
                "query": query,
                "limit": limit,
                "offset": offset,
                "enable_reranking": enable_reranking,
                "adaptive_weighting": adaptive_weighting
            }
        )
        response.raise_for_status()
        return response.json()
    
    def compare_methods(self, query: str, limit: int = 20) -> Dict:
        """Compare all search methods side-by-side."""
        response = requests.get(
            f"{self.base_url}/search/compare-methods",
            params={"query": query, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def evaluate_search(
        self,
        query: str,
        relevance_judgments: Dict[str, int]
    ) -> Dict:
        """Evaluate search quality with relevance judgments."""
        response = requests.post(
            f"{self.base_url}/search/evaluate",
            json={
                "query": query,
                "relevance_judgments": relevance_judgments
            }
        )
        response.raise_for_status()
        return response.json()
    
    def generate_sparse_embeddings(
        self,
        resource_ids: Optional[List[str]] = None,
        batch_size: int = 32
    ) -> Dict:
        """Batch generate sparse embeddings."""
        payload = {"batch_size": batch_size}
        if resource_ids:
            payload["resource_ids"] = resource_ids
        
        response = requests.post(
            f"{self.base_url}/admin/sparse-embeddings/generate",
            json=payload
        )
        response.raise_for_status()
        return response.json()

# Usage examples
client = ThreeWaySearchClient()

# Basic three-way search
results = client.search_three_way("machine learning", limit=20)
print(f"Found {results['total']} results in {results['latency_ms']:.1f}ms")
print(f"Method contributions: FTS5={results['method_contributions']['fts5']}, "
      f"Dense={results['method_contributions']['dense']}, "
      f"Sparse={results['method_contributions']['sparse']}")
print(f"Weights used: {results['weights_used']}")

# Fast search without reranking
fast_results = client.search_three_way(
    "neural networks",
    limit=10,
    enable_reranking=False
)
print(f"Fast search completed in {fast_results['latency_ms']:.1f}ms")

# Compare all methods
comparison = client.compare_methods("deep learning", limit=10)
print("\nMethod comparison:")
for method, data in comparison["methods"].items():
    print(f"  {method}: {data['count']} results in {data['latency_ms']:.1f}ms")

# Evaluate search quality
relevance = {
    "550e8400-e29b-41d4-a716-446655440000": 3,  # Highly relevant
    "660e8400-e29b-41d4-a716-446655440001": 2,  # Relevant
    "770e8400-e29b-41d4-a716-446655440002": 1,  # Marginally relevant
}
metrics = client.evaluate_search("artificial intelligence", relevance)
print(f"\nSearch quality metrics:")
print(f"  nDCG@20: {metrics['metrics']['ndcg@20']:.3f}")
print(f"  Recall@20: {metrics['metrics']['recall@20']:.3f}")
print(f"  Precision@20: {metrics['metrics']['precision@20']:.3f}")
print(f"  MRR: {metrics['metrics']['mrr']:.3f}")
if "baseline_comparison" in metrics:
    print(f"  Improvement over baseline: {metrics['baseline_comparison']['improvement']:.1%}")

# Generate sparse embeddings
job = client.generate_sparse_embeddings(batch_size=32)
print(f"\nSparse embedding generation queued:")
print(f"  Job ID: {job['job_id']}")
print(f"  Resources to process: {job['resources_to_process']}")
print(f"  Estimated duration: {job['estimated_duration_minutes']} minutes")
```

#### Advanced Search Analysis

```python
import requests
from typing import Dict, List
import statistics

class SearchAnalyzer:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
    
    def analyze_query_types(self, queries: List[str]) -> Dict:
        """Analyze how different query types perform."""
        results = {}
        
        for query in queries:
            response = requests.get(
                f"{self.base_url}/search/three-way-hybrid",
                params={"query": query, "limit": 20}
            )
            data = response.json()
            
            results[query] = {
                "latency_ms": data["latency_ms"],
                "total_results": data["total"],
                "method_contributions": data["method_contributions"],
                "weights_used": data["weights_used"]
            }
        
        return results
    
    def benchmark_search_methods(self, query: str, iterations: int = 5) -> Dict:
        """Benchmark different search methods."""
        latencies = {
            "fts5_only": [],
            "dense_only": [],
            "sparse_only": [],
            "two_way_hybrid": [],
            "three_way_hybrid": [],
            "three_way_reranked": []
        }
        
        for _ in range(iterations):
            response = requests.get(
                f"{self.base_url}/search/compare-methods",
                params={"query": query, "limit": 20}
            )
            data = response.json()
            
            for method, method_data in data["methods"].items():
                latencies[method].append(method_data["latency_ms"])
        
        # Compute statistics
        stats = {}
        for method, times in latencies.items():
            stats[method] = {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "min": min(times),
                "max": max(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0
            }
        
        return stats

# Usage
analyzer = SearchAnalyzer()

# Analyze different query types
queries = [
    "ML",  # Short query
    "machine learning algorithms for classification",  # Long query
    "def train_model(X, y):",  # Technical query
    "what is deep learning?"  # Question query
]

analysis = analyzer.analyze_query_types(queries)
print("Query type analysis:")
for query, data in analysis.items():
    print(f"\nQuery: '{query}'")
    print(f"  Latency: {data['latency_ms']:.1f}ms")
    print(f"  Results: {data['total_results']}")
    print(f"  Contributions: FTS5={data['method_contributions']['fts5']}, "
          f"Dense={data['method_contributions']['dense']}, "
          f"Sparse={data['method_contributions']['sparse']}")
    print(f"  Weights: {data['weights_used']}")

# Benchmark search methods
stats = analyzer.benchmark_search_methods("machine learning", iterations=10)
print("\n\nSearch method benchmarks (10 iterations):")
for method, method_stats in stats.items():
    print(f"\n{method}:")
    print(f"  Mean: {method_stats['mean']:.1f}ms")
    print(f"  Median: {method_stats['median']:.1f}ms")
    print(f"  Min: {method_stats['min']:.1f}ms")
    print(f"  Max: {method_stats['max']:.1f}ms")
    print(f"  StdDev: {method_stats['stdev']:.1f}ms")
```

### JavaScript Examples

#### Three-Way Search Client

```javascript
class ThreeWaySearchClient {
    constructor(baseUrl = 'http://127.0.0.1:8000') {
        this.baseUrl = baseUrl;
    }
    
    async searchThreeWay(query, options = {}) {
        const {
            limit = 20,
            offset = 0,
            enableReranking = true,
            adaptiveWeighting = true
        } = options;
        
        const params = new URLSearchParams({
            query,
            limit: limit.toString(),
            offset: offset.toString(),
            enable_reranking: enableReranking.toString(),
            adaptive_weighting: adaptiveWeighting.toString()
        });
        
        const response = await fetch(
            `${this.baseUrl}/search/three-way-hybrid?${params}`
        );
        
        if (!response.ok) {
            throw new Error(`Search failed: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async compareMethods(query, limit = 20) {
        const params = new URLSearchParams({
            query,
            limit: limit.toString()
        });
        
        const response = await fetch(
            `${this.baseUrl}/search/compare-methods?${params}`
        );
        
        if (!response.ok) {
            throw new Error(`Comparison failed: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async evaluateSearch(query, relevanceJudgments) {
        const response = await fetch(
            `${this.baseUrl}/search/evaluate`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query,
                    relevance_judgments: relevanceJudgments
                })
            }
        );
        
        if (!response.ok) {
            throw new Error(`Evaluation failed: ${response.statusText}`);
        }
        
        return response.json();
    }
}

// Usage
const client = new ThreeWaySearchClient();

// Basic three-way search
client.searchThreeWay('machine learning', { limit: 20 })
    .then(results => {
        console.log(`Found ${results.total} results in ${results.latency_ms}ms`);
        console.log('Method contributions:', results.method_contributions);
        console.log('Weights used:', results.weights_used);
        
        results.results.forEach(result => {
            console.log(`- ${result.title} (score: ${result.relevance_score})`);
        });
    })
    .catch(error => console.error('Search failed:', error));

// Compare methods
client.compareMethods('deep learning', 10)
    .then(comparison => {
        console.log('\nMethod comparison:');
        Object.entries(comparison.methods).forEach(([method, data]) => {
            console.log(`  ${method}: ${data.count} results in ${data.latency_ms}ms`);
        });
    })
    .catch(error => console.error('Comparison failed:', error));

// Evaluate search quality
const relevance = {
    '550e8400-e29b-41d4-a716-446655440000': 3,
    '660e8400-e29b-41d4-a716-446655440001': 2,
    '770e8400-e29b-41d4-a716-446655440002': 1
};

client.evaluateSearch('artificial intelligence', relevance)
    .then(metrics => {
        console.log('\nSearch quality metrics:');
        console.log(`  nDCG@20: ${metrics.metrics['ndcg@20'].toFixed(3)}`);
        console.log(`  Recall@20: ${metrics.metrics['recall@20'].toFixed(3)}`);
        console.log(`  Precision@20: ${metrics.metrics['precision@20'].toFixed(3)}`);
        console.log(`  MRR: ${metrics.metrics.mrr.toFixed(3)}`);
    })
    .catch(error => console.error('Evaluation failed:', error));
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
