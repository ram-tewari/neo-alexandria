import { useState, useEffect } from 'react';
import { motion, useMotionValue, useAnimationFrame } from 'framer-motion';
import './Carousel.css';

interface CarouselProps {
  children: React.ReactNode[];
  speed?: number;
  pauseOnHover?: boolean;
}

export const Carousel = ({ children, speed = 30, pauseOnHover = true }: CarouselProps) => {
  const [isPaused, setIsPaused] = useState(false);
  const x = useMotionValue(0);
  
  // Calculate speed in pixels per frame (assuming 60fps)
  const pixelsPerFrame = speed / 60;

  useAnimationFrame(() => {
    if (!isPaused) {
      const currentX = x.get();
      // Move left continuously
      const newX = currentX - pixelsPerFrame;
      
      // Reset when we've scrolled through half the content (one set of children)
      // This creates the seamless loop effect
      if (newX <= -100 * children.length) {
        x.set(0);
      } else {
        x.set(newX);
      }
    }
  });

  return (
    <div 
      className="carousel-container"
      onMouseEnter={() => pauseOnHover && setIsPaused(true)}
      onMouseLeave={() => pauseOnHover && setIsPaused(false)}
      style={{ 
        overflowX: 'auto',
        overflowY: 'hidden',
        cursor: 'grab',
        userSelect: 'none'
      }}
    >
      <motion.div
        className="carousel-content"
        style={{ x }}
        drag="x"
        dragConstraints={{ left: -100 * children.length, right: 0 }}
        dragElastic={0.1}
        onDragStart={() => setIsPaused(true)}
        onDragEnd={() => setIsPaused(false)}
      >
        {/* Render items twice for seamless loop */}
        {children.map((child, index) => (
          <div key={`first-${index}`} className="carousel-item">
            {child}
          </div>
        ))}
        {children.map((child, index) => (
          <div key={`second-${index}`} className="carousel-item">
            {child}
          </div>
        ))}
      </motion.div>
    </div>
  );
};
