import { useState, KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Tag } from '@/components/common/Tag';
import { Icon } from '@/components/common/Icon';
import { icons } from '@/config/icons';
import { X, Plus } from 'lucide-react';

interface InterestTagsEditorProps {
    tags: string[];
    onChange: (tags: string[]) => void;
    suggestions?: string[];
    label?: string;
    placeholder?: string;
}

export const InterestTagsEditor = ({
    tags,
    onChange,
    suggestions = [],
    label = 'Interests',
    placeholder = 'Add an interest...'
}: InterestTagsEditorProps) => {
    const [inputValue, setInputValue] = useState('');

    const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && inputValue.trim()) {
            e.preventDefault();
            if (!tags.includes(inputValue.trim())) {
                onChange([...tags, inputValue.trim()]);
            }
            setInputValue('');
        } else if (e.key === 'Backspace' && !inputValue && tags.length > 0) {
            onChange(tags.slice(0, -1));
        }
    };

    const removeTag = (tagToRemove: string) => {
        onChange(tags.filter(tag => tag !== tagToRemove));
    };

    const addTag = (tag: string) => {
        if (!tags.includes(tag)) {
            onChange([...tags, tag]);
        }
        setInputValue('');
    };

    return (
        <div className="interest-tags-editor">
            {label && (
                <label style={{
                    display: 'block',
                    marginBottom: '0.5rem',
                    color: 'var(--text-secondary)',
                    fontSize: '0.875rem',
                    fontWeight: 500
                }}>
                    {label}
                </label>
            )}

            <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '8px',
                padding: '8px',
                background: 'var(--surface-subtle)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)',
                minHeight: '42px'
            }}>
                <AnimatePresence>
                    {tags.map((tag, index) => (
                        <motion.div
                            key={tag}
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.8, opacity: 0 }}
                            layout
                        >
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                background: 'var(--surface-elevated)',
                                border: '1px solid var(--border-hover)',
                                borderRadius: '16px',
                                padding: '2px 8px 2px 12px',
                                fontSize: '0.875rem',
                                color: 'var(--text-primary)'
                            }}>
                                <span style={{ marginRight: '6px' }}>{tag}</span>
                                <button
                                    onClick={() => removeTag(tag)}
                                    style={{
                                        background: 'none',
                                        border: 'none',
                                        cursor: 'pointer',
                                        padding: '2px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        color: 'var(--text-secondary)'
                                    }}
                                >
                                    <X size={14} />
                                </button>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={tags.length === 0 ? placeholder : ''}
                    style={{
                        background: 'transparent',
                        border: 'none',
                        outline: 'none',
                        color: 'var(--text-primary)',
                        flex: 1,
                        minWidth: '120px',
                        fontSize: '0.875rem',
                        padding: '4px'
                    }}
                />
            </div>

            {suggestions.length > 0 && (
                <div style={{ marginTop: '0.75rem', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', width: '100%' }}>Suggestions:</span>
                    {suggestions.filter(s => !tags.includes(s)).map(suggestion => (
                        <button
                            key={suggestion}
                            onClick={() => addTag(suggestion)}
                            style={{
                                background: 'transparent',
                                border: '1px dashed var(--border)',
                                borderRadius: '16px',
                                padding: '2px 10px',
                                fontSize: '0.75rem',
                                color: 'var(--text-secondary)',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px',
                                transition: 'all 0.2s'
                            }}
                        >
                            <Plus size={12} />
                            {suggestion}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};
