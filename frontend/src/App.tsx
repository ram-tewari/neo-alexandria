import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './contexts/ThemeContext';
import { MainLayout } from './components/layout/MainLayout';
import { Home } from './pages/Home';
import { Library } from './pages/Library';
import { Search } from './pages/Search';
import { Recommendations } from './pages/Recommendations';
import { Annotations } from './pages/Annotations';
import { Graph } from './pages/Graph';
import { Quality } from './pages/Quality';
import { Taxonomy } from './pages/Taxonomy';
import { Monitoring } from './pages/Monitoring';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { ToastContainer } from './components/common/Toast';
import { CommandPalette } from './components/layout/CommandPalette';
import { useCommandPalette } from './hooks/useKeyboard';
import { useCommandStore } from './store/commandStore';
import './styles/globals.css';
import './styles/dual-theme.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function AppContent() {
  const { togglePalette } = useCommandStore();
  useCommandPalette(togglePalette);

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Home />} />
            <Route path="library" element={<Library />} />
            <Route path="search" element={<Search />} />
            <Route path="recommendations" element={<Recommendations />} />
            <Route path="annotations" element={<Annotations />} />
            <Route path="graph" element={<Graph />} />
            <Route path="quality" element={<Quality />} />
            <Route path="taxonomy" element={<Taxonomy />} />
            <Route path="monitoring" element={<Monitoring />} />
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
