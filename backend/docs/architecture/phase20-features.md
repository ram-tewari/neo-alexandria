# Phase 20 Features Architecture

Frontend-Backend Infrastructure Support features for Neo Alexandria 2.0.

> **Phase**: 20 - Frontend-Backend Infrastructure Support  
> **Status**: Complete  
> **Last Updated**: January 2026

## Table of Contents

1. [Overview](#overview)
2. [Code Intelligence Architecture](#code-intelligence-architecture)
3. [Document Intelligence Architecture](#document-intelligence-architecture)
4. [Graph Intelligence Architecture](#graph-intelligence-architecture)
5. [AI Planning Architecture](#ai-planning-architecture)
6. [MCP Server Architecture](#mcp-server-architecture)
7. [Performance Characteristics](#performance-characteristics)
8. [Integration Points](#integration-points)

---

## Overview

Phase 20 delivers 7 new capabilities and 3 extensions to existing services:

**New Capabilities:**
1. Hover information API for code intelligence
2. PDF metadata extraction with page boundaries
3. Auto-linking service for PDF-to-code connections
4. Centrality metrics computation (degree, betweenness, PageRank)
5. Community detection using Louvain algorithm
6. Graph visualization layouts (force-directed, hierarchical, circular)
7. MCP server infrastructure for tool registration and invocation

**Extended Services:**
1. PDF extractor - Enhanced with metadata extraction
2. Graph service - Extended with centrality and community detection
3. Repository parser - Extended with best practices detection

**Key Principles:**
- Leverage existing infrastructure (embeddings, static analysis, event bus)
- Extend existing services minimally
- Build only genuinely missing features
- Meet strict performance requirements

---

## Code Intelligence Architecture

### Hover Information System

```
┌─────────────────────────────────────────────────────────────────┐
│                   Hover Information Flow                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client Request                                                 │
│  ──────────────                                                 │
│  GET /api/code/hover?file_path=src/utils.py&line=42&column=4   │
│                                                                 │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────┐                                          │
│  │  Graph Router    │                                          │
│  └────────┬─────────┘                                          │
│           │                                                    │
│           ▼                                                    │
│  ┌──────────────────────────────────────────────────────┐      │
│  │           Check Redis Cache (5-min TTL)              │      │
│  │  Key: hover:{resource_id}:{file_path}:{line}:{col}   │      │
│  └────────┬─────────────────────────────────────────────┘      │
│           │                                                    │
│           ├─── Cache Hit ──► Return cached response           │
│           │                                                    │
│           └─── Cache Miss                                     │
│                    │                                          │
│                    ▼                                          │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  StaticAnalyzer (existing from Phase 18)             │      │
│  │  • Parse file with Tree-Sitter                       │      │
│  │  • Extract symbol at position                        │      │
│  │  • Get definition, docstring, type info              │      │
│  └────────┬─────────────────────────────────────────────┘      │
│           │                                                    │
│           ▼                                                    │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Query DocumentChunk (existing embeddings)           │      │
│  │  • Compute query embedding for symbol                │      │
│  │  • Cosine similarity with chunk.embedding            │      │
│  │  • Filter by threshold (0.7)                         │      │
│  │  • Return top 5 related chunks                       │      │
│  └────────┬─────────────────────────────────────────────┘      │
│           │                                                    │
│           ▼                                                    │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Cache result in Redis (5-min TTL)                   │      │
│  └────────┬─────────────────────────────────────────────┘      │
│           │                                                    │
│           ▼                                                    │
│  Return HoverInformationResponse                              │
│  {                                                            │
│    symbol_info: {...},                                        │
│    related_chunks: [...]                                      │
│  }                                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

