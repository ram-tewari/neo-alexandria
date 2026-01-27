import { useState } from 'react';
import { DocumentGrid } from './DocumentGrid';
import { DocumentFilters } from './DocumentFilters';
import { DocumentUpload } from './DocumentUpload';
import { CollectionManager } from './CollectionManager';
import { BatchOperations } from './BatchOperations';
import { PDFViewer } from './PDFViewer';
import { EquationDrawer } from './EquationDrawer';
import { TableDrawer } from './TableDrawer';
import { MetadataPanel } from './MetadataPanel';
import { RelatedCodePanel } from './RelatedCodePanel';
import { RelatedPapersPanel } from './RelatedPapersPanel';
import { useDocuments } from '@/lib/hooks/useDocuments';
import { useCollectionsStore } from '@/stores/collections';
import { usePDFViewerStore } from '@/stores/pdfViewer';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from '@/components/ui/resizable';
import { ScrollArea } from '@/components/ui/scroll-area';
import { BookOpen, Grid3x3, FolderOpen, Upload } from 'lucide-react';
import type { Document } from '@/types/library';

export function LibraryPage() {
  const [activeView, setActiveView] = useState<'grid' | 'collections'>('grid');
  const [showUpload, setShowUpload] = useState(false);
  
  const { documents, isLoading, error } = useDocuments();
  const batchMode = useCollectionsStore((state) => state.batchMode);
  const currentDocument = usePDFViewerStore((state) => state.currentDocument);

  const handleDocumentSelect = (document: Document) => {
    usePDFViewerStore.getState().setCurrentDocument(document);
  };

  const handleCollectionSelect = (collectionId: string) => {
    // Filter documents by collection
    console.log('Selected collection:', collectionId);
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b p-4">
        <div className="flex items-center gap-2">
          <BookOpen className="h-5 w-5" />
          <h1 className="text-2xl font-bold">Library</h1>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant={activeView === 'grid' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveView('grid')}
          >
            <Grid3x3 className="mr-2 h-4 w-4" />
            Documents
          </Button>
          <Button
            variant={activeView === 'collections' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveView('collections')}
          >
            <FolderOpen className="mr-2 h-4 w-4" />
            Collections
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowUpload(true)}
          >
            <Upload className="mr-2 h-4 w-4" />
            Upload
          </Button>
        </div>
      </div>

      {/* Batch Operations Toolbar */}
      {batchMode && <BatchOperations />}

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <ResizablePanelGroup direction="horizontal">
          {/* Left Panel - Document List or Collections */}
          <ResizablePanel defaultSize={currentDocument ? 40 : 100} minSize={30}>
            <div className="flex h-full flex-col">
              {activeView === 'grid' ? (
                <>
                  {/* Filters */}
                  <div className="border-b p-4">
                    <DocumentFilters />
                  </div>
                  
                  {/* Document Grid */}
                  <ScrollArea className="flex-1">
                    <div className="p-4">
                      <DocumentGrid
                        documents={documents}
                        isLoading={isLoading}
                        error={error}
                        onDocumentSelect={handleDocumentSelect}
                      />
                    </div>
                  </ScrollArea>
                </>
              ) : (
                <ScrollArea className="flex-1">
                  <div className="p-4">
                    <CollectionManager onCollectionSelect={handleCollectionSelect} />
                  </div>
                </ScrollArea>
              )}
            </div>
          </ResizablePanel>

          {/* Right Panel - PDF Viewer & Details (only shown when document selected) */}
          {currentDocument && (
            <>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize={60} minSize={40}>
                <Tabs defaultValue="viewer" className="flex h-full flex-col">
                  <TabsList className="w-full justify-start rounded-none border-b">
                    <TabsTrigger value="viewer">PDF Viewer</TabsTrigger>
                    <TabsTrigger value="metadata">Metadata</TabsTrigger>
                    <TabsTrigger value="equations">Equations</TabsTrigger>
                    <TabsTrigger value="tables">Tables</TabsTrigger>
                    <TabsTrigger value="related-code">Related Code</TabsTrigger>
                    <TabsTrigger value="related-papers">Related Papers</TabsTrigger>
                  </TabsList>

                  <TabsContent value="viewer" className="flex-1 overflow-hidden">
                    <PDFViewer document={currentDocument} />
                  </TabsContent>

                  <TabsContent value="metadata" className="flex-1 overflow-auto">
                    <div className="p-4">
                      <MetadataPanel document={currentDocument} />
                    </div>
                  </TabsContent>

                  <TabsContent value="equations" className="flex-1 overflow-hidden">
                    <EquationDrawer documentId={currentDocument.id} />
                  </TabsContent>

                  <TabsContent value="tables" className="flex-1 overflow-hidden">
                    <TableDrawer documentId={currentDocument.id} />
                  </TabsContent>

                  <TabsContent value="related-code" className="flex-1 overflow-auto">
                    <div className="p-4">
                      <RelatedCodePanel documentId={currentDocument.id} />
                    </div>
                  </TabsContent>

                  <TabsContent value="related-papers" className="flex-1 overflow-auto">
                    <div className="p-4">
                      <RelatedPapersPanel documentId={currentDocument.id} />
                    </div>
                  </TabsContent>
                </Tabs>
              </ResizablePanel>
            </>
          )}
        </ResizablePanelGroup>
      </div>

      {/* Upload Dialog */}
      {showUpload && (
        <DocumentUpload
          open={showUpload}
          onOpenChange={setShowUpload}
        />
      )}
    </div>
  );
}
