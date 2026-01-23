# Requirements Document - Phase 2: Living Code Editor

## Introduction

Phase 2 delivers an intelligent code viewing experience that transforms static code into an interactive "living document" with semantic understanding, quality insights, and collaborative annotations. This phase builds on the Phase 1 workbench foundation to provide the core active reading experience for code repositories.

## Glossary

- **Living_Code_Editor**: Monaco-based read-only code viewer with intelligence overlays
- **Semantic_Chunk**: AST-based code segment (not line-based) representing logical units
- **Quality_Badge**: Visual indicator showing multi-dimensional quality scores
- **Annotation_Gutter**: Left margin displaying colored annotation chips
- **Hover_Card**: Contextual popup showing Node2Vec summaries and graph connections
- **Reference_Overlay**: Visual indicators linking code to external papers/documentation
- **Tree_Sitter**: Parser library providing semantic syntax highlighting
- **Node2Vec**: Graph embedding algorithm generating code summaries
- **AST**: Abstract Syntax Tree representing code structure

## Requirements

### Requirement 1: Monaco Editor Integration

**User Story:** As a developer, I want to view code in a familiar IDE-like editor, so that I can read and navigate code comfortably.

#### Acceptance Criteria

1. WHEN a code file is opened, THE Living_Code_Editor SHALL render it using Monaco Editor in read-only mode
2. WHEN the editor loads, THE Living_Code_Editor SHALL apply Tree_Sitter semantic highlighting based on file language
3. WHEN a user scrolls through code, THE Living_Code_Editor SHALL maintain smooth 60fps performance for files up to 10,000 lines
4. WHEN a user uses keyboard shortcuts (Cmd+F, Cmd+G), THE Living_Code_Editor SHALL support standard editor navigation
5. WHEN the theme changes, THE Living_Code_Editor SHALL update Monaco's theme to match (light/dark)

### Requirement 2: Semantic Chunk Visualization

**User Story:** As a developer, I want to see logical code segments highlighted, so that I can understand code structure at a glance.

#### Acceptance Criteria

1. WHEN a code file is displayed, THE Living_Code_Editor SHALL fetch AST-based chunks from the backend
2. WHEN chunks are received, THE Living_Code_Editor SHALL render visual boundaries around each Semantic_Chunk
3. WHEN a user hovers over a chunk boundary, THE Living_Code_Editor SHALL highlight the entire chunk with a subtle background color
4. WHEN a user clicks a chunk, THE Living_Code_Editor SHALL select the entire chunk and show chunk metadata in a sidebar
5. WHEN chunks overlap or nest, THE Living_Code_Editor SHALL display the most specific (innermost) chunk boundary

### Requirement 3: Quality Badge Display

**User Story:** As a developer, I want to see quality scores for code segments, so that I can identify areas needing attention.

#### Acceptance Criteria

1. WHEN a code file has quality scores, THE Living_Code_Editor SHALL fetch multi-dimensional quality data from the backend
2. WHEN quality data is available, THE Living_Code_Editor SHALL display Quality_Badge indicators in the gutter for relevant lines
3. WHEN a user hovers over a Quality_Badge, THE Living_Code_Editor SHALL show a tooltip with detailed quality metrics
4. WHEN quality scores are below threshold (< 0.6), THE Living_Code_Editor SHALL use warning colors (yellow/red)
5. WHEN quality scores are above threshold (>= 0.8), THE Living_Code_Editor SHALL use success colors (green)

### Requirement 4: Annotation System

**User Story:** As a developer, I want to add and view annotations on code, so that I can capture insights and collaborate with others.

#### Acceptance Criteria

1. WHEN a user selects text in the editor, THE Living_Code_Editor SHALL show an annotation creation button
2. WHEN a user creates an annotation, THE Living_Code_Editor SHALL display a colored chip in the Annotation_Gutter
3. WHEN a user hovers over an annotation chip, THE Living_Code_Editor SHALL highlight the annotated text range
4. WHEN a user clicks an annotation chip, THE Living_Code_Editor SHALL open a popover showing the annotation content
5. WHEN multiple annotations exist on the same line, THE Living_Code_Editor SHALL stack chips vertically in the gutter
6. WHEN a user edits an annotation, THE Living_Code_Editor SHALL update the annotation via the backend API
7. WHEN a user deletes an annotation, THE Living_Code_Editor SHALL remove the chip and update the backend

### Requirement 5: Hover Card Intelligence

**User Story:** As a developer, I want to see contextual information when hovering over code, so that I can understand relationships without leaving the editor.

#### Acceptance Criteria

1. WHEN a user hovers over a function or class name, THE Living_Code_Editor SHALL fetch Node2Vec summary from the backend
2. WHEN Node2Vec data is available, THE Living_Code_Editor SHALL display a Hover_Card with the summary
3. WHEN the Hover_Card is shown, THE Living_Code_Editor SHALL include 1-hop graph connections (related functions/classes)
4. WHEN a user clicks a related item in the Hover_Card, THE Living_Code_Editor SHALL navigate to that code location
5. WHEN hover data is loading, THE Living_Code_Editor SHALL show a loading skeleton in the Hover_Card
6. WHEN hover data fails to load, THE Living_Code_Editor SHALL show basic symbol information from Monaco's language service

### Requirement 6: Reference Overlay System

**User Story:** As a researcher, I want to see which papers or documentation are referenced in code, so that I can explore the theoretical foundation.

#### Acceptance Criteria

1. WHEN a code file has external references, THE Living_Code_Editor SHALL fetch reference metadata from the backend
2. WHEN references are available, THE Living_Code_Editor SHALL display book icons in the gutter next to relevant lines
3. WHEN a user hovers over a reference icon, THE Living_Code_Editor SHALL show a tooltip with paper title and authors
4. WHEN a user clicks a reference icon, THE Living_Code_Editor SHALL open a Reference_Overlay panel showing full citation details
5. WHEN a reference links to a PDF in the library, THE Living_Code_Editor SHALL provide a "View in Library" button

### Requirement 7: Performance and Responsiveness

**User Story:** As a developer, I want the editor to remain responsive with large files, so that I can work efficiently.

#### Acceptance Criteria

1. WHEN a file larger than 5,000 lines is opened, THE Living_Code_Editor SHALL use virtualized rendering
2. WHEN annotations are loaded, THE Living_Code_Editor SHALL render them incrementally to avoid blocking the UI
3. WHEN quality badges are displayed, THE Living_Code_Editor SHALL lazy-load badge data as the user scrolls
4. WHEN hover cards are triggered, THE Living_Code_Editor SHALL debounce requests by 300ms to reduce API calls
5. WHEN the editor is resized, THE Living_Code_Editor SHALL reflow content within 100ms

### Requirement 8: Keyboard Navigation

**User Story:** As a power user, I want keyboard shortcuts for all editor actions, so that I can work without using the mouse.

#### Acceptance Criteria

1. WHEN a user presses Cmd+K, THE Living_Code_Editor SHALL open the command palette with editor-specific commands
2. WHEN a user presses Cmd+/, THE Living_Code_Editor SHALL toggle annotation mode
3. WHEN a user presses Cmd+Shift+A, THE Living_Code_Editor SHALL show all annotations in the current file
4. WHEN a user presses Cmd+Shift+Q, THE Living_Code_Editor SHALL toggle quality badge visibility
5. WHEN a user presses Cmd+Shift+C, THE Living_Code_Editor SHALL toggle chunk boundary visibility

### Requirement 9: State Persistence

**User Story:** As a developer, I want my editor preferences to persist across sessions, so that I don't have to reconfigure each time.

#### Acceptance Criteria

1. WHEN a user changes editor settings (font size, line numbers), THE Living_Code_Editor SHALL save preferences to local storage
2. WHEN a user returns to a file, THE Living_Code_Editor SHALL restore scroll position and cursor location
3. WHEN a user toggles visibility options (badges, chunks), THE Living_Code_Editor SHALL persist these preferences
4. WHEN a user switches repositories, THE Living_Code_Editor SHALL maintain per-repository editor state
5. WHEN local storage is unavailable, THE Living_Code_Editor SHALL use sensible defaults without errors

### Requirement 10: Error Handling and Fallbacks

**User Story:** As a developer, I want the editor to handle errors gracefully, so that I can continue working even when backend services fail.

#### Acceptance Criteria

1. WHEN the backend API is unavailable, THE Living_Code_Editor SHALL display code without intelligence features
2. WHEN AST chunking fails, THE Living_Code_Editor SHALL fall back to line-based display
3. WHEN quality scores fail to load, THE Living_Code_Editor SHALL hide quality badges without breaking the UI
4. WHEN annotation API fails, THE Living_Code_Editor SHALL show cached annotations with a warning banner
5. WHEN hover card data fails, THE Living_Code_Editor SHALL show basic Monaco IntelliSense information
