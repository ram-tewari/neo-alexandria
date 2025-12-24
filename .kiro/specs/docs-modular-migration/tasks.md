# Implementation Plan: Documentation Modular Migration

## Overview

This plan consolidates the documentation migration into 3 main tasks: API documentation, Architecture & Guides documentation, and finalization with deprecation notices.

## Tasks

- [x] 1. Migrate API Documentation
  - Extract all API endpoints from API_DOCUMENTATION.md into modular files
  - Populate `api/overview.md` with base URL, authentication, error handling, pagination
  - Populate `api/resources.md` with /resources/* endpoints
  - Populate `api/search.md` with /search/* endpoints
  - Populate `api/collections.md` with /collections/* endpoints
  - Populate `api/annotations.md` with /annotations/* endpoints
  - Populate `api/taxonomy.md` with /taxonomy/* endpoints
  - Populate `api/graph.md` with /graph/*, /citations/* endpoints
  - Populate `api/recommendations.md` with /recommendations/* endpoints
  - Populate `api/quality.md` with /quality/*, /curation/* endpoints
  - Populate `api/monitoring.md` with /monitoring/*, /health endpoints
  - Preserve all request/response examples, parameter tables, and curl commands
  - Add Related Documentation sections with cross-references
  - _Requirements: 1.1-1.10, 4.1, 4.2, 4.4, 5.1, 5.2_

- [x] 2. Migrate Architecture and Developer Guide Documentation
  - Extract architecture content from ARCHITECTURE_DIAGRAM.md into modular files
  - Create `architecture/overview.md` with high-level system diagrams
  - Create `architecture/database.md` with schema, models, migrations
  - Create `architecture/event-system.md` with event bus documentation
  - Create `architecture/modules.md` with vertical slice documentation
  - Create `architecture/decisions.md` with design decisions
  - Extract developer guide content from DEVELOPER_GUIDE.md into modular files
  - Create `guides/setup.md` with installation and environment setup
  - Create `guides/workflows.md` with common development tasks
  - Create `guides/testing.md` with testing strategies
  - Create `guides/deployment.md` with Docker and production deployment
  - Create `guides/troubleshooting.md` with common issues and FAQ
  - Preserve all diagrams (ASCII and Mermaid), code examples, and tables
  - Add Related Documentation sections with cross-references
  - _Requirements: 2.1-2.5, 3.1-3.5, 4.2, 4.3, 4.4, 5.1, 5.2_

- [x] 3. Finalize Migration and Update References
  - Update `backend/docs/index.md` with complete navigation to all new files
  - Verify all internal links resolve correctly
  - Add deprecation notice to `API_DOCUMENTATION.md` listing new locations
  - Add deprecation notice to `ARCHITECTURE_DIAGRAM.md` listing new locations
  - Add deprecation notice to `DEVELOPER_GUIDE.md` listing new locations
  - Update `.kiro/steering/structure.md` with new documentation hierarchy
  - Verify `AGENTS.md` routing rules point to new locations
  - Update `backend/docs/MODULAR_DOCS_MIGRATION.md` to mark tasks complete
  - _Requirements: 5.3, 5.4, 6.1-6.4, 7.1-7.3_

## Notes

- Each task builds on the previous - complete in order
- Use relative paths for all cross-references (e.g., `../architecture/overview.md`)
- Target 5-15KB per file where practical
- Deprecation notices should follow the template in the design document
