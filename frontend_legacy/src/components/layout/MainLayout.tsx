import { Outlet } from 'react-router-dom';
import { AnimatedOrbs } from '../background/AnimatedOrbs';
import { GridPattern } from '../background/GridPattern';
import { MarbleBackdrop } from '../background/MarbleBackdrop';
import { Navbar } from './Navbar';
import { AppSidebar } from './AppSidebar';
import { SidebarProvider, SidebarTrigger } from '../ui/sidebar';
import { SkipToContent } from '../ui/SkipToContent';
import { ThemeToggle } from '../ui/ThemeToggle';
import { ScrollToTop } from '../common/ScrollToTop';
import './MainLayout.css';

export const MainLayout = () => {
  return (
    <SidebarProvider defaultOpen={true}>
      <SkipToContent />
      <div className="app">
        <MarbleBackdrop />
        <AnimatedOrbs />
        <GridPattern />
        <Navbar />
        <div className="app-container">
          <AppSidebar />
          <main className="main-content" id="main-content">
            <div className="main-content-header">
              <SidebarTrigger />
              <div className="ml-auto">
                <ThemeToggle />
              </div>
            </div>
            <Outlet />
          </main>
        </div>
        <ScrollToTop />
      </div>
    </SidebarProvider>
  );
};
