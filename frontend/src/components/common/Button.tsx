import './Button.css';

interface ButtonProps {
  variant?: 'primary' | 'secondary';
  icon?: string;
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

export const Button = ({ variant = 'primary', icon, children, onClick, className = '' }: ButtonProps) => {
  return (
    <button className={`btn btn-${variant} btn-shine ${className}`} onClick={onClick}>
      {icon && <i className={icon}></i>}
      {children}
    </button>
  );
};
