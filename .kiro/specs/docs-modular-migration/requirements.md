# Requirements Document

## Introduction

This specification covers the migration of Neo Alexandria 2.0's monolithic documentation files into a modular, topic-focused structure. The goal is to improve documentation discoverability, reduce context loading for AI agents, and enable incremental updates without affecting unrelated content.

## Glossary

- **Migration_System**: The process and tooling for splitting monolithic documentation into modular files
- **Source_File**: Original monolithic documentation file (API_DOCUMENTATION.md, ARCHITECTURE_DIAGRAM.md, DEVELOPER_GUIDE.md)
- **Destination_File**: New modular documentation file in the organized directory structure
- **Cross_Reference**: Internal links between documentation files
- **Deprecation_Notice**: Warning added to old files directing users to new locations

## Requirements

### Requirement 1: API Documentation Migration

**User Story:** As a developer, I want API documentation split by domain, so that I can quickly find endpoints for a specific feature without loading the entire 132KB file.

#### Acceptance Criteria

1. WHEN migrating API documentation, THE Migration_System SHALL extract resource endpoints (`/resources/*`) into `api/resources.md`
2. WHEN migrating API documentation, THE Migration_System SHALL extract search endpoints (`/search/*`) into `api/search.md`
3. WHEN migrating API documentation, THE Migration_System SHALL extract collection endpoints (`/collections/*`) into `api/collections.md`
4. WHEN migrating API documentation, THE Migration_System SHALL extract annotation endpoints (`/annotations/*`) into `api/annotations.md`
5. WHEN migrating API documentation, THE Migration_System SHALL extract taxonomy endpoints (`/taxonomy/*`) into `api/taxonomy.md`
6. WHEN migrating API documentation, THE Migration_System SHALL extract graph and citation endpoints (`/graph/*`, `/citations/*`) into `api/graph.md`
7. WHEN migrating API documentation, THE Migration_System SHALL extract recommendation endpoints (`/recommendations/*`) into `api/recommendations.md`
8. WHEN migrating API documentation, THE Migration_System SHALL extract quality and curation endpoints (`/quality/*`, `/curation/*`) into `api/quality.md`
9. WHEN migrating API documentation, THE Migration_System SHALL extract monitoring endpoints (`/monitoring/*`, `/health`) into `api/monitoring.md`
10. WHEN migrating API documentation, THE Migration_System SHALL update `api/overview.md` with base URL, authentication, error handling, and pagination information

### Requirement 2: Architecture Documentation Migration

**User Story:** As a developer, I want architecture documentation split by topic, so that I can understand specific system components without reading the entire architecture file.

#### Acceptance Criteria

1. WHEN migrating architecture documentation, THE Migration_System SHALL extract high-level system diagrams into `architecture/overview.md`
2. WHEN migrating architecture documentation, THE Migration_System SHALL extract database schema, models, and migration information into `architecture/database.md`
3. WHEN migrating architecture documentation, THE Migration_System SHALL extract event system and event bus documentation into `architecture/event-system.md`
4. WHEN migrating architecture documentation, THE Migration_System SHALL extract vertical slice module documentation into `architecture/modules.md`
5. WHEN migrating architecture documentation, THE Migration_System SHALL extract design decisions and ADRs into `architecture/decisions.md`

### Requirement 3: Developer Guide Migration

**User Story:** As a new contributor, I want developer guides split by workflow, so that I can find setup instructions without reading deployment documentation.

#### Acceptance Criteria

1. WHEN migrating developer guide, THE Migration_System SHALL extract installation and environment setup into `guides/setup.md`
2. WHEN migrating developer guide, THE Migration_System SHALL extract common development tasks and code patterns into `guides/workflows.md`
3. WHEN migrating developer guide, THE Migration_System SHALL extract testing strategies and coverage information into `guides/testing.md`
4. WHEN migrating developer guide, THE Migration_System SHALL extract Docker and production deployment into `guides/deployment.md`
5. WHEN migrating developer guide, THE Migration_System SHALL extract troubleshooting and FAQ into `guides/troubleshooting.md`

### Requirement 4: Content Preservation

**User Story:** As a documentation maintainer, I want all content preserved during migration, so that no information is lost.

#### Acceptance Criteria

1. THE Migration_System SHALL preserve all endpoint documentation including request/response examples
2. THE Migration_System SHALL preserve all code examples and curl commands
3. THE Migration_System SHALL preserve all diagrams (ASCII and Mermaid)
4. THE Migration_System SHALL preserve all tables and parameter documentation
5. IF content does not fit a specific destination file, THEN THE Migration_System SHALL create an appropriate section or note its location

### Requirement 5: Cross-Reference Updates

**User Story:** As a documentation reader, I want working internal links, so that I can navigate between related topics.

#### Acceptance Criteria

1. WHEN creating destination files, THE Migration_System SHALL add cross-references to related documentation
2. WHEN a destination file references another topic, THE Migration_System SHALL use relative links to the appropriate file
3. THE Migration_System SHALL update `backend/docs/index.md` with accurate navigation to all new files
4. THE Migration_System SHALL verify all internal links resolve to existing files

### Requirement 6: Deprecation Notices

**User Story:** As a developer using old documentation paths, I want clear deprecation notices, so that I know where to find the new documentation.

#### Acceptance Criteria

1. WHEN migration is complete, THE Migration_System SHALL add deprecation notices to the top of `API_DOCUMENTATION.md`
2. WHEN migration is complete, THE Migration_System SHALL add deprecation notices to the top of `ARCHITECTURE_DIAGRAM.md`
3. WHEN migration is complete, THE Migration_System SHALL add deprecation notices to the top of `DEVELOPER_GUIDE.md`
4. WHEN adding deprecation notices, THE Migration_System SHALL list all new file locations for the migrated content

### Requirement 7: Steering Documentation Updates

**User Story:** As an AI agent, I want updated routing rules, so that I can find documentation efficiently.

#### Acceptance Criteria

1. WHEN migration is complete, THE Migration_System SHALL update `.kiro/steering/structure.md` with the new documentation hierarchy
2. WHEN migration is complete, THE Migration_System SHALL verify `AGENTS.md` routing rules point to new locations
3. WHEN migration is complete, THE Migration_System SHALL update `backend/docs/MODULAR_DOCS_MIGRATION.md` to mark tasks as complete

### Requirement 8: File Size Guidelines

**User Story:** As an AI agent, I want focused documentation files, so that I can load only relevant context.

#### Acceptance Criteria

1. THE Migration_System SHALL target 5-15KB per destination file where practical
2. IF a topic requires more than 15KB, THEN THE Migration_System SHALL consider further subdivision
3. THE Migration_System SHALL ensure each file covers a single cohesive topic
