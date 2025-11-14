import { useState } from 'react';
import { motion } from 'framer-motion';
import { pulseVariants } from '../../animations/variants';
import { Icon } from './Icon';
import { icons } from '../../config/icons';
import './SearchInput.css';

interface SearchInputProps {
  placeholder: string;
  value?: string;
  onChange?: (value: string) => void;
}

export const SearchInput = ({ placeholder, value = '', onChange }: SearchInputProps) => {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="search-container">
      <motion.div
        className="search-pulse"
        variants={pulseVariants}
        animate={isFocused ? 'focus' : 'rest'}
      />
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        className="search-input"
      />
      <button className="search-button" aria-label="Search">
        <Icon icon={icons.search} size={20} color="white" />
      </button>
    </div>
  );
};
