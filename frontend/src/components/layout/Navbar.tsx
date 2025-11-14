import { useNavigate, useLocation } from 'react-router-dom';
import { useScrollPosition } from '../../hooks/useScrollPosition';
import { useNavigationStore } from '../../store/navigationStore';
import type { NavLink } from '../../types';
import './Navbar.css';

const navLinks: NavLink[] = [
  { path: '/', label: 'Dashboard' },
  { path: '/library', label: 'Library' },
  { path: '/graph', label: 'Knowledge Graph' },
];

export const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const scrolled = useScrollPosition();
  const { toggleSidebar } = useNavigationStore();

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`} aria-label="Main navigation">
      <div className="navbar-glass">
        <div className="nav-content">
          <button 
            className="mobile-menu-toggle"
            onClick={toggleSidebar}
            aria-label="Toggle menu"
          >
            <i className="fas fa-bars"></i>
          </button>

          <div className="nav-logo" onClick={() => navigate('/')}>
            <div className="logo-icon">
              <i className="fas fa-brain" style={{ color: 'white' }}></i>
            </div>
            <span className="logo-text">Neo Alexandria</span>
          </div>

          <div className="nav-links">
            {navLinks.map((link) => (
              <a
                key={link.path}
                href="#"
                className={`nav-link ${location.pathname === link.path ? 'active' : ''}`}
                aria-current={location.pathname === link.path ? 'page' : undefined}
                onClick={(e) => {
                  e.preventDefault();
                  navigate(link.path);
                }}
              >
                {link.label}
              </a>
            ))}
          </div>

          <div className="nav-actions">
            <button className="notification-btn" aria-label="Notifications">
              <i className="fas fa-bell"></i>
              <span className="notification-badge">3</span>
            </button>
            <div className="user-avatar">
              <img src="https://i.pravatar.cc/100?img=12" alt="User" />
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};
