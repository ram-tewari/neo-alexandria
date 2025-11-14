import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { FAB } from './components/layout/FAB';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import './styles/globals.css';

// Lazy load page components
const Dashboard = lazy(() => import('./components/pages/Dashboard').then(module => ({ default: module.Dashboard })));
const Library = lazy(() => import('./components/pages/Library').then(module => ({ default: module.Library })));
const KnowledgeGraph = lazy(() => import('./components/pages/KnowledgeGraph').then(module => ({ default: module.KnowledgeGraph })));

function App() {
  return (
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
            <Route index element={<Dashboard />} />
            <Route path="library" element={<Library />} />
            <Route path="graph" element={<KnowledgeGraph />} />
          </Route>
        </Routes>
        <FAB />
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
