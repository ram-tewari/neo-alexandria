// Neo Alexandria 2.0 Frontend - TransparentNavbar Component
// Adaptive navigation bar with scroll detection and mobile menu

import React, { useState, useEffect, useCallback } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAppStore } from '@/store';
import { cn } from '@/utils/cn';
import { 
  Menu, 
  X, 
  Library, 
  Search, 
  Lightbulb, 
  Network, 
  FolderTree,
  FolderOpen,
  User,
  Home
} from 'lucide-react';
import { Button } from '@/components/ui/Button';

const TransparentNavbar: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  // Throttled scroll handler
  const handleScroll = useCallback(() => {
    const scrollPosition = window.scrollY;
    setIsScrolled(scrollPosition > 50);
  }, []);

  useEffect(() => {
    // Throttle scroll events
    let timeoutId: ReturnType<typeof setTimeout> | null = null;
    const throttledScroll = () => {
      if (timeoutId) return;
      timeoutId = setTimeout(() => {
        handleScroll();
        timeoutId = null;
      }, 100);
    };

    window.addEventListener('scroll', throttledScroll);
    
    // Check initial scroll position
    handleScroll();

    return () => {
      window.removeEventListener('scroll', throttledScroll);
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [handleScroll]);

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [navigate]);

  const navigationItems = [
    { label: 'Home', href: '/', icon: Home },
    { label: 'Library', href: '/library', icon: Library },
    { label: 'Search', href: '/search', icon: Search },
    { label: 'Recommendations', href: '/recommendations', icon: Lightbulb },
    { label: 'Knowledge Graph', href: '/graph', icon: Network },
    { label: 'Classification', href: '/classification', icon: FolderTree },
    { label: 'Collections', href: '/collections', icon: FolderOpen },
    { label: 'Profile', href: '/profile', icon: User },
  ];

  return (
    <>
      <nav
        className={cn(
          'fixed top-0 left-0 right-0 z-50 transition-all duration-200 ease-in-out',
          isScrolled
            ? 'bg-charcoal-grey-900/95 backdrop-blur-md shadow-lg border-b border-charcoal-grey-700'
            : 'bg-transparent'
        )}
      >
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link 
              to="/" 
              className="flex items-center space-x-2 group"
            >
              <div className="w-8 h-8 bg-accent-blue-500 rounded-lg flex items-center justify-center transition-transform duration-200 group-hover:scale-110">
                <Library className="w-5 h-5 text-white" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg font-semibold text-charcoal-grey-50">
                  Neo Alexandria
                </h1>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-1">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.href}
                    to={item.href}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150',
                        isActive
                          ? 'bg-accent-blue-500/20 text-accent-blue-400'
                          : 'text-charcoal-grey-300 hover:text-charcoal-grey-50 hover:bg-charcoal-grey-800'
                      )
                    }
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="lg:hidden p-2 rounded-lg text-charcoal-grey-300 hover:text-charcoal-grey-50 hover:bg-charcoal-grey-800 transition-colors"
              aria-label="Toggle mobile menu"
            >
              {isMobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu */}
      <div
        className={cn(
          'fixed inset-0 z-40 lg:hidden transition-opacity duration-300',
          isMobileMenuOpen
            ? 'opacity-100 pointer-events-auto'
            : 'opacity-0 pointer-events-none'
        )}
      >
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          onClick={() => setIsMobileMenuOpen(false)}
        />

        {/* Menu Panel */}
        <div
          className={cn(
            'absolute top-16 right-0 bottom-0 w-64 bg-charcoal-grey-900 border-l border-charcoal-grey-700 shadow-2xl transition-transform duration-300',
            isMobileMenuOpen ? 'translate-x-0' : 'translate-x-full'
          )}
        >
          <div className="flex flex-col h-full p-4 space-y-2 overflow-y-auto">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.href}
                  to={item.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center space-x-3 px-4 py-3 rounded-lg text-base font-medium transition-all duration-150',
                      isActive
                        ? 'bg-accent-blue-500/20 text-accent-blue-400'
                        : 'text-charcoal-grey-300 hover:text-charcoal-grey-50 hover:bg-charcoal-grey-800'
                    )
                  }
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </div>
        </div>
      </div>

      {/* Spacer to prevent content from going under fixed navbar */}
      <div className="h-16" />
    </>
  );
};

export { TransparentNavbar };
