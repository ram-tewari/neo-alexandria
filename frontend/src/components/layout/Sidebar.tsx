import { useNavigate, useLocation } from 'react-router-dom';
import { useNavigationStore } from '../../store/navigationStore';
import { useIsMobile } from '../../hooks/useMediaQuery';
import type { SidebarItem } from '../../types';
import './Sidebar.css';

const mainItems: SidebarItem[] = [
  { icon: 'fas fa-home', label: 'Dashboard', path: '/' },
  { icon: 'fas fa-book', label: 'Library', path: '/library' },
  { icon: 'fas fa-search', label: 'Search', path: '/search' },
  { icon: 'fas fa-project-diagram', label: 'Knowledge Graph', path: '/graph' },
];

const collections: SidebarItem[] = [
  { icon: 'fas fa-star', label: 'Favorites', path: '/favorites' },
  { icon: 'fas fa-clock', label: 'Recent', path: '/recent' },
  { icon: 'fas fa-bookmark', label: 'Read Later', path: '/read-later' },
];

export const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarOpen, toggleSidebar } = useNavigationStore();
  const isMobile = useIsMobile();

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      toggleSidebar();
    }
  };

  return (
    <>
      {isMobile && sidebarOpen && (
        <div className="sidebar-overlay" onClick={toggleSidebar} aria-hidden="true"></div>
      )}
      <aside className={`sidebar ${isMobile && sidebarOpen ? 'open' : ''}`} aria-label="Sidebar navigation">
        <div className="sidebar-glass">
        <div className="sidebar-section">
          <div className="sidebar-title">Main</div>
          {mainItems.map((item) => (
            <a
              key={item.path}
              href="#"
              className={`sidebar-item ${location.pathname === item.path ? 'active' : ''}`}
              aria-current={location.pathname === item.path ? 'page' : undefined}
              onClick={(e) => {
                e.preventDefault();
                handleNavigation(item.path);
              }}
            >
              <i className={item.icon} aria-hidden="true"></i>
              <span>{item.label}</span>
            </a>
          ))}
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Collections</div>
          {collections.map((item) => (
            <a
              key={item.path}
              href="#"
              className={`sidebar-item ${location.pathname === item.path ? 'active' : ''}`}
              aria-current={location.pathname === item.path ? 'page' : undefined}
              onClick={(e) => {
                e.preventDefault();
                handleNavigation(item.path);
              }}
            >
              <i className={item.icon} aria-hidden="true"></i>
              <span>{item.label}</span>
            </a>
          ))}
        </div>
      </div>
    </aside>
    </>
  );
};
