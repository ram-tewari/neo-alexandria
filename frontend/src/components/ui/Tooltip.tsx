// Neo Alexandria 2.0 Frontend - Tooltip Component
// Tooltip with positioning logic and animations

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/utils/cn';

interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number;
  className?: string;
  disabled?: boolean;
}

const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = 'top',
  delay = 200,
  className,
  disabled = false,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const handleMouseEnter = () => {
    if (disabled) return;
    
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };

  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  // Calculate tooltip position
  useEffect(() => {
    if (!isVisible || !triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const spacing = 8; // Gap between trigger and tooltip

    let top = 0;
    let left = 0;

    switch (position) {
      case 'top':
        top = triggerRect.top - tooltipRect.height - spacing;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case 'bottom':
        top = triggerRect.bottom + spacing;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case 'left':
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.left - tooltipRect.width - spacing;
        break;
      case 'right':
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.right + spacing;
        break;
    }

    // Ensure tooltip stays within viewport
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    if (left < 0) left = spacing;
    if (left + tooltipRect.width > viewportWidth) {
      left = viewportWidth - tooltipRect.width - spacing;
    }
    if (top < 0) top = spacing;
    if (top + tooltipRect.height > viewportHeight) {
      top = viewportHeight - tooltipRect.height - spacing;
    }

    setTooltipPosition({ top, left });
  }, [isVisible, position]);

  const positionVariants = {
    top: { y: 5 },
    bottom: { y: -5 },
    left: { x: 5 },
    right: { x: -5 },
  };

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onFocus={handleMouseEnter}
        onBlur={handleMouseLeave}
        className="inline-block"
      >
        {children}
      </div>

      <AnimatePresence>
        {isVisible && !disabled && (
          <motion.div
            ref={tooltipRef}
            role="tooltip"
            className={cn(
              'fixed z-50 px-3 py-2 text-sm',
              'bg-charcoal-grey-900 text-charcoal-grey-50',
              'border border-charcoal-grey-700 rounded-lg shadow-lg',
              'pointer-events-none',
              'max-w-xs',
              className
            )}
            style={{
              top: tooltipPosition.top,
              left: tooltipPosition.left,
            }}
            initial={{ opacity: 0, ...positionVariants[position] }}
            animate={{ opacity: 1, y: 0, x: 0 }}
            exit={{ opacity: 0, ...positionVariants[position] }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
          >
            {content}
            
            {/* Arrow */}
            <div
              className={cn(
                'absolute w-2 h-2 bg-charcoal-grey-900 border-charcoal-grey-700',
                'transform rotate-45',
                position === 'top' && 'bottom-[-5px] left-1/2 -translate-x-1/2 border-r border-b',
                position === 'bottom' && 'top-[-5px] left-1/2 -translate-x-1/2 border-l border-t',
                position === 'left' && 'right-[-5px] top-1/2 -translate-y-1/2 border-r border-t',
                position === 'right' && 'left-[-5px] top-1/2 -translate-y-1/2 border-l border-b'
              )}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export { Tooltip };
export type { TooltipProps };
