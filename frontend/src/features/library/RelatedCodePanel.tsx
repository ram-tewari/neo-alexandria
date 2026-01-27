import { useState } from 'react';
import { FileCode, RefreshCw, ExternalLink, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/loading/Skeleton';
import { useAutoLinking } from '@/lib/hooks/useAutoLinking';

interface RelatedCodePanelProps {
  resourceId: string;
  onCodeFileClick?: (resourceId: string) => void;
  className?: string;
}

/**
 * RelatedCodePanel displays code files related to the current document
 * Uses vector embeddings to find semantically similar code
 */
export function RelatedCodePanel({
  resourceId,
  onCodeFileClick,
  className = '',
}: RelatedCodePanelProps) {
  const {
    relatedCode,
    isLoadingCode,
    codeError,
    hasRelatedCode,
    refreshSuggestions,
  } = useAutoLinking(resourceId);

  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await refreshSuggestions();
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleCodeClick = (codeResourceId: string) => {
    onCodeFileClick?.(codeResourceId);
  };

  const getSimilarityColor = (similarity: number): string => {
    if (similarity >= 0.8) return 'text-green-600';
    if (similarity >= 0.6) return 'text-blue-600';
    if (similarity >= 0.4) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getRelationshipLabel = (type: string): string => {
    switch (type) {
      case 'citation':
        return 'Citation';
      case 'semantic':
        return 'Semantic';
      case 'code_reference':
        return 'Reference';
      default:
        return 'Related';
    }
  };

  if (isLoadingCode) {
    return (
      <div className={`related-code-panel flex flex-col h-full ${className}`}>
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Related Code</h3>
            <Skeleton className="h-8 w-8" />
          </div>
        </div>
        <div className="p-4 space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (codeError) {
    return (
      <div className={`related-code-panel flex flex-col h-full ${className}`}>
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold">Related Code</h3>
        </div>
        <div className="p-4">
          <Alert variant="destructive">
            <AlertDescription>
              Failed to load related code files. Please try again.
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  if (!hasRelatedCode) {
    return (
      <div className={`related-code-panel flex flex-col h-full ${className}`}>
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Related Code</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRefresh}
              disabled={isRefreshing}
            >
              <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center text-muted-foreground">
            <FileCode className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No related code files found</p>
            <p className="text-sm mt-1">Try refreshing suggestions</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`related-code-panel flex flex-col h-full ${className}`}>
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold">Related Code</h3>
            <Badge variant="secondary">{relatedCode.length}</Badge>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
            title="Refresh suggestions"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {relatedCode.map((item, index) => (
            <div
              key={item.resource.id}
              className="p-3 border rounded-lg hover:bg-accent cursor-pointer transition-colors"
              onClick={() => handleCodeClick(item.resource.id)}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <FileCode className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
                    <span className="font-medium text-sm truncate">
                      {item.resource.title}
                    </span>
                  </div>
                  {item.resource.description && (
                    <p className="text-xs text-muted-foreground line-clamp-2 ml-6">
                      {item.resource.description}
                    </p>
                  )}
                  <div className="flex items-center gap-2 mt-2 ml-6">
                    <Badge variant="outline" className="text-xs">
                      {getRelationshipLabel(item.relationship_type)}
                    </Badge>
                    <div className="flex items-center gap-1">
                      <TrendingUp className={`h-3 w-3 ${getSimilarityColor(item.similarity)}`} />
                      <span className={`text-xs font-medium ${getSimilarityColor(item.similarity)}`}>
                        {(item.similarity * 100).toFixed(0)}% match
                      </span>
                    </div>
                  </div>
                </div>
                <ExternalLink className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      <div className="p-3 border-t bg-muted/50">
        <p className="text-xs text-muted-foreground text-center">
          Suggestions based on semantic similarity and code references
        </p>
      </div>
    </div>
  );
}
