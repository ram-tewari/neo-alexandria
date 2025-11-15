import { Outlet } from 'react-router-dom';
import { AnimatedOrbs } from '../background/AnimatedOrbs';
import { GridPattern } from '../background/GridPattern';
import { Navbar } from './Navbar';
import { AppSidebar } from './AppSidebar';
import { SidebarProvider, SidebarTrigger } from '../ui/sidebar';
import './MainLayout.css';

export const MainLayout = () => {
  return (
    <SidebarProvider defaultOpen={true}>
      <div className="app">
        <AnimatedOrbs />
        <GridPattern />
        <Navbar />
        <div className="app-container">
          <AppSidebar />
          <main className="main-content">
            <div className="main-content-header">
              <SidebarTrigger />
            </div>
            <Outlet />
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
};
