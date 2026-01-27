import { useState, useMemo } from 'react';
import { Copy, ExternalLink, Search, Download } from 'lucide-react';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useScholarlyAssets } from '@/lib/hooks/useScholarlyAssets';
import { Skeleton } from '@/components/loading/Skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';

interface EquationDrawerProps {
  resourceId: string;
  onJumpToEquation?: (equationId: string, pageNumber: number) => void;
  className?: string;
}

export function EquationDrawer({
  resourceId,
  onJumpToEquation,
  className = '',
}: EquationDrawerProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const { equations, isLoadingEquations, hasEquations } =
    useScholarlyAssets(resourceId);
  const { toast } = useToast();

  // Filter equations based on search query
  const filteredEquations = useMemo(() => {
    if (!searchQuery.trim()) return equations;

    const query = searchQuery.toLowerCase();
    return equations.filter(
      (eq) =>
        eq.latex.toLowerCase().includes(query) ||
        eq.equation_number?.toLowerCase().includes(query)
    );
  }, [equations, searchQuery]);

  const handleCopyLatex = async (latex: string) => {
    try {
      await navigator.clipboard.writeText(latex);
      toast({
        title: 'Copied!',
        description: 'LaTeX source copied to clipboard',
      });
    } catch (error) {
      toast({
        title: 'Copy failed',
        description: 'Failed to copy to clipboard',
        variant: 'destructive',
      });
    }
  };

  const handleJumpToEquation = (equationId: string, pageNumber: number) => {
    if (onJumpToEquation) {
      onJumpToEquation(equationId, pageNumber);
    }
  };

  const handleExportEquations = () => {
    const data = equations.map((eq) => ({
      number: eq.equation_number,
      latex: eq.latex,
      page: eq.page_number,
    }));

    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `equations-${resourceId}.json`;
    a.click();
    URL.revokeObjectURL(url);

    toast({
      title: 'Exported!',
      description: `${equations.length} equations exported`,
    });
  };

  if (isLoadingEquations) {
    return (
      <div className={`equation-drawer p-4 ${className}`}>
        <div className="space-y-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      </div>
    );
  }

  if (!hasEquations) {
    return (
      <div className={`equation-drawer p-4 ${className}`}>
        <Alert>
          <AlertDescription>
            No equations found in this document.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className={`equation-drawer flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="p-4 border-b space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">
            Equations ({equations.length})
          </h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleExportEquations}
            title="Export all equations"
          >
            <Download className="h-4 w-4" />
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search equations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Equation List */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {filteredEquations.length === 0 ? (
            <Alert>
              <AlertDescription>
                No equations match your search.
              </AlertDescription>
            </Alert>
          ) : (
            filteredEquations.map((equation) => (
              <div
                key={equation.id}
                className="border rounded-lg p-4 space-y-3 hover:bg-accent/50 transition-colors"
              >
                {/* Equation Number */}
                {equation.equation_number && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">
                      {equation.equation_number}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      Page {equation.page_number}
                    </span>
                  </div>
                )}

                {/* Rendered Equation */}
                <div className="bg-background p-4 rounded border overflow-x-auto">
                  <BlockMath math={equation.latex} />
                </div>

                {/* LaTeX Source */}
                <div className="bg-muted p-2 rounded text-xs font-mono overflow-x-auto">
                  {equation.latex}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopyLatex(equation.latex)}
                    title="Copy LaTeX source"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy LaTeX
                  </Button>

                  {onJumpToEquation && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        handleJumpToEquation(equation.id, equation.page_number)
                      }
                      title="Jump to equation in PDF"
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
