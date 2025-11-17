import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '../common/Button';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ViewModeSelector } from '../common/ViewModeSelector';
import { FilterBar } from '../common/FilterBar';
import { GridView } from '../views/GridView';
import { ListView } from '../views/ListView';
import { HeadlinesView } from '../views/HeadlinesView';
import { MasonryView } from '../views/MasonryView';
import { GradientOrbs } from '../background/GradientOrbs';
import { pageVariants } from '../../animations/variants';
import { useResourceStore } from '@/store';
import './Library.css';

export const Library = () => {
  const {
    resources,
    isLoading,
    error,
    viewMode,
    filters,
    pagination,
    fetchResources,
    setViewMode,
    updateFilters,
    clearFilters,
    updateResourceStatus,
    archiveResource,
    setPage,
  } = useResourceStore();

  useEffect(() => {
    fetchResources();
  }, [fetchResources]);

  const handleRead = async (id: string) => {
    try {
      await updateResourceStatus(id, 'completed');
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const handleArchive = async (id: string) => {
    try {
      await archiveResource(id);
    } catch (error) {
      console.error('Failed to archive:', error);
    }
  };

  const handleAnnotate = (id: string) => {
    console.log('Annotate:', id);
    // TODO: Implement annotation feature
  };

  const handleShare = (id: string) => {
    console.log('Share:', id);
    // TODO: Implement share feature
  };

  const handleSearchChange = (query: string) => {
    updateFilters({ search: query });
  };

  const handleFiltersChange = (newFilters: any) => {
    updateFilters(newFilters);
  };

  const renderView = () => {
    const viewProps = {
      resources,
      onRead: handleRead,
      onArchive: handleArchive,
      onAnnotate: handleAnnotate,
      onShare: handleShare,
    };

    switch (viewMode) {
      case 'list':
        return <ListView {...viewProps} />;
      case 'headlines':
        return <HeadlinesView {...viewProps} />;
      case 'masonry':
        return <MasonryView {...viewProps} />;
      case 'grid':
      default:
        return <GridView {...viewProps} />;
    }
  };

  return (
    <motion.div
      className="container library-container"
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <GradientOrbs />
      
      <div className="page-header" style={{ position: 'relative', zIndex: 1 }}>
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <motion.h1 
            className="page-title"
            style={{
              background: 'linear-gradient(135deg, var(--white) 0%, var(--purple-bright) 50%, var(--purple-vibrant) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              backgroundSize: '200% 200%',
            }}
            animate={{
              backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            Library
          </motion.h1>
          <motion.p 
            className="page-subtitle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            Browse and manage your knowledge resources.
          </motion.p>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Button variant="primary" iconName="add">Add Resource</Button>
        </motion.div>
      </div>

      <div className="library-controls">
        <FilterBar
          searchQuery={filters.search}
          onSearchChange={handleSearchChange}
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onClearFilters={clearFilters}
        />
        
        <div className="library-toolbar">
          <div className="library-info">
            {pagination.total > 0 && (
              <span>
                Showing {(pagination.page - 1) * pagination.limit + 1}-
                {Math.min(pagination.page * pagination.limit, pagination.total)} of {pagination.total} resources
              </span>
            )}
          </div>
          <ViewModeSelector currentMode={viewMode} onChange={setViewMode} />
        </div>
      </div>

      {error && (
        <div className="library-error">
          <p>Error loading resources: {error}</p>
          <Button variant="secondary" onClick={() => fetchResources()}>
            Retry
          </Button>
        </div>
      )}

      {isLoading ? (
        <div className="library-loading">
          <LoadingSpinner size="lg" />
          <p>Loading resources...</p>
        </div>
      ) : resources.length > 0 ? (
        <>
          <div className="library-content">
            {renderView()}
          </div>

          {pagination.pages > 1 && (
            <div className="pagination">
              <div className="pagination-info">
                Page {pagination.page} of {pagination.pages}
              </div>
              <div className="pagination-controls">
                <button
                  className="pagination-btn"
                  disabled={pagination.page === 1}
                  onClick={() => setPage(pagination.page - 1)}
                >
                  ‹
                </button>
                
                {Array.from({ length: Math.min(5, pagination.pages) }, (_, i) => {
                  let pageNum;
                  if (pagination.pages <= 5) {
                    pageNum = i + 1;
                  } else if (pagination.page <= 3) {
                    pageNum = i + 1;
                  } else if (pagination.page >= pagination.pages - 2) {
                    pageNum = pagination.pages - 4 + i;
                  } else {
                    pageNum = pagination.page - 2 + i;
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      className={`pagination-btn ${pagination.page === pageNum ? 'active' : ''}`}
                      onClick={() => setPage(pageNum)}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                
                {pagination.pages > 5 && pagination.page < pagination.pages - 2 && (
                  <>
                    <span className="pagination-dots">...</span>
                    <button
                      className="pagination-btn"
                      onClick={() => setPage(pagination.pages)}
                    >
                      {pagination.pages}
                    </button>
                  </>
                )}
                
                <button
                  className="pagination-btn"
                  disabled={pagination.page === pagination.pages}
                  onClick={() => setPage(pagination.page + 1)}
                >
                  ›
                </button>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="library-empty">
          <p>No resources found.</p>
          <p className="library-empty-hint">
            {filters.search || Object.keys(filters).length > 0
              ? 'Try adjusting your filters or search query.'
              : 'Start by adding some resources to your library!'}
          </p>
          {(filters.search || Object.keys(filters).length > 0) && (
            <Button variant="secondary" onClick={clearFilters}>
              Clear Filters
            </Button>
          )}
        </div>
      )}
    </motion.div>
  );
};
