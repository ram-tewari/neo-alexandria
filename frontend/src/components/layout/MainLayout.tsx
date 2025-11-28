import { Outlet } from 'react-router-dom';
import { Home, Library, Network, Search, Sparkles, Highlighter, BarChart3, FolderTree, Activity } from 'lucide-react';
import { Navbar } from './Navbar';
import { Sidebar, SidebarItem } from './Sidebar';
import { Footer } from './Footer';
import { useNavigationStore } from '../../store/navigationStore';
import './MainLayout.css';

const sidebarItems: SidebarItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: <Home size={20} />,
    href: '/',
  },
  {
    id: 'library',
    label: 'Library',
    icon: <Library size={20} />,
    href: '/library',
  },
  {
    id: 'search',
    label: 'Search',
    icon: <Search size={20} />,
    href: '/search',
  },
  {
    id: 'recommendations',
    label: 'For You',
    icon: <Sparkles size={20} />,
    href: '/recommendations',
  },
  {
    id: 'annotations',
    label: 'Annotations',
    icon: <Highlighter size={20} />,
    href: '/annotations',
  },
  {
    id: 'graph',
    label: 'Knowledge Graph',
    icon: <Network size={20} />,
    href: '/graph',
  },
  {
    id: 'quality',
    label: 'Quality',
    icon: <BarChart3 size={20} />,
    href: '/quality',
  },
  {
    id: 'taxonomy',
    label: 'Taxonomy',
    icon: <FolderTree size={20} />,
    href: '/taxonomy',
  },
  {
    id: 'monitoring',
    label: 'Monitoring',
    icon: <Activity size={20} />,
    href: '/monitoring',
  },
];

export const MainLayout = () => {
  const { sidebarOpen } = useNavigationStore();

  return (
    <div className="app">
      <Navbar />
      <div className="app-container">
        <Sidebar items={sidebarItems} />
        <main className={`main-content ${sidebarOpen ? 'sidebar-open' : ''}`}>
          <Outlet />
        </main>
      </div>
      <Footer
        links={[
          { label: 'About', href: '/about' },
          { label: 'Privacy', href: '/privacy' },
          { label: 'Terms', href: '/terms' },
          { label: 'GitHub', href: 'https://github.com', external: true },
        ]}
      />
    </div>
  );
};
