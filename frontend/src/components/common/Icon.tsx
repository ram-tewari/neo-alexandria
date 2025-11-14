import { LucideIcon } from 'lucide-react';

interface IconProps {
  icon: LucideIcon;
  size?: number;
  color?: string;
  className?: string;
}

export const Icon = ({ 
  icon: IconComponent, 
  size = 20, 
  color, 
  className = '' 
}: IconProps) => {
  return (
    <IconComponent 
      size={size} 
      color={color}
      className={className}
      strokeWidth={2}
    />
  );
};
