# Neo Alexandria 2.0 - Complete Documentation

**Generated:** December 28, 2025

---

# Table of Contents

1. [Agent Context Management](#agent-context-management)
2. [Product Overview](#product-overview)
3. [Technical Stack](#technical-stack)
4. [Repository Structure](#repository-structure)
5. [Backend Documentation](#backend-documentation)
   - [API Reference](#api-reference)
   - [Architecture](#architecture)
   - [Developer Guides](#developer-guides)
6. [Frontend Documentation](#frontend-documentation)
7. [Specifications](#specifications)
8. [Testing Documentation](#testing-documentation)

---


# 1. Agent Context Management

# Agent Context Management

## Purpose

This document provides routing rules for AI agents working with Neo Alexandria 2.0. It ensures efficient context usage and points to the right documentation.

## Token Hygiene Rules

1. **Never load entire files** unless explicitly needed for the current task
2. **Use targeted reads** with line ranges when possible
3. **Reference documentation** by path rather than loading it
4. **Close completed specs** - archive or mark as done when features are implemented
5. **Rotate context** - only keep active work in focus

## Quick Reference

| Need | Read |
|------|------|
| What is this project? | `.kiro/steering/product.md` |
| What tech do we use? | `.kiro/steering/tech.md` |
| Where is X located? | `.kiro/steering/structure.md` |
| How do I implement Y? | `.kiro/specs/[feature]/design.md` |
| What's the API? | `backend/docs/index.md` → `api/` |
| What's the architecture? | `backend/docs/architecture/overview.md` |
| How do I set up dev env? | `backend/docs/guides/setup.md` |
| How do I test? | `backend/docs/guides/testing.md` |

---

# 2. Product Overview

# Neo Alexandria 2.0 - Product Overview

## Purpose

Neo Alexandria 2.0 is an advanced knowledge management system that combines traditional information retrieval with modern AI-powered features to deliver intelligent content processing, advanced search, and personalized recommendations.

## Target Users

1. **Researchers** - Academic and industry researchers managing papers, articles, and datasets
2. **Knowledge Workers** - Professionals curating domain-specific knowledge bases
3. **Students** - Learners organizing study materials and research
4. **Teams** - Collaborative knowledge management for organizations

## Core Value Propositions

### Intelligent Content Processing
- Automatic summarization, tagging, and classification
- Quality assessment and metadata extraction
- Multi-format support (HTML, PDF, plain text)

### Advanced Discovery
- Hybrid search combining keyword and semantic approaches
- Knowledge graph for relationship exploration
- Citation network analysis
- Personalized recommendations

### Active Reading & Annotation
- Precise text highlighting with notes
- Semantic search across annotations
- Export to external tools (Markdown, JSON)

### Organization & Curation
- Flexible collection management
- Hierarchical taxonomy
- Quality-based filtering
- Batch operations

## Non-Goals

### What We Are NOT Building

❌ **Social Network** - No user profiles, followers, or social features
❌ **Content Creation Platform** - No authoring tools or publishing workflows
❌ **File Storage Service** - No general-purpose file hosting
❌ **Real-time Collaboration** - No simultaneous editing or live cursors
❌ **Mobile Apps** - Web-first, responsive design only
❌ **Enterprise SSO** - Simple authentication only
❌ **Multi-tenancy** - Single-user or small team focus
❌ **Blockchain/Web3** - Traditional database architecture
❌ **Video/Audio Processing** - Text and document focus only

## Product Principles

1. **API-First** - All features accessible via RESTful API
2. **Privacy-Focused** - User data stays local or self-hosted
3. **Open Source** - Transparent, extensible, community-driven
4. **Performance** - Fast response times (<200ms for most operations)
5. **Simplicity** - Clean interfaces, minimal configuration
6. **Extensibility** - Plugin architecture for custom features

## Success Metrics

- **Search Quality**: nDCG > 0.7 for hybrid search
- **Response Time**: P95 < 200ms for API endpoints
- **Classification Accuracy**: > 85% for ML taxonomy
- **User Satisfaction**: Qualitative feedback from early adopters
- **System Reliability**: 99.9% uptime for self-hosted deployments

---

