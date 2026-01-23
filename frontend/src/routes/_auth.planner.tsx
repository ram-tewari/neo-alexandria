import { createFileRoute } from '@tanstack/react-router';

const PlannerPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Planner</h1>
        <p className="text-muted-foreground">
          Plan and organize your tasks
        </p>
      </div>
      
      <div className="rounded-lg border bg-card p-8 text-center">
        <p className="text-muted-foreground">
          Task planner interface coming soon...
        </p>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/_auth/planner')({
  component: PlannerPage,
});
