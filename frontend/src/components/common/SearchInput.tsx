import './SearchInput.css';

interface SearchInputProps {
  placeholder: string;
  value?: string;
  onChange?: (value: string) => void;
}

export const SearchInput = ({ placeholder, value = '', onChange }: SearchInputProps) => {
  return (
    <div className="search-container">
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        className="search-input"
      />
      <button className="search-button">
        <i className="fas fa-search" style={{ color: 'white' }}></i>
      </button>
    </div>
  );
};
