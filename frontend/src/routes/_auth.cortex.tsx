import { createFileRoute } from '@tanstack/react-router';

const CortexPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Cortex</h1>
        <p className="text-muted-foreground">
          AI-powered insights and analysis
        </p>
      </div>
      
      <div className="rounded-lg border bg-card p-8 text-center">
        <p className="text-muted-foreground">
          AI insights interface coming soon...
        </p>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/_auth/cortex')({
  component: CortexPage,
});
