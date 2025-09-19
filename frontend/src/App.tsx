// Neo Alexandria 2.0 Frontend - Main App Component
// Application root with routing, providers, and global components

import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Layout } from '@/components/layout/Layout';
import { NotificationProvider } from '@/components/ui/NotificationProvider';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';

// Pages
import { Library } from '@/pages/Library';
import { AddResource } from '@/pages/AddResource';
import { Search } from '@/pages/Search';
import { ResourceDetail } from '@/pages/ResourceDetail';
import { Recommendations } from '@/pages/Recommendations';
import { KnowledgeGraph } from '@/pages/KnowledgeGraph';
import { KnowledgeMap } from '@/pages/KnowledgeMap';
import { Curation } from '@/pages/Curation';
import { Settings } from '@/pages/Settings';
import { NotFound } from '@/pages/NotFound';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

const RouteFade: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  return (
    <div key={location.pathname} className="animate-appear">
      {children}
    </div>
  );
};

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <NotificationProvider>
            <Layout>
              <RouteFade>
              <Routes>
                {/* Main Library */}
                <Route path="/" element={<Library />} />
                
                {/* Resource Management */}
                <Route path="/add" element={<AddResource />} />
                <Route path="/resource/:id" element={<ResourceDetail />} />
                <Route path="/resource/:id/edit" element={<ResourceDetail edit />} />
                
                {/* Search and Discovery */}
                <Route path="/search" element={<Search />} />
                <Route path="/recommendations" element={<Recommendations />} />
                
                {/* Knowledge Graph */}
                <Route path="/graph" element={<KnowledgeGraph />} />
                <Route path="/graph/:id" element={<KnowledgeGraph />} />
                
                {/* Knowledge Map */}
                <Route path="/map" element={<KnowledgeMap />} />
                
                {/* Curation */}
                <Route path="/curation" element={<Curation />} />
                <Route path="/curation/review" element={<Curation view="review" />} />
                <Route path="/curation/quality" element={<Curation view="quality" />} />
                
                {/* Settings */}
                <Route path="/settings" element={<Settings />} />
                
                {/* 404 */}
                <Route path="*" element={<NotFound />} />
              </Routes>
              </RouteFade>
            </Layout>
          </NotificationProvider>
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
