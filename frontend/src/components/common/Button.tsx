import { useState } from 'react';
import { motion } from 'framer-motion';
import { Icon } from './Icon';
import { icons, IconName } from '../../config/icons';
import './Button.css';

interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md';
  iconName?: IconName;
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
}

interface Ripple {
  x: number;
  y: number;
  id: number;
}

export const Button = ({ 
  variant = 'primary',
  size = 'md',
  iconName, 
  children, 
  onClick, 
  className = '',
  disabled = false
}: ButtonProps) => {
  const [ripples, setRipples] = useState<Ripple[]>([]);

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const newRipple: Ripple = { x, y, id: Date.now() };
    setRipples([...ripples, newRipple]);
    
    setTimeout(() => {
      setRipples(ripples => ripples.filter(r => r.id !== newRipple.id));
    }, 600);
    
    onClick?.();
  };

  const IconComponent = iconName ? icons[iconName] : null;
  const sizeClass = size === 'sm' ? 'btn-sm' : '';

  return (
    <motion.button
      className={`btn btn-${variant} ${sizeClass} ${className}`}
      onClick={handleClick}
      disabled={disabled}
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
    >
      {ripples.map(ripple => (
        <motion.span
          key={ripple.id}
          className="ripple"
          style={{ left: ripple.x, top: ripple.y }}
          initial={{ scale: 0, opacity: 0.5 }}
          animate={{ scale: 2, opacity: 0 }}
          transition={{ duration: 0.6 }}
        />
      ))}
      {IconComponent && <Icon icon={IconComponent} size={18} />}
      {children}
    </motion.button>
  );
};
