/**
 * ScrollReveal Component
 * Wrapper for scroll-triggered animations using Intersection Observer
 * Requirements: 3.1, 3.2, 8.1, 8.2, 8.3, 8.4, 8.5
 */

import React, { useEffect, useRef, useState } from 'react';
import { motion, useInView } from 'framer-motion';

export interface ScrollRevealProps {
  children: React.ReactNode;
  threshold?: number;
  once?: boolean;
  animationType?: 'fade' | 'slide' | 'scale';
  delay?: number;
  className?: string;
}

export function ScrollReveal({
  children,
  threshold = 0.1,
  once = true,
  animationType = 'fade',
  delay = 0,
  className = '',
}: ScrollRevealProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once, amount: threshold });

  const variants = {
    fade: {
      hidden: { opacity: 0 },
      visible: { opacity: 1 },
    },
    slide: {
      hidden: { opacity: 0, y: 50 },
      visible: { opacity: 1, y: 0 },
    },
    scale: {
      hidden: { opacity: 0, scale: 0.8 },
      visible: { opacity: 1, scale: 1 },
    },
  };

  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      variants={variants[animationType]}
      transition={{
        duration: 0.6,
        delay,
        ease: [0.4, 0, 0.2, 1],
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
