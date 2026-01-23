import { createFileRoute } from '@tanstack/react-router';

const WikiPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Wiki</h1>
        <p className="text-muted-foreground">
          Documentation and knowledge articles
        </p>
      </div>
      
      <div className="rounded-lg border bg-card p-8 text-center">
        <p className="text-muted-foreground">
          Wiki interface coming soon...
        </p>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/_auth/wiki')({
  component: WikiPage,
});
