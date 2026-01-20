import { memo } from 'react';
import { motion } from 'framer-motion';
import { Icon } from './Icon';
import { icons } from '../../config/icons';
import './Avatar.css';

interface AvatarProps {
  src?: string;
  alt?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const Avatar = memo(({ src, alt = 'User avatar', size = 'md' }: AvatarProps) => {
  const sizeClass = `avatar-${size}`;
  
  return (
    <motion.div
      className={`avatar ${sizeClass}`}
      whileHover={{ scale: 1.1 }}
      transition={{ duration: 0.2 }}
    >
      {src ? (
        <img src={src} alt={alt} />
      ) : (
        <Icon icon={icons.user} size={20} />
      )}
    </motion.div>
  );
});
