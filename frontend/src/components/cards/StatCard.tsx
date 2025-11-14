import { memo } from 'react';
import { motion } from 'framer-motion';
import type { StatData } from '../../types';
import { useCountUp } from '../../animations/utils';
import { fadeInUpVariants } from '../../animations/variants';
import { Icon } from '../common/Icon';
import { icons } from '../../config/icons';
import './StatCard.css';

interface StatCardProps extends StatData {
  delay?: number;
}

export const StatCard = memo(({ iconName, value, label, color, delay = 0 }: StatCardProps) => {
  const animatedValue = useCountUp(value, 2000);
  const IconComponent = icons[iconName];

  return (
    <motion.div
      className="card stat-card"
      variants={fadeInUpVariants}
      initial="hidden"
      animate="visible"
      transition={{ delay }}
    >
      <div className={`stat-icon-wrapper ${color}`}>
        <Icon icon={IconComponent} size={24} />
      </div>
      <div className="stat-value">{animatedValue.toLocaleString()}</div>
      <div className="stat-label">{label}</div>
    </motion.div>
  );
});
