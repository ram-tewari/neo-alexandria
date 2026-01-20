/**
 * Command Palette Component
 * 
 * Keyboard-driven interface for quick actions and navigation
 * Trigger with Cmd/Ctrl+K
 * 
 * Enhanced with Global Search capabilities:
 * - Search History
 * - Quick Filters
 * - Backend Search Integration
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
import { registerPhase1Commands, unregisterPhase1Commands } from '@/services/phase1Commands';
import { highlightMatches } from '@/utils/fuzzySearch';
import { searchApi, type SearchResponse, type SearchResultItem } from '@/lib/api/search';
import { useSearchHistory } from '@/lib/hooks/useSearchHistory';
import './CommandPalette.css';

// Quick Filters
const QUICK_FILTERS = [
  { id: 'this-week', label: 'This Week', icon: icons.calendar, filter: { date_from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString() } },
  { id: 'high-quality', label: 'High Quality', icon: icons.star, filter: { min_quality: 0.8 } },
  // { id: 'my-collections', label: 'My Collections', icon: icons.collection, filter: { collection: 'mine' } }, // Stub
];

export const CommandPalette = () => {
  const navigate = useNavigate();
  const { commandPaletteOpen, closeCommandPalette } = useUIStore();
  const prefersReducedMotion = useReducedMotion();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isExecuting, setIsExecuting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Search State
  const [mode, setMode] = useState<'command' | 'search'>('command');
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeQuickFilter, setActiveQuickFilter] = useState<string | null>(null);

  const { history, addToHistory, removeFromHistory, clearHistory } = useSearchHistory();

  // Debounce search query
  const [debouncedQuery, setDebouncedQuery] = useState(query);
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  // Register commands
  useEffect(() => {
    registerBuiltInCommands(navigate);
    registerPhase1Commands(navigate);
    return () => {
      unregisterBuiltInCommands();
      unregisterPhase1Commands();
    };
  }, [navigate]);

  // Command Search
  const commandResults = useMemo(() => {
    if (mode === 'search') return [];
    return commandRegistry.search(query, 10);
  }, [query, mode]);

  const filteredCommands = useMemo(() => {
    return commandResults.map(result => result.item);
  }, [commandResults]);

  // Group commands
  const groupedCommands = useMemo(() => {
    return filteredCommands.reduce((acc, cmd) => {
      if (!acc[cmd.category]) acc[cmd.category] = [];
      acc[cmd.category].push(cmd);
      return acc;
    }, {} as Record<string, typeof filteredCommands>);
  }, [filteredCommands]);

  // Perform Global Search
  useEffect(() => {
    const performSearch = async () => {
      if (mode === 'search' && debouncedQuery.trim().length > 1) {
        setIsSearching(true);
        try {
          const filter = activeQuickFilter ? QUICK_FILTERS.find(f => f.id === activeQuickFilter)?.filter : undefined;
          const response = await searchApi.globalSearch(debouncedQuery, filter);
          setSearchResults(response.items);
        } catch (error) {
          console.error('Search failed:', error);
          // TODO: Toast error
        } finally {
          setIsSearching(false);
        }
      } else if (debouncedQuery.trim().length === 0) {
        setSearchResults([]);
      }
    };

    performSearch();
  }, [debouncedQuery, mode, activeQuickFilter]);

  // Reset selection on query change
  useEffect(() => {
    setSelectedIndex(0);
  }, [query, searchResults, filteredCommands]);

  // Focus management
  const previousFocusRef = useRef<HTMLElement | null>(null);
  useEffect(() => {
    if (commandPaletteOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      inputRef.current?.focus();
      setQuery('');
      setSelectedIndex(0);
      setMode('command'); // Default to command mode
      setSearchResults([]);
    } else {
      if (previousFocusRef.current) previousFocusRef.current.focus();
    }
  }, [commandPaletteOpen]);

  // Keyboard Navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!commandPaletteOpen) return;

      const totalItems = mode === 'command'
        ? filteredCommands.length
        : (query.trim() ? searchResults.length : history.length + (history.length > 0 ? 1 : 0)); // +1 for clear history if needed, but let's keep it simple

      // Allow switching modes with Tab if query is empty? Or maybe a specific shortcut?
      // For now, let's stick to simple navigation.

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => (prev >= totalItems - 1 ? 0 : prev + 1));
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => (prev <= 0 ? totalItems - 1 : prev - 1));
          break;
        case 'Enter':
          e.preventDefault();
          handleSelection();
          break;
        case 'Escape':
          e.preventDefault();
          closeCommandPalette();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [commandPaletteOpen, selectedIndex, filteredCommands, searchResults, history, mode, query, closeCommandPalette]);

  const handleSelection = async () => {
    if (mode === 'command') {
      if (filteredCommands[selectedIndex]) {
        await executeCommand(filteredCommands[selectedIndex]);
      }
    } else {
      // Search Mode
      if (query.trim()) {
        if (searchResults[selectedIndex]) {
          // Navigate to resource
          const resource = searchResults[selectedIndex].resource;
          addToHistory(query, activeQuickFilter ? QUICK_FILTERS.find(f => f.id === activeQuickFilter)?.filter : undefined);
          navigate(`/resources/${resource.id}`);
          closeCommandPalette();
        }
      } else {
        // History selection
        if (history[selectedIndex]) {
          const item = history[selectedIndex];
          setQuery(item.query);
          // Optionally restore filters
        }
      }
    }
  };

  const executeCommand = useCallback(async (command: typeof filteredCommands[0]) => {
    try {
      setIsExecuting(true);
      await command.action();
      closeCommandPalette();
    } catch (error) {
      console.error('Command execution failed:', error);
    } finally {
      setIsExecuting(false);
    }
  }, [closeCommandPalette]);

  // Toggle Mode
  const toggleMode = () => {
    setMode(prev => prev === 'command' ? 'search' : 'command');
    setQuery('');
    setSearchResults([]);
    setActiveQuickFilter(null);
    inputRef.current?.focus();
  };

  // Animation variants
  const overlayVariants = { hidden: { opacity: 0 }, visible: { opacity: 1 }, exit: { opacity: 0 } };
  const modalVariants = {
    hidden: { opacity: 0, scale: 0.95, y: -20 },
    visible: { opacity: 1, scale: 1, y: 0 },
    exit: { opacity: 0, scale: 0.95, y: -20 },
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
        onClick={closeCommandPalette}
      >
        <motion.div
          className="command-palette"
          variants={modalVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          onClick={e => e.stopPropagation()}
          role="dialog"
          aria-modal="true"
        >
          <div className="command-palette__header">
            <div className="command-palette__mode-toggle" onClick={toggleMode}>
              <Icon icon={mode === 'command' ? icons.command : icons.search} size={20} />
              <span className="text-xs font-medium ml-2 uppercase tracking-wider text-gray-500">
                {mode === 'command' ? 'Command' : 'Search'}
              </span>
            </div>
            <input
              ref={inputRef}
              type="text"
              placeholder={mode === 'command' ? "Type a command..." : "Search resources..."}
              value={query}
              onChange={e => setQuery(e.target.value)}
              className="command-palette__input"
              autoFocus
            />
            {isSearching && <div className="command-palette__loader" />}
          </div>

          {/* Quick Filters (Search Mode Only) */}
          {mode === 'search' && (
            <div className="command-palette__filters">
              {QUICK_FILTERS.map(filter => (
                <button
                  key={filter.id}
                  className={`command-palette__filter-chip ${activeQuickFilter === filter.id ? 'active' : ''}`}
                  onClick={() => setActiveQuickFilter(prev => prev === filter.id ? null : filter.id)}
                >
                  <Icon icon={filter.icon} size={12} />
                  {filter.label}
                </button>
              ))}
            </div>
          )}

          <div className="command-palette__content">
            {mode === 'command' ? (
              // Command Results
              filteredCommands.length === 0 ? (
                <div className="command-palette__empty">No commands found</div>
              ) : (
                Object.entries(groupedCommands).map(([category, cmds]) => (
                  <div key={category} className="command-palette__group">
                    <div className="command-palette__category">{category}</div>
                    {cmds.map((cmd) => {
                      const globalIndex = filteredCommands.indexOf(cmd);
                      const isSelected = globalIndex === selectedIndex;
                      return (
                        <div
                          key={cmd.id}
                          className={`command-palette__item ${isSelected ? 'selected' : ''}`}
                          onClick={() => executeCommand(cmd)}
                          onMouseEnter={() => setSelectedIndex(globalIndex)}
                        >
                          <Icon icon={cmd.icon} size={16} />
                          <span className="command-palette__item-label">{cmd.label}</span>
                          {cmd.shortcut && <kbd className="command-palette__shortcut">{cmd.shortcut}</kbd>}
                        </div>
                      );
                    })}
                  </div>
                ))
              )
            ) : (
              // Search Results & History
              query.trim() ? (
                // Show Search Results
                searchResults.length === 0 && !isSearching ? (
                  <div className="command-palette__empty">No results found</div>
                ) : (
                  <div className="command-palette__group">
                    <div className="command-palette__category">Results</div>
                    {searchResults.map((item, index) => {
                      const isSelected = index === selectedIndex;
                      return (
                        <div
                          key={item.resource.id}
                          className={`command-palette__item ${isSelected ? 'selected' : ''}`}
                          onClick={() => {
                            addToHistory(query);
                            navigate(`/resources/${item.resource.id}`);
                            closeCommandPalette();
                          }}
                          onMouseEnter={() => setSelectedIndex(index)}
                        >
                          <Icon icon={icons.document} size={16} />
                          <div className="flex flex-col ml-2">
                            <span className="command-palette__item-label">{item.resource.title}</span>
                            <span className="text-xs text-gray-400 truncate max-w-[300px]">
                              {item.resource.description || 'No description'}
                            </span>
                          </div>
                          {item.score > 0 && (
                            <span className="ml-auto text-xs text-gray-400">
                              {Math.round(item.score * 100)}%
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )
              ) : (
                // Show History
                history.length === 0 ? (
                  <div className="command-palette__empty">Type to search...</div>
                ) : (
                  <div className="command-palette__group">
                    <div className="command-palette__category flex justify-between items-center">
                      <span>Recent Searches</span>
                      <button onClick={clearHistory} className="text-xs text-blue-500 hover:underline">Clear</button>
                    </div>
                    {history.map((item, index) => {
                      const isSelected = index === selectedIndex;
                      return (
                        <div
                          key={item.id}
                          className={`command-palette__item ${isSelected ? 'selected' : ''}`}
                          onClick={() => setQuery(item.query)}
                          onMouseEnter={() => setSelectedIndex(index)}
                        >
                          <Icon icon={icons.history} size={16} />
                          <span className="command-palette__item-label">{item.query}</span>
                          <button
                            className="ml-auto p-1 hover:bg-gray-200 rounded-full"
                            onClick={(e) => {
                              e.stopPropagation();
                              removeFromHistory(item.id);
                            }}
                          >
                            <Icon icon={icons.close} size={12} />
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )
              )
            )}
          </div>

          <div className="command-palette__footer">
            <div className="command-palette__hint">
              <kbd>Tab</kbd> Switch Mode
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
