import { useState } from 'react';
import { motion } from 'framer-motion';
import './Carousel.css';

interface CarouselProps {
  children: React.ReactNode[];
  speed?: number;
  pauseOnHover?: boolean;
}

export const Carousel = ({ children, speed = 30, pauseOnHover = true }: CarouselProps) => {
  const [isPaused, setIsPaused] = useState(false);
  
  // Calculate duration based on number of items and speed (lower speed = faster)
  const duration = children.length * (60 / speed);

  return (
    <div 
      className="carousel-container"
      onMouseEnter={() => pauseOnHover && setIsPaused(true)}
      onMouseLeave={() => pauseOnHover && setIsPaused(false)}
    >
      <motion.div
        className="carousel-content"
        animate={{
          x: isPaused ? undefined : [0, -100 * children.length],
        }}
        transition={{
          x: {
            repeat: Infinity,
            repeatType: "loop",
            duration: duration,
            ease: "linear",
          },
        }}
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
