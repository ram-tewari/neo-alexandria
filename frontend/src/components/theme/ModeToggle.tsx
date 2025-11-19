import { Moon, Sun, Monitor } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from './ThemeProvider';
import './ModeToggle.css';

export function ModeToggle() {
  const { theme, setTheme, actualTheme } = useTheme();

  const themes = [
    { value: 'light' as const, label: 'Light', icon: Sun },
    { value: 'dark' as const, label: 'Dark', icon: Moon },
    { value: 'system' as const, label: 'System', icon: Monitor },
  ];

  return (
    <div className="mode-toggle">
      <motion.button
        className="mode-toggle-button"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => {
          // Cycle through themes
          const currentIndex = themes.findIndex(t => t.value === theme);
          const nextIndex = (currentIndex + 1) % themes.length;
          setTheme(themes[nextIndex].value);
        }}
        aria-label="Toggle theme"
      >
        <AnimatePresence mode="wait">
          {actualTheme === 'light' ? (
            <motion.div
              key="sun"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <Sun size={20} />
            </motion.div>
          ) : (
            <motion.div
              key="moon"
              initial={{ rotate: 90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: -90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <Moon size={20} />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      <div className="mode-toggle-dropdown">
        {themes.map(({ value, label, icon: Icon }) => (
          <motion.button
            key={value}
            className={`mode-toggle-option ${theme === value ? 'active' : ''}`}
            onClick={() => setTheme(value)}
            whileHover={{ x: 4 }}
            whileTap={{ scale: 0.98 }}
          >
            <Icon size={16} />
            <span>{label}</span>
            {theme === value && (
              <motion.div
                className="mode-toggle-indicator"
                layoutId="active-theme"
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              />
            )}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
