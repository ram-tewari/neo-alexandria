/**
 * Headlines View Component
 * 
 * Text-only dense layout for quick scanning
 */

import { motion } from 'framer-motion';
import { Icon } from '../common/Icon';
import { icons } from '@/config/icons';
import type { Resource } from '@/types/resource';
import './HeadlinesView.css';

interface HeadlinesViewProps {
  resources: Resource[];
  onRead?: (id: string) => void;
  onArchive?: (id: string) => void;
  onAnnotate?: (id: string) => void;
  onShare?: (id: string) => void;
}

export const HeadlinesView = ({
  resources,
  onRead,
  onArchive,
  onAnnotate,
  onShare,
}: HeadlinesViewProps) => {
  const getQualityColor = (score: number) => {
    if (score >= 0.8) return 'oklch(0.7 0.2 120)'; // Green
    if (score >= 0.6) return 'oklch(0.7 0.2 200)'; // Blue
    if (score >= 0.4) return 'oklch(0.7 0.2 50)';  // Orange
    return 'var(--destructive)'; // Red
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return icons.check;
      case 'in_progress': return icons.clock;
      case 'archived': return icons.archive;
      default: return null;
    }
  };

  return (
    <div className="headlines-view">
      {resources.map((resource, index) => {
        const statusIcon = getStatusIcon(resource.read_status);
        
        return (
          <motion.div
            key={resource.id}
            className="headline-item"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: index * 0.02, duration: 0.2 }}
          >
            <div className="headline-main">
              <div className="headline-header">
                <h3 className="headline-title">{resource.title}</h3>
                {statusIcon && (
                  <div className="headline-status">
                    <Icon icon={statusIcon} size={14} />
                  </div>
                )}
              </div>
              
              {resource.description && (
                <p className="headline-description">{resource.description}</p>
              )}
              
              <div className="headline-meta">
                <span 
                  className="headline-quality" 
                  style={{ color: getQualityColor(resource.quality_score) }}
                >
                  <Icon icon={icons.star} size={12} />
                  {(resource.quality_score * 100).toFixed(0)}%
                </span>
                
                {resource.creator && (
                  <>
                    <span className="headline-separator">•</span>
                    <span className="headline-author">{resource.creator}</span>
                  </>
                )}
                
                {resource.type && (
                  <>
                    <span className="headline-separator">•</span>
                    <span className="headline-type">{resource.type}</span>
                  </>
                )}
                
                {resource.subject.length > 0 && (
                  <>
                    <span className="headline-separator">•</span>
                    <span className="headline-tags">
                      {resource.subject.slice(0, 2).join(', ')}
                      {resource.subject.length > 2 && ` +${resource.subject.length - 2}`}
                    </span>
                  </>
                )}
              </div>
            </div>
            
            <div className="headline-actions">
              {onRead && (
                <button 
                  onClick={() => onRead(resource.id)} 
                  title="Mark as read"
                  className="headline-action-btn"
                >
                  <Icon icon={icons.check} size={16} />
                </button>
              )}
              {onArchive && (
                <button 
                  onClick={() => onArchive(resource.id)} 
                  title="Archive"
                  className="headline-action-btn"
                >
                  <Icon icon={icons.archive} size={16} />
                </button>
              )}
              {onAnnotate && (
                <button 
                  onClick={() => onAnnotate(resource.id)} 
                  title="Annotate"
                  className="headline-action-btn"
                >
                  <Icon icon={icons.edit} size={16} />
                </button>
              )}
              {onShare && (
                <button 
                  onClick={() => onShare(resource.id)} 
                  title="Share"
                  className="headline-action-btn"
                >
                  <Icon icon={icons.share} size={16} />
                </button>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};
