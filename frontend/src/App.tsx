import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './contexts/ThemeContext';
import { MainLayout } from './components/layout/MainLayout';
import { Home } from './pages/Home';
import { PlaceholderPage } from './pages/PlaceholderPage';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { ToastContainer } from './components/common/Toast';
import { CommandPalette } from './components/layout/CommandPalette';
import { useCommandPalette } from './hooks/useKeyboard';
import { useCommandStore } from './store/commandStore';
import './styles/globals.css';
import './styles/dual-theme.css';

// Lazy load pages to catch errors better
import { lazy, Suspense } from 'react';

const Library = lazy(() => import('./pages/Library').then(m => ({ default: m.Library })).catch(() => ({ default: () => <PlaceholderPage title="Library" /> })));
const Search = lazy(() => import('./pages/Search').then(m => ({ default: m.Search })).catch(() => ({ default: () => <PlaceholderPage title="Search" /> })));
const Recommendations = lazy(() => import('./pages/Recommendations').then(m => ({ default: m.Recommendations })).catch(() => ({ default: () => <PlaceholderPage title="Recommendations" /> })));
const Annotations = lazy(() => import('./pages/Annotations').then(m => ({ default: m.Annotations })).catch(() => ({ default: () => <PlaceholderPage title="Annotations" /> })));
const Graph = lazy(() => import('./pages/Graph').then(m => ({ default: m.Graph })).catch(() => ({ default: () => <PlaceholderPage title="Knowledge Graph" /> })));
const Quality = lazy(() => import('./pages/Quality').then(m => ({ default: m.Quality })).catch(() => ({ default: () => <PlaceholderPage title="Quality" /> })));
const Taxonomy = lazy(() => import('./pages/Taxonomy').then(m => ({ default: m.Taxonomy })).catch(() => ({ default: () => <PlaceholderPage title="Taxonomy" /> })));
const Monitoring = lazy(() => import('./pages/Monitoring').then(m => ({ default: m.Monitoring })).catch(() => ({ default: () => <PlaceholderPage title="Monitoring" /> })));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const LoadingFallback = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
      <p className="text-gray-600 dark:text-gray-400">Loading...</p>
    </div>
  </div>
);

function AppContent() {
  const { togglePalette } = useCommandStore();
  useCommandPalette(togglePalette);

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Home />} />
            <Route path="library" element={
              <ErrorBoundary fallback={<PlaceholderPage title="Library" description="This page encountered an error. We're working on it!" />}>
                <Suspense fallback={<LoadingFallback />}>
                  <Library />
                </Suspense>
              </ErrorBoundary>
            } />
            <Route path="search" element={
              <ErrorBoundary fallback={<PlaceholderPage title="Search" description="This page encountered an error. We're working on it!" />}>
                <Suspense fallback={<LoadingFallback />}>
                  <Search />
                </Suspense>
              </ErrorBoundary>
            } />
            <Route path="recommendations" element={
              <ErrorBoundary fallback={<PlaceholderPage title="Recommendations" description="This page encountered an error. We're working on it!" />}>
                <Suspense fallback={<LoadingFallback />}>
                  <Recommendations />
                </Suspense>
              </ErrorBoundary>
            } />
            <Route path="annotations" element={
              <ErrorBoundary fallback={<PlaceholderPage title="Annotations" description="This page encountered an error. We're working on it!" />}>
                <Suspense fallback={<LoadingFallback />}>
                  <Annotations />
                </Suspense>
              </ErrorBoundary>
            } />
            <Route path="graph" element={
              <ErrorBoundary fallback={<PlaceholderPage title="Knowledge Graph" description="This page encountered an error. We're working on it!" />}>
                <Suspense fallback={<LoadingFallback />}>
                  <Graph />
                </Suspense>
              </ErrorBoundary>
            } />
            <Route path="quality" element={
              <ErrorBoundary fallback={<PlaceholderPage title="Quality" description="This page encountered an error. We're working on it!" />}>
                <Suspense fallback={<LoadingFallback />}>
                  <Quality />
                </Suspense>
              </ErrorBoundary>
            } />
            <Route path="taxonomy" element={
              <ErrorBoundary fallback={<PlaceholderPage title="Taxonomy" description="This page encountered an error. We're working on it!" />}>
                <Suspense fallback={<LoadingFallback />}>
                  <Taxonomy />
                </Suspense>
              </ErrorBoundary>
            } />
            <Route path="monitoring" element={
              <ErrorBoundary fallback={<PlaceholderPage title="Monitoring" description="This page encountered an error. We're working on it!" />}>
                <Suspense fallback={<LoadingFallback />}>
                  <Monitoring />
                </Suspense>
              </ErrorBoundary>
            } />
          </Route>
        </Routes>
      </BrowserRouter>
      <CommandPalette />
      <ToastContainer />
    </>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <AppContent />
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
