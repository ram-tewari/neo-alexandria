import './LibraryBackground.css';

interface LibraryBackgroundProps {
  showAccents?: boolean;
}

export const LibraryBackground = ({ showAccents = true }: LibraryBackgroundProps) => {
  return (
    <div 
      className={`library-background ${showAccents ? 'with-accents' : ''}`}
      aria-hidden="true"
    >
      {/* Solid black background with optional subtle purple accents */}
      {showAccents && (
        <>
          <div className="library-accent library-accent-1" />
          <div className="library-accent library-accent-2" />
        </>
      )}
    </div>
  );
};
