/**
 * Phase 1 Commands
 * 
 * Commands for Phase 1 Core Resource Management features:
 * - File upload
 * - URL ingestion
 * - Resource filtering
 * - Batch mode toggle
 */

import { commandRegistry, type Command } from './commandRegistry';
import { icons } from '@/config/icons';

export function registerPhase1Commands(
  navigate: (path: string) => void,
  callbacks?: {
    onUploadFile?: () => void;
    onUploadURL?: () => void;
    onFilterResources?: () => void;
    onToggleBatchMode?: () => void;
  }
) {
  const commands: Command[] = [
    // Upload Commands
    {
      id: 'phase1-upload-file',
      label: 'Upload File',
      description: 'Upload files to your library',
      icon: icons.add,
      keywords: ['upload', 'file', 'add', 'import', 'document', 'pdf'],
      category: 'action',
      action: () => {
        if (callbacks?.onUploadFile) {
          callbacks.onUploadFile();
        } else {
          navigate('/upload');
        }
      },
      shortcut: 'U F',
      priority: 85,
    },
    {
      id: 'phase1-upload-url',
      label: 'Upload from URL',
      description: 'Add a resource by URL',
      icon: icons.add,
      keywords: ['upload', 'url', 'link', 'web', 'import', 'online'],
      category: 'action',
      action: () => {
        if (callbacks?.onUploadURL) {
          callbacks.onUploadURL();
        } else {
          navigate('/upload');
        }
      },
      shortcut: 'U U',
      priority: 80,
    },
    
    // Filter Commands
    {
      id: 'phase1-filter-resources',
      label: 'Filter Resources',
      description: 'Open filter sidebar to refine results',
      icon: icons.filter,
      keywords: ['filter', 'search', 'refine', 'narrow', 'sort'],
      category: 'filter',
      action: () => {
        if (callbacks?.onFilterResources) {
          callbacks.onFilterResources();
        } else {
          // Default: navigate to library with focus on filters
          navigate('/library');
        }
      },
      shortcut: 'F',
      priority: 75,
    },
    
    // Batch Mode Commands
    {
      id: 'phase1-batch-mode',
      label: 'Toggle Batch Mode',
      description: 'Enable batch selection for bulk operations',
      icon: icons.check,
      keywords: ['batch', 'select', 'multiple', 'bulk', 'mass'],
      category: 'action',
      action: () => {
        if (callbacks?.onToggleBatchMode) {
          callbacks.onToggleBatchMode();
        } else {
          console.log('Batch mode toggle - navigate to library');
          navigate('/library');
        }
      },
      shortcut: 'B',
      priority: 70,
    },
  ];

  // Register all commands
  commandRegistry.registerMany(commands);
}

export function unregisterPhase1Commands() {
  const commandIds = [
    'phase1-upload-file',
    'phase1-upload-url',
    'phase1-filter-resources',
    'phase1-batch-mode',
  ];

  commandIds.forEach(id => commandRegistry.unregister(id));
}
