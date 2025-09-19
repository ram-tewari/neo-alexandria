// Neo Alexandria 2.0 Frontend - Main Layout Component
// Primary application layout with sidebar, header, and main content area

import React from 'react';
import { cn } from '@/utils/cn';
import { useAppStore } from '@/store';
import { 
  Menu, 
  X, 
  Library, 
  Search, 
  Lightbulb, 
  Network, 
  Settings,
  Plus,
  BookOpen,
  Users,
  Map
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { NavLink, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

interface SidebarNavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
  badge?: string;
  active?: boolean;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const sidebarOpen = useAppStore(state => state.sidebarOpen);
  const processingResources = useAppStore(state => state.processingResources);
  const toggleSidebar = useAppStore(state => state.toggleSidebar);
  const setSidebarOpen = useAppStore(state => state.setSidebarOpen);

  const activeProcessingCount = processingResources.filter(
    r => r.status === 'pending' || r.status === 'processing'
  ).length;

  const navigationItems: SidebarNavItem[] = [
    {
      label: 'Library',
      href: '/',
      icon: <Library className="w-5 h-5" />,
      active: location.pathname === '/',
    },
    {
      label: 'Search',
      href: '/search',
      icon: <Search className="w-5 h-5" />,
      active: location.pathname === '/search',
    },
    {
      label: 'Recommendations',
      href: '/recommendations',
      icon: <Lightbulb className="w-5 h-5" />,
      active: location.pathname === '/recommendations',
    },
    {
      label: 'Knowledge Graph',
      href: '/graph',
      icon: <Network className="w-5 h-5" />,
      active: location.pathname === '/graph',
    },
    {
      label: 'Knowledge Map',
      href: '/map',
      icon: <Map className="w-5 h-5" />,
      active: location.pathname === '/map',
    },
    {
      label: 'Curation',
      href: '/curation',
      icon: <BookOpen className="w-5 h-5" />,
      active: location.pathname.startsWith('/curation'),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      {/* Sidebar */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 border-r border-gray-200 bg-white transition-transform duration-300',
          sidebarOpen ? 'transform-none' : '-translate-x-full',
          'lg:relative lg:transform-none'
        )}
      >
        {/* Sidebar Header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-gray-200 bg-white">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Library className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                Neo Alexandria
              </h1>
              <p className="text-xs text-gray-500">Knowledge Library</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebar}
            className="lg:hidden"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Add Resource Button */}
        <div className="p-4">
          <Button
            variant="primary"
            fullWidth
            icon={<Plus className="w-4 h-4" />}
            onClick={() => {
              // Navigate to add resource or open modal
              window.location.href = '/add';
            }}
          >
            Add Resource
          </Button>
        </div>

        {/* Navigation */}
        <nav className="px-2 space-y-1">
          {navigationItems.map((item) => (
            <NavLink
              key={item.href}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                  isActive || item.active
                    ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                )
              }
              onClick={() => setSidebarOpen(false)} // Close sidebar on mobile
            >
              <span className="mr-3">{item.icon}</span>
              {item.label}
              {item.badge && (
                <Badge variant="info" size="sm" className="ml-auto">
                  {item.badge}
                </Badge>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Processing Status */}
        {activeProcessingCount > 0 && (
          <div className="p-4 mt-4 border-t border-gray-200">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse mr-2" />
                <span className="text-sm text-blue-700 font-medium">
                  Processing {activeProcessingCount} resource{activeProcessingCount === 1 ? '' : 's'}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Settings */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white">
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              cn(
                'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 w-full',
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              )
            }
          >
            <Settings className="w-5 h-5 mr-3" />
            Settings
          </NavLink>
        </div>
      </div>

      {/* Main Content */}
      <div className={cn('relative z-10 lg:ml-64', sidebarOpen && 'lg:ml-64')}>
        {/* Top Header */}
        <header className="border-b border-gray-200 px-4 py-3 lg:px-6 bg-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleSidebar}
                className="lg:hidden"
              >
                <Menu className="w-5 h-5" />
              </Button>
              
              {/* Breadcrumbs or page title could go here */}
              <div className="hidden lg:block">
                {/* This could be enhanced with dynamic breadcrumbs */}
              </div>
            </div>

            {/* Header actions */}
            <div className="flex items-center space-x-2">
              {/* Future: User menu, notifications, etc. */}
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="p-4 lg:p-6">
          {children}
        </main>
      </div>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export { Layout };
