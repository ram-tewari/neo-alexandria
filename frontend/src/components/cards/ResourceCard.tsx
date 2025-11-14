import { memo } from 'react';
import type { Resource } from '../../types';
import { Tag } from '../common/Tag';
import './ResourceCard.css';

interface ResourceCardProps {
  resource: Resource;
  delay?: number;
}

export const ResourceCard = memo(({ resource, delay = 0 }: ResourceCardProps) => {
  const getTypeIcon = () => {
    switch (resource.type) {
      case 'article': return 'fas fa-file-alt';
      case 'video': return 'fas fa-video';
      case 'book': return 'fas fa-book';
      case 'paper': return 'fas fa-newspaper';
      default: return 'fas fa-file';
    }
  };

  const getTypeColor = () => {
    switch (resource.type) {
      case 'article': return 'rgba(59, 130, 246, 0.2)';
      case 'video': return 'rgba(6, 182, 212, 0.2)';
      case 'book': return 'rgba(139, 92, 246, 0.2)';
      case 'paper': return 'rgba(20, 184, 166, 0.2)';
      default: return 'rgba(59, 130, 246, 0.2)';
    }
  };

  return (
    <div className="card resource-card float-animation fade-in" style={{ animationDelay: `${delay}s` }}>
      <div className="resource-header">
        <div className="resource-type-icon" style={{ background: getTypeColor() }}>
          <i className={getTypeIcon()} style={{ color: 'var(--accent-blue-light)' }}></i>
        </div>
        <div className="resource-rating">
          <i className="fas fa-star"></i>
          <span>{resource.rating}</span>
        </div>
      </div>
      
      <h3 className="resource-title">{resource.title}</h3>
      <p className="resource-description">{resource.description}</p>
      
      <div className="resource-tags">
        {resource.tags.map((tag, i) => (
          <Tag key={i} label={tag} variant={i % 3 === 0 ? 'blue' : i % 3 === 1 ? 'cyan' : 'purple'} />
        ))}
      </div>
      
      <div className="resource-meta">
        <div className="resource-author">
          <i className="fas fa-user"></i>
          <span>{resource.author}</span>
        </div>
        <div className="resource-time">
          <i className="fas fa-clock"></i>
          <span>{resource.readTime} min</span>
        </div>
      </div>
    </div>
  );
});
