/**
 * Command Palette Component
 * 
 * Keyboard-driven interface for quick actions and navigation
 * Trigger with Cmd/Ctrl+K
 */

import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Icon } from './Icon';
import { icons } from '@/config/icons';
import { useUIStore } from '@/store';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { commandRegistry } from '@/services/commandRegistry';
import { registerBuiltInCommands, unregisterBuiltInCommands } from '@/services/builtInCommands';
import { highlightMatches } from '@/utils/fuzzySearch';
import './CommandPalette.css';

export const CommandPalette = () => {
  const navigate = useNavigate();
  const { commandPaletteOpen, closeCommandPalette } = useUIStore();
  const prefersReducedMotion = useReducedMotion();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isExecuting, setIsExecuting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Register built-in commands on mount
  useEffect(() => {
    registerBuiltInCommands(navigate);
    return () => {
      unregisterBuiltInCommands();
    };
  }, [navigate]);

  // Use command registry search with memoization
  const searchResults = useMemo(() => {
    return commandRegistry.search(query, 10);
  }, [query]);

  const filteredCommands = useMemo(() => {
    return searchResults.map(result => result.item);
  }, [searchResults]);

  // Group commands by category with memoization
  const groupedCommands = useMemo(() => {
    return filteredCommands.reduce((acc, cmd) => {
      if (!acc[cmd.category]) {
        acc[cmd.category] = [];
      }
      acc[cmd.category].push(cmd);
      return acc;
    }, {} as Record<string, typeof filteredCommands>);
  }, [filteredCommands]);

  // Reset selection when filtered commands change
  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Focus management and focus trap
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (commandPaletteOpen) {
      // Store previous focus
      previousFocusRef.current = document.activeElement as HTMLElement;
      
      // Focus input
      inputRef.current?.focus();
      setQuery('');
      setSelectedIndex(0);
    } else {
      // Restore previous focus
      if (previousFocusRef.current) {
        previousFocusRef.current.focus();
      }
    }
  }, [commandPaletteOpen]);

  // Handle keyboard navigation with wrap-around
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!commandPaletteOpen) return;

      switch (e.key) {
        case 'ArrowDown':
        case 'Tab':
          e.preventDefault();
          setSelectedIndex((prev) => {
            // Wrap to first if at last
            return prev >= filteredCommands.length - 1 ? 0 : prev + 1;
          });
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((prev) => {
            // Wrap to last if at first
            return prev <= 0 ? filteredCommands.length - 1 : prev - 1;
          });
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

  const executeCommand = useCallback(async (command: typeof filteredCommands[0]) => {
    try {
      setIsExecuting(true);
      
      // Execute command action
      await command.action();
      
      // Close palette
      closeCommandPalette();
    } catch (error) {
      console.error('Command execution failed:', error);
      // TODO: Show error toast notification
    } finally {
      setIsExecuting(false);
    }
  }, [closeCommandPalette]);

  const getCategoryLabel = useCallback((category: string) => {
    switch (category) {
      case 'navigation': return 'Navigation';
      case 'action': return 'Actions';
      case 'filter': return 'Filters';
      case 'search': return 'Search';
      case 'help': return 'Help';
      default: return category;
    }
  }, []);

  // Animation variants - smooth and graceful like macOS
  const overlayVariants = prefersReducedMotion
    ? { hidden: { opacity: 0 }, visible: { opacity: 1 }, exit: { opacity: 0 } }
    : { 
        hidden: { opacity: 0 }, 
        visible: { opacity: 1 }, 
        exit: { opacity: 0 } 
      };

  const modalVariants = prefersReducedMotion
    ? { hidden: { opacity: 0 }, visible: { opacity: 1 }, exit: { opacity: 0 } }
    : {
        hidden: { opacity: 0, scale: 0.92, y: -30, filter: 'blur(10px)' },
        visible: { opacity: 1, scale: 1, y: 0, filter: 'blur(0px)' },
        exit: { opacity: 0, scale: 0.95, y: -20, filter: 'blur(8px)' },
      };

  const overlayTransition = prefersReducedMotion
    ? { duration: 0.15 }
    : { 
        duration: 0.35,
        ease: [0.32, 0.72, 0, 1] // Custom easing curve for smooth feel
      };

  const modalTransition = prefersReducedMotion
    ? { duration: 0.15 }
    : { 
        type: 'spring', 
        damping: 30, 
        stiffness: 260,
        mass: 0.8
      };

  if (!commandPaletteOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="command-palette-overlay"
        variants={overlayVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
        transition={overlayTransition}
        onClick={closeCommandPalette}
      >
        <motion.div
          className="command-palette"
          variants={modalVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          transition={modalTransition}
          onClick={(e) => e.stopPropagation()}
          role="dialog"
          aria-modal="true"
          aria-labelledby="command-palette-label"
        >
          <div className="command-palette__header">
            <Icon icon={icons.search} size={36} className="command-palette__search-icon" aria-hidden="true" />
            <input
              ref={inputRef}
              type="text"
              placeholder="Search commands..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="command-palette__input"
              role="combobox"
              aria-expanded={filteredCommands.length > 0}
              aria-controls="command-palette-results"
              aria-activedescendant={filteredCommands[selectedIndex] ? `command-${filteredCommands[selectedIndex].id}` : undefined}
              aria-label="Search commands"
              id="command-palette-label"
            />
          </div>

          {query.trim() && (
            <div className="command-palette__content" id="command-palette-results" role="listbox">
              {filteredCommands.length === 0 ? (
                <div className="command-palette__empty" role="status">
                  <Icon icon={icons.search} size={48} aria-hidden="true" />
                  <p>No commands found</p>
                  <span>Try a different search term</span>
                </div>
              ) : (
                Object.entries(groupedCommands).map(([category, cmds]) => (
                  <div key={category} className="command-palette__group" role="group" aria-labelledby={`category-${category}`}>
                    <div className="command-palette__category" id={`category-${category}`}>
                      {getCategoryLabel(category)}
                    </div>
                    {cmds.map((cmd) => {
                      const globalIndex = filteredCommands.indexOf(cmd);
                      const isSelected = globalIndex === selectedIndex;
                      
                      // Get match highlighting
                      const result = searchResults.find(r => r.item.id === cmd.id);
                      const segments = result ? highlightMatches(cmd.label, result.matches) : [{ text: cmd.label, isMatch: false }];

                      return (
                        <motion.button
                          key={cmd.id}
                          className={`command-palette__item ${isSelected ? 'selected' : ''}`}
                          onClick={() => executeCommand(cmd)}
                          onMouseEnter={() => setSelectedIndex(globalIndex)}
                          whileHover={prefersReducedMotion ? {} : { x: 4 }}
                          transition={prefersReducedMotion ? {} : { type: 'spring', stiffness: 400, damping: 25 }}
                          disabled={isExecuting}
                          role="option"
                          id={`command-${cmd.id}`}
                          aria-selected={isSelected}
                          aria-label={cmd.description ? `${cmd.label}. ${cmd.description}` : cmd.label}
                        >
                          <div className="command-palette__item-left">
                            <Icon icon={cmd.icon} size={18} aria-hidden="true" />
                            <div className="command-palette__item-text">
                              <span className="command-palette__item-label">
                                {segments.map((segment, i) => (
                                  segment.isMatch ? (
                                    <mark key={i} className="command-palette__match">{segment.text}</mark>
                                  ) : (
                                    <span key={i}>{segment.text}</span>
                                  )
                                ))}
                              </span>
                              {cmd.description && (
                                <span className="command-palette__item-description">{cmd.description}</span>
                              )}
                            </div>
                          </div>
                          {cmd.shortcut && (
                            <kbd className="command-palette__shortcut" aria-label={`Keyboard shortcut: ${cmd.shortcut}`}>{cmd.shortcut}</kbd>
                          )}
                        </motion.button>
                      );
                    })}
                  </div>
                ))
              )}
            </div>
          )}

          {query.trim() && (
            <div className="command-palette__footer">
              <div className="command-palette__hint">
                <kbd>↑↓</kbd> Navigate
                <kbd>↵</kbd> Select
                <kbd>ESC</kbd> Close
              </div>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
