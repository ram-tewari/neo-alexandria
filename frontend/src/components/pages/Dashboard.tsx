import { motion } from 'framer-motion';
import { SearchInput } from '../common/SearchInput';
import { Button } from '../common/Button';
import { StatCard } from '../cards/StatCard';
import { ResourceCard } from '../cards/ResourceCard';
import { Carousel } from '../common/Carousel';
import { MiniKnowledgeGraph } from '../common/MiniKnowledgeGraph';
import { pageVariants, staggerContainer, staggerItem } from '../../animations/variants';
import type { StatData, Resource } from '../../types';
import './Dashboard.css';

const stats: StatData[] = [
  { iconName: 'library', value: 524, label: 'Resources', color: 'blue' },
  { iconName: 'chart', value: 86, label: 'Collections', color: 'cyan' },
  { iconName: 'book', value: 142, label: 'Annotations', color: 'purple' },
  { iconName: 'trending', value: 38, label: 'Citations', color: 'teal' },
];

const resources: Resource[] = [
  {
    title: 'Introduction to Neural Networks',
    description: 'A comprehensive guide to understanding neural networks and their applications.',
    author: 'John Doe',
    readTime: 25,
    rating: 4.8,
    tags: ['AI', 'Neural Networks', 'Tutorial'],
    type: 'article',
  },
  {
    title: 'Quantum Computing Explained',
    description: 'Visual introduction to quantum computing principles.',
    author: 'Dr. Smith',
    readTime: 45,
    rating: 4.6,
    tags: ['Physics', 'Quantum', 'Technology'],
    type: 'video',
  },
  {
    title: 'Data Science Fundamentals',
    description: 'Complete guide to data science concepts and best practices.',
    author: 'Jane Wilson',
    readTime: 180,
    rating: 4.9,
    tags: ['Data Science', 'Analytics'],
    type: 'book',
  },
];

export const Dashboard = () => {
  return (
    <motion.div
      className="container"
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <div className="page-header">
        <h1 className="page-title">Welcome back, User</h1>
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
        {stats.map((stat, index) => (
          <motion.div key={index} variants={staggerItem}>
            <StatCard {...stat} />
          </motion.div>
        ))}
      </motion.div>

      <div style={{ marginBottom: '3rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary-white)' }}>Recommended for You</h2>
          <Button variant="secondary" size="sm">Refresh</Button>
        </div>
        <Carousel speed={20} pauseOnHover={true}>
          {resources.map((resource, index) => (
            <div key={index} style={{ width: '380px' }}>
              <ResourceCard resource={resource} />
            </div>
          ))}
        </Carousel>
      </div>

      <div className="activity-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary-white)' }}>Knowledge Network</h2>
          <Button variant="secondary" size="sm">Explore Graph</Button>
        </div>
        <MiniKnowledgeGraph />
      </div>
    </motion.div>
  );
};
