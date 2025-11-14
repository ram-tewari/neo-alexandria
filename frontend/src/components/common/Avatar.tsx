import './Avatar.css';

interface AvatarProps {
  src?: string;
  alt?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const Avatar = ({ src, alt = 'User avatar', size = 'md' }: AvatarProps) => {
  const sizeClass = `avatar-${size}`;
  
  return (
    <div className={`avatar ${sizeClass}`}>
      {src ? (
        <img src={src} alt={alt} />
      ) : (
        <i className="fas fa-user"></i>
      )}
    </div>
  );
};
