import { useEffect } from 'react';
import { useWorkbenchStore } from '../stores/workbench';
import { WorkbenchSidebar } from './WorkbenchSidebar';
import { WorkbenchHeader } from './WorkbenchHeader';
import { motion, AnimatePresence } from 'framer-motion';

interface WorkbenchLayoutProps {
  children: React.ReactNode;
}

export function WorkbenchLayout({ children }: WorkbenchLayoutProps) {
  const { sidebarOpen, sidebarCollapsed, setSidebarOpen } = useWorkbenchStore();

  // Handle responsive behavior
  useEffect(() => {
    const handleResize = () => {
      const isMobile = window.innerWidth < 768;
      if (isMobile && sidebarOpen && !sidebarCollapsed) {
        setSidebarOpen(false);
      }
    };

    handleResize(); // Check on mount
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [sidebarOpen, sidebarCollapsed, setSidebarOpen]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      {/* Sidebar */}
      <AnimatePresence mode="wait">
        {sidebarOpen && (
          <motion.aside
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
            className={`
              fixed left-0 top-0 z-40 h-full border-r bg-card
              ${sidebarCollapsed ? 'w-16' : 'w-64'}
              transition-all duration-200
              md:relative md:z-0
            `}
          >
            <WorkbenchSidebar />
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <WorkbenchHeader />
        
        <main className="flex-1 overflow-auto">
          <div className="container mx-auto p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
