// Neo Alexandria 2.0 Frontend - Quick Search Panel Component
// Search input with autocomplete suggestions and keyboard navigation

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Search, ArrowRight, Clock } from 'lucide-react';
import { apiService } from '@/services/api';

const QuickSearchPanel: React.FC = () => {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // Debounce the query input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  // Fetch autocomplete suggestions
  const { data: suggestions } = useQuery({
    queryKey: ['suggestions', debouncedQuery],
    queryFn: () => apiService.getSubjectSuggestions(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
    staleTime: 5 * 60 * 1000,
  });

  // Get recent searches from localStorage
  const getRecentSearches = (): string[] => {
    try {
      const recent = localStorage.getItem('recentSearches');
      return recent ? JSON.parse(recent) : [];
    } catch {
      return [];
    }
  };

  const saveRecentSearch = (searchQuery: string) => {
    try {
      const recent = getRecentSearches();
      const updated = [
        searchQuery,
        ...recent.filter((s) => s !== searchQuery),
      ].slice(0, 5);
      localStorage.setItem('recentSearches', JSON.stringify(updated));
    } catch {
      // Ignore localStorage errors
    }
  };

  const recentSearches = getRecentSearches();
  const showSuggestions = isFocused && (suggestions?.length || recentSearches.length);
  const displayItems = query.length >= 2 ? suggestions || [] : recentSearches;

  // Handle search submission
  const handleSearch = (searchQuery: string) => {
    if (searchQuery.trim()) {
      saveRecentSearch(searchQuery.trim());
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setQuery('');
      setIsFocused(false);
      inputRef.current?.blur();
    }
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!displayItems.length) {
      if (e.key === 'Enter') {
        handleSearch(query);
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < displayItems.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && displayItems[selectedIndex]) {
          handleSearch(displayItems[selectedIndex]);
        } else {
          handleSearch(query);
        }
        break;
      case 'Escape':
        setIsFocused(false);
        inputRef.current?.blur();
        break;
    }
  };

  return (
    <div className="relative max-w-3xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-charcoal-grey-800 rounded-lg p-6 shadow-lg"
      >
        <div className="flex items-center mb-2">
          <Search className="w-5 h-5 text-accent-blue-500 mr-2" />
          <h3 className="text-lg font-semibold text-charcoal-grey-50">
            Quick Search
          </h3>
        </div>

        <div className="relative">
          <div className="relative">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setSelectedIndex(-1);
              }}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => {
                // Delay to allow click on suggestions
                setTimeout(() => setIsFocused(false), 200);
              }}
              placeholder="Search your knowledge library..."
              className="w-full px-4 py-3 pr-12 bg-charcoal-grey-700 text-charcoal-grey-50 placeholder-charcoal-grey-400 rounded-lg border border-charcoal-grey-600 focus:border-accent-blue-500 focus:ring-2 focus:ring-accent-blue-500/20 focus:outline-none transition-all"
            />
            <button
              onClick={() => handleSearch(query)}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-accent-blue-500 hover:bg-accent-blue-600 text-white rounded-md transition-colors"
              aria-label="Search"
            >
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Autocomplete Dropdown */}
          <AnimatePresence>
            {showSuggestions && displayItems.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.15 }}
                className="absolute z-50 w-full mt-2 bg-charcoal-grey-700 border border-charcoal-grey-600 rounded-lg shadow-xl overflow-hidden"
              >
                <div className="py-2">
                  {query.length < 2 && recentSearches.length > 0 && (
                    <div className="px-4 py-2 text-xs font-medium text-charcoal-grey-400 uppercase tracking-wide">
                      Recent Searches
                    </div>
                  )}
                  {displayItems.map((item, index) => (
                    <button
                      key={index}
                      onClick={() => handleSearch(item)}
                      onMouseEnter={() => setSelectedIndex(index)}
                      className={`w-full px-4 py-2 text-left flex items-center transition-colors ${
                        selectedIndex === index
                          ? 'bg-accent-blue-500/20 text-accent-blue-300'
                          : 'text-charcoal-grey-200 hover:bg-charcoal-grey-600'
                      }`}
                    >
                      {query.length < 2 ? (
                        <Clock className="w-4 h-4 mr-3 text-charcoal-grey-400" />
                      ) : (
                        <Search className="w-4 h-4 mr-3 text-charcoal-grey-400" />
                      )}
                      <span className="flex-1">{item}</span>
                      <ArrowRight className="w-4 h-4 text-charcoal-grey-500" />
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <p className="text-sm text-charcoal-grey-400 mt-3">
          Press <kbd className="px-2 py-1 bg-charcoal-grey-700 rounded text-xs">Enter</kbd> to
          search or use <kbd className="px-2 py-1 bg-charcoal-grey-700 rounded text-xs">↑</kbd>{' '}
          <kbd className="px-2 py-1 bg-charcoal-grey-700 rounded text-xs">↓</kbd> to navigate
          suggestions
        </p>
      </motion.div>
    </div>
  );
};

export { QuickSearchPanel };
