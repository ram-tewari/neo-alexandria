import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@/components/common/Icon';
import { icons } from '@/config/icons';
import { Button } from '@/components/ui/Button';
import type { SearchResultItem } from '@/lib/api/search';
import { highlightMatches } from '@/utils/fuzzySearch'; // Reusing existing util or I might need a new one for server-side highlights

interface SearchResultCardProps {
    item: SearchResultItem;
    onSelect?: () => void;
    selected?: boolean;
}

export const SearchResultCard: React.FC<SearchResultCardProps> = ({
    item,
    onSelect,
    selected,
}) => {
    const [expanded, setExpanded] = useState(false);
    const { resource, score, explanation, highlights } = item;

    // Helper to render highlighted text
    const renderHighlight = (text: string, field: string) => {
        if (!highlights || !highlights[field]) return text;

        // This is a simplified highlighter. Real implementation would parse the fragments.
        // Assuming backend returns fragments with <em> tags or similar, or just list of fragments.
        // For now, let's just show the fragments if available, otherwise the full text.

        const fragments = highlights[field];
        if (fragments.length > 0) {
            return (
                <span dangerouslySetInnerHTML={{ __html: fragments.join(' ... ') }} />
            );
        }
        return text;
    };

    return (
        <motion.div
            layout
            className={`group relative p-4 bg-white dark:bg-gray-800 rounded-lg border transition-all ${selected
                ? 'border-blue-500 ring-1 ring-blue-500'
                : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700'
                }`}
        >
            <div className="flex gap-4">
                {/* Selection Checkbox */}
                {onSelect && (
                    <div className="pt-1">
                        <input
                            type="checkbox"
                            checked={selected}
                            onChange={onSelect}
                            className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                    </div>
                )}

                {/* Icon */}
                <div className="pt-1 text-gray-400">
                    <Icon icon={icons.document} size={24} />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                        <h3 className="text-lg font-medium text-blue-600 dark:text-blue-400 truncate pr-4">
                            <a href={`/resources/${resource.id}`} className="hover:underline">
                                {renderHighlight(resource.title, 'title')}
                            </a>
                        </h3>

                        {/* Score Badge */}
                        <div
                            className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-xs font-medium text-gray-600 dark:text-gray-300 cursor-help"
                            title="Relevance Score"
                        >
                            <Icon icon={icons.activity} size={12} />
                            {Math.round(score * 100)}%
                        </div>
                    </div>

                    {/* Snippet / Description */}
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
                        {renderHighlight(resource.description || '', 'description')}
                    </p>

                    {/* Metadata */}
                    <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500 dark:text-gray-400">
                        {resource.type && (
                            <span className="flex items-center gap-1">
                                <Icon icon={icons.file} size={12} />
                                {resource.type}
                            </span>
                        )}
                        {resource.date_created && (
                            <span className="flex items-center gap-1">
                                <Icon icon={icons.calendar} size={12} />
                                {new Date(resource.date_created).toLocaleDateString()}
                            </span>
                        )}
                        {resource.quality_score !== undefined && (
                            <span className="flex items-center gap-1">
                                <Icon icon={icons.star} size={12} />
                                Quality: {Math.round(resource.quality_score * 100)}
                            </span>
                        )}
                    </div>

                    {/* Explanation Toggle */}
                    {explanation && (
                        <button
                            onClick={() => setExpanded(!expanded)}
                            className="mt-3 text-xs font-medium text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 flex items-center gap-1"
                        >
                            <Icon icon={expanded ? icons.chevronDown : icons.chevronRight} size={12} />
                            Why this result?
                        </button>
                    )}
                </div>
            </div>

            {/* Explanation Panel */}
            <AnimatePresence>
                {expanded && explanation && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                    >
                        <div className="mt-3 ml-12 p-3 bg-gray-50 dark:bg-gray-900/50 rounded text-xs text-gray-600 dark:text-gray-400 border border-gray-100 dark:border-gray-800">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <span className="font-semibold block mb-1">Matched Fields:</span>
                                    <div className="flex flex-wrap gap-1">
                                        {explanation.matched_fields.map(f => (
                                            <span key={f} className="px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                                                {f}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                                <div>
                                    <span className="font-semibold block mb-1">Scores:</span>
                                    <div className="space-y-1">
                                        {explanation.keyword_score !== undefined && (
                                            <div className="flex justify-between">
                                                <span>Keyword:</span>
                                                <span>{explanation.keyword_score.toFixed(2)}</span>
                                            </div>
                                        )}
                                        {explanation.vector_similarity !== undefined && (
                                            <div className="flex justify-between">
                                                <span>Vector:</span>
                                                <span>{explanation.vector_similarity.toFixed(2)}</span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                            {explanation.description && (
                                <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                                    <p>{explanation.description}</p>
                                </div>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};
