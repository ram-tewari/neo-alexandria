import { memo } from 'react';
import { motion } from 'framer-motion';
import { fadeInVariants } from '../../animations/variants';
import { Icon } from '../common/Icon';
import { icons, IconName } from '../../config/icons';
import './ActivityCard.css';

interface ActivityCardProps {
  iconName: IconName;
  text: string;
  timestamp: string;
  color?: 'blue' | 'cyan' | 'purple' | 'teal';
  delay?: number;
}

export const ActivityCard = memo(({ 
  iconName, 
  text, 
  timestamp, 
  color = 'blue',
  delay = 0 
}: ActivityCardProps) => {
  const IconComponent = icons[iconName];

  return (
    <motion.div
      className="activity-card"
      variants={fadeInVariants}
      initial="hidden"
      animate="visible"
      transition={{ delay }}
    >
      <div className={`activity-icon activity-icon-${color}`}>
        <Icon icon={IconComponent} size={20} />
      </div>
      <div className="activity-content">
        <p className="activity-text">{text}</p>
        <span className="activity-timestamp">{timestamp}</span>
      </div>
    </motion.div>
  );
});
