import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useScrollPosition } from '../../hooks/useScrollPosition';
import { useSidebar } from '../ui/sidebar';
import { ModeToggle } from '../theme/ModeToggle';
import { Icon } from '../common/Icon';
import { icons } from '../../config/icons';
import type { NavLink } from '../../types';
import './Navbar.css';

const navLinks: NavLink[] = [
  { path: '/', label: 'Dashboard' },
  { path: '/library', label: 'Library' },
  { path: '/collections', label: 'Collections' },
  { path: '/graph', label: 'Knowledge Graph' },
];

export const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const scrolled = useScrollPosition();
  const { toggleSidebar } = useSidebar();

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`} aria-label="Main navigation">
      <div className="navbar-glass">
        <div className="nav-content">
          <motion.button
            className="mobile-menu-toggle"
            onClick={toggleSidebar}
            aria-label="Toggle menu"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <Icon icon={icons.menu} size={20} />
          </motion.button>

          <motion.div
            className="nav-logo"
            onClick={() => navigate('/')}
            whileHover={{ scale: 1.02 }}
            style={{ cursor: 'pointer' }}
          >
            <div className="logo-icon">
              <Icon icon={icons.brain} size={20} />
            </div>
            <span className="logo-text">Neo Alexandria</span>
          </motion.div>

          <div className="nav-links">
            {navLinks.map((link) => (
              <motion.a
                key={link.path}
                href="#"
                className={`nav-link ${location.pathname === link.path ? 'active' : ''}`}
                aria-current={location.pathname === link.path ? 'page' : undefined}
                onClick={(e) => {
                  e.preventDefault();
                  navigate(link.path);
                }}
                whileHover={{ y: -2 }}
                transition={{ duration: 0.2 }}
              >
                {link.label}
              </motion.a>
            ))}
          </div>

          <div className="nav-actions">
            <ModeToggle />
            <motion.button
              className="notification-btn"
              aria-label="Notifications"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              <Icon icon={icons.notification} size={20} />
              <span className="notification-badge">3</span>
            </motion.button>
            <motion.div
              className="user-avatar"
              whileHover={{ scale: 1.1 }}
            >
              <img src="https://i.pravatar.cc/100?img=12" alt="User" />
            </motion.div>
          </div>
        </div>
      </div>
    </nav>
  );
};
