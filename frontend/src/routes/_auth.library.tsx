import { createFileRoute } from '@tanstack/react-router';

const LibraryPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Library</h1>
        <p className="text-muted-foreground">
          Browse and manage your knowledge base
        </p>
      </div>
      
      <div className="rounded-lg border bg-card p-8 text-center">
        <p className="text-muted-foreground">
          Library interface coming soon...
        </p>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/_auth/library')({
  component: LibraryPage,
});
