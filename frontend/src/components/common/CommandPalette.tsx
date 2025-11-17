/**
 * Command Palette Component
 * 
 * Keyboard-driven interface for quick actions and navigation
 * Trigger with Cmd/Ctrl+K
 */

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Icon } from './Icon';
import { icons } from '@/config/icons';
import { useUIStore } from '@/store';
import type { LucideIcon } from 'lucide-react';
import './CommandPalette.css';

export interface Command {
  id: string;
  label: string;
  icon: LucideIcon;
  keywords: string[];
  category: 'navigation' | 'action' | 'filter' | 'search';
  action: () => void | Promise<void>;
  shortcut?: string;
}

interface CommandPaletteProps {
  commands?: Command[];
}

const defaultCommands: Command[] = [
  {
    id: 'nav-dashboard',
    label: 'Go to Dashboard',
    icon: icons.dashboard,
    keywords: ['dashboard', 'home', 'overview'],
    category: 'navigation',
    action: () => {},
    shortcut: 'G D',
  },
  {
    id: 'nav-library',
    label: 'Go to Library',
    icon: icons.library,
    keywords: ['library', 'resources', 'browse'],
    category: 'navigation',
    action: () => {},
    shortcut: 'G L',
  },
  {
    id: 'nav-graph',
    label: 'Go to Knowledge Graph',
    icon: icons.graph,
    keywords: ['graph', 'network', 'connections'],
    category: 'navigation',
    action: () => {},
    shortcut: 'G G',
  },
  {
    id: 'action-add',
    label: 'Add New Resource',
    icon: icons.add,
    keywords: ['add', 'new', 'create', 'resource'],
    category: 'action',
    action: () => {},
    shortcut: 'N',
  },
  {
    id: 'action-collection',
    label: 'Create Collection',
    icon: icons.library,
    keywords: ['collection', 'folder', 'organize'],
    category: 'action',
    action: () => {},
  },
  {
    id: 'filter-unread',
    label: 'Filter: Unread',
    icon: icons.filter,
    keywords: ['filter', 'unread', 'status'],
    category: 'filter',
    action: () => {},
  },
  {
    id: 'filter-completed',
    label: 'Filter: Completed',
    icon: icons.check,
    keywords: ['filter', 'completed', 'read', 'done'],
    category: 'filter',
    action: () => {},
  },
];

export const CommandPalette = ({ commands = defaultCommands }: CommandPaletteProps) => {
  const navigate = useNavigate();
  const { commandPaletteOpen, closeCommandPalette } = useUIStore();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Filter commands based on query
  const filteredCommands = commands.filter((cmd) => {
    const searchText = query.toLowerCase();
    return (
      cmd.label.toLowerCase().includes(searchText) ||
      cmd.keywords.some((keyword) => keyword.toLowerCase().includes(searchText))
    );
  });

  // Group commands by category
  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    if (!acc[cmd.category]) {
      acc[cmd.category] = [];
    }
    acc[cmd.category].push(cmd);
    return acc;
  }, {} as Record<string, Command[]>);

  // Reset selection when filtered commands change
  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Focus input when palette opens
  useEffect(() => {
    if (commandPaletteOpen) {
      inputRef.current?.focus();
      setQuery('');
      setSelectedIndex(0);
    }
  }, [commandPaletteOpen]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!commandPaletteOpen) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex((prev) => Math.min(prev + 1, filteredCommands.length - 1));
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
          break;
        case 'Enter':
          e.preventDefault();
          if (filteredCommands[selectedIndex]) {
            executeCommand(filteredCommands[selectedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          closeCommandPalette();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [commandPaletteOpen, selectedIndex, filteredCommands, closeCommandPalette]);

  const executeCommand = async (command: Command) => {
    // Handle navigation commands
    if (command.category === 'navigation') {
      if (command.id === 'nav-dashboard') navigate('/');
      else if (command.id === 'nav-library') navigate('/library');
      else if (command.id === 'nav-graph') navigate('/graph');
    }

    // Execute command action
    await command.action();
    
    // Close palette
    closeCommandPalette();
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'navigation': return 'Navigation';
      case 'action': return 'Actions';
      case 'filter': return 'Filters';
      case 'search': return 'Search';
      default: return category;
    }
  };

  if (!commandPaletteOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="command-palette-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={closeCommandPalette}
      >
        <motion.div
          className="command-palette"
          initial={{ opacity: 0, scale: 0.95, y: -20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="command-palette__header">
            <Icon icon={icons.search} size={20} />
            <input
              ref={inputRef}
              type="text"
              placeholder="Type a command or search..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="command-palette__input"
            />
            <kbd className="command-palette__kbd">ESC</kbd>
          </div>

          <div className="command-palette__content">
            {filteredCommands.length === 0 ? (
              <div className="command-palette__empty">
                <p>No commands found</p>
                <span>Try searching for something else</span>
              </div>
            ) : (
              Object.entries(groupedCommands).map(([category, cmds]) => (
                <div key={category} className="command-palette__group">
                  <div className="command-palette__category">
                    {getCategoryLabel(category)}
                  </div>
                  {cmds.map((cmd, index) => {
                    const globalIndex = filteredCommands.indexOf(cmd);
                    const isSelected = globalIndex === selectedIndex;

                    return (
                      <motion.button
                        key={cmd.id}
                        className={`command-palette__item ${isSelected ? 'selected' : ''}`}
                        onClick={() => executeCommand(cmd)}
                        onMouseEnter={() => setSelectedIndex(globalIndex)}
                        whileHover={{ x: 4 }}
                      >
                        <div className="command-palette__item-left">
                          <Icon icon={cmd.icon} size={18} />
                          <span>{cmd.label}</span>
                        </div>
                        {cmd.shortcut && (
                          <kbd className="command-palette__shortcut">{cmd.shortcut}</kbd>
                        )}
                      </motion.button>
                    );
                  })}
                </div>
              ))
            )}
          </div>

          <div className="command-palette__footer">
            <div className="command-palette__hint">
              <kbd>↑↓</kbd> Navigate
              <kbd>↵</kbd> Select
              <kbd>ESC</kbd> Close
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
