import { SearchInput } from '../common/SearchInput';
import { Button } from '../common/Button';
import { StatCard } from '../cards/StatCard';
import { ResourceCard } from '../cards/ResourceCard';
import { ActivityCard } from '../cards/ActivityCard';
import type { StatData, Resource } from '../../types';
import './Dashboard.css';

const stats: StatData[] = [
  { icon: 'fas fa-book', value: '524', label: 'Resources', color: 'blue' },
  { icon: 'fas fa-tags', value: '86', label: 'Collections', color: 'cyan' },
  { icon: 'fas fa-sticky-note', value: '142', label: 'Annotations', color: 'purple' },
  { icon: 'fas fa-link', value: '38', label: 'Citations', color: 'teal' },
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

const activities = [
  { icon: 'fas fa-book-open', text: 'Started reading "Introduction to Neural Networks"', timestamp: '2 hours ago', color: 'blue' as const },
  { icon: 'fas fa-sticky-note', text: 'Added 3 annotations to "Quantum Computing Explained"', timestamp: '5 hours ago', color: 'purple' as const },
  { icon: 'fas fa-star', text: 'Saved "Data Science Fundamentals" to Favorites', timestamp: '1 day ago', color: 'cyan' as const },
  { icon: 'fas fa-link', text: 'Created citation link between 2 resources', timestamp: '2 days ago', color: 'teal' as const },
  { icon: 'fas fa-tags', text: 'Created new collection "Machine Learning"', timestamp: '3 days ago', color: 'blue' as const },
];

export const Dashboard = () => {
  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Welcome back, User</h1>
        <p className="page-subtitle">Here's what's happening in your knowledge space today.</p>
      </div>

      <SearchInput placeholder="Search resources, tags, or topics..." />

      <div className="stats-grid">
        {stats.map((stat, index) => (
          <StatCard key={index} {...stat} delay={index * 0.1} />
        ))}
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '700' }}>Recommended for You</h2>
          <Button variant="secondary" icon="fas fa-sync-alt">Refresh</Button>
        </div>
        <div className="resource-grid">
          {resources.map((resource, index) => (
            <ResourceCard key={index} resource={resource} delay={index * 0.15} />
          ))}
        </div>
      </div>

      <div className="activity-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '700' }}>Recent Activity</h2>
          <Button variant="secondary">View All</Button>
        </div>
        <div className="activity-list">
          {activities.map((activity, index) => (
            <ActivityCard key={index} {...activity} />
          ))}
        </div>
      </div>
    </div>
  );
};
