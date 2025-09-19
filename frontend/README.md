# Neo Alexandria 2.0 - Frontend Interface

A modern, responsive web interface for the Neo Alexandria 2.0 Knowledge Management System. Built with React, TypeScript, and Tailwind CSS to provide a seamless experience for managing your personal knowledge library.

## 🚀 Features

### Core Functionality
- **📚 Library Dashboard**: Browse, filter, and manage your resource collection
- **🔍 Intelligent Search**: Hybrid keyword/semantic search with advanced filtering
- **➕ URL Ingestion**: Add resources with real-time processing status
- **📄 Resource Management**: Detailed view and editing capabilities
- **🧠 Knowledge Graph**: Visualize connections between resources
- **💡 Recommendations**: AI-powered content discovery
- **🎯 Curation Tools**: Quality control and batch operations

### Technical Features
- **Responsive Design**: Optimized for desktop, tablet, and mobile
- **Real-time Updates**: Live status tracking for resource processing
- **Modern UI/UX**: Clean, intuitive interface with dark/light theme support
- **Type Safety**: Full TypeScript implementation
- **Performance**: Optimized with React Query and efficient state management
- **Error Handling**: Comprehensive error boundaries and user feedback

## 🛠 Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Tailwind CSS with custom component library
- **State Management**: Zustand for lightweight, scalable state
- **Data Fetching**: TanStack React Query for server state management
- **Routing**: React Router v6 for client-side navigation
- **Icons**: Lucide React for consistent iconography
- **HTTP Client**: Axios with interceptors and error handling

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm
- Neo Alexandria 2.0 backend running on `http://127.0.0.1:8000`

### Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
```

### Build for Production
```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## 🏗 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/              # Base UI components (Button, Input, etc.)
│   │   ├── layout/          # Layout components (Header, Sidebar)
│   │   └── resources/       # Resource-specific components
│   ├── pages/               # Page components for routing
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API service layer
│   ├── store/               # Zustand state management
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   └── assets/              # Static assets
├── public/                  # Public assets
└── dist/                    # Production build output
```

## 🎨 Design System

### Color Palette
- **Primary**: Blue variants for main actions and highlights
- **Secondary**: Gray variants for content and backgrounds
- **Semantic**: Green (success), Red (error), Yellow (warning), Blue (info)

### Typography
- **Headings**: Inter font family with appropriate weights
- **Body**: Inter for readability
- **Code**: JetBrains Mono for technical content

### Components
All components are built with:
- Consistent spacing using Tailwind utilities
- Accessible color contrast ratios
- Focus states for keyboard navigation
- Responsive design patterns
- Dark mode support (coming soon)

## 🔌 API Integration

The frontend communicates with the Neo Alexandria 2.0 backend through a well-defined REST API:

### Key Endpoints
- `POST /resources` - Add new resources via URL
- `GET /resources` - List resources with filtering/pagination
- `POST /search` - Hybrid search with semantic capabilities
- `GET /recommendations` - Personalized content recommendations
- `GET /graph/*` - Knowledge graph data for visualization

### Error Handling
- Automatic retry logic for transient failures
- User-friendly error messages
- Global error boundary for unhandled exceptions
- Offline state detection and handling

## 📱 Responsive Design

The interface adapts seamlessly across devices:

### Desktop (1024px+)
- Full sidebar navigation
- Multi-column layouts
- Advanced filter panels
- Comprehensive data tables

### Tablet (768px - 1023px)
- Collapsible sidebar
- Two-column layouts where appropriate
- Touch-optimized interactions
- Simplified filter interfaces

### Mobile (< 768px)
- Hidden sidebar with overlay
- Single-column layouts
- Bottom navigation consideration
- Thumb-friendly touch targets

## 🎯 Key User Flows

### Adding a Resource
1. Click "Add Resource" in sidebar or header
2. Paste URL in the input field
3. Optionally add custom title
4. Submit for processing
5. Monitor real-time status updates
6. View completed resource in library

### Searching Knowledge
1. Navigate to Search page
2. Enter search query
3. Adjust hybrid search weight (keyword ↔ semantic)
4. Apply advanced filters as needed
5. Browse results with relevance scoring
6. Use facets to refine further

### Exploring Connections
1. View any resource detail page
2. Click "View Connections" or navigate to graph
3. Explore interactive visualization
4. Click connected nodes to traverse
5. Adjust similarity thresholds
6. Export or share interesting patterns

## 🔧 Configuration

### Environment Variables
```bash
# API base URL (default: /api with proxy)
VITE_API_BASE_URL=http://127.0.0.1:8000

# Enable development features
VITE_DEV_MODE=true
```

### Proxy Configuration
The Vite dev server proxies `/api/*` requests to the backend at `http://127.0.0.1:8000`, allowing seamless development without CORS issues.

## 🧪 Testing Strategy

### Unit Tests (Coming Soon)
- Component rendering and behavior
- Utility function correctness
- Hook functionality
- API service layer

### Integration Tests (Coming Soon)
- End-to-end user flows
- API integration scenarios
- Error handling paths
- Performance benchmarks

### Manual Testing Checklist
- [ ] Resource ingestion flow
- [ ] Search functionality
- [ ] Responsive layouts
- [ ] Error states
- [ ] Loading states
- [ ] Accessibility compliance

## 🚀 Performance Optimizations

### Code Splitting
- Route-based splitting for smaller initial bundles
- Component lazy loading for non-critical features
- Dynamic imports for heavy libraries

### Caching Strategy
- React Query handles server state caching
- Zustand persists user preferences
- Browser caching for static assets
- Service worker for offline functionality (planned)

### Bundle Optimization
- Tree shaking to eliminate unused code
- Asset optimization and compression
- Modern browser targeting
- CSS purging for minimal stylesheets

## 🔒 Security Considerations

### Data Handling
- No sensitive data stored in localStorage
- Secure HTTP-only cookie support (when authentication added)
- Input sanitization for user-generated content
- XSS prevention in dynamic content rendering

### API Security
- Request/response interceptors for security headers
- Rate limiting awareness in UI
- Graceful handling of authentication errors
- Secure token storage patterns (future)

## 🎨 Customization

### Theming
The application uses CSS custom properties and Tailwind's theming system:

```css
/* Custom theme colors in tailwind.config.js */
colors: {
  primary: { /* Blue variants */ },
  secondary: { /* Gray variants */ },
}
```

### Component Variants
UI components support multiple variants:
- `Button`: primary, secondary, ghost, danger, outline
- `Badge`: default, success, warning, error, info, outline
- `Card`: with hover states and padding options

## 📈 Roadmap

### Phase 1 ✅
- Core library management
- URL ingestion with status tracking
- Basic search functionality
- Responsive design implementation

### Phase 2 🚧
- Advanced search with facets
- Knowledge graph visualization
- Recommendation system integration
- Quality curation tools

### Phase 3 📋
- Real-time collaborative features
- Advanced export/import options
- Plugin system for extensions
- Offline support and PWA features

### Phase 4 📋
- AI-powered insights dashboard
- Advanced graph analytics
- Integration with external services
- Mobile app development

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit pull request with description
5. Address code review feedback

### Code Standards
- TypeScript strict mode enabled
- Prettier for code formatting
- ESLint for code quality
- Conventional commits for changelog
- Component documentation with JSDoc

## 📞 Support

For questions, issues, or feature requests:
- GitHub Issues for bug reports
- Discussions for feature ideas
- Documentation for implementation guides
- Code examples for common patterns

---

**Neo Alexandria 2.0** - Transform your knowledge into wisdom through intelligent organization and discovery.
