import { createFileRoute } from '@tanstack/react-router';
import { useEffect, useState } from 'react';
import { useRepositoryStore, mapResourceToRepository } from '@/stores/repository';
import { useEditorStore } from '@/stores/editor';
import { useResources } from '@/lib/hooks/useWorkbenchData';
import { CodeEditorView } from '@/features/editor/CodeEditorView';
import type { CodeFile } from '@/features/editor/types';
import { FileTree } from '@/components/features/repositories/FileTree';
import { RepositoryHeader } from '@/components/features/repositories/RepositoryHeader';
import { Loader2 } from 'lucide-react';

const RepositoriesPage = () => {
  // Use TanStack Query hook for data fetching
  const { data: resources, isLoading, error } = useResources();
  
  // Use repository store for UI state
  const { activeRepositoryId, setActiveRepository } = useRepositoryStore();
  const { activeFile, setActiveFile } = useEditorStore();
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);

  // Map resources to repositories
  const repositories = resources?.map(mapResourceToRepository) || [];
  const activeRepository = repositories.find(r => r.id === activeRepositoryId);

  // Set first repository as active if none selected
  useEffect(() => {
    if (repositories.length > 0 && !activeRepositoryId) {
      setActiveRepository(repositories[0].id);
    }
  }, [repositories, activeRepositoryId, setActiveRepository]);

  // Handle file selection from file tree
  const handleFileSelect = async (fileId: string) => {
    setSelectedFileId(fileId);
    
    // TODO: Replace with actual API call to fetch file content
    // For now, create a mock CodeFile
    const mockFile: CodeFile = {
      id: fileId,
      resource_id: activeRepository?.id || '',
      path: `src/components/${fileId}.tsx`,
      name: `${fileId}.tsx`,
      language: 'typescript',
      content: `// Mock file content for ${fileId}\n\nfunction ${fileId}() {\n  return <div>Hello from ${fileId}</div>;\n}\n\nexport default ${fileId};`,
      size: 1024,
      lines: 5,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    setActiveFile(mockFile);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Repositories</h1>
          <p className="text-muted-foreground">
            Manage and explore your code repositories
          </p>
        </div>
        
        <div className="rounded-lg border bg-destructive/10 p-8 text-center">
          <p className="text-destructive">
            Failed to load repositories. Please try again later.
          </p>
        </div>
      </div>
    );
  }

  // No repositories state
  if (!activeRepository) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Repositories</h1>
          <p className="text-muted-foreground">
            Manage and explore your code repositories
          </p>
        </div>
        
        <div className="rounded-lg border bg-card p-8 text-center">
          <p className="text-muted-foreground">
            No repositories found. Add a repository to get started.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Repository Header */}
      <RepositoryHeader repository={activeRepository} />

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* File Tree Sidebar */}
        <div className="w-64 border-r bg-card overflow-y-auto">
          <FileTree
            repositoryId={activeRepository.id}
            selectedFileId={selectedFileId}
            onFileSelect={handleFileSelect}
          />
        </div>

        {/* Code Editor Area */}
        <div className="flex-1 overflow-hidden">
          {activeFile ? (
            <CodeEditorView file={activeFile} className="h-full" />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-2">
                <p className="text-muted-foreground">
                  Select a file from the tree to view its contents
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/_auth/repositories')({
  component: RepositoriesPage,
});
