import { createFileRoute } from '@tanstack/react-router';
import { useEffect, useState } from 'react';
import { useRepositoryStore } from '@/stores/repository';
import { useEditorStore } from '@/stores/editor';
import { CodeEditorView } from '@/features/editor/CodeEditorView';
import type { CodeFile } from '@/features/editor/types';
import { FileTree } from '@/components/features/repositories/FileTree';
import { RepositoryHeader } from '@/components/features/repositories/RepositoryHeader';
import { Loader2 } from 'lucide-react';

const RepositoriesPage = () => {
  const { repositories, activeRepository, isLoading, fetchRepositories } = useRepositoryStore();
  const { activeFile, setActiveFile } = useEditorStore();
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);

  // Fetch repositories on mount
  useEffect(() => {
    fetchRepositories();
  }, [fetchRepositories]);

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
