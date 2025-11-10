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
      {/* Transparent Navbar */}
      <TransparentNavbar />
      
      {/* Main Content Area */}
      <main className="flex-1">
        <Suspense 
          fallback={
            <div className="flex items-center justify-center min-h-[60vh]">
              <LoadingSpinner size="lg" />
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
