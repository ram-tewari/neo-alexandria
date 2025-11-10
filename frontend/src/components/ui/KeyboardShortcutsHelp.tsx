// Neo Alexandria 2.0 Frontend - Keyboard Shortcuts Help Modal
// Displays available keyboard shortcuts to users

import React from 'react';
import { Modal } from './Modal';
import { getKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { Keyboard } from 'lucide-react';

interface KeyboardShortcutsHelpProps {
  isOpen: boolean;
  onClose: () => void;
}

export const KeyboardShortcutsHelp: React.FC<KeyboardShortcutsHelpProps> = ({
  isOpen,
  onClose,
}) => {
  const shortcuts = getKeyboardShortcuts();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Keyboard Shortcuts"
      size="lg"
    >
      <div className="space-y-4">
        <p className="text-sm text-charcoal-grey-300">
          Use these keyboard shortcuts to navigate and interact with Neo Alexandria more efficiently.
        </p>

        <div className="space-y-2">
          {shortcuts.map((shortcut, index) => (
            <div
              key={index}
              className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-charcoal-grey-700/50 transition-colors"
            >
              <span className="text-sm text-charcoal-grey-200">
                {shortcut.description}
              </span>
              <kbd className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-charcoal-grey-200 bg-charcoal-grey-700 border border-charcoal-grey-600 rounded-md shadow-sm">
                <Keyboard className="w-3 h-3" aria-hidden="true" />
                {shortcut.key}
              </kbd>
            </div>
          ))}
        </div>

        <div className="pt-4 border-t border-charcoal-grey-700">
          <p className="text-xs text-charcoal-grey-400">
            Press <kbd className="px-2 py-0.5 text-xs bg-charcoal-grey-700 border border-charcoal-grey-600 rounded">?</kbd> anytime to show this help.
          </p>
        </div>
      </div>
    </Modal>
  );
};
