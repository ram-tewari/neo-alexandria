import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Folder, BookOpen, GraduationCap, Briefcase, Star, Sparkles } from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import { Button } from '../../../ui/Button/Button';
import { Input } from '../../../ui/Input/Input';
import { collectionsApi } from '../../../../lib/api/collections';
import { useToast } from '../../../../contexts/ToastContext';
import { SmartCollectionDefinition } from '../../../../types/collection';
import { SmartCollectionRuleBuilder } from '../smart/SmartCollectionRuleBuilder';
import { SmartCollectionPreview } from '../smart/SmartCollectionPreview';

interface CreateCollectionModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const TEMPLATES = [
    {
        id: 'empty',
        name: 'Empty Collection',
        description: 'Start from scratch',
        icon: Folder,
        color: 'text-gray-500',
        bg: 'bg-gray-100 dark:bg-gray-800'
    },
    {
        id: 'research',
        name: 'Research Project',
        description: 'Organize papers and notes',
        icon: BookOpen,
        color: 'text-blue-500',
        bg: 'bg-blue-100 dark:bg-blue-900/20'
    },
    {
        id: 'course',
        name: 'Course Materials',
        description: 'Readings and assignments',
        icon: GraduationCap,
        color: 'text-green-500',
        bg: 'bg-green-100 dark:bg-green-900/20'
    },
    {
        id: 'work',
        name: 'Work Project',
        description: 'Documents and resources',
        icon: Briefcase,
        color: 'text-purple-500',
        bg: 'bg-purple-100 dark:bg-purple-900/20'
    },
    {
        id: 'favorites',
        name: 'Favorites',
        description: 'Your top resources',
        icon: Star,
        color: 'text-yellow-500',
        bg: 'bg-yellow-100 dark:bg-yellow-900/20'
    }
];

export const CreateCollectionModal: React.FC<CreateCollectionModalProps> = ({
    isOpen,
    onClose
}) => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [selectedTemplate, setSelectedTemplate] = useState('empty');
    const [isSmart, setIsSmart] = useState(false);
    const [smartDefinition, setSmartDefinition] = useState<SmartCollectionDefinition>({
        rules: [],
        matchType: 'all'
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const queryClient = useQueryClient();
    const { showToast } = useToast();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;

        setIsSubmitting(true);
        try {
            await collectionsApi.createCollection({
                name,
                description,
                visibility: 'private', // Default to private
                smart_definition: isSmart ? smartDefinition : undefined
            });

            queryClient.invalidateQueries({ queryKey: ['collections'] });
            showToast({ message: 'Collection created successfully', variant: 'success' });
            onClose();
            resetForm();
        } catch (error) {
            showToast({ message: 'Failed to create collection', variant: 'error' });
        } finally {
            setIsSubmitting(false);
        }
    };

    const resetForm = () => {
        setName('');
        setDescription('');
        setSelectedTemplate('empty');
        setIsSmart(false);
        setSmartDefinition({ rules: [], matchType: 'all' });
    };

    const handleTemplateSelect = (templateId: string) => {
        setSelectedTemplate(templateId);
        const template = TEMPLATES.find(t => t.id === templateId);
        if (template && template.id !== 'empty' && !name) {
            setName(template.name);
            setDescription(template.description);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 z-50 backdrop-blur-sm"
                        onClick={onClose}
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
                    >
                        <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-2xl pointer-events-auto max-h-[90vh] overflow-y-auto flex flex-col">
                            <div className="p-6 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center shrink-0">
                                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Create New Collection</h2>
                                <button
                                    onClick={onClose}
                                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <form onSubmit={handleSubmit} className="p-6 space-y-6 overflow-y-auto">
                                <div>
                                    <div className="flex items-center justify-between mb-3">
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                            Collection Type
                                        </label>
                                        <div className="flex items-center gap-2">
                                            <span className={`text-sm ${!isSmart ? 'font-medium text-gray-900 dark:text-white' : 'text-gray-500'}`}>Standard</span>
                                            <button
                                                type="button"
                                                onClick={() => setIsSmart(!isSmart)}
                                                className={`
                                                    relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                                                    ${isSmart ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'}
                                                `}
                                            >
                                                <span
                                                    className={`
                                                        inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                                                        ${isSmart ? 'translate-x-6' : 'translate-x-1'}
                                                    `}
                                                />
                                            </button>
                                            <span className={`text-sm flex items-center gap-1 ${isSmart ? 'font-medium text-blue-600 dark:text-blue-400' : 'text-gray-500'}`}>
                                                <Sparkles className="w-3 h-3" />
                                                Smart
                                            </span>
                                        </div>
                                    </div>

                                    {!isSmart && (
                                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
                                            {TEMPLATES.map((template) => {
                                                const Icon = template.icon;
                                                const isSelected = selectedTemplate === template.id;

                                                return (
                                                    <button
                                                        key={template.id}
                                                        type="button"
                                                        onClick={() => handleTemplateSelect(template.id)}
                                                        className={`
                                                            flex flex-col items-center p-3 rounded-lg border-2 transition-all
                                                            ${isSelected
                                                                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                                                                : 'border-transparent bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700'
                                                            }
                                                        `}
                                                    >
                                                        <div className={`p-2 rounded-full mb-2 ${template.bg} ${template.color}`}>
                                                            <Icon className="w-5 h-5" />
                                                        </div>
                                                        <span className={`text-sm font-medium ${isSelected ? 'text-blue-700 dark:text-blue-300' : 'text-gray-700 dark:text-gray-300'}`}>
                                                            {template.name}
                                                        </span>
                                                    </button>
                                                );
                                            })}
                                        </div>
                                    )}
                                </div>

                                <div className="space-y-4">
                                    <div>
                                        <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                            Collection Name
                                        </label>
                                        <Input
                                            id="name"
                                            value={name}
                                            onChange={(e) => setName(e.target.value)}
                                            placeholder="e.g., Summer Reading List"
                                            required
                                        />
                                    </div>

                                    <div>
                                        <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                            Description (Optional)
                                        </label>
                                        <textarea
                                            id="description"
                                            value={description}
                                            onChange={(e) => setDescription(e.target.value)}
                                            rows={3}
                                            className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            placeholder="What is this collection about?"
                                        />
                                    </div>

                                    {isSmart && (
                                        <div className="pt-4 border-t border-gray-200 dark:border-gray-800 space-y-6">
                                            <div>
                                                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                                                    <Sparkles className="w-5 h-5 text-blue-500" />
                                                    Smart Rules
                                                </h3>
                                                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                                                    Define rules to automatically populate this collection.
                                                </p>
                                                <SmartCollectionRuleBuilder
                                                    definition={smartDefinition}
                                                    onChange={setSmartDefinition}
                                                />
                                            </div>

                                            <SmartCollectionPreview definition={smartDefinition} />
                                        </div>
                                    )}
                                </div>
                            </form>

                            <div className="p-6 border-t border-gray-200 dark:border-gray-800 flex justify-end gap-3 shrink-0 bg-white dark:bg-gray-900 rounded-b-xl">
                                <Button type="button" variant="ghost" onClick={onClose}>
                                    Cancel
                                </Button>
                                <Button
                                    onClick={handleSubmit}
                                    disabled={isSubmitting || !name.trim() || (isSmart && smartDefinition.rules.length === 0)}
                                >
                                    {isSubmitting ? 'Creating...' : 'Create Collection'}
                                </Button>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};
