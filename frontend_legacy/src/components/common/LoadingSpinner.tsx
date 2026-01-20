import './LoadingSpinner.css';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
}

export const LoadingSpinner = ({ size = 'md' }: LoadingSpinnerProps) => {
  return (
    <div className={`loading-spinner loading-spinner-${size}`} role="status" aria-label="Loading">
      <div className="spinner"></div>
    </div>
  );
};
