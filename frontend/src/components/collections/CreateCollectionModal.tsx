// Neo Alexandria 2.0 Frontend - Create Collection Modal
// Modal for creating new collections with hierarchical parent selection

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Modal, ModalFooter } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useCreateCollection, useCollections } from '@/hooks/useCollections';
import { useAppStore } from '@/store';
import { toast } from '@/store/toastStore';
import { FolderPlus, Lock, Users, Globe } from 'lucide-react';
import { cn } from '@/utils/cn';
import type { CreateCollectionRequest } from '@/services/api/collections';

interface CreateCollectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  parentId?: string;
}

type Visibility = 'private' | 'shared' | 'public';

const CreateCollectionModal: React.FC<CreateCollectionModalProps> = ({
  isOpen,
  onClose,
  parentId,
}) => {
  const navigate = useNavigate();
  const userId = useAppStore((state) => state.userId) || 'demo-user';
  
  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [visibility, setVisibility] = useState<Visibility>('private');
  const [selectedParentId, setSelectedParentId] = useState<string | undefined>(parentId);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch collections for parent selector
  const { data: collectionsData } = useCollections({ user_id: userId });
  const collections = collectionsData?.items || [];

  // Create collection mutation
  const createMutation = useCreateCollection();

  // Visibility options
  const visibilityOptions = [
    {
      value: 'private' as Visibility,
      label: 'Private',
      description: 'Only you can see this collection',
      icon: <Lock className="w-5 h-5" />,
    },
    {
      value: 'shared' as Visibility,
      label: 'Shared',
      description: 'Share with specific users',
      icon: <Users className="w-5 h-5" />,
    },
    {
      value: 'public' as Visibility,
      label: 'Public',
      description: 'Anyone can view this collection',
      icon: <Globe className="w-5 h-5" />,
    },
  ];

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!name.trim()) {
      newErrors.name = 'Collection name is required';
    } else if (name.trim().length < 3) {
      newErrors.name = 'Collection name must be at least 3 characters';
    } else if (name.trim().length > 100) {
      newErrors.name = 'Collection name must be less than 100 characters';
    }

    if (description && description.length > 500) {
      newErrors.description = 'Description must be less than 500 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const collectionData: CreateCollectionRequest = {
      name: name.trim(),
      description: description.trim() || undefined,
      visibility,
      parent_id: selectedParentId,
    };

    try {
      const newCollection = await createMutation.mutateAsync({
        data: collectionData,
        userId,
      });

      toast.success('Collection created', `"${collectionData.name}" has been created successfully`);
      
      // Reset form
      handleClose();
      
      // Navigate to the new collection
      if (newCollection && typeof newCollection === 'object' && 'id' in newCollection) {
        navigate(`/collections/${newCollection.id}`);
      } else {
        navigate('/collections');
      }
    } catch (error: any) {
      toast.error('Failed to create collection', error?.response?.data?.detail || error.message);
    }
  };

  // Handle modal close
  const handleClose = () => {
    setName('');
    setDescription('');
    setVisibility('private');
    setSelectedParentId(parentId);
    setErrors({});
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Create New Collection"
      description="Organize your resources into collections"
      size="lg"
    >
      <form onSubmit={handleSubmit}>
        <div className="space-y-6">
          {/* Collection Name */}
          <Input
            label="Collection Name"
            placeholder="e.g., Machine Learning Papers"
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={errors.name}
            leftIcon={<FolderPlus className="w-4 h-4" />}
            required
            autoFocus
          />

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-charcoal-grey-300 mb-1">
              Description (Optional)
            </label>
            <textarea
              className={cn(
                'w-full px-3 py-2 text-sm',
                'bg-charcoal-grey-900 border border-charcoal-grey-700 rounded-lg text-charcoal-grey-50',
                'placeholder-charcoal-grey-500',
                'transition-colors duration-200',
                'focus:outline-none focus:ring-2 focus:ring-accent-blue-500 focus:border-accent-blue-500',
                'resize-none',
                errors.description && 'border-red-500 focus:ring-red-500'
              )}
              placeholder="Describe what this collection is about..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-500">{errors.description}</p>
            )}
            <p className="mt-1 text-xs text-charcoal-grey-500">
              {description.length}/500 characters
            </p>
          </div>

          {/* Visibility */}
          <div>
            <label className="block text-sm font-medium text-charcoal-grey-300 mb-3">
              Visibility
            </label>
            <div className="grid grid-cols-1 gap-3">
              {visibilityOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setVisibility(option.value)}
                  className={cn(
                    'flex items-start p-4 rounded-lg border-2 transition-all duration-200',
                    'hover:border-accent-blue-500/50',
                    visibility === option.value
                      ? 'border-accent-blue-500 bg-accent-blue-500/10'
                      : 'border-charcoal-grey-700 bg-charcoal-grey-900'
                  )}
                >
                  <div
                    className={cn(
                      'flex-shrink-0 mt-0.5',
                      visibility === option.value ? 'text-accent-blue-400' : 'text-charcoal-grey-500'
                    )}
                  >
                    {option.icon}
                  </div>
                  <div className="ml-3 text-left">
                    <div className="text-sm font-medium text-charcoal-grey-50">
                      {option.label}
                    </div>
                    <div className="text-xs text-charcoal-grey-400 mt-0.5">
                      {option.description}
                    </div>
                  </div>
                  {visibility === option.value && (
                    <div className="ml-auto flex-shrink-0">
                      <div className="w-5 h-5 rounded-full bg-accent-blue-500 flex items-center justify-center">
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                          <path d="M10 3L4.5 8.5L2 6" stroke="currentColor" strokeWidth="2" fill="none" />
                        </svg>
                      </div>
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Parent Collection */}
          {collections.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-charcoal-grey-300 mb-1">
                Parent Collection (Optional)
              </label>
              <select
                className={cn(
                  'w-full px-3 py-2 text-sm',
                  'bg-charcoal-grey-900 border border-charcoal-grey-700 rounded-lg text-charcoal-grey-50',
                  'focus:outline-none focus:ring-2 focus:ring-accent-blue-500 focus:border-accent-blue-500',
                  'transition-colors duration-200'
                )}
                value={selectedParentId || ''}
                onChange={(e) => setSelectedParentId(e.target.value || undefined)}
              >
                <option value="">None (Top-level collection)</option>
                {collections.map((collection) => (
                  <option key={collection.id} value={collection.id}>
                    {collection.name}
                  </option>
                ))}
              </select>
              <p className="mt-1 text-xs text-charcoal-grey-500">
                Nest this collection under another collection
              </p>
            </div>
          )}
        </div>

        <ModalFooter className="mt-6">
          <Button
            type="button"
            variant="ghost"
            onClick={handleClose}
            disabled={createMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            loading={createMutation.isPending}
            icon={<FolderPlus className="w-4 h-4" />}
          >
            Create Collection
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
};

export { CreateCollectionModal };
export type { CreateCollectionModalProps };
