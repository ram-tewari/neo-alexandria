import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Link, FileText, Upload, Globe, CheckCircle2, AlertCircle } from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import { Button } from '../../ui/Button/Button';
import { Input } from '../../ui/Input/Input';
import { resourcesApi } from '../../../lib/api/resources';
import { useToast } from '../../../contexts/ToastContext';

interface CreateResourceModalProps {
    isOpen: boolean;
    onClose: () => void;
}

type InputType = 'url' | 'file';

export const CreateResourceModal: React.FC<CreateResourceModalProps> = ({
    isOpen,
    onClose
}) => {
    const [inputType, setInputType] = useState<InputType>('url');
    const [url, setUrl] = useState('');
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [file, setFile] = useState<File | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const queryClient = useQueryClient();
    const { showToast } = useToast();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (inputType === 'url' && !url) return;
        if (inputType === 'file' && !file) return;

        setIsSubmitting(true);
        try {
            await resourcesApi.create({
                url: inputType === 'url' ? url : undefined,
                file: inputType === 'file' ? file || undefined : undefined,
                title: title || undefined,
                description: description || undefined,
                type: inputType === 'url' ? 'website' : 'document'
            });

            queryClient.invalidateQueries({ queryKey: ['resources'] });
            showToast({ message: 'Resource added successfully', variant: 'success' });
            onClose();
            resetForm();
        } catch (error) {
            showToast({ message: 'Failed to add resource', variant: 'error' });
        } finally {
            setIsSubmitting(false);
        }
    };

    const resetForm = () => {
        setUrl('');
        setTitle('');
        setDescription('');
        setFile(null);
        setInputType('url');
        setDragActive(false);
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFileSelect(e.target.files[0]);
        }
    };

    const handleFileSelect = (selectedFile: File) => {
        setFile(selectedFile);
        if (!title) {
            setTitle(selectedFile.name.split('.')[0]);
        }
    };

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelect(e.dataTransfer.files[0]);
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
                        className="fixed inset-0 bg-black/60 z-50 backdrop-blur-sm"
                        onClick={onClose}
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
                    >
                        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-lg pointer-events-auto flex flex-col border border-gray-200 dark:border-gray-800 overflow-hidden">
                            {/* Header */}
                            <div className="p-6 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center shrink-0 bg-gray-50/50 dark:bg-gray-800/50">
                                <div>
                                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">Add Resource</h2>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Add a new item to your library</p>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="p-2 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <form onSubmit={handleSubmit} className="p-6 space-y-6">
                                {/* Custom Tab Selector */}
                                <div className="p-1 bg-gray-100 dark:bg-gray-800 rounded-xl flex relative">
                                    <div
                                        className="absolute top-1 bottom-1 rounded-lg bg-white dark:bg-gray-700 shadow-sm transition-all duration-300 ease-out"
                                        style={{
                                            left: inputType === 'url' ? '4px' : '50%',
                                            width: 'calc(50% - 4px)'
                                        }}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setInputType('url')}
                                        className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-medium rounded-lg relative z-10 transition-colors ${inputType === 'url'
                                                ? 'text-blue-600 dark:text-blue-400'
                                                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                                            }`}
                                    >
                                        <Globe className="w-4 h-4" />
                                        URL Link
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setInputType('file')}
                                        className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-medium rounded-lg relative z-10 transition-colors ${inputType === 'file'
                                                ? 'text-blue-600 dark:text-blue-400'
                                                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                                            }`}
                                    >
                                        <Upload className="w-4 h-4" />
                                        Upload File
                                    </button>
                                </div>

                                <AnimatePresence mode="wait">
                                    {inputType === 'url' ? (
                                        <motion.div
                                            key="url-input"
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, y: -10 }}
                                            transition={{ duration: 0.2 }}
                                        >
                                            <label htmlFor="url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                                                Resource URL
                                            </label>
                                            <div className="relative group">
                                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                                    <Link className="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                                                </div>
                                                <Input
                                                    id="url"
                                                    value={url}
                                                    onChange={(e) => setUrl(e.target.value)}
                                                    placeholder="https://example.com/article"
                                                    className="pl-10 bg-white dark:bg-gray-950 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                                                    required={inputType === 'url'}
                                                    autoFocus
                                                />
                                            </div>
                                        </motion.div>
                                    ) : (
                                        <motion.div
                                            key="file-input"
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, y: -10 }}
                                            transition={{ duration: 0.2 }}
                                        >
                                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                                                Select File
                                            </label>
                                            <div
                                                className={`
                                                    relative mt-1 flex flex-col justify-center px-6 pt-8 pb-8 border-2 border-dashed rounded-xl transition-all duration-200 cursor-pointer
                                                    ${dragActive
                                                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 scale-[1.02]'
                                                        : 'border-gray-300 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-gray-50 dark:hover:bg-gray-800/50'
                                                    }
                                                    ${file ? 'border-green-500 bg-green-50 dark:bg-green-900/20' : 'bg-white dark:bg-gray-950'}
                                                `}
                                                onDragEnter={handleDrag}
                                                onDragLeave={handleDrag}
                                                onDragOver={handleDrag}
                                                onDrop={handleDrop}
                                                onClick={() => fileInputRef.current?.click()}
                                            >
                                                <input
                                                    ref={fileInputRef}
                                                    type="file"
                                                    className="hidden"
                                                    onChange={handleFileChange}
                                                    required={inputType === 'file'}
                                                />

                                                <div className="space-y-2 text-center">
                                                    {file ? (
                                                        <motion.div
                                                            initial={{ scale: 0.5, opacity: 0 }}
                                                            animate={{ scale: 1, opacity: 1 }}
                                                            className="flex flex-col items-center"
                                                        >
                                                            <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mb-2">
                                                                <CheckCircle2 className="w-6 h-6 text-green-600 dark:text-green-400" />
                                                            </div>
                                                            <p className="text-sm font-medium text-green-700 dark:text-green-300 truncate max-w-[200px]">
                                                                {file.name}
                                                            </p>
                                                            <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                                                                {(file.size / 1024 / 1024).toFixed(2)} MB
                                                            </p>
                                                            <button
                                                                type="button"
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    setFile(null);
                                                                }}
                                                                className="mt-3 text-xs text-red-500 hover:text-red-600 font-medium hover:underline"
                                                            >
                                                                Remove file
                                                            </button>
                                                        </motion.div>
                                                    ) : (
                                                        <>
                                                            <div className="mx-auto w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform duration-200">
                                                                <Upload className="w-6 h-6 text-blue-500 dark:text-blue-400" />
                                                            </div>
                                                            <div className="flex flex-col text-sm text-gray-600 dark:text-gray-400">
                                                                <span className="font-semibold text-blue-600 dark:text-blue-400">Click to upload</span>
                                                                <span className="mt-1">or drag and drop</span>
                                                            </div>
                                                            <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                                                                PDF, DOCX, TXT up to 10MB
                                                            </p>
                                                        </>
                                                    )}
                                                </div>
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>

                                <div className="space-y-4 pt-2">
                                    <div>
                                        <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                                            Title <span className="text-gray-400 font-normal">(Optional)</span>
                                        </label>
                                        <Input
                                            id="title"
                                            value={title}
                                            onChange={(e) => setTitle(e.target.value)}
                                            placeholder="Enter a custom title"
                                            className="bg-white dark:bg-gray-950 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                                        />
                                    </div>

                                    <div>
                                        <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                                            Description <span className="text-gray-400 font-normal">(Optional)</span>
                                        </label>
                                        <textarea
                                            id="description"
                                            value={description}
                                            onChange={(e) => setDescription(e.target.value)}
                                            rows={3}
                                            className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition-shadow resize-none text-gray-900 dark:text-gray-100"
                                            placeholder="Add a brief description..."
                                        />
                                    </div>
                                </div>
                            </form>

                            <div className="p-6 border-t border-gray-100 dark:border-gray-800 flex justify-end gap-3 shrink-0 bg-gray-50/50 dark:bg-gray-800/50">
                                <Button type="button" variant="ghost" onClick={onClose} className="hover:bg-gray-200/50 dark:hover:bg-gray-700/50">
                                    Cancel
                                </Button>
                                <Button
                                    onClick={handleSubmit}
                                    disabled={isSubmitting || (inputType === 'url' && !url) || (inputType === 'file' && !file)}
                                    className="min-w-[120px] shadow-lg shadow-blue-500/20"
                                >
                                    {isSubmitting ? (
                                        <span className="flex items-center gap-2">
                                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                            Adding...
                                        </span>
                                    ) : (
                                        'Add Resource'
                                    )}
                                </Button>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};
