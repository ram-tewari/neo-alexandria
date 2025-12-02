import { useLocalStorage } from './useLocalStorage';
import type { SearchHistoryItem, SearchFilters } from '../api/search';
import { nanoid } from 'nanoid';

const MAX_HISTORY_ITEMS = 10;

export function useSearchHistory() {
    const [history, setHistory] = useLocalStorage<SearchHistoryItem[]>('search-history', []);

    const addToHistory = (query: string, filters?: SearchFilters) => {
        if (!query.trim()) return;

        const newItem: SearchHistoryItem = {
            id: nanoid(),
            query: query.trim(),
            timestamp: Date.now(),
            filters,
        };

        setHistory((prev) => {
            // Remove duplicates (same query)
            const filtered = prev.filter((item) => item.query.toLowerCase() !== query.trim().toLowerCase());
            // Add new item to top
            return [newItem, ...filtered].slice(0, MAX_HISTORY_ITEMS);
        });
    };

    const removeFromHistory = (id: string) => {
        setHistory((prev) => prev.filter((item) => item.id !== id));
    };

    const clearHistory = () => {
        setHistory([]);
    };

    return {
        history,
        addToHistory,
        removeFromHistory,
        clearHistory,
    };
}
