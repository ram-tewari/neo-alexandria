import React, { useState, useRef, useEffect } from 'react';
import type { AnnotationColor } from '../../../../types/annotations';
import './ColorPicker.css';

interface ColorPickerProps {
    selectedColor: AnnotationColor;
    onColorChange: (color: AnnotationColor) => void;
    disabled?: boolean;
}

const COLORS: Array<{ value: AnnotationColor; label: string }> = [
    { value: 'yellow', label: 'Yellow' },
    { value: 'green', label: 'Green' },
    { value: 'blue', label: 'Blue' },
    { value: 'pink', label: 'Pink' },
    { value: 'orange', label: 'Orange' },
];

/**
 * ColorPicker - Dropdown for selecting highlight colors
 * 
 * Features:
 * - Predefined color palette
 * - Keyboard navigation (Arrow keys, Enter, Escape)
 * - Accessible with ARIA roles
 */
export const ColorPicker: React.FC<ColorPickerProps> = ({
    selectedColor,
    onColorChange,
    disabled = false,
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const [focusedIndex, setFocusedIndex] = useState(
        COLORS.findIndex(c => c.value === selectedColor)
    );
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!isOpen) return;

        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [isOpen]);

    const handleKeyDown = (event: React.KeyboardEvent) => {
        if (!isOpen) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                setIsOpen(true);
            }
            return;
        }

        switch (event.key) {
            case 'Escape':
                event.preventDefault();
                setIsOpen(false);
                break;
            case 'ArrowRight':
            case 'ArrowDown':
                event.preventDefault();
                setFocusedIndex(prev => (prev + 1) % COLORS.length);
                break;
            case 'ArrowLeft':
            case 'ArrowUp':
                event.preventDefault();
                setFocusedIndex(prev => (prev - 1 + COLORS.length) % COLORS.length);
                break;
            case 'Enter':
            case ' ':
                event.preventDefault();
                onColorChange(COLORS[focusedIndex].value);
                setIsOpen(false);
                break;
        }
    };

    const handleColorSelect = (color: AnnotationColor) => {
        onColorChange(color);
        setIsOpen(false);
    };

    const selectedColorObj = COLORS.find(c => c.value === selectedColor) || COLORS[0];

    return (
        <div className="color-picker" ref={dropdownRef}>
            <button
                className="color-picker-trigger"
                onClick={() => setIsOpen(!isOpen)}
                onKeyDown={handleKeyDown}
                disabled={disabled}
                aria-label="Select highlight color"
                aria-haspopup="listbox"
                aria-expanded={isOpen}
            >
                <div className={`color-swatch color-${selectedColor}`} />
                <span>{selectedColorObj.label}</span>
            </button>

            {isOpen && (
                <div className="color-picker-dropdown" role="listbox" aria-label="Highlight colors">
                    <span className="color-picker-label">Highlight Color</span>
                    <div className="color-picker-swatches">
                        {COLORS.map((color, index) => (
                            <button
                                key={color.value}
                                className={`color-swatch-button color-${color.value} ${color.value === selectedColor ? 'selected' : ''
                                    }`}
                                onClick={() => handleColorSelect(color.value)}
                                onFocus={() => setFocusedIndex(index)}
                                role="option"
                                aria-label={color.label}
                                aria-selected={color.value === selectedColor}
                                tabIndex={focusedIndex === index ? 0 : -1}
                            />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};
