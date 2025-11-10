// Neo Alexandria 2.0 Frontend - AppLayout Component
// Main application layout with routing structure and nested routes

import React, { Suspense } from 'react';
import { Outlet } from 'react-router-dom';
import { TransparentNavbar } from './TransparentNavbar';
import { Footer } from './Footer';
import { PageTransition } from './PageTransition';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

interface AppLayoutProps {
  children?: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-charcoal-grey-900 text-charcoal-grey-50 flex flex-col">
      {/* Skip Links for Accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-accent-blue-500 focus:text-white focus:rounded-lg focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-accent-blue-400 focus:ring-offset-2 focus:ring-offset-charcoal-grey-900"
      >
        Skip to main content
      </a>
      <a
        href="#navigation"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-40 focus:z-[100] focus:px-4 focus:py-2 focus:bg-accent-blue-500 focus:text-white focus:rounded-lg focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-accent-blue-400 focus:ring-offset-2 focus:ring-offset-charcoal-grey-900"
      >
        Skip to navigation
      </a>
      
      {/* Transparent Navbar */}
      <TransparentNavbar />
      
      {/* Main Content Area */}
      <main id="main-content" className="flex-1" role="main">
        <Suspense 
          fallback={
            <div className="flex items-center justify-center min-h-[60vh]" role="status" aria-live="polite">
              <LoadingSpinner size="lg" />
              <span className="sr-only">Loading page content...</span>
            </div>
          }
        >
          <PageTransition>
            {children || <Outlet />}
          </PageTransition>
        </Suspense>
      </main>
      
      {/* Footer */}
      <Footer />
    </div>
  );
};

export { AppLayout };
