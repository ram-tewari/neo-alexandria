import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { SearchInput } from '../common/SearchInput';
import { Button } from '../common/Button';
import { StatCard } from '../cards/StatCard';
import { ResourceCard } from '../cards/ResourceCard';
import { Carousel } from '../common/Carousel';
import { MiniKnowledgeGraph } from '../common/MiniKnowledgeGraph';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { GradientOrbs } from '../background/GradientOrbs';
import { DeepPurpleOrbs } from '../background/DeepPurpleOrbs';
import { pageVariants, staggerContainer, staggerItem } from '../../animations/variants';
import { useResourceStore } from '@/store';
import type { StatData } from '../../types';
import './Dashboard.css';

const stats: StatData[] = [
  { iconName: 'library', value: 0, label: 'Resources', color: 'blue' },
  { iconName: 'chart', value: 0, label: 'Collections', color: 'cyan' },
  { iconName: 'book', value: 0, label: 'Annotations', color: 'purple' },
  { iconName: 'trending', value: 0, label: 'Citations', color: 'teal' },
];

export const Dashboard = () => {
  const { 
    resources, 
    isLoading, 
    error, 
    viewMode,
    pagination,
    fetchResources,
    updateResourceStatus,
    archiveResource
  } = useResourceStore();

  useEffect(() => {
    // Fetch resources on mount
    fetchResources({ limit: 20, sort_by: 'created_at', sort_order: 'desc' });
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

  const handleRefresh = () => {
    fetchResources({ limit: 20, sort_by: 'created_at', sort_order: 'desc' });
  };

  // Update stats with real data
  const updatedStats = [
    { ...stats[0], value: pagination.total },
    stats[1],
    stats[2],
    stats[3],
  ];

  return (
    <motion.div
      className="dashboard-container"
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <GradientOrbs />
      <DeepPurpleOrbs />
      
      <div className="container">
        <div className="page-header">
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
            Welcome back, User
          </motion.h1>
          <p className="page-subtitle">Here's what's happening in your knowledge space today.</p>
        </div>

      <div style={{ marginBottom: '2.5rem' }}>
        <SearchInput placeholder="Search resources, tags, or topics..." />
      </div>

      <motion.div
        className="stats-grid"
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
      >
        {updatedStats.map((stat, index) => (
          <motion.div key={index} variants={staggerItem}>
            <StatCard {...stat} />
          </motion.div>
        ))}
      </motion.div>

      <div style={{ marginBottom: '3rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary-white)' }}>
            Recent Resources
          </h2>
          <Button variant="secondary" size="sm" onClick={handleRefresh}>
            Refresh
          </Button>
        </div>

        {error && (
          <div style={{ 
            padding: '1rem', 
            background: 'rgba(239, 68, 68, 0.1)', 
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--destructive)',
            marginBottom: '1rem'
          }}>
            Error loading resources: {error}
          </div>
        )}

        {isLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
            <LoadingSpinner size="lg" />
          </div>
        ) : resources.length > 0 ? (
          <Carousel speed={20} pauseOnHover={true}>
            {resources.slice(0, 10).map((resource, index) => (
              <div key={resource.id} style={{ width: '380px' }}>
                <ResourceCard 
                  resource={resource}
                  viewMode={viewMode}
                  delay={index * 0.1}
                  onRead={handleRead}
                  onArchive={handleArchive}
                  onAnnotate={handleAnnotate}
                  onShare={handleShare}
                />
              </div>
            ))}
          </Carousel>
        ) : (
          <div style={{ 
            padding: '3rem', 
            textAlign: 'center',
            color: 'var(--text-secondary)'
          }}>
            <p>No resources found. Start by adding some resources to your library!</p>
          </div>
        )}
      </div>

        <div className="activity-section">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary-white)' }}>Knowledge Network</h2>
            <Button variant="secondary" size="sm">Explore Graph</Button>
          </div>
          <MiniKnowledgeGraph />
        </div>
      </div>
    </motion.div>
  );
};
