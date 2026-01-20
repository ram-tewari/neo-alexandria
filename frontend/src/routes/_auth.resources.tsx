import { useState, lazy, Suspense } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { ResourceDataTable } from '@/features/resources/components/ResourceDataTable';
import { useResourceList } from '@/features/resources/hooks/useResourceList';
import { useMinimumLoadingDuration } from '@/features/resources/hooks/useMinimumLoadingDuration';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

// Lazy load the IngestionWizard dialog
const IngestionWizard = lazy(() => 
  import('@/features/resources/components/IngestionWizard').then(module => ({
    default: module.IngestionWizard
  }))
);

export const Route = createFileRoute('/_auth/resources')({
  component: ResourcesPage,
});

function ResourcesPage() {
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState('created_at:desc');
  const [showWizard, setShowWizard] = useState(false);
  const limit = 25;

  const { data, isLoading } = useResourceList({ page, limit, sort });
  const isLoadingWithMinimum = useMinimumLoadingDuration(isLoading);

  const totalPages = Math.ceil((data?.total || 0) / limit);

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Resource Library</h1>
          <p className="text-muted-foreground">
            Manage and browse your knowledge base
          </p>
        </div>
        {showWizard ? (
          <Suspense fallback={
            <Button disabled>
              <Plus className="mr-2 h-4 w-4" />
              Add Resource
            </Button>
          }>
            <IngestionWizard />
          </Suspense>
        ) : (
          <Button onClick={() => setShowWizard(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Add Resource
          </Button>
        )}
      </div>

      <ResourceDataTable
        data={data?.items || []}
        isLoading={isLoadingWithMinimum}
        page={page}
        totalPages={totalPages}
        totalResources={data?.total || 0}
        onPageChange={setPage}
        onSortChange={setSort}
      />
    </div>
  );
}
