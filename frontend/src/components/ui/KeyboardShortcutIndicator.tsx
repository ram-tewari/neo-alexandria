import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './KeyboardShortcutIndicator.css';

interface KeyboardShortcutIndicatorProps {
  shortcut: string;
  visible?: boolean;
  onDismiss?: () => void;
  maxUses?: number;
}

const STORAGE_KEY = 'sidebar-shortcut-uses';

export function KeyboardShortcutIndicator({
  shortcut,
  visible: visibleProp = true,
  onDismiss,
  maxUses = 3,
}: KeyboardShortcutIndicatorProps) {
  const [visible, setVisible] = useState(false);
  const [uses, setUses] = useState(0);

  useEffect(() => {
    // Check localStorage for usage count
    const storedUses = localStorage.getItem(STORAGE_KEY);
    const usageCount = storedUses ? parseInt(storedUses, 10) : 0;
    setUses(usageCount);

    // Show indicator if under max uses
    if (usageCount < maxUses && visibleProp) {
      setVisible(true);
    }
  }, [maxUses, visibleProp]);

  useEffect(() => {
    // Listen for Ctrl+B keyboard shortcut
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'b' && (event.ctrlKey || event.metaKey)) {
        const newUses = uses + 1;
        setUses(newUses);
        localStorage.setItem(STORAGE_KEY, newUses.toString());

        // Hide after max uses
        if (newUses >= maxUses) {
          setVisible(false);
          onDismiss?.();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [uses, maxUses, onDismiss]);

  const handleDismiss = () => {
    setVisible(false);
    localStorage.setItem(STORAGE_KEY, maxUses.toString());
    onDismiss?.();
  };

  // Parse shortcut string (e.g., "Ctrl+B" -> ["Ctrl", "B"])
  const keys = shortcut.split('+').map(k => k.trim());

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className="keyboard-shortcut-indicator"
          initial={{ opacity: 0, scale: 0.9, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: -10 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
        >
          <div className="shortcut-content">
            <span className="shortcut-label">Tip:</span>
            <div className="shortcut-keys">
              {keys.map((key, index) => (
                <span key={index} className="shortcut-key-group">
                  <kbd className="shortcut-key">{key}</kbd>
                  {index < keys.length - 1 && <span className="shortcut-plus">+</span>}
                </span>
              ))}
            </div>
            <span className="shortcut-description">to toggle sidebar</span>
          </div>
          <button
            className="shortcut-dismiss"
            onClick={handleDismiss}
            aria-label="Dismiss hint"
          >
            ×
          </button>
          <div className="shortcut-progress">
            <div
              className="shortcut-progress-bar"
              style={{ width: `${(uses / maxUses) * 100}%` }}
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
