import { useState } from 'react';
import { Edit2, Save, X, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useScholarlyAssets } from '@/lib/hooks/useScholarlyAssets';
import { Skeleton } from '@/components/loading/Skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { Badge } from '@/components/ui/badge';
import type { Metadata } from '@/types/library';

interface MetadataPanelProps {
  resourceId: string;
  onSaveMetadata?: (metadata: Partial<Metadata>) => Promise<void>;
  className?: string;
}

export function MetadataPanel({
  resourceId,
  onSaveMetadata,
  className = '',
}: MetadataPanelProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const { metadata, isLoadingMetadata } = useScholarlyAssets(resourceId);
  const { toast } = useToast();

  const [editedMetadata, setEditedMetadata] = useState<Partial<Metadata>>({});

  const handleEdit = () => {
    if (metadata) {
      setEditedMetadata({
        title: metadata.title,
        authors: metadata.authors,
        abstract: metadata.abstract,
        keywords: metadata.keywords,
        publication_date: metadata.publication_date,
        doi: metadata.doi,
        journal: metadata.journal,
        volume: metadata.volume,
        issue: metadata.issue,
        pages: metadata.pages,
      });
      setIsEditing(true);
    }
  };

  const handleCancel = () => {
    setEditedMetadata({});
    setIsEditing(false);
  };

  const handleSave = async () => {
    if (!onSaveMetadata) return;

    setIsSaving(true);
    try {
      await onSaveMetadata(editedMetadata);
      setIsEditing(false);
      toast({
        title: 'Saved!',
        description: 'Metadata updated successfully',
      });
    } catch (error) {
      toast({
        title: 'Save failed',
        description: 'Failed to update metadata',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const calculateCompleteness = (meta: Metadata | undefined): number => {
    if (!meta) return 0;

    const fields = [
      meta.title,
      meta.authors,
      meta.abstract,
      meta.keywords,
      meta.publication_date,
      meta.doi,
      meta.journal,
    ];

    const filledFields = fields.filter((field) => {
      if (Array.isArray(field)) return field.length > 0;
      return field && field.trim().length > 0;
    }).length;

    return Math.round((filledFields / fields.length) * 100);
  };

  const completeness = calculateCompleteness(metadata);

  if (isLoadingMetadata) {
    return (
      <div className={`metadata-panel p-4 ${className}`}>
        <div className="space-y-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>
      </div>
    );
  }

  if (!metadata) {
    return (
      <div className={`metadata-panel p-4 ${className}`}>
        <Alert>
          <AlertDescription>
            No metadata available for this document.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className={`metadata-panel flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="p-4 border-b space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Metadata</h3>
          {!isEditing ? (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleEdit}
              disabled={!onSaveMetadata}
              title="Edit metadata"
            >
              <Edit2 className="h-4 w-4" />
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCancel}
                disabled={isSaving}
              >
                <X className="h-4 w-4" />
              </Button>
              <Button
                variant="default"
                size="sm"
                onClick={handleSave}
                disabled={isSaving}
              >
                <Save className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>

        {/* Completeness Indicator */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Completeness</span>
            <span className="font-medium">{completeness}%</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className={`h-full transition-all ${
                completeness >= 80
                  ? 'bg-green-500'
                  : completeness >= 50
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${completeness}%` }}
            />
          </div>
        </div>
      </div>

      {/* Metadata Fields */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title" className="flex items-center gap-2">
              Title
              {!metadata.title && (
                <AlertCircle className="h-3 w-3 text-yellow-500" />
              )}
            </Label>
            {isEditing ? (
              <Input
                id="title"
                value={editedMetadata.title || ''}
                onChange={(e) =>
                  setEditedMetadata({ ...editedMetadata, title: e.target.value })
                }
              />
            ) : (
              <p className="text-sm">
                {metadata.title || (
                  <span className="text-muted-foreground italic">Not provided</span>
                )}
              </p>
            )}
          </div>

          {/* Authors */}
          <div className="space-y-2">
            <Label htmlFor="authors" className="flex items-center gap-2">
              Authors
              {(!metadata.authors || metadata.authors.length === 0) && (
                <AlertCircle className="h-3 w-3 text-yellow-500" />
              )}
            </Label>
            {isEditing ? (
              <Input
                id="authors"
                value={editedMetadata.authors?.join(', ') || ''}
                onChange={(e) =>
                  setEditedMetadata({
                    ...editedMetadata,
                    authors: e.target.value.split(',').map((a) => a.trim()),
                  })
                }
                placeholder="Comma-separated list"
              />
            ) : (
              <div className="flex flex-wrap gap-2">
                {metadata.authors && metadata.authors.length > 0 ? (
                  metadata.authors.map((author, idx) => (
                    <Badge key={idx} variant="secondary">
                      {author}
                    </Badge>
                  ))
                ) : (
                  <span className="text-sm text-muted-foreground italic">
                    Not provided
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Abstract */}
          <div className="space-y-2">
            <Label htmlFor="abstract" className="flex items-center gap-2">
              Abstract
              {!metadata.abstract && (
                <AlertCircle className="h-3 w-3 text-yellow-500" />
              )}
            </Label>
            {isEditing ? (
              <Textarea
                id="abstract"
                value={editedMetadata.abstract || ''}
                onChange={(e) =>
                  setEditedMetadata({ ...editedMetadata, abstract: e.target.value })
                }
                rows={4}
              />
            ) : (
              <p className="text-sm">
                {metadata.abstract || (
                  <span className="text-muted-foreground italic">Not provided</span>
                )}
              </p>
            )}
          </div>

          {/* Keywords */}
          <div className="space-y-2">
            <Label htmlFor="keywords" className="flex items-center gap-2">
              Keywords
              {(!metadata.keywords || metadata.keywords.length === 0) && (
                <AlertCircle className="h-3 w-3 text-yellow-500" />
              )}
            </Label>
            {isEditing ? (
              <Input
                id="keywords"
                value={editedMetadata.keywords?.join(', ') || ''}
                onChange={(e) =>
                  setEditedMetadata({
                    ...editedMetadata,
                    keywords: e.target.value.split(',').map((k) => k.trim()),
                  })
                }
                placeholder="Comma-separated list"
              />
            ) : (
              <div className="flex flex-wrap gap-2">
                {metadata.keywords && metadata.keywords.length > 0 ? (
                  metadata.keywords.map((keyword, idx) => (
                    <Badge key={idx} variant="outline">
                      {keyword}
                    </Badge>
                  ))
                ) : (
                  <span className="text-sm text-muted-foreground italic">
                    Not provided
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Publication Date */}
          <div className="space-y-2">
            <Label htmlFor="publication_date">Publication Date</Label>
            {isEditing ? (
              <Input
                id="publication_date"
                type="date"
                value={editedMetadata.publication_date || ''}
                onChange={(e) =>
                  setEditedMetadata({
                    ...editedMetadata,
                    publication_date: e.target.value,
                  })
                }
              />
            ) : (
              <p className="text-sm">
                {metadata.publication_date || (
                  <span className="text-muted-foreground italic">Not provided</span>
                )}
              </p>
            )}
          </div>

          {/* DOI */}
          <div className="space-y-2">
            <Label htmlFor="doi">DOI</Label>
            {isEditing ? (
              <Input
                id="doi"
                value={editedMetadata.doi || ''}
                onChange={(e) =>
                  setEditedMetadata({ ...editedMetadata, doi: e.target.value })
                }
              />
            ) : (
              <p className="text-sm">
                {metadata.doi || (
                  <span className="text-muted-foreground italic">Not provided</span>
                )}
              </p>
            )}
          </div>

          {/* Journal */}
          <div className="space-y-2">
            <Label htmlFor="journal">Journal</Label>
            {isEditing ? (
              <Input
                id="journal"
                value={editedMetadata.journal || ''}
                onChange={(e) =>
                  setEditedMetadata({ ...editedMetadata, journal: e.target.value })
                }
              />
            ) : (
              <p className="text-sm">
                {metadata.journal || (
                  <span className="text-muted-foreground italic">Not provided</span>
                )}
              </p>
            )}
          </div>

          {/* Volume, Issue, Pages */}
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="volume">Volume</Label>
              {isEditing ? (
                <Input
                  id="volume"
                  value={editedMetadata.volume || ''}
                  onChange={(e) =>
                    setEditedMetadata({ ...editedMetadata, volume: e.target.value })
                  }
                />
              ) : (
                <p className="text-sm">
                  {metadata.volume || (
                    <span className="text-muted-foreground italic">-</span>
                  )}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="issue">Issue</Label>
              {isEditing ? (
                <Input
                  id="issue"
                  value={editedMetadata.issue || ''}
                  onChange={(e) =>
                    setEditedMetadata({ ...editedMetadata, issue: e.target.value })
                  }
                />
              ) : (
                <p className="text-sm">
                  {metadata.issue || (
                    <span className="text-muted-foreground italic">-</span>
                  )}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="pages">Pages</Label>
              {isEditing ? (
                <Input
                  id="pages"
                  value={editedMetadata.pages || ''}
                  onChange={(e) =>
                    setEditedMetadata({ ...editedMetadata, pages: e.target.value })
                  }
                />
              ) : (
                <p className="text-sm">
                  {metadata.pages || (
                    <span className="text-muted-foreground italic">-</span>
                  )}
                </p>
              )}
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}
