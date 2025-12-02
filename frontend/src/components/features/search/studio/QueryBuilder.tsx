import React from 'react';
import { Icon } from '@/components/common/Icon';
import { icons } from '@/config/icons';
import { Button } from '@/components/ui/Button';
import type { BooleanClause } from '@/lib/api/search';

interface QueryBuilderProps {
    clauses: BooleanClause[];
    onChange: (clauses: BooleanClause[]) => void;
}

const FIELDS = [
    { value: 'title', label: 'Title' },
    { value: 'description', label: 'Description' },
    { value: 'content', label: 'Content' },
    { value: 'author', label: 'Author' },
    { value: 'tags', label: 'Tags' },
];

export const QueryBuilder: React.FC<QueryBuilderProps> = ({ clauses, onChange }) => {
    const addClause = () => {
        onChange([...clauses, { operator: 'AND', field: 'content', value: '' }]);
    };

    const removeClause = (index: number) => {
        const newClauses = [...clauses];
        newClauses.splice(index, 1);
        onChange(newClauses);
    };

    const updateClause = (index: number, field: keyof BooleanClause, value: string) => {
        const newClauses = [...clauses];
        newClauses[index] = { ...newClauses[index], [field]: value };
        onChange(newClauses);
    };

    return (
        <div className="space-y-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Query Builder</h3>
                <Button variant="ghost" size="sm" onClick={addClause} className="text-xs">
                    <Icon icon={icons.plus} size={14} className="mr-1" />
                    Add Clause
                </Button>
            </div>

            <div className="space-y-3">
                {clauses.length === 0 ? (
                    <div className="text-sm text-gray-500 text-center py-4 italic">
                        No advanced clauses. Add one to refine your search.
                    </div>
                ) : (
                    clauses.map((clause, index) => (
                        <div key={index} className="flex items-center gap-2">
                            {/* Operator */}
                            <select
                                value={clause.operator}
                                onChange={(e) => updateClause(index, 'operator', e.target.value)}
                                className="w-20 text-sm rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700"
                            >
                                <option value="AND">AND</option>
                                <option value="OR">OR</option>
                                <option value="NOT">NOT</option>
                            </select>

                            {/* Field */}
                            <select
                                value={clause.field}
                                onChange={(e) => updateClause(index, 'field', e.target.value)}
                                className="w-32 text-sm rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700"
                            >
                                {FIELDS.map((f) => (
                                    <option key={f.value} value={f.value}>{f.label}</option>
                                ))}
                            </select>

                            {/* Value */}
                            <input
                                type="text"
                                value={clause.value}
                                onChange={(e) => updateClause(index, 'value', e.target.value)}
                                placeholder="Value..."
                                className="flex-1 text-sm rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700"
                            />

                            {/* Remove */}
                            <button
                                onClick={() => removeClause(index)}
                                className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                                aria-label="Remove clause"
                            >
                                <Icon icon={icons.close} size={16} />
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
