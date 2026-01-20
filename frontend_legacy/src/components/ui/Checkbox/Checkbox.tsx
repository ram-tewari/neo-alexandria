/**
 * Checkbox component
 * Accessible checkbox with label support
 */

import React from 'react';
import './Checkbox.css';

export interface CheckboxProps {
  /** Whether the checkbox is checked */
  checked: boolean;
  /** Callback when checkbox state changes */
  onChange: (checked: boolean) => void;
  /** Optional label text */
  label?: string;
  /** Optional disabled state */
  disabled?: boolean;
  /** Optional aria-label for accessibility */
  'aria-label'?: string;
  /** Optional className for custom styling */
  className?: string;
}

/**
 * Checkbox component with accessible markup
 * 
 * @example
 * ```tsx
 * <Checkbox
 *   checked={isSelected}
 *   onChange={setIsSelected}
 *   label="Select item"
 * />
 * ```
 */
export const Checkbox: React.FC<CheckboxProps> = ({
  checked,
  onChange,
  label,
  disabled = false,
  'aria-label': ariaLabel,
  className = '',
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.checked);
  };

  return (
    <label className={`checkbox-container ${disabled ? 'checkbox-disabled' : ''} ${className}`}>
      <input
        type="checkbox"
        checked={checked}
        onChange={handleChange}
        disabled={disabled}
        aria-label={ariaLabel || label}
        className="checkbox-input"
      />
      <span className="checkbox-custom">
        {checked && (
          <svg
            className="checkbox-icon"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M13.5 4L6 11.5L2.5 8"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </span>
      {label && <span className="checkbox-label">{label}</span>}
    </label>
  );
};
