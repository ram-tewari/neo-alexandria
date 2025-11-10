// Neo Alexandria 2.0 Frontend - Bulk Action Bar Component
// Sticky action bar for bulk operations on selected resources

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Trash2, 
  Edit, 
  FolderPlus, 
  Tag, 
  X,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { useAppStore } from '@/store';
import { useDeleteResource, useUpdateResource, useBatchUpdate } from '@/hooks/useApi';
import { cn } from '@/utils/cn';

interface BulkActionBarProps {
  selectedCount: number;
  onClearSelection: () => void;
}

export const BulkActionBar: React.FC<BulkActionBarProps> = ({
  selectedCount,
  onClearSelection,
}) => {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showCollectionModal, setShowCollectionModal] = useState(false);
  const [showClassifyModal, setShowClassifyModal] = useState(false);
  
  const selectedResources = useAppStore(state => state.selectedResources);
  const addNotification = useAppStore(state => state.addNotification);
  
  const deleteResource = useDeleteResource();
  const batchUpdate = useBatchUpdate();

  const handleBulkDelete = async () => {
    try {
      // Delete resources one by one
      for (const resourceId of selectedResources) {
        await deleteResource.mutateAsync(resourceId);
      }
      
      addNotification({
        type: 'success',
        title: 'Resources Deleted',
        message: `Successfully deleted ${selectedCount} resource${selectedCount > 1 ? 's' : ''}`,
      });
      
      onClearSelection();
      setShowDeleteConfirm(false);
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Delete Failed',
        message: 'Failed to delete some resources',
      });
    }
  };

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="sticky top-16 z-10 bg-accent-blue-600 rounded-lg shadow-lg p-4 mb-4"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-white" />
              <span className="text-white font-medium">
                {selectedCount} resource{selectedCount > 1 ? 's' : ''} selected
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowEditModal(true)}
                icon={<Edit className="w-4 h-4" />}
                className="text-white hover:bg-white/20"
              >
                Edit Metadata
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowCollectionModal(true)}
                icon={<FolderPlus className="w-4 h-4" />}
                className="text-white hover:bg-white/20"
              >
                Add to Collection
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowClassifyModal(true)}
                icon={<Tag className="w-4 h-4" />}
                className="text-white hover:bg-white/20"
              >
                Classify
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDeleteConfirm(true)}
                icon={<Trash2 className="w-4 h-4" />}
                className="text-white hover:bg-red-500/20"
              >
                Delete
              </Button>
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onClearSelection}
            icon={<X className="w-4 h-4" />}
            className="text-white hover:bg-white/20"
          >
            Clear Selection
          </Button>
        </div>
      </motion.div>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        title="Delete Resources"
      >
        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-charcoal-grey-200">
                Are you sure you want to delete {selectedCount} resource{selectedCount > 1 ? 's' : ''}?
              </p>
              <p className="text-charcoal-grey-400 text-sm mt-1">
                This action cannot be undone.
              </p>
            </div>
          </div>
          
          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => setShowDeleteConfirm(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleBulkDelete}
              loading={deleteResource.isPending}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete {selectedCount} Resource{selectedCount > 1 ? 's' : ''}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Edit Metadata Modal */}
      <BulkEditModal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        selectedResources={selectedResources}
        onSuccess={onClearSelection}
      />

      {/* Add to Collection Modal */}
      <AddToCollectionModal
        isOpen={showCollectionModal}
        onClose={() => setShowCollectionModal(false)}
        selectedResources={selectedResources}
        onSuccess={onClearSelection}
      />

      {/* Classify Modal */}
      <BulkClassifyModal
        isOpen={showClassifyModal}
        onClose={() => setShowClassifyModal(false)}
        selectedResources={selectedResources}
        onSuccess={onClearSelection}
      />
    </>
  );
};

// Bulk Edit Modal Component
interface BulkEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedResources: string[];
  onSuccess: () => void;
}

const BulkEditModal: React.FC<BulkEditModalProps> = ({
  isOpen,
  onClose,
  selectedResources,
  onSuccess,
}) => {
  const [readStatus, setReadStatus] = useState<string>('');
  const [addSubjects, setAddSubjects] = useState<string>('');
  
  const batchUpdate = useBatchUpdate();
  const addNotification = useAppStore(state => state.addNotification);

  const handleSubmit = async () => {
    const updates: any = {};
    
    if (readStatus) {
      updates.read_status = readStatus;
    }
    
    if (addSubjects) {
      updates.subject = addSubjects.split(',').map(s => s.trim()).filter(Boolean);
    }
    
    if (Object.keys(updates).length === 0) {
      addNotification({
        type: 'warning',
        title: 'No Changes',
        message: 'Please specify at least one field to update',
      });
      return;
    }
    
    try {
      await batchUpdate.mutateAsync({
        resource_ids: selectedResources,
        updates,
      });
      
      onSuccess();
      onClose();
    } catch (error) {
      // Error handled by mutation
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Edit Metadata">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-charcoal-grey-200 mb-2">
            Read Status
          </label>
          <select
            value={readStatus}
            onChange={(e) => setReadStatus(e.target.value)}
            className="w-full px-3 py-2 bg-charcoal-grey-800 border border-charcoal-grey-700 rounded-lg text-charcoal-grey-200 focus:outline-none focus:ring-2 focus:ring-accent-blue-500"
          >
            <option value="">-- No Change --</option>
            <option value="unread">Unread</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="archived">Archived</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-charcoal-grey-200 mb-2">
            Add Subjects (comma-separated)
          </label>
          <Input
            value={addSubjects}
            onChange={(e) => setAddSubjects(e.target.value)}
            placeholder="e.g., machine learning, AI, research"
          />
        </div>
        
        <div className="flex justify-end gap-2 pt-4">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            loading={batchUpdate.isPending}
          >
            Update {selectedResources.length} Resource{selectedResources.length > 1 ? 's' : ''}
          </Button>
        </div>
      </div>
    </Modal>
  );
};

// Add to Collection Modal Component
interface AddToCollectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedResources: string[];
  onSuccess: () => void;
}

const AddToCollectionModal: React.FC<AddToCollectionModalProps> = ({
  isOpen,
  onClose,
  selectedResources,
  onSuccess,
}) => {
  const addNotification = useAppStore(state => state.addNotification);

  const handleSubmit = () => {
    // TODO: Implement collection API integration
    addNotification({
      type: 'info',
      title: 'Coming Soon',
      message: 'Collection management will be available soon',
    });
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add to Collection">
      <div className="space-y-4">
        <p className="text-charcoal-grey-300">
          Select a collection to add {selectedResources.length} resource{selectedResources.length > 1 ? 's' : ''} to:
        </p>
        
        <div className="text-center py-8 text-charcoal-grey-400">
          Collection selection UI will be implemented in the Collections feature.
        </div>
        
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSubmit}>
            Add to Collection
          </Button>
        </div>
      </div>
    </Modal>
  );
};

// Bulk Classify Modal Component
interface BulkClassifyModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedResources: string[];
  onSuccess: () => void;
}

const BulkClassifyModal: React.FC<BulkClassifyModalProps> = ({
  isOpen,
  onClose,
  selectedResources,
  onSuccess,
}) => {
  const [classificationCode, setClassificationCode] = useState('');
  const batchUpdate = useBatchUpdate();
  const addNotification = useAppStore(state => state.addNotification);

  const handleSubmit = async () => {
    if (!classificationCode.trim()) {
      addNotification({
        type: 'warning',
        title: 'Missing Classification',
        message: 'Please enter a classification code',
      });
      return;
    }
    
    try {
      await batchUpdate.mutateAsync({
        resource_ids: selectedResources,
        updates: {
          classification_code: classificationCode.trim(),
        },
      });
      
      onSuccess();
      onClose();
    } catch (error) {
      // Error handled by mutation
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Classify Resources">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-charcoal-grey-200 mb-2">
            Classification Code
          </label>
          <Input
            value={classificationCode}
            onChange={(e) => setClassificationCode(e.target.value)}
            placeholder="e.g., 000, 100, 200"
          />
          <p className="text-xs text-charcoal-grey-400 mt-1">
            Enter a Dewey Decimal Classification code
          </p>
        </div>
        
        <div className="flex justify-end gap-2 pt-4">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            loading={batchUpdate.isPending}
          >
            Classify {selectedResources.length} Resource{selectedResources.length > 1 ? 's' : ''}
          </Button>
        </div>
      </div>
    </Modal>
  );
};
