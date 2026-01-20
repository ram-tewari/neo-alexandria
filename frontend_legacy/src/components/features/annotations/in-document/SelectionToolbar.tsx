import React, { useState, useEffect, useRef } from 'react';
import { ColorPicker } from './ColorPicker';
import type { AnnotationColor, TextSelection } from '../../../../types/annotations';
import './SelectionToolbar.css';

interface SelectionToolbarProps {
    selection: TextSelection;
    onHighlight: (color: AnnotationColor) => void;
    onAddNote: () => void;
    onClose: () => void;
}

/**
 * SelectionToolbar - Floating toolbar that appears on text selection
 * 
 * Features:
 * - Positioned near text selection
 * - Actions: Highlight, Add Note
 * - Color picker for highlight color
 * - Keyboard accessible
 * - Auto-dismiss on selection clear
 */
export const SelectionToolbar: React.FC<SelectionToolbarProps> = ({
    selection,
    onHighlight,
    onAddNote,
    onClose,
}) => {
    const [selectedColor, setSelectedColor] = useState<AnnotationColor>('yellow');
    const [position, setPosition] = useState({ top: 0, left: 0 });
    const toolbarRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Calculate position based on selection bounding rect
        const rect = selection.boundingRect;
        const toolbarHeight = 50; // Approximate toolbar height
        const spacing = 8;

        let top = rect.top - toolbarHeight - spacing;
        let left = rect.left + rect.width / 2;

        // Adjust if toolbar would be off-screen
        if (top < 0) {
            top = rect.bottom + spacing;
        }

        // Center horizontally but keep on screen
        if (toolbarRef.current) {
            const toolbarWidth = toolbarRef.current.offsetWidth;
            left = Math.max(
                spacing,
                Math.min(left - toolbarWidth / 2, window.innerWidth - toolbarWidth - spacing)
            );
        }

        setPosition({ top: top + window.scrollY, left });
    }, [selection]);

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                onClose();
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [onClose]);

    const handleHighlight = () => {
        onHighlight(selectedColor);
    };

    const handleAddNote = () => {
        // First create a highlight, then open note editor
        onAddNote();
    };

    return (
        <div
            ref={toolbarRef}
            className="selection-toolbar"
            style={{ top: position.top, left: position.left }}
            role="toolbar"
            aria-label="Text selection actions"
        >
            <ColorPicker
                selectedColor={selectedColor}
                onColorChange={setSelectedColor}
            />

            <div className="selection-toolbar-divider" />

            <button
                className="selection-toolbar-button"
                onClick={handleHighlight}
                aria-label="Highlight selection"
            >
                <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                        d="M2 12L10 4L12 6L4 14H2V12Z"
                        fill="currentColor"
                        opacity="0.3"
                    />
                    <path
                        d="M10 4L12 6M2 12L10 4L12 6L4 14H2V12Z"
                        stroke="currentColor"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                </svg>
                Highlight
            </button>

            <button
                className="selection-toolbar-button"
                onClick={handleAddNote}
                aria-label="Add note to selection"
            >
                <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                        d="M3 3h10v7l-3 3H3V3z"
                        fill="currentColor"
                        opacity="0.3"
                    />
                    <path
                        d="M3 3h10v7l-3 3H3V3z M10 10v3l3-3h-3z"
                        stroke="currentColor"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                </svg>
                Add Note
            </button>
        </div>
    );
};
