import { useState, useMemo } from 'react';
import { Copy, ExternalLink, Search, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useScholarlyAssets } from '@/lib/hooks/useScholarlyAssets';
import { Skeleton } from '@/components/loading/Skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface TableDrawerProps {
  resourceId: string;
  onJumpToTable?: (tableId: string, pageNumber: number) => void;
  className?: string;
}

type ExportFormat = 'csv' | 'json' | 'markdown';

export function TableDrawer({
  resourceId,
  onJumpToTable,
  className = '',
}: TableDrawerProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const { tables, isLoadingTables, hasTables } =
    useScholarlyAssets(resourceId);
  const { toast } = useToast();

  // Filter tables based on search query
  const filteredTables = useMemo(() => {
    if (!searchQuery.trim()) return tables;

    const query = searchQuery.toLowerCase();
    return tables.filter(
      (table) =>
        table.caption?.toLowerCase().includes(query) ||
        table.table_number?.toLowerCase().includes(query) ||
        JSON.stringify(table.data).toLowerCase().includes(query)
    );
  }, [tables, searchQuery]);

  const formatTableAsCSV = (tableData: string[][]): string => {
    return tableData
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\n');
  };

  const formatTableAsMarkdown = (tableData: string[][]): string => {
    if (tableData.length === 0) return '';

    const header = tableData[0];
    const rows = tableData.slice(1);

    let md = '| ' + header.join(' | ') + ' |\n';
    md += '| ' + header.map(() => '---').join(' | ') + ' |\n';
    rows.forEach((row) => {
      md += '| ' + row.join(' | ') + ' |\n';
    });

    return md;
  };

  const handleCopyTable = async (
    tableData: string[][],
    format: ExportFormat
  ) => {
    let content: string;

    switch (format) {
      case 'csv':
        content = formatTableAsCSV(tableData);
        break;
      case 'json':
        content = JSON.stringify(tableData, null, 2);
        break;
      case 'markdown':
        content = formatTableAsMarkdown(tableData);
        break;
      default:
        content = JSON.stringify(tableData);
    }

    try {
      await navigator.clipboard.writeText(content);
      toast({
        title: 'Copied!',
        description: `Table copied as ${format.toUpperCase()}`,
      });
    } catch (error) {
      toast({
        title: 'Copy failed',
        description: 'Failed to copy to clipboard',
        variant: 'destructive',
      });
    }
  };

  const handleJumpToTable = (tableId: string, pageNumber: number) => {
    if (onJumpToTable) {
      onJumpToTable(tableId, pageNumber);
    }
  };

  const handleExportTables = () => {
    const data = tables.map((table) => ({
      number: table.table_number,
      caption: table.caption,
      page: table.page_number,
      data: table.data,
    }));

    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tables-${resourceId}.json`;
    a.click();
    URL.revokeObjectURL(url);

    toast({
      title: 'Exported!',
      description: `${tables.length} tables exported`,
    });
  };

  if (isLoadingTables) {
    return (
      <div className={`table-drawer p-4 ${className}`}>
        <div className="space-y-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      </div>
    );
  }

  if (!hasTables) {
    return (
      <div className={`table-drawer p-4 ${className}`}>
        <Alert>
          <AlertDescription>No tables found in this document.</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className={`table-drawer flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="p-4 border-b space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Tables ({tables.length})</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleExportTables}
            title="Export all tables"
          >
            <Download className="h-4 w-4" />
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search tables..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Table List */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {filteredTables.length === 0 ? (
            <Alert>
              <AlertDescription>
                No tables match your search.
              </AlertDescription>
            </Alert>
          ) : (
            filteredTables.map((table) => (
              <div
                key={table.id}
                className="border rounded-lg p-4 space-y-3 hover:bg-accent/50 transition-colors"
              >
                {/* Table Header */}
                <div className="flex items-center justify-between">
                  {table.table_number && (
                    <span className="text-sm font-medium text-muted-foreground">
                      {table.table_number}
                    </span>
                  )}
                  <span className="text-xs text-muted-foreground">
                    Page {table.page_number}
                  </span>
                </div>

                {/* Caption */}
                {table.caption && (
                  <p className="text-sm font-medium">{table.caption}</p>
                )}

                {/* Rendered Table */}
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        {table.data[0]?.map((header, idx) => (
                          <th
                            key={idx}
                            className="border px-3 py-2 text-left font-medium"
                          >
                            {header}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {table.data.slice(1).map((row, rowIdx) => (
                        <tr key={rowIdx} className="border-b hover:bg-muted/30">
                          {row.map((cell, cellIdx) => (
                            <td key={cellIdx} className="border px-3 py-2">
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-wrap">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopyTable(table.data, 'csv')}
                    title="Copy as CSV"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy CSV
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopyTable(table.data, 'json')}
                    title="Copy as JSON"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy JSON
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopyTable(table.data, 'markdown')}
                    title="Copy as Markdown"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy MD
                  </Button>

                  {onJumpToTable && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        handleJumpToTable(table.id, table.page_number)
                      }
                      title="Jump to table in PDF"
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Jump to PDF
                    </Button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
