import { createFileRoute } from '@tanstack/react-router';

const OpsPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Ops</h1>
        <p className="text-muted-foreground">
          System operations and monitoring
        </p>
      </div>
      
      <div className="rounded-lg border bg-card p-8 text-center">
        <p className="text-muted-foreground">
          Operations dashboard coming soon...
        </p>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/_auth/ops')({
  component: OpsPage,
});
