// Neo Alexandria 2.0 Frontend - Footer Component
// Application footer with links and copyright

import React from 'react';
import { Link } from 'react-router-dom';
import { Library, Github, Mail } from 'lucide-react';
import { cn } from '@/utils/cn';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  const footerLinks = [
    {
      title: 'Product',
      links: [
        { label: 'Library', href: '/library' },
        { label: 'Search', href: '/search' },
        { label: 'Knowledge Graph', href: '/graph' },
        { label: 'Collections', href: '/collections' },
      ],
    },
    {
      title: 'Resources',
      links: [
        { label: 'Documentation', href: '#' },
        { label: 'API Reference', href: '#' },
        { label: 'Support', href: '#' },
        { label: 'Status', href: '#' },
      ],
    },
    {
      title: 'Company',
      links: [
        { label: 'About', href: '#' },
        { label: 'Blog', href: '#' },
        { label: 'Privacy', href: '#' },
        { label: 'Terms', href: '#' },
      ],
    },
  ];

  return (
    <footer className="bg-charcoal-grey-900 border-t border-charcoal-grey-800 mt-auto">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-accent-blue-500 rounded-lg flex items-center justify-center">
                <Library className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-charcoal-grey-50">
                Neo Alexandria
              </h3>
            </div>
            <p className="text-charcoal-grey-400 text-sm mb-4 max-w-sm">
              A futuristic knowledge management system for researchers in Humanities and STEM fields.
            </p>
            <div className="flex items-center space-x-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-charcoal-grey-400 hover:text-accent-blue-400 transition-colors"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="mailto:contact@neoalexandria.com"
                className="text-charcoal-grey-400 hover:text-accent-blue-400 transition-colors"
                aria-label="Email"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Link Sections */}
          {footerLinks.map((section) => (
            <div key={section.title}>
              <h4 className="text-sm font-semibold text-charcoal-grey-50 mb-4">
                {section.title}
              </h4>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.label}>
                    {link.href.startsWith('#') ? (
                      <a
                        href={link.href}
                        className="text-sm text-charcoal-grey-400 hover:text-accent-blue-400 transition-colors"
                      >
                        {link.label}
                      </a>
                    ) : (
                      <Link
                        to={link.href}
                        className="text-sm text-charcoal-grey-400 hover:text-accent-blue-400 transition-colors"
                      >
                        {link.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-charcoal-grey-800">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <p className="text-sm text-charcoal-grey-400">
              © {currentYear} Neo Alexandria. All rights reserved.
            </p>
            <div className="flex items-center space-x-6">
              <a
                href="#"
                className="text-sm text-charcoal-grey-400 hover:text-accent-blue-400 transition-colors"
              >
                Privacy Policy
              </a>
              <a
                href="#"
                className="text-sm text-charcoal-grey-400 hover:text-accent-blue-400 transition-colors"
              >
                Terms of Service
              </a>
              <a
                href="#"
                className="text-sm text-charcoal-grey-400 hover:text-accent-blue-400 transition-colors"
              >
                Cookie Policy
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export { Footer };
