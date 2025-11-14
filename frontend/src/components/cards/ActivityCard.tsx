import { memo } from 'react';
import './ActivityCard.css';

interface ActivityCardProps {
  icon: string;
  text: string;
  timestamp: string;
  color?: 'blue' | 'cyan' | 'purple' | 'teal';
}

export const ActivityCard = memo(({ icon, text, timestamp, color = 'blue' }: ActivityCardProps) => {
  return (
    <div className="activity-card">
      <div className={`activity-icon activity-icon-${color}`}>
        <i className={icon}></i>
      </div>
      <div className="activity-content">
        <p className="activity-text">{text}</p>
        <span className="activity-timestamp">{timestamp}</span>
      </div>
    </div>
  );
});
