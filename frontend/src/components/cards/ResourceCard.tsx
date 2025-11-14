import { memo } from 'react';
import { motion } from 'framer-motion';
import type { Resource } from '../../types';
import { cardHoverVariants } from '../../animations/variants';
import { Icon } from '../common/Icon';
import { icons } from '../../config/icons';
import { Tag } from '../common/Tag';
import './ResourceCard.css';

interface ResourceCardProps {
  resource: Resource;
  delay?: number;
}

export const ResourceCard = memo(({ resource, delay = 0 }: ResourceCardProps) => {
  const getTypeIcon = () => {
    switch (resource.type) {
      case 'article': return icons.article;
      case 'video': return icons.video;
      case 'book': return icons.book;
      case 'paper': return icons.paper;
      default: return icons.article;
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

  const typeIcon = getTypeIcon();

  return (
    <motion.div
      className="card resource-card float-animation"
      variants={cardHoverVariants}
      initial="rest"
      whileHover="hover"
      whileTap={{ scale: 0.98 }}
      style={{ animationDelay: `${delay}s` }}
    >
      <div className="resource-header">
        <div className="resource-type-icon" style={{ background: getTypeColor() }}>
          <Icon icon={typeIcon} size={20} />
        </div>
        <div className="resource-rating">
          <Icon icon={icons.star} size={16} />
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
          <Icon icon={icons.user} size={16} />
          <span>{resource.author}</span>
        </div>
        <div className="resource-time">
          <Icon icon={icons.clock} size={16} />
          <span>{resource.readTime} min</span>
        </div>
      </div>
    </motion.div>
  );
});
