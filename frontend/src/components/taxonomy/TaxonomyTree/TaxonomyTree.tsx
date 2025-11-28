import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronDown, Plus, Edit2, Trash2, GripVertical } from 'lucide-react';
import { TaxonomyNode } from '@/types/taxonomy';
import { useCreateNode, useUpdateNode, useMoveNode, useDeleteNode } from '@/hooks/useTaxonomy';
import { useReducedMotion } from '@/hooks/useReducedMotion';

interface TaxonomyTreeProps {
  nodes: TaxonomyNode[];
  selectedId?: string;
  onNodeSelect?: (id: string) => void;
}

export const TaxonomyTree: React.FC<TaxonomyTreeProps> = ({
  nodes,
  selectedId,
  onNodeSelect,
}) => {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState('');
  const [creatingParentId, setCreatingParentId] = useState<string | null>(null);
  const [newNodeName, setNewNodeName] = useState('');

  const createNode = useCreateNode();
  const updateNode = useUpdateNode();
  const moveNode = useMoveNode();
  const deleteNode = useDeleteNode();
  const prefersReducedMotion = useReducedMotion();

  const toggleExpand = (id: string) => {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedIds(newExpanded);
  };

  const startEdit = (node: TaxonomyNode) => {
    setEditingId(node.id);
    setEditName(node.name);
  };

  const saveEdit = () => {
    if (editingId && editName.trim()) {
      updateNode.mutate({ nodeId: editingId, name: editName.trim() });
      setEditingId(null);
    }
  };

  const startCreate = (parentId: string | null) => {
    setCreatingParentId(parentId);
    setNewNodeName('');
  };

  const saveCreate = () => {
    if (newNodeName.trim()) {
      createNode.mutate({ parentId: creatingParentId, name: newNodeName.trim() });
      setCreatingParentId(null);
    }
  };

  const handleDelete = (nodeId: string) => {
    if (window.confirm('Delete this category and all subcategories?')) {
      deleteNode.mutate(nodeId);
    }
  };

  const renderNode = (node: TaxonomyNode, depth: number = 0) => {
    const isExpanded = expandedIds.has(node.id);
    const isSelected = selectedId === node.id;
    const isEditing = editingId === node.id;
    const hasChildren = node.children.length > 0;

    return (
      <div key={node.id}>
        <motion.div
          initial={prefersReducedMotion ? {} : { opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className={`flex items-center gap-2 py-2 px-3 rounded-lg transition-colors ${
            isSelected
              ? 'bg-primary-100 dark:bg-primary-900/20'
              : 'hover:bg-gray-100 dark:hover:bg-gray-800'
          }`}
          style={{ paddingLeft: `${depth * 24 + 12}px` }}
        >
          {/* Expand/Collapse */}
          {hasChildren ? (
            <button
              onClick={() => toggleExpand(node.id)}
              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            >
              {isExpanded ? (
                <ChevronDown className="w-4 h-4 text-gray-600 dark:text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-600 dark:text-gray-400" />
              )}
            </button>
          ) : (
            <div className="w-6" />
          )}

          {/* Drag Handle */}
          <GripVertical className="w-4 h-4 text-gray-400 cursor-move" />

          {/* Node Content */}
          {isEditing ? (
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && saveEdit()}
              onBlur={saveEdit}
              className="flex-1 px-2 py-1 text-sm border border-primary-500 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none"
              autoFocus
            />
          ) : (
            <button
              onClick={() => onNodeSelect?.(node.id)}
              className="flex-1 text-left text-sm font-medium text-gray-900 dark:text-white"
            >
              {node.name}
            </button>
          )}

          {/* Resource Count Badge */}
          <span className="px-2 py-0.5 text-xs font-medium bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">
            {node.resourceCount}
          </span>

          {/* Actions */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => startCreate(node.id)}
              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
              title="Add subcategory"
            >
              <Plus className="w-3 h-3 text-gray-600 dark:text-gray-400" />
            </button>
            <button
              onClick={() => startEdit(node)}
              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
              title="Edit"
            >
              <Edit2 className="w-3 h-3 text-gray-600 dark:text-gray-400" />
            </button>
            <button
              onClick={() => handleDelete(node.id)}
              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
              title="Delete"
            >
              <Trash2 className="w-3 h-3 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        </motion.div>

        {/* Create New Node */}
        {creatingParentId === node.id && (
          <motion.div
            initial={prefersReducedMotion ? {} : { opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="flex items-center gap-2 py-2 px-3"
            style={{ paddingLeft: `${(depth + 1) * 24 + 12}px` }}
          >
            <div className="w-6" />
            <input
              type="text"
              value={newNodeName}
              onChange={(e) => setNewNodeName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && saveCreate()}
              onBlur={saveCreate}
              placeholder="New category name..."
              className="flex-1 px-2 py-1 text-sm border border-primary-500 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none"
              autoFocus
            />
          </motion.div>
        )}

        {/* Children */}
        <AnimatePresence>
          {isExpanded && hasChildren && (
            <motion.div
              initial={prefersReducedMotion ? {} : { opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              {node.children.map((child) => renderNode(child, depth + 1))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  };

  return (
    <div className="space-y-1">
      {/* Root Level Create */}
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Categories
        </h3>
        <button
          onClick={() => startCreate(null)}
          className="flex items-center gap-1 px-2 py-1 text-xs bg-primary-600 hover:bg-primary-700 text-white rounded transition-colors"
        >
          <Plus className="w-3 h-3" />
          Add Root
        </button>
      </div>

      {creatingParentId === null && (
        <motion.div
          initial={prefersReducedMotion ? {} : { opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="flex items-center gap-2 py-2 px-3"
        >
          <input
            type="text"
            value={newNodeName}
            onChange={(e) => setNewNodeName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && saveCreate()}
            onBlur={saveCreate}
            placeholder="New root category..."
            className="flex-1 px-2 py-1 text-sm border border-primary-500 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none"
            autoFocus
          />
        </motion.div>
      )}

      {/* Tree */}
      {nodes.map((node) => renderNode(node, 0))}

      {nodes.length === 0 && !creatingParentId && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
          No categories yet. Click "Add Root" to create one.
        </div>
      )}
    </div>
  );
};
