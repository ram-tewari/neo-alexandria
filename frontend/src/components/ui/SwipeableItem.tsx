// Neo Alexandria 2.0 Frontend - Swipeable Item Component
// Provides swipe-to-delete functionality for mobile lists

import React, { useRef, useState } from 'react';
import { motion, PanInfo, useMotionValue, useTransform } from 'framer-motion';
import { Trash2 } from 'lucide-react';
import { cn } from '@/utils/cn';

interface SwipeableItemProps {
  children: React.ReactNode;
  onDelete?: () => void;
  disabled?: boolean;
  deleteThreshold?: number;
  className?: string;
}

const SwipeableItem: React.FC<SwipeableItemProps> = ({
  children,
  onDelete,
  disabled = false,
  deleteThreshold = -100,
  className,
}) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const x = useMotionValue(0);
  const constraintsRef = useRef(null);

  // Transform x position to background color opacity
  const deleteOpacity = useTransform(
    x,
    [deleteThreshold, 0],
    [1, 0]
  );

  const handleDragEnd = (_event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    // If swiped past threshold, trigger delete
    if (info.offset.x < deleteThreshold && onDelete && !disabled) {
      setIsDeleting(true);
      // Animate out before deleting
      setTimeout(() => {
        onDelete();
      }, 300);
    }
  };

  // Only enable swipe on mobile/touch devices
  const isTouchDevice = typeof window !== 'undefined' && 
    ('ontouchstart' in window || navigator.maxTouchPoints > 0);

  if (!isTouchDevice || disabled) {
    return <div className={className}>{children}</div>;
  }

  return (
    <div className={cn('relative overflow-hidden', className)} ref={constraintsRef}>
      {/* Delete background */}
      <motion.div
        className="absolute inset-0 bg-red-500 flex items-center justify-end px-6"
        style={{ opacity: deleteOpacity }}
      >
        <Trash2 className="w-6 h-6 text-white" />
      </motion.div>

      {/* Swipeable content */}
      <motion.div
        drag="x"
        dragConstraints={{ left: deleteThreshold * 1.5, right: 0 }}
        dragElastic={0.2}
        onDragEnd={handleDragEnd}
        style={{ x }}
        animate={isDeleting ? { x: -1000, opacity: 0 } : {}}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className="relative bg-white touch-pan-y"
      >
        {children}
      </motion.div>
    </div>
  );
};

export { SwipeableItem };
