import { motion } from 'framer-motion';
import { SearchInput } from '../common/SearchInput';
import { Button } from '../common/Button';
import { Tag } from '../common/Tag';
import { ResourceCard } from '../cards/ResourceCard';
import { pageVariants, staggerContainer, staggerItem } from '../../animations/variants';
import type { Resource } from '../../types';
import './Library.css';

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
  {
    title: 'Machine Learning Research Paper',
    description: 'Latest research on deep learning architectures.',
    author: 'Dr. Johnson',
    readTime: 60,
    rating: 4.7,
    tags: ['ML', 'Research', 'Deep Learning'],
    type: 'paper',
  },
  {
    title: 'Web Development Best Practices',
    description: 'Modern approaches to building scalable web applications.',
    author: 'Sarah Chen',
    readTime: 30,
    rating: 4.5,
    tags: ['Web Dev', 'JavaScript', 'Best Practices'],
    type: 'article',
  },
  {
    title: 'Cloud Architecture Patterns',
    description: 'Design patterns for cloud-native applications.',
    author: 'Mike Brown',
    readTime: 40,
    rating: 4.8,
    tags: ['Cloud', 'Architecture', 'DevOps'],
    type: 'article',
  },
];

const activeFilters = ['AI', 'Tutorial'];

export const Library = () => {
  return (
    <motion.div
      className="container"
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <div className="page-header">
        <h1 className="page-title">Library</h1>
        <p className="page-subtitle">Browse and manage your knowledge resources.</p>
      </div>

      <div className="library-toolbar">
        <SearchInput placeholder="Search library..." />
        <div className="toolbar-actions">
          <Button variant="secondary" iconName="filter">Filter</Button>
          <Button variant="secondary" iconName="sort">Sort</Button>
          <Button variant="primary" iconName="add">Add Resource</Button>
        </div>
      </div>

      <div className="filter-tags">
        {activeFilters.map((filter, index) => (
          <Tag key={index} label={filter} variant="blue" />
        ))}
        <button className="clear-filters">
          Clear all
        </button>
      </div>

      <motion.div
        className="resource-grid"
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
      >
        {resources.map((resource, index) => (
          <motion.div key={index} variants={staggerItem}>
            <ResourceCard resource={resource} />
          </motion.div>
        ))}
      </motion.div>

      <div className="pagination">
        <div className="pagination-info">
          Showing 1-6 of 524 resources
        </div>
        <div className="pagination-controls">
          <button className="pagination-btn" disabled>
            ‹
          </button>
          <button className="pagination-btn active">1</button>
          <button className="pagination-btn">2</button>
          <button className="pagination-btn">3</button>
          <span className="pagination-dots">...</span>
          <button className="pagination-btn">88</button>
          <button className="pagination-btn">
            ›
          </button>
        </div>
      </div>
    </motion.div>
  );
};
