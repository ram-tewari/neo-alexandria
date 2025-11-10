// Neo Alexandria 2.0 Frontend - TransparentNavbar Component
// Adaptive navigation bar with scroll detection and mobile menu

import React, { useState, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { cn } from '@/utils/cn';
import { Menu, X } from 'lucide-react';

const TransparentNavbar: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [navigate]);

  const navigationItems = [
    { label: 'Home', href: '/' },
    { label: 'Library', href: '/library' },
    { label: 'Search', href: '/search' },
    { label: 'Recommendations', href: '/recommendations' },
    { label: 'Knowledge Graph', href: '/graph' },
    { label: 'Classification', href: '/classification' },
    { label: 'Collections', href: '/collections' },
    { label: 'Profile', href: '/profile' },
  ];

  return (
    <>
      <nav
        id="navigation"
        role="navigation"
        aria-label="Main navigation"
        className="fixed top-0 left-0 right-0 z-50 bg-black border-b border-zinc-900"
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center h-12">
            {/* Logo */}
            <Link 
              to="/" 
              className="flex items-center gap-2 mr-8 group"
              aria-label="Neo Alexandria home"
            >
              <div className="text-xs font-semibold text-zinc-100 tracking-wide">
                NA
              </div>
              <div className="hidden sm:block text-xs font-medium text-zinc-400 group-hover:text-zinc-100 transition-colors">
                Neo Alexandria
              </div>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-1 flex-1" role="menubar">
              {navigationItems.map((item) => {
                return (
                  <NavLink
                    key={item.href}
                    to={item.href}
                    role="menuitem"
                    aria-label={`Navigate to ${item.label}`}
                    className={({ isActive }) =>
                      cn(
                        'px-3 py-1.5 rounded text-xs font-medium transition-colors',
                        'focus-visible:ring-2 focus-visible:ring-accent-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-black',
                        isActive
                          ? 'bg-accent-blue-500/10 text-accent-blue-400 border border-accent-blue-500/20'
                          : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 border border-transparent'
                      )
                    }
                  >
                    {item.label}
                  </NavLink>
                );
              })}
            </div>

            {/* Mobile Menu Button - Touch-friendly 44x44px */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden min-w-[44px] min-h-[44px] flex items-center justify-center rounded text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 transition-colors ml-auto"
              aria-label="Toggle mobile menu"
              aria-expanded={isMobileMenuOpen}
            >
              {isMobileMenuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
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
            'absolute top-14 right-0 bottom-0 w-72 sm:w-80 bg-black border-l border-zinc-900 shadow-2xl transition-transform duration-300 ease-out',
            isMobileMenuOpen ? 'translate-x-0' : 'translate-x-full'
          )}
        >
          <div className="flex flex-col h-full overflow-y-auto">
            {/* Close button at top */}
            <div className="flex items-center justify-between p-4 border-b border-zinc-900">
              <h2 className="text-sm font-medium text-zinc-100">Menu</h2>
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="min-w-[44px] min-h-[44px] flex items-center justify-center rounded text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 transition-colors"
                aria-label="Close menu"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Navigation items with touch-friendly spacing */}
            <nav className="flex flex-col p-3 space-y-0.5" role="menu" aria-label="Mobile navigation menu">
              {navigationItems.map((item) => {
                return (
                  <NavLink
                    key={item.href}
                    to={item.href}
                    role="menuitem"
                    aria-label={`Navigate to ${item.label}`}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center min-h-[44px] px-3 py-2.5 rounded text-sm font-medium transition-colors',
                        'focus-visible:ring-2 focus-visible:ring-accent-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-black',
                        isActive
                          ? 'bg-accent-blue-500/10 text-accent-blue-400 border border-accent-blue-500/20'
                          : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 border border-transparent'
                      )
                    }
                  >
                    {item.label}
                  </NavLink>
                );
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* Spacer to prevent content from going under fixed navbar */}
      <div className="h-12" />
    </>
  );
};

export { TransparentNavbar };
