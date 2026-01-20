import React from 'react';
import { Plus, Trash2, X } from 'lucide-react';
import { Button } from '../../../ui/Button/Button';
import { Input } from '../../../ui/Input/Input';
import {
    SmartCollectionDefinition,
    SmartCollectionRule,
    SmartCollectionRuleField,
    SmartCollectionRuleOperator
} from '../../../../types/collection';

interface SmartCollectionRuleBuilderProps {
    definition: SmartCollectionDefinition;
    onChange: (definition: SmartCollectionDefinition) => void;
}

const FIELDS: { label: string; value: SmartCollectionRuleField }[] = [
    { label: 'Quality Score', value: 'quality' },
    { label: 'Classification', value: 'classification' },
    { label: 'Tags', value: 'tags' },
    { label: 'Created Date', value: 'created_at' },
    { label: 'Author', value: 'author' }
];

const OPERATORS: { label: string; value: SmartCollectionRuleOperator }[] = [
    { label: 'Equals', value: 'equals' },
    { label: 'Contains', value: 'contains' },
    { label: 'Greater Than', value: 'gt' },
    { label: 'Less Than', value: 'lt' },
    { label: 'Greater or Equal', value: 'gte' },
    { label: 'Less or Equal', value: 'lte' },
    { label: 'In List', value: 'in' }
];

export const SmartCollectionRuleBuilder: React.FC<SmartCollectionRuleBuilderProps> = ({
    definition,
    onChange
}) => {
    const addRule = () => {
        const newRule: SmartCollectionRule = {
            id: crypto.randomUUID(),
            field: 'quality',
            operator: 'gt',
            value: ''
        };
        onChange({
            ...definition,
            rules: [...definition.rules, newRule]
        });
    };

    const removeRule = (id: string) => {
        onChange({
            ...definition,
            rules: definition.rules.filter(r => r.id !== id)
        });
    };

    const updateRule = (id: string, updates: Partial<SmartCollectionRule>) => {
        onChange({
            ...definition,
            rules: definition.rules.map(r => r.id === id ? { ...r, ...updates } : r)
        });
    };

    const setMatchType = (type: 'all' | 'any') => {
        onChange({ ...definition, matchType: type });
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-gray-900 dark:text-white">Rules</h3>
                <div className="flex items-center gap-2 text-sm">
                    <span className="text-gray-500">Match</span>
                    <select
                        value={definition.matchType}
                        onChange={(e) => setMatchType(e.target.value as 'all' | 'any')}
                        className="bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded px-2 py-1 text-sm"
                    >
                        <option value="all">All (AND)</option>
                        <option value="any">Any (OR)</option>
                    </select>
                    <span className="text-gray-500">of the following rules:</span>
                </div>
            </div>

            <div className="space-y-3">
                {definition.rules.map((rule) => (
                    <div key={rule.id} className="flex items-start gap-2 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div className="grid grid-cols-12 gap-2 flex-1">
                            <div className="col-span-4">
                                <select
                                    value={rule.field}
                                    onChange={(e) => updateRule(rule.id, { field: e.target.value as SmartCollectionRuleField })}
                                    className="w-full bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded px-3 py-2 text-sm"
                                >
                                    {FIELDS.map(f => (
                                        <option key={f.value} value={f.value}>{f.label}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="col-span-3">
                                <select
                                    value={rule.operator}
                                    onChange={(e) => updateRule(rule.id, { operator: e.target.value as SmartCollectionRuleOperator })}
                                    className="w-full bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded px-3 py-2 text-sm"
                                >
                                    {OPERATORS.map(op => (
                                        <option key={op.value} value={op.value}>{op.label}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="col-span-5">
                                <Input
                                    value={rule.value as string}
                                    onChange={(e) => updateRule(rule.id, { value: e.target.value })}
                                    placeholder="Value..."
                                    className="h-[38px]"
                                />
                            </div>
                        </div>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeRule(rule.id)}
                            className="text-gray-400 hover:text-red-500"
                        >
                            <Trash2 className="w-4 h-4" />
                        </Button>
                    </div>
                ))}

                {definition.rules.length === 0 && (
                    <div className="text-center py-8 border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-lg">
                        <p className="text-sm text-gray-500">No rules defined. Add a rule to start.</p>
                    </div>
                )}

                <Button
                    variant="secondary"
                    size="sm"
                    onClick={addRule}
                    className="w-full"
                >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Rule
                </Button>
            </div>
        </div>
    );
};
