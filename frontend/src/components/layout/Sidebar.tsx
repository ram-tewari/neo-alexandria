import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useNavigationStore } from '../../store/navigationStore';
import { useUIStore } from '../../store';
import { useIsMobile } from '../../hooks/useMediaQuery';
import { sidebarItemVariants } from '../../animations/variants';
import { Icon } from '../common/Icon';
import { icons } from '../../config/icons';
import type { SidebarItem } from '../../types';
import './Sidebar.css';

const mainItems: SidebarItem[] = [
  { iconName: 'dashboard', label: 'Dashboard', path: '/' },
  { iconName: 'library', label: 'Library', path: '/library' },
  { iconName: 'graph', label: 'Knowledge Graph', path: '/graph' },
];

const collections: SidebarItem[] = [
  { iconName: 'favorites', label: 'Favorites', path: '/favorites' },
  { iconName: 'recent', label: 'Recent', path: '/recent' },
  { iconName: 'readLater', label: 'Read Later', path: '/read-later' },
];

export const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarOpen, toggleSidebar } = useNavigationStore();
  const { openCommandPalette } = useUIStore();
  const isMobile = useIsMobile();

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      toggleSidebar();
    }
  };

  const handleSearchClick = () => {
    openCommandPalette();
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
        {/* Search Button */}
        <div className="sidebar-search">
          <motion.button
            className="sidebar-search-button"
            onClick={handleSearchClick}
            variants={sidebarItemVariants}
            initial="rest"
            whileHover="hover"
            aria-label="Open search"
          >
            <motion.div 
              className="sidebar-item-glow"
              initial={{ opacity: 0 }}
              whileHover={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            />
            <Icon icon={icons.search} size={20} />
            <span>Search</span>
            <kbd className="sidebar-search-kbd">⌘K</kbd>
          </motion.button>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Main</div>
          {mainItems.map((item) => {
            const IconComponent = icons[item.iconName];
            const isActive = location.pathname === item.path;
            
            return (
              <motion.a
                key={item.path}
                href="#"
                className={`sidebar-item ${isActive ? 'active' : ''}`}
                aria-current={isActive ? 'page' : undefined}
                onClick={(e) => {
                  e.preventDefault();
                  if (item.path) handleNavigation(item.path);
                }}
                variants={sidebarItemVariants}
                initial="rest"
                whileHover="hover"
              >
                <motion.div 
                  className="sidebar-item-glow"
                  initial={{ opacity: 0 }}
                  whileHover={{ opacity: 1 }}
                  transition={{ duration: 0.3 }}
                />
                <Icon icon={IconComponent} size={20} />
                <span>{item.label}</span>
              </motion.a>
            );
          })}
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Collections</div>
          {collections.map((item) => {
            const IconComponent = icons[item.iconName];
            const isActive = location.pathname === item.path;
            
            return (
              <motion.a
                key={item.path}
                href="#"
                className={`sidebar-item ${isActive ? 'active' : ''}`}
                aria-current={isActive ? 'page' : undefined}
                onClick={(e) => {
                  e.preventDefault();
                  if (item.path) handleNavigation(item.path);
                }}
                variants={sidebarItemVariants}
                initial="rest"
                whileHover="hover"
              >
                <motion.div 
                  className="sidebar-item-glow"
                  initial={{ opacity: 0 }}
                  whileHover={{ opacity: 1 }}
                  transition={{ duration: 0.3 }}
                />
                <Icon icon={IconComponent} size={20} />
                <span>{item.label}</span>
              </motion.a>
            );
          })}
        </div>
      </div>
    </aside>
    </>
  );
};
