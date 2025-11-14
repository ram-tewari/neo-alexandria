import './FAB.css';

interface FABProps {
  onClick?: () => void;
  icon?: string;
}

export const FAB = ({ onClick, icon = 'fas fa-plus' }: FABProps) => {
  return (
    <button className="fab" onClick={onClick} aria-label="Add new resource">
      <i className={icon} aria-hidden="true"></i>
    </button>
  );
};
