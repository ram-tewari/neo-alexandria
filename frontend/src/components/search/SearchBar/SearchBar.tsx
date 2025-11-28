import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Clock, X, Filter as FilterIcon } from 'lucide-react';
import { useSearchSuggestions, useSearchHistory, useAddToHistory } from '@/hooks/useSearch';
import { SearchSuggestion, QuickFilter } from '@/types/search';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (query: string) => void;
  quickFilters?: QuickFilter[];
  onQuickFilterClick?: (filter: QuickFilter) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  onSubmit,
  quickFilters = [],
  onQuickFilterClick,
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const { data: suggestions = [] } = useSearchSuggestions(value);
  const { data: history = [] } = useSearchHistory();
  const addToHistory = useAddToHistory();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      addToHistory.mutate(value);
      onSubmit(value);
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    onChange(suggestion.text);
    addToHistory.mutate(suggestion.text);
    onSubmit(suggestion.text);
    setShowSuggestions(false);
  };

  const handleHistoryClick = (query: string) => {
    onChange(query);
    onSubmit(query);
    setShowSuggestions(false);
  };

  const highlightMatch = (text: string, highlights: [number, number][]) => {
    if (!highlights.length) return text;

    const parts: React.ReactNode[] = [];
    let lastIndex = 0;

    highlights.forEach(([start, end], index) => {
      if (start > lastIndex) {
        parts.push(text.substring(lastIndex, start));
      }
      parts.push(
        <mark key={index} className="bg-yellow-200 dark:bg-yellow-800">
          {text.substring(start, end)}
        </mark>
      );
      lastIndex = end;
    });

    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    return parts;
  };

  const showDropdown = showSuggestions && (suggestions.length > 0 || history.length > 0);

  return (
    <div ref={containerRef} className="relative w-full">
      <form onSubmit={handleSubmit} className="relative">
        <div
          className={`
            flex items-center gap-2 px-4 py-3 bg-white dark:bg-gray-800 rounded-lg border-2 transition-all
            ${
              isFocused
                ? 'border-primary-500 ring-2 ring-primary-200 dark:ring-primary-800'
                : 'border-gray-300 dark:border-gray-600'
            }
          `}
        >
          <Search className="w-5 h-5 text-gray-400 flex-shrink-0" aria-hidden="true" />

          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onFocus={() => {
              setIsFocused(true);
              setShowSuggestions(true);
            }}
            onBlur={() => setIsFocused(false)}
            placeholder="Search resources..."
            className="flex-1 bg-transparent border-none outline-none text-gray-900 dark:text-white placeholder-gray-400"
            aria-label="Search"
            aria-autocomplete="list"
            aria-controls="search-suggestions"
            aria-expanded={showDropdown}
          />

          {value && (
            <button
              type="button"
              onClick={() => onChange('')}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              aria-label="Clear search"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </form>

      {/* Quick Filters */}
      {quickFilters.length > 0 && (
        <div className="flex items-center gap-2 mt-2">
          <FilterIcon className="w-4 h-4 text-gray-400" aria-hidden="true" />
          {quickFilters.map((filter) => (
            <button
              key={filter.id}
              onClick={() => onQuickFilterClick?.(filter)}
              className="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full transition-colors"
            >
              {filter.label}
            </button>
          ))}
        </div>
      )}

      {/* Suggestions Dropdown */}
      <AnimatePresence>
        {showDropdown && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
            className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-lg overflow-hidden z-50"
            id="search-suggestions"
            role="listbox"
          >
            {/* History */}
            {history.length > 0 && !value && (
              <div>
                <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                  <Clock className="w-3 h-3" />
                  Recent Searches
                </div>
                {history.slice(0, 5).map((query, index) => (
                  <button
                    key={index}
                    onClick={() => handleHistoryClick(query)}
                    className="w-full flex items-center gap-3 px-4 py-2 text-left text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    role="option"
                  >
                    <Clock className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    <span className="flex-1 truncate">{query}</span>
                  </button>
                ))}
              </div>
            )}

            {/* Suggestions */}
            {suggestions.length > 0 && (
              <div>
                {history.length > 0 && !value && (
                  <div className="border-t border-gray-200 dark:border-gray-700" />
                )}
                <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Suggestions
                </div>
                {suggestions.map((suggestion, index) => (
                  <motion.button
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.03 }}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="w-full flex items-center gap-3 px-4 py-2 text-left text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    role="option"
                  >
                    <Search className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    <span className="flex-1">
                      {highlightMatch(suggestion.text, suggestion.highlight)}
                    </span>
                    <span className="text-xs text-gray-500 capitalize">
                      {suggestion.type}
                    </span>
                  </motion.button>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
