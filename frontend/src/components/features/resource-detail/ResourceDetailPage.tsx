import { useParams, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { resourcesApi } from '../../../lib/api/resources';
import { Breadcrumbs } from './Breadcrumbs';
import { ResourceHeader } from './ResourceHeader';
import { ResourceTabs } from './ResourceTabs';
import { ContentTab } from './ContentTab';
import { AnnotationsTab } from './AnnotationsTab';
import { MetadataTab } from './MetadataTab';
import { GraphTab } from './GraphTab';
import { QualityTab } from './QualityTab';
import { FloatingActionButton } from './FloatingActionButton';
import { Skeleton } from '../../ui/Skeleton/Skeleton';
import { Button } from '../../ui/Button';
import './ResourceDetailPage.css';

/**
 * ResourceDetailPage - Main detail page for viewing comprehensive resource information
 * 
 * Features:
 * - Breadcrumb navigation
 * - Resource header with metadata
 * - Tabbed interface for different views
 * - URL-synced tab state
 * - Floating action button
 */
export const ResourceDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'content';

  // Fetch resource data
  const { data: resource, isLoading, error } = useQuery({
    queryKey: ['resource', id],
    queryFn: () => resourcesApi.get(id!),
    enabled: !!id,
  });

  const handleTabChange = (tab: string) => {
    setSearchParams({ tab });
  };

  if (isLoading) {
    return (
      <div className="resource-detail-page">
        <div className="resource-detail-container">
          <Skeleton width="300px" height="20px" className="mb-4" />
          <Skeleton width="100%" height="40px" className="mb-2" />
          <Skeleton width="80%" height="24px" className="mb-6" />
          <Skeleton width="100%" height="400px" />
        </div>
      </div>
    );
  }

  if (error) {
    // Check if it's a 404 error
    const is404 = error instanceof Error && 
      ('status' in error && (error as any).status === 404);
    
    return (
      <div className="resource-detail-page">
        <div className="resource-detail-container">
          <div className="error-state" style={{
            textAlign: 'center',
            padding: '3rem',
            maxWidth: '600px',
            margin: '0 auto',
          }}>
            <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>
              {is404 ? '🔍' : '⚠️'}
            </div>
            <h2 style={{
              fontSize: '1.5rem',
              fontWeight: 600,
              marginBottom: '0.5rem',
            }}>
              {is404 ? 'Resource Not Found' : 'Error Loading Resource'}
            </h2>
            <p style={{
              color: 'var(--color-text-secondary)',
              marginBottom: '1.5rem',
            }}>
              {is404 
                ? "The resource you're looking for doesn't exist or has been removed."
                : error instanceof Error 
                  ? error.message 
                  : 'An error occurred while loading this resource'}
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
              <Button
                variant="primary"
                onClick={() => window.location.href = '/library'}
              >
                ← Back to Library
              </Button>
              {!is404 && (
                <Button
                  variant="secondary"
                  onClick={() => window.location.reload()}
                >
                  Retry
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!resource) {
    return null;
  }

  return (
    <div className="resource-detail-page">
      <div className="resource-detail-container">
        <Breadcrumbs
          items={[
            { label: 'Library', href: '/library' },
            { label: resource.title, href: `/resources/${id}` },
          ]}
        />

        <ResourceHeader resource={resource} />

        <ResourceTabs
          activeTab={activeTab}
          onTabChange={handleTabChange}
        />

        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
            className="tab-content"
          >
            {activeTab === 'content' && <ContentTab resource={resource} />}
            {activeTab === 'annotations' && <AnnotationsTab resourceId={id!} />}
            {activeTab === 'metadata' && <MetadataTab resource={resource} />}
            {activeTab === 'graph' && <GraphTab resourceId={id!} />}
            {activeTab === 'quality' && <QualityTab resourceId={id!} />}
          </motion.div>
        </AnimatePresence>

        <FloatingActionButton resource={resource} />
      </div>
    </div>
  );
};
