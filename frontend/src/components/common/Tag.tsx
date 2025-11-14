import './Tag.css';

interface TagProps {
  label: string;
  variant?: 'blue' | 'cyan' | 'purple';
  onClick?: () => void;
}

export const Tag = ({ label, variant = 'blue', onClick }: TagProps) => {
  return (
    <span className={`tag tag-${variant}`} onClick={onClick}>
      {label}
    </span>
  );
};
