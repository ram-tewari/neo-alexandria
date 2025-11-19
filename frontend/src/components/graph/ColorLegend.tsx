import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { topicCategoriesArray, type TopicCategory } from '../../config/topicColors';
import { useTheme } from '../theme/ThemeProvider';
import './ColorLegend.css';

interface ColorLegendProps {
  visibleCategories: Set<string>;
  onToggleCategory: (id: string) => void;
  onHoverCategory?: (id: string | null) => void;
  position?: 'top-right' | 'bottom-right' | 'bottom-left';
  collapsible?: boolean;
}

export function ColorLegend({
  visibleCategories,
  onToggleCategory,
  onHoverCategory,
  position = 'bottom-right',
  collapsible = true,
}: ColorLegendProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { actualTheme } = useTheme();

  const getColorForTheme = (color: string) => {
    if (actualTheme === 'light') {
      return color.replace(/oklch\(0\.7/, 'oklch(0.5');
    }
    return color;
  };

  return (
    <motion.div
      className={`color-legend color-legend-${position}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="color-legend-header">
        <h3 className="color-legend-title">Topic Categories</h3>
        {collapsible && (
          <motion.button
            className="color-legend-toggle"
            onClick={() => setIsCollapsed(!isCollapsed)}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            aria-label={isCollapsed ? 'Expand legend' : 'Collapse legend'}
          >
            {isCollapsed ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </motion.button>
        )}
      </div>

      <AnimatePresence>
        {!isCollapsed && (
          <motion.div
            className="color-legend-content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="color-legend-items">
              {topicCategoriesArray
                .filter((cat) => cat.id !== 'uncategorized')
                .map((category) => {
                  const isVisible = visibleCategories.has(category.id);
                  const color = getColorForTheme(category.color);

                  return (
                    <motion.button
                      key={category.id}
                      className={`color-legend-item ${isVisible ? 'active' : 'inactive'}`}
                      onClick={() => onToggleCategory(category.id)}
                      onMouseEnter={() => onHoverCategory?.(category.id)}
                      onMouseLeave={() => onHoverCategory?.(null)}
                      whileHover={{ x: 4 }}
                      whileTap={{ scale: 0.98 }}
                      title={category.description}
                      aria-pressed={isVisible}
                    >
                      <motion.div
                        className="color-legend-swatch"
                        style={{ backgroundColor: color }}
                        animate={{
                          opacity: isVisible ? 1 : 0.3,
                          scale: isVisible ? 1 : 0.9,
                        }}
                        transition={{ duration: 0.2 }}
                      />
                      <span className="color-legend-label">{category.name}</span>
                      <motion.div
                        className="color-legend-indicator"
                        initial={false}
                        animate={{
                          opacity: isVisible ? 1 : 0,
                          scale: isVisible ? 1 : 0,
                        }}
                        transition={{ duration: 0.2 }}
                      />
                    </motion.button>
                  );
                })}
            </div>

            <div className="color-legend-footer">
              <button
                className="color-legend-action"
                onClick={() => {
                  const allCategories = topicCategoriesArray
                    .filter((cat) => cat.id !== 'uncategorized')
                    .map((cat) => cat.id);
                  
                  if (visibleCategories.size === allCategories.length) {
                    // Hide all
                    allCategories.forEach((id) => onToggleCategory(id));
                  } else {
                    // Show all
                    allCategories.forEach((id) => {
                      if (!visibleCategories.has(id)) {
                        onToggleCategory(id);
                      }
                    });
                  }
                }}
              >
                {visibleCategories.size === topicCategoriesArray.length - 1
                  ? 'Hide All'
                  : 'Show All'}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
