import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { MainLayout } from './components/layout/MainLayout';
import { FAB } from './components/layout/FAB';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import { CommandPalette } from './components/common/CommandPalette';
import { KeyboardShortcutIndicator } from './components/ui/KeyboardShortcutIndicator';
import { ThemeProvider } from './components/theme/ThemeProvider';
import { ToastProvider } from './contexts/ToastContext';
import { ToastContainer } from './components/ui/Toast';
import { FeatureErrorBoundary } from './components/common/FeatureErrorBoundary';
import { useCommandPalette } from './hooks/useCommandPalette';
import { queryClient } from './lib/query/queryClient';
import './styles/globals.css';

// Lazy load page components
const Dashboard = lazy(() => import('./components/pages/Dashboard').then(module => ({ default: module.Dashboard })));
const Library = lazy(() => import('./components/pages/Library').then(module => ({ default: module.Library })));
const KnowledgeGraph = lazy(() => import('./components/pages/KnowledgeGraph').then(module => ({ default: module.KnowledgeGraph })));
const ResourceDetailPage = lazy(() => import('./components/features/resource-detail/ResourceDetailPage').then(module => ({ default: module.ResourceDetailPage })));
const SearchStudioPage = lazy(() => import('./components/features/search/studio/SearchStudioPage').then(module => ({ default: module.SearchStudioPage })));
const ProfilePage = lazy(() => import('./components/features/profile/ProfilePage').then(module => ({ default: module.ProfilePage })));
const Collections = lazy(() => import('./components/pages/Collections').then(module => ({ default: module.Collections })));
const CollectionDetailPage = lazy(() => import('./components/features/collections/detail/CollectionDetailPage').then(module => ({ default: module.CollectionDetailPage })));
const AnnotationNotebookPage = lazy(() => import('./components/features/annotations/notebook/AnnotationNotebookPage').then(module => ({ default: module.AnnotationNotebookPage })));

function App() {
  // Initialize command palette keyboard shortcut
  useCommandPalette();

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <ToastProvider>
          <BrowserRouter>
            <Suspense fallback={
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '100vh',
                background: 'var(--primary-black)'
              }}>
                <LoadingSpinner size="lg" />
              </div>
            }>
              <Routes>
                <Route path="/" element={<MainLayout />}>
                  <Route index element={
                    <FeatureErrorBoundary featureName="Dashboard">
                      <Dashboard />
                    </FeatureErrorBoundary>
                  } />
                  <Route path="library" element={
                    <FeatureErrorBoundary featureName="Library">
                      <Library />
                    </FeatureErrorBoundary>
                  } />
                  <Route path="graph" element={
                    <FeatureErrorBoundary featureName="Knowledge Graph">
                      <KnowledgeGraph />
                    </FeatureErrorBoundary>
                  } />
                  <Route path="resources/:id" element={
                    <FeatureErrorBoundary featureName="Resource Detail">
                      <ResourceDetailPage />
                    </FeatureErrorBoundary>
                  } />
                  <Route path="search/studio" element={
                    <FeatureErrorBoundary featureName="Search Studio">
                      <SearchStudioPage />
                    </FeatureErrorBoundary>
                  } />
                  <Route path="profile" element={
                    <FeatureErrorBoundary featureName="Profile">
                      <ProfilePage />
                    </FeatureErrorBoundary>
                  } />
                  <Route path="collections" element={
                    <FeatureErrorBoundary featureName="Collections">
                      <Collections />
                    </FeatureErrorBoundary>
                  } />
                  <Route path="collections/:id" element={
                    <FeatureErrorBoundary featureName="Collection Detail">
                      <CollectionDetailPage />
                    </FeatureErrorBoundary>
                  } />
                  <Route path="annotations" element={
                    <FeatureErrorBoundary featureName="Annotations">
                      <AnnotationNotebookPage />
                    </FeatureErrorBoundary>
                  } />
                </Route>
              </Routes>
              <FAB />
              <CommandPalette />
              <KeyboardShortcutIndicator shortcut="Ctrl+B" maxUses={3} />
            </Suspense>
            <ToastContainer />
          </BrowserRouter>
        </ToastProvider>
      </ThemeProvider>
      {/* React Query DevTools - only in development */}
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}

export default App;
