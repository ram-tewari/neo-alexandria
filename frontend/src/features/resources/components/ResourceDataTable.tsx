/**
 * ResourceDataTable component
 * 
 * Displays paginated resource list with sorting, status badges, and quality indicators.
 */
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  type ColumnDef,
} from '@tanstack/react-table';
import { Link } from '@tanstack/react-router';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { StatusBadge } from './StatusBadge';
import { TableSkeleton } from './TableSkeleton';
import type { Resource } from '@/core/types/resource';
import { cn } from '@/lib/utils';

interface ResourceDataTableProps {
  data: Resource[];
  isLoading: boolean;
  page: number;
  totalPages: number;
  totalResources: number;
  onPageChange: (page: number) => void;
  onSortChange?: (sort: string) => void;
}

/**
 * Data table for displaying resources with pagination
 */
export function ResourceDataTable({
  data,
  isLoading,
  page,
  totalPages,
  totalResources,
  onPageChange,
}: ResourceDataTableProps) {
  const columns: ColumnDef<Resource>[] = [
    {
      accessorKey: 'ingestion_status',
      header: 'Status',
      cell: ({ row }) => (
        <StatusBadge status={row.original.ingestion_status} />
      ),
    },
    {
      accessorKey: 'title',
      header: 'Title',
      cell: ({ row }) => (
        <Link
          to="/resources/$resourceId"
          params={{ resourceId: row.original.id }}
          className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
        >
          {row.original.title}
        </Link>
      ),
    },
    {
      accessorKey: 'classification_code',
      header: 'Classification',
      cell: ({ row }) => {
        const code = row.original.classification_code;
        return code ? (
          <Badge variant="outline">{code}</Badge>
        ) : (
          <span className="text-gray-400">—</span>
        );
      },
    },
    {
      accessorKey: 'quality_score',
      header: 'Quality',
      cell: ({ row }) => {
        const score = row.original.quality_score;
        const colorClass = getQualityColorClass(score);
        return (
          <span className={cn('font-medium', colorClass)}>
            {score.toFixed(2)}
          </span>
        );
      },
    },
    {
      accessorKey: 'created_at',
      header: 'Date',
      cell: ({ row }) => {
        const date = new Date(row.original.created_at);
        return (
          <span className="text-sm text-gray-600">
            {date.toLocaleDateString()}
          </span>
        );
      },
    },
  ];

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
    manualSorting: true,
    pageCount: totalPages,
  });

  if (isLoading) {
    return <TableSkeleton />;
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No resources found</p>
        <p className="text-sm mt-2">Start by ingesting your first resource</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Page {page} of {totalPages} ({totalResources} total resources)
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(page - 1)}
            disabled={page === 1}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(page + 1)}
            disabled={page === totalPages}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}

/**
 * Get color class based on quality score
 */
function getQualityColorClass(score: number): string {
  if (score < 0.5) {
    return 'text-red-600';
  } else if (score < 0.7) {
    return 'text-yellow-600';
  } else {
    return 'text-green-600';
  }
}
