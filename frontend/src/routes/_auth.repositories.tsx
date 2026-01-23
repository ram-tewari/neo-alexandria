import { createFileRoute } from '@tanstack/react-router';

const RepositoriesPage = () => {
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
          Repository management interface coming soon...
        </p>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/_auth/repositories')({
  component: RepositoriesPage,
});
