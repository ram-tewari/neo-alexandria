# Neo Alexandria Frontend Roadmap
## "Second Brain" for Code - Fresh Start

**Philosophy**: Dual-Head Architecture (Dashboard + MCP)
**Current Status**: Auth foundation ✅ | Clean slate for features

---

## Pharos-Specific Enhancements

This roadmap leverages Neo Alexandria's unique backend capabilities:

**🧠 Terminology**: "Cortex/Knowledge Base" (Phase 4) emphasizes the "Second Brain" concept
**🔬 LBD Integration**: "Hypothesis Mode" in Phase 4 utilizes Literature-Based Discovery for contradiction detection and hidden connections
**⭐ Quality System**: "Quality Badges" in Phase 2 visualize multi-dimensional quality scores
**📐 Scholarly Assets**: "Equation/Table Drawers" in Phase 3 showcase extracted scholarly metadata
**🧩 AST Chunking**: Phase 2 visualizes "Semantic Chunks" using AST-based chunking, not just lines

---

## Phase Overview

| Phase | Name | Focus | Complexity |
|-------|------|-------|------------|
| Phase 1 | Core Workbench & Navigation | Foundation layout, sidebar, command palette | ⭐⭐⭐ Medium |
| Phase 2 | Living Code Editor | Monaco editor, AST chunks, quality badges, annotations | ⭐⭐⭐⭐ High |
| Phase 3 | Living Library | PDF management, scholarly assets (equations/tables) | ⭐⭐⭐⭐ High |
| Phase 4 | Cortex/Knowledge Base | Visual graph, hypothesis mode (LBD), contradictions | ⭐⭐⭐⭐⭐ Very High |
| Phase 5 | Implementation Planner | AI-powered planning, Kanban checklist | ⭐⭐⭐ Medium |
| Phase 6 | Unified RAG Interface | Split-pane search, streaming answers, evidence | ⭐⭐⭐⭐ High |
| Phase 7 | Ops & Edge Management | System health, worker status, monitoring | ⭐⭐ Low |
| Phase 8 | MCP Client Integration | IDE ghost interface, headless tools | ⭐⭐⭐⭐ High |

---

## Tech Stack

**Framework**: React 18 + TypeScript + Vite
**Routing**: TanStack Router
**State**: Zustand
**Data Fetching**: TanStack Query
**Styling**: Tailwind CSS

**UI Component Strategy**:
- **shadcn-ui MCP** (`@jpisnice/shadcn-ui-mcp-server`) - Core primitives
- **magic-ui MCP** (`@magicuidesign/mcp`) - Animations & effects
- **magic-mcp** (`@21st-dev/magic-mcp`) - AI component generation

**Specialized Libraries**:
- Monaco Editor (code viewing)
- React Flow (graph visualization)
- React-PDF / PDF.js (PDF rendering)
- Dnd-Kit (drag & drop)
- Framer Motion (animations)

---


## Phase 1: Core Workbench & Navigation

**What It Delivers**: The foundational "Command Center" layout

**Key Features**:
- Sidebar navigation (Repositories, Cortex, Library, Planner, Wiki, Ops)
- Global Command Palette (Cmd+K)
- Repository switcher
- Responsive workbench layout
- Theme system

**Backend Dependencies**: Minimal (auth + basic resource listing)

### Implementation Options

#### Option A: "Clean & Fast" ⭐⭐ Low Complexity
- **Style**: VS Code-inspired, minimalist, monochrome
- **Components**: shadcn-ui Command, Sheet, Sidebar
- **Interaction**: Keyboard-first, Vim-style navigation
- **Pros**: Fast, accessible, familiar to developers
- **Cons**: Less visually impressive

#### Option B: "Rich & Visual" ⭐⭐⭐⭐ High Complexity
- **Style**: Glassmorphism, animated, modern
- **Components**: magic-ui Dock, Spotlight, animated sidebar
- **Interaction**: Mouse-friendly, smooth animations
- **Pros**: Beautiful, impressive, high engagement
- **Cons**: Larger bundle, performance concerns

#### Option C: "Hybrid Power" ⭐⭐⭐ Medium Complexity ⭐ RECOMMENDED
- **Style**: Clean base with strategic animations
- **Components**: magic-mcp generated + shadcn-ui + magic-ui accents
- **Interaction**: Keyboard shortcuts + mouse polish
- **Pros**: Professional, performant, balanced
- **Cons**: Requires careful integration

---

## Phase 2: Living Code Editor (Active Reading)

**What It Delivers**: Monaco-based code viewer with intelligence

**Key Features**:
- Monaco Editor (read-only)
- **Semantic Chunk Visualization** (AST-based, not just lines)
- **Quality Badges** (leverages Quality scoring system)
- Annotation gutter with colored chips
- Hover cards (Node2Vec summaries + 1-hop graph)
- Reference overlay (book icons link to papers)
- Tree-sitter semantic highlighting

**Backend Dependencies**: 
- Annotation API ✅
- Code embeddings (needs work)
- Node2Vec summaries (needs work)
- Quality scoring API ✅
- AST chunking API ✅

### Implementation Options

#### Option A: "Clean & Fast" ⭐⭐⭐ Medium Complexity
- **Style**: IDE-like, minimal chrome
- **Components**: Monaco + shadcn-ui Popover, Tooltip, Badge
- **Interaction**: Click to annotate, hover for info
- **Pros**: Familiar IDE feel, fast rendering
- **Cons**: Basic visuals

#### Option B: "Rich & Visual" ⭐⭐⭐⭐ High Complexity
- **Style**: Animated annotations, glowing highlights
- **Components**: Monaco + magic-ui neon badges, spotlight
- **Interaction**: Smooth animations, cinematic hover
- **Pros**: Impressive demos, engaging
- **Cons**: Performance with large files

#### Option C: "Hybrid Power" ⭐⭐⭐⭐ Medium-High Complexity ⭐ RECOMMENDED
- **Style**: Professional with strategic polish
- **Components**: magic-mcp Monaco wrapper + shadcn-ui + magic-ui accents
- **Interaction**: Hover preview, click detail, keyboard nav
- **Pros**: Professional, performant, intelligent
- **Cons**: Requires Monaco expertise

---


## Phase 3: Living Library (PDF/Docs Management)

**What It Delivers**: PDF upload, viewing, and intelligent linking

**Key Features**:
- Grid view of uploaded PDFs/docs
- PDF viewer with text highlighting
- Auto-link suggestions (PDF ↔ Code via embeddings)
- **Equation/Table Drawers** (leverages Scholarly extraction metadata)
- Page-level navigation
- Search within PDFs
- Extracted scholarly assets visualization

**Backend Dependencies**:
- PDF ingestion API (needs work)
- PDF chunking service (needs work)
- Vector similarity for auto-linking (needs work)
- Scholarly metadata API ✅ (equations, tables, citations)

### Implementation Options

#### Option A: "Clean & Fast" ⭐⭐⭐ Medium Complexity
- **Style**: Document-focused, clean grid
- **Components**: shadcn-ui Card, Dialog, Table + react-pdf
- **Interaction**: Click to open, scroll to navigate
- **Pros**: Fast PDF rendering, simple
- **Cons**: Basic visuals, limited preview

#### Option B: "Rich & Visual" ⭐⭐⭐⭐⭐ Very High Complexity
- **Style**: Magazine-style, animated previews
- **Components**: magic-ui Bento grid + custom PDF renderer
- **Interaction**: Hover previews, smooth transitions
- **Pros**: Beautiful library view, impressive
- **Cons**: PDF rendering complexity, performance

#### Option C: "Hybrid Power" ⭐⭐⭐⭐ High Complexity ⭐ RECOMMENDED
- **Style**: Professional document manager
- **Components**: magic-mcp library grid + shadcn-ui + react-pdf
- **Interaction**: Search, filter, preview, smart linking
- **Pros**: Powerful features, good UX
- **Cons**: Complex PDF/code syncing logic

---

## Phase 4: Cortex/Knowledge Base (Visual Intelligence + Hypothesis Mode)

**What It Delivers**: Interactive knowledge graph with 3 views + Hypothesis Mode

**Key Features**:
- **City Map**: High-level clusters
- **Blast Radius**: Refactoring impact analysis
- **Dependency Waterfall**: Data flow DAG
- **Hypothesis Mode** (NEW): Leverages LBD (Literature-Based Discovery) backend
  - Contradiction detection between papers
  - Hidden connection discovery
  - Research gap identification
- Node2Vec visualization
- Interactive zoom/pan/filter

**Backend Dependencies**:
- Graph computation API (needs work)
- Node2Vec embeddings (needs work)
- Cluster detection (needs work)
- Dependency analysis (needs work)
- **LBD hypothesis API** ✅ (contradiction detection, hidden connections)

### Implementation Options

#### Option A: "Clean & Fast" ⭐⭐⭐ Medium Complexity
- **Style**: Technical diagram, clear nodes/edges
- **Components**: React Flow + shadcn-ui controls
- **Interaction**: Click to select, drag to pan
- **Pros**: Fast rendering, clear visualization
- **Cons**: Basic visuals, limited interactivity

#### Option B: "Rich & Visual" ⭐⭐⭐⭐⭐ Very High Complexity
- **Style**: Animated graph, glowing nodes, particles
- **Components**: Custom WebGL/D3 + magic-ui effects
- **Interaction**: Cinematic animations, smooth zoom
- **Pros**: Stunning visuals, memorable
- **Cons**: Performance with large graphs, very complex

#### Option C: "Hybrid Power" ⭐⭐⭐⭐ High Complexity ⭐ RECOMMENDED
- **Style**: Professional graph with smart interactions
- **Components**: React Flow + magic-mcp nodes + magic-ui effects
- **Interaction**: Semantic zoom, smart filtering
- **Pros**: Powerful, performant, professional
- **Cons**: Complex graph algorithms

---


## Phase 5: Implementation Planner (Action)

**What It Delivers**: AI-powered implementation planning

**Key Features**:
- Natural language input ("Plan Payment Service")
- Kanban-style checklist
- Links to architecture docs
- Links to sample code
- Step tracking and completion
- Progress visualization

**Backend Dependencies**:
- Multi-hop MCP agent (needs work)
- Architecture doc parsing (needs work)
- Sample repo analysis (needs work)

### Implementation Options

#### Option A: "Clean & Fast" ⭐⭐ Low Complexity ⭐ RECOMMENDED
- **Style**: Simple checklist, text-focused
- **Components**: shadcn-ui Checkbox, Card, Accordion
- **Interaction**: Check off steps, click links
- **Pros**: Clear, simple, fast to implement
- **Cons**: Basic visuals, limited engagement

#### Option B: "Rich & Visual" ⭐⭐⭐⭐ High Complexity
- **Style**: Animated Kanban, progress viz
- **Components**: magic-ui cards + dnd-kit + confetti
- **Interaction**: Drag to reorder, animations on complete
- **Pros**: Engaging, motivating, beautiful
- **Cons**: May be overkill for planning

#### Option C: "Hybrid Power" ⭐⭐⭐⭐ High Complexity
- **Style**: Smart planner with AI assistance
- **Components**: magic-mcp planner + shadcn-ui + magic-ui accents
- **Interaction**: AI suggestions, smart linking
- **Pros**: Intelligent, helpful, professional
- **Cons**: Requires robust backend agent

---

## Phase 6: Unified RAG Interface (Deep Integration)

**What It Delivers**: Split-pane search with streaming answers

**Key Features**:
- Natural language queries
- Streaming markdown answers (left pane)
- Evidence rail (right pane) with tabs
- Code/Paper snippet highlighting
- Hover-to-highlight synchronization
- Citation tracking

**Backend Dependencies**:
- Hybrid search ✅
- RAG pipeline ✅
- PDF chunk retrieval (needs work)
- Reverse HyDE ✅

### Implementation Options

#### Option A: "Clean & Fast" ⭐⭐⭐ Medium Complexity
- **Style**: Split pane, clean markdown
- **Components**: shadcn-ui Tabs, Card + markdown renderer
- **Interaction**: Type query, read answer, click evidence
- **Pros**: Clear, fast, focused on content
- **Cons**: Basic visuals, limited interactivity

#### Option B: "Rich & Visual" ⭐⭐⭐⭐⭐ Very High Complexity
- **Style**: Cinematic search, animated streaming
- **Components**: magic-ui text animation + custom streaming
- **Interaction**: Smooth animations, hover effects
- **Pros**: Impressive, engaging, memorable
- **Cons**: Complex synchronization, performance

#### Option C: "Hybrid Power" ⭐⭐⭐⭐ High Complexity ⭐ RECOMMENDED
- **Style**: Professional RAG interface
- **Components**: magic-mcp RAG structure + shadcn-ui + magic-ui streaming
- **Interaction**: Natural queries, smart highlighting
- **Pros**: Powerful, professional, intelligent UX
- **Cons**: Complex PDF/code synchronization

---


## Phase 7: Ops & Edge Management

**What It Delivers**: System health and operations dashboard

**Key Features**:
- Live status board
- Ingestion queue visualization
- GPU worker heartbeat
- Manual re-index buttons
- Performance metrics
- Error tracking

**Backend Dependencies**:
- Redis queue API ✅
- Edge worker status API ✅
- Monitoring endpoints ✅

### Implementation Options

#### Option A: "Clean & Fast" ⭐⭐ Low Complexity ⭐ RECOMMENDED
- **Style**: Dashboard, simple metrics
- **Components**: shadcn-ui Card, Badge, Progress + recharts
- **Interaction**: View status, click to refresh
- **Pros**: Clear, functional, reliable
- **Cons**: Basic visuals, limited insights

#### Option B: "Rich & Visual" ⭐⭐⭐⭐ High Complexity
- **Style**: Animated dashboard, real-time effects
- **Components**: magic-ui animated progress + orbiting circles
- **Interaction**: Real-time updates, smooth animations
- **Pros**: Engaging, impressive, real-time feel
- **Cons**: Complexity, potential performance issues

#### Option C: "Hybrid Power" ⭐⭐⭐ Medium Complexity
- **Style**: Professional ops dashboard
- **Components**: magic-mcp dashboard + shadcn-ui + magic-ui alerts
- **Interaction**: Auto-refresh, smart alerts
- **Pros**: Professional, informative, reliable
- **Cons**: Requires robust monitoring backend

---

## Phase 8: MCP Client Integration (IDE Ghost Interface)

**What It Delivers**: Headless MCP tools for IDE integration

**Key Features**:
- `@SecondBrain search` - Text search with file links
- `@SecondBrain plan` - Implementation plan generator
- `@SecondBrain context` - Contextual suggestions
- IDE integration (VS Code, Cursor, Claude)
- Local file linking

**Backend Dependencies**:
- MCP server implementation (needs work)
- Tool definitions (needs work)
- Context management (needs work)

### Implementation Options

#### Option A: "Clean & Fast" ⭐⭐ Low Complexity
- **Style**: Text-based responses
- **Components**: Simple MCP tool definitions
- **Interaction**: Command-based, text responses
- **Pros**: Simple, reliable, fast
- **Cons**: Basic functionality, limited richness

#### Option B: "Rich & Visual" ⭐⭐⭐⭐ High Complexity
- **Style**: Rich markdown, embedded previews
- **Components**: Rich MCP tools + embedded code previews
- **Interaction**: Rich responses, embedded interactions
- **Pros**: Rich experience, engaging, powerful
- **Cons**: Complex MCP implementation, IDE limitations

#### Option C: "Hybrid Power" ⭐⭐⭐⭐ High Complexity ⭐ RECOMMENDED
- **Style**: Smart responses with contextual richness
- **Components**: magic-mcp tool structure + adaptive responses
- **Interaction**: Smart, adaptive, context-aware
- **Pros**: Intelligent, flexible, powerful
- **Cons**: Complex context management

---


## Recommended Implementation Strategy

### Phase Priority & Approach

**Tier 1 (Foundation)** - Build First:
1. **Phase 1** (Workbench) - Option C: Hybrid Power
   - Establishes the entire UI foundation
   - All other phases depend on this

**Tier 2 (Core Features)** - Build in Parallel:
2. **Phase 2** (Code Editor) - Option C: Hybrid Power
3. **Phase 3** (Library) - Option C: Hybrid Power
4. **Phase 7** (Ops) - Option A: Clean & Fast
   - These can be developed independently

**Tier 3 (Advanced Features)** - Build After Core:
5. **Phase 6** (RAG Interface) - Option C: Hybrid Power
   - Depends on Phase 2 & 3 for full power
6. **Phase 4** (Cortex/Knowledge Base) - Option C: Hybrid Power
   - Complex, can be developed independently
7. **Phase 5** (Planner) - Option A: Clean & Fast
   - Simpler, can be added anytime

**Tier 4 (Integration)** - Build Last:
8. **Phase 8** (MCP Client) - Option C: Hybrid Power
   - Requires all other phases to be valuable

### Why "Hybrid Power" (Option C) for Most Phases?

**Balanced Approach**:
- Professional polish without over-engineering
- Strategic use of animations where they add value
- Leverages all 3 MCP servers effectively
- Manageable complexity
- Good performance

**MCP Server Usage**:
- **magic-mcp**: Generate initial component structure (saves time)
- **shadcn-ui**: Core UI primitives (reliability)
- **magic-ui**: Strategic animations and effects (delight)

### Backend Work Needed

**Before Phase 2**:
- Code embeddings API
- Node2Vec graph summaries

**Before Phase 3**:
- PDF ingestion API
- PDF chunking service
- Vector similarity for auto-linking

**Before Phase 4**:
- Graph computation API
- Cluster detection
- Dependency analysis

**Before Phase 5**:
- Multi-hop MCP agent
- Architecture doc parsing

**Before Phase 8**:
- MCP server implementation
- Tool definitions

---

## Next Steps

1. **Choose Phase 1 Option** (Recommended: Option C - Hybrid Power)
2. **I'll create the full spec** (requirements.md, design.md, tasks.md)
3. **Start implementation** with the new UI MCP servers
4. **Iterate through phases** building the "Second Brain"

**Ready to start Phase 1?** Let me know which option you prefer!
