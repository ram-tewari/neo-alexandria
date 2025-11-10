// Neo Alexandria 2.0 Frontend - Main App Component
// Application root with routing, providers, and global components

import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AppLayout } from '@/components/layout/AppLayout';
import { NotificationProvider } from '@/components/ui/NotificationProvider';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { ToastContainer } from '@/components/ui/Toast';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { queryClient } from '@/services/api/queryClient';

// Lazy load pages for code splitting
const HomePage = lazy(() => import('@/pages/HomePage').then(m => ({ default: m.HomePage })));
const LibraryPage = lazy(() => import('@/pages/LibraryPage').then(m => ({ default: m.LibraryPage })));
const AddResource = lazy(() => import('@/pages/AddResource').then(m => ({ default: m.AddResource })));
const SearchPage = lazy(() => import('@/pages/SearchPage').then(m => ({ default: m.SearchPage })));
const ResourceDetail = lazy(() => import('@/pages/ResourceDetail').then(m => ({ default: m.ResourceDetail })));
const Recommendations = lazy(() => import('@/pages/Recommendations').then(m => ({ default: m.Recommendations })));
const KnowledgeGraph = lazy(() => import('@/pages/KnowledgeGraph').then(m => ({ default: m.KnowledgeGraph })));
const KnowledgeMap = lazy(() => import('@/pages/KnowledgeMap').then(m => ({ default: m.KnowledgeMap })));
const ClassificationPage = lazy(() => import('@/pages/ClassificationPage').then(m => ({ default: m.ClassificationPage })));
const CollectionsPage = lazy(() => import('@/pages/CollectionsPage').then(m => ({ default: m.CollectionsPage })));
const CollectionDetailPage = lazy(() => import('@/pages/CollectionDetailPage').then(m => ({ default: m.CollectionDetailPage })));
const ProfilePage = lazy(() => import('@/pages/ProfilePage').then(m => ({ default: m.ProfilePage })));
const Curation = lazy(() => import('@/pages/Curation').then(m => ({ default: m.Curation })));
const Settings = lazy(() => import('@/pages/Settings').then(m => ({ default: m.Settings })));
const NotFound = lazy(() => import('@/pages/NotFound').then(m => ({ default: m.NotFound })));

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <NotificationProvider>
            <AppLayout>
              <Routes>
                {/* Home */}
                <Route path="/" element={<HomePage />} />
                
                {/* Library */}
                <Route path="/library" element={<LibraryPage />} />
                
                {/* Resource Management */}
                <Route path="/add" element={<AddResource />} />
                <Route path="/resources/:id" element={<ResourceDetail />} />
                <Route path="/resources/:id/edit" element={<ResourceDetail edit />} />
                
                {/* Search and Discovery */}
                <Route path="/search" element={<SearchPage />} />
                <Route path="/recommendations" element={<Recommendations />} />
                
                {/* Knowledge Graph */}
                <Route path="/graph" element={<KnowledgeGraph />} />
                <Route path="/graph/:id" element={<KnowledgeGraph />} />
                
                {/* Knowledge Map */}
                <Route path="/map" element={<KnowledgeMap />} />
                
                {/* Classification */}
                <Route path="/classification" element={<ClassificationPage />} />
                
                {/* Collections */}
                <Route path="/collections" element={<CollectionsPage />} />
                <Route path="/collections/:id" element={<CollectionDetailPage />} />
                
                {/* Profile */}
                <Route path="/profile" element={<ProfilePage />} />
                
                {/* Curation */}
                <Route path="/curation" element={<Curation />} />
                <Route path="/curation/review" element={<Curation view="review" />} />
                <Route path="/curation/quality" element={<Curation view="quality" />} />
                
                {/* Settings */}
                <Route path="/settings" element={<Settings />} />
                
                {/* 404 */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </AppLayout>
          </NotificationProvider>
          
          {/* Toast Notifications */}
          <ToastContainer />
        </Router>
        
        {/* React Query DevTools - only in development */}
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
