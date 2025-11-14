import { motion } from 'framer-motion';
import { Icon } from '../common/Icon';
import { icons, IconName } from '../../config/icons';
import './FAB.css';

interface FABProps {
  onClick?: () => void;
  iconName?: IconName;
}

export const FAB = ({ onClick, iconName = 'add' }: FABProps) => {
  const IconComponent = icons[iconName];

  return (
    <motion.button
      className="fab"
      onClick={onClick}
      aria-label="Add new resource"
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      transition={{ duration: 0.2 }}
    >
      <Icon icon={IconComponent} size={24} color="white" />
    </motion.button>
  );
};
