import React from 'react';
import { motion } from 'framer-motion';
import type { SearchMethod, SearchWeights } from '@/lib/api/search';
import './MethodControls.css';

interface MethodControlsProps {
    method: SearchMethod;
    onMethodChange: (method: SearchMethod) => void;
    weights: SearchWeights;
    onWeightsChange: (weights: SearchWeights) => void;
}

export const MethodControls: React.FC<MethodControlsProps> = ({
    method,
    onMethodChange,
    weights,
    onWeightsChange,
}) => {
    return (
        <div className="method-controls space-y-6 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Search Method</h3>
                <div className="flex bg-gray-100 dark:bg-gray-900 p-1 rounded-lg relative">
                    {/* Animated Background */}
                    <motion.div
                        className="absolute top-1 bottom-1 bg-white dark:bg-gray-700 rounded-md shadow-sm"
                        initial={false}
                        animate={{
                            left: method === 'fts5' ? '4px' : method === 'vector' ? '33.33%' : '66.66%',
                            width: 'calc(33.33% - 4px)',
                        }}
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    />

                    {(['fts5', 'vector', 'hybrid'] as SearchMethod[]).map((m) => (
                        <button
                            key={m}
                            onClick={() => onMethodChange(m)}
                            className={`flex-1 relative z-10 py-1.5 text-sm font-medium transition-colors ${method === m ? 'text-gray-900 dark:text-gray-100' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                                }`}
                        >
                            {m === 'fts5' ? 'Keyword' : m === 'vector' ? 'Semantic' : 'Hybrid'}
                        </button>
                    ))}
                </div>
            </div>

            {method === 'hybrid' && (
                <div className="space-y-4">
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Hybrid Weights</h3>

                    <div className="space-y-2">
                        <div className="flex justify-between text-xs text-gray-500">
                            <span>Keyword ({weights.keyword}%)</span>
                            <span>Semantic ({weights.semantic}%)</span>
                        </div>
                        <input
                            type="range"
                            min="0"
                            max="100"
                            value={weights.keyword}
                            onChange={(e) => {
                                const val = parseInt(e.target.value);
                                onWeightsChange({ keyword: val, semantic: 100 - val });
                            }}
                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 accent-blue-600"
                        />
                    </div>
                </div>
            )}
        </div>
    );
};
