/**
 * FileTree Component
 * 
 * Displays a hierarchical file tree for repository navigation.
 * For now, this is a simple list view. Future enhancements will add:
 * - Hierarchical folder structure
 * - File icons by type
 * - Search/filter functionality
 * - Lazy loading for large repositories
 */

import { useState, useEffect } from 'react';
import { File, Folder, ChevronRight, ChevronDown, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface FileNode {
  id: string;
  name: string;
  type: 'file' | 'folder';
  path: string;
  children?: FileNode[];
}

interface FileTreeProps {
  repositoryId: string;
  selectedFileId: string | null;
  onFileSelect: (fileId: string) => void;
}

// ============================================================================
// Mock Data (TODO: Replace with API call)
// ============================================================================

const mockFileTree: FileNode[] = [
  {
    id: 'src',
    name: 'src',
    type: 'folder',
    path: 'src',
    children: [
      {
        id: 'components',
        name: 'components',
        type: 'folder',
        path: 'src/components',
        children: [
          { id: 'Button', name: 'Button.tsx', type: 'file', path: 'src/components/Button.tsx' },
          { id: 'Card', name: 'Card.tsx', type: 'file', path: 'src/components/Card.tsx' },
          { id: 'Input', name: 'Input.tsx', type: 'file', path: 'src/components/Input.tsx' },
        ],
      },
      {
        id: 'lib',
        name: 'lib',
        type: 'folder',
        path: 'src/lib',
        children: [
          { id: 'utils', name: 'utils.ts', type: 'file', path: 'src/lib/utils.ts' },
          { id: 'api', name: 'api.ts', type: 'file', path: 'src/lib/api.ts' },
        ],
      },
      { id: 'App', name: 'App.tsx', type: 'file', path: 'src/App.tsx' },
      { id: 'main', name: 'main.tsx', type: 'file', path: 'src/main.tsx' },
    ],
  },
  {
    id: 'public',
    name: 'public',
    type: 'folder',
    path: 'public',
    children: [
      { id: 'index', name: 'index.html', type: 'file', path: 'public/index.html' },
    ],
  },
  { id: 'package', name: 'package.json', type: 'file', path: 'package.json' },
  { id: 'tsconfig', name: 'tsconfig.json', type: 'file', path: 'tsconfig.json' },
  { id: 'README', name: 'README.md', type: 'file', path: 'README.md' },
];

// ============================================================================
// FileTreeNode Component
// ============================================================================

interface FileTreeNodeProps {
  node: FileNode;
  level: number;
  selectedFileId: string | null;
  onFileSelect: (fileId: string) => void;
}

function FileTreeNode({ node, level, selectedFileId, onFileSelect }: FileTreeNodeProps) {
  const [isExpanded, setIsExpanded] = useState(level === 0); // Auto-expand root level

  const handleClick = () => {
    if (node.type === 'folder') {
      setIsExpanded(!isExpanded);
    } else {
      onFileSelect(node.id);
    }
  };

  const isSelected = node.type === 'file' && node.id === selectedFileId;

  return (
    <div>
      {/* Node Item */}
      <button
        onClick={handleClick}
        className={cn(
          'w-full flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-accent rounded-sm transition-colors',
          isSelected && 'bg-accent text-accent-foreground font-medium'
        )}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
      >
        {/* Folder Chevron */}
        {node.type === 'folder' && (
          <span className="flex-shrink-0">
            {isExpanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </span>
        )}

        {/* Icon */}
        <span className="flex-shrink-0">
          {node.type === 'folder' ? (
            <Folder className="h-4 w-4 text-blue-500" />
          ) : (
            <File className="h-4 w-4 text-muted-foreground" />
          )}
        </span>

        {/* Name */}
        <span className="truncate text-left">{node.name}</span>
      </button>

      {/* Children */}
      {node.type === 'folder' && isExpanded && node.children && (
        <div>
          {node.children.map((child) => (
            <FileTreeNode
              key={child.id}
              node={child}
              level={level + 1}
              selectedFileId={selectedFileId}
              onFileSelect={onFileSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// FileTree Component
// ============================================================================

export function FileTree({ repositoryId, selectedFileId, onFileSelect }: FileTreeProps) {
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // TODO: Replace with actual API call
    // const fetchFileTree = async () => {
    //   const response = await fetch(`/api/repositories/${repositoryId}/files`);
    //   const data = await response.json();
    //   setFileTree(data);
    // };

    // Simulate API delay
    setTimeout(() => {
      setFileTree(mockFileTree);
      setIsLoading(false);
    }, 300);
  }, [repositoryId]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="py-2">
      <div className="px-3 py-2 text-sm font-semibold text-muted-foreground">
        Files
      </div>
      <div className="space-y-0.5">
        {fileTree.map((node) => (
          <FileTreeNode
            key={node.id}
            node={node}
            level={0}
            selectedFileId={selectedFileId}
            onFileSelect={onFileSelect}
          />
        ))}
      </div>
    </div>
  );
}
