import { memo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { Resource } from '@/types/resource';
import type { ViewMode } from '@/types/api';
import { cardHoverVariants } from '../../animations/variants';
import { Icon } from '../common/Icon';
import { icons } from '../../config/icons';
import { Tag } from '../common/Tag';
import './ResourceCard.css';

interface ResourceCardProps {
  resource: Resource;
  viewMode: ViewMode;
  delay?: number;
  onRead?: (id: string) => void;
  onArchive?: (id: string) => void;
  onAnnotate?: (id: string) => void;
  onShare?: (id: string) => void;
}

export const ResourceCard = memo(({ 
  resource, 
  viewMode,
  delay = 0,
  onRead,
  onArchive,
  onAnnotate,
  onShare
}: ResourceCardProps) => {
  const [showActions, setShowActions] = useState(false);

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

  const getQualityColor = (score: number) => {
    if (score >= 0.8) return '#10b981'; // green
    if (score >= 0.6) return '#3b82f6'; // blue
    if (score >= 0.4) return '#f59e0b'; // orange
    return '#ef4444'; // red
  };

  const getStatusIcon = () => {
    switch (resource.read_status) {
      case 'completed': return icons.check;
      case 'in_progress': return icons.clock;
      case 'archived': return icons.archive;
      default: return null;
    }
  };

  const typeIcon = getTypeIcon();
  const statusIcon = getStatusIcon();

  // Render different layouts based on view mode
  if (viewMode === 'list') {
    return (
      <motion.div
        className="resource-card resource-card--list"
        variants={cardHoverVariants}
        initial="rest"
        whileHover="hover"
        onHoverStart={() => setShowActions(true)}
        onHoverEnd={() => setShowActions(false)}
      >
        <div className="resource-card__content">
          <div className="resource-card__type-icon" style={{ background: getTypeColor() }}>
            <Icon icon={typeIcon} size={20} />
          </div>
          
          <div className="resource-card__main">
            <div className="resource-card__header">
              <h3 className="resource-card__title">{resource.title}</h3>
              {statusIcon && (
                <div className="resource-card__status">
                  <Icon icon={statusIcon} size={16} />
                </div>
              )}
            </div>
            <p className="resource-card__description">{resource.description || 'No description available'}</p>
            
            <div className="resource-card__tags">
              {resource.subject.slice(0, 3).map((tag, i) => (
                <Tag key={i} label={tag} variant={i % 3 === 0 ? 'blue' : i % 3 === 1 ? 'cyan' : 'purple'} />
              ))}
              {resource.subject.length > 3 && (
                <span className="resource-card__more-tags">+{resource.subject.length - 3}</span>
              )}
            </div>
          </div>
          
          <div className="resource-card__meta">
            <div className="resource-card__quality" style={{ color: getQualityColor(resource.quality_score) }}>
              <Icon icon={icons.star} size={16} />
              <span>{(resource.quality_score * 100).toFixed(0)}%</span>
            </div>
            {resource.creator && (
              <div className="resource-card__author">
                <Icon icon={icons.user} size={16} />
                <span>{resource.creator}</span>
              </div>
            )}
          </div>
        </div>

        <AnimatePresence>
          {showActions && (
            <motion.div
              className="resource-card__actions"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
            >
              {onRead && (
                <button onClick={() => onRead(resource.id)} title="Mark as read">
                  <Icon icon={icons.check} size={18} />
                </button>
              )}
              {onArchive && (
                <button onClick={() => onArchive(resource.id)} title="Archive">
                  <Icon icon={icons.archive} size={18} />
                </button>
              )}
              {onAnnotate && (
                <button onClick={() => onAnnotate(resource.id)} title="Annotate">
                  <Icon icon={icons.edit} size={18} />
                </button>
              )}
              {onShare && (
                <button onClick={() => onShare(resource.id)} title="Share">
                  <Icon icon={icons.share} size={18} />
                </button>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    );
  }

  // Grid/Masonry view (default)
  return (
    <motion.div
      className="card resource-card resource-card--grid"
      variants={cardHoverVariants}
      initial="rest"
      whileHover="hover"
      whileTap={{ scale: 0.98 }}
      style={{ animationDelay: `${delay}s` }}
      onHoverStart={() => setShowActions(true)}
      onHoverEnd={() => setShowActions(false)}
    >
      <div className="resource-header">
        <div className="resource-type-icon" style={{ background: getTypeColor() }}>
          <Icon icon={typeIcon} size={20} />
        </div>
        <div className="resource-rating" style={{ color: getQualityColor(resource.quality_score) }}>
          <Icon icon={icons.star} size={16} />
          <span>{(resource.quality_score * 100).toFixed(0)}%</span>
        </div>
        {statusIcon && (
          <div className="resource-status">
            <Icon icon={statusIcon} size={16} />
          </div>
        )}
      </div>
      
      <h3 className="resource-title">{resource.title}</h3>
      <p className="resource-description">{resource.description || 'No description available'}</p>
      
      <div className="resource-tags">
        {resource.subject.slice(0, 3).map((tag, i) => (
          <Tag key={i} label={tag} variant={i % 3 === 0 ? 'blue' : i % 3 === 1 ? 'cyan' : 'purple'} />
        ))}
        {resource.subject.length > 3 && (
          <span className="resource-more-tags">+{resource.subject.length - 3}</span>
        )}
      </div>
      
      <div className="resource-meta">
        {resource.creator && (
          <div className="resource-author">
            <Icon icon={icons.user} size={16} />
            <span>{resource.creator}</span>
          </div>
        )}
        {resource.type && (
          <div className="resource-type">
            <span>{resource.type}</span>
          </div>
        )}
      </div>

      <AnimatePresence>
        {showActions && (
          <motion.div
            className="resource-actions-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="resource-actions">
              {onRead && (
                <button onClick={() => onRead(resource.id)} title="Mark as read">
                  <Icon icon={icons.check} size={20} />
                  <span>Read</span>
                </button>
              )}
              {onArchive && (
                <button onClick={() => onArchive(resource.id)} title="Archive">
                  <Icon icon={icons.archive} size={20} />
                  <span>Archive</span>
                </button>
              )}
              {onAnnotate && (
                <button onClick={() => onAnnotate(resource.id)} title="Annotate">
                  <Icon icon={icons.edit} size={20} />
                  <span>Annotate</span>
                </button>
              )}
              {onShare && (
                <button onClick={() => onShare(resource.id)} title="Share">
                  <Icon icon={icons.share} size={20} />
                  <span>Share</span>
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});
