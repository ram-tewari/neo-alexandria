import { memo } from 'react';
import { motion } from 'framer-motion';
import './Tag.css';

interface TagProps {
  label: string;
  variant?: 'blue' | 'cyan' | 'purple';
  onClick?: () => void;
}

export const Tag = memo(({ label, variant = 'blue', onClick }: TagProps) => {
  return (
    <motion.span
      className={`tag tag-${variant}`}
      onClick={onClick}
      whileHover={{ y: -2, scale: 1.05 }}
      transition={{ duration: 0.2 }}
    >
      {label}
    </motion.span>
  );
});
