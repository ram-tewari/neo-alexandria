/**
 * ContentSection Component
 * Reusable content block with scroll-triggered animations
 * Requirements: 3.1, 3.2, 8.1, 8.2, 8.3, 8.4, 8.5
 */

import React from 'react';
import { motion } from 'framer-motion';
import { ScrollReveal } from '../common/ScrollReveal';
import { useTheme } from '../../contexts/ThemeContext';
import './ContentSection.css';

export interface ContentSectionProps {
  children: React.ReactNode;
  animationType?: 'fade' | 'slide' | 'scale';
  delay?: number;
  className?: string;
  title?: string;
  subtitle?: string;
}

/**
 * ContentSection Component
 * Features:
 * - Intersection Observer for viewport detection
 * - Configurable animation types
 * - Staggered child animations
 * - Theme-aware styling
 */
export function ContentSection({
  children,
  animationType = 'fade',
  delay = 0,
  className = '',
  title,
  subtitle,
}: ContentSectionProps) {
  const { theme } = useTheme();

  // Animation variants based on type
  const getAnimationVariants = () => {
    switch (animationType) {
      case 'slide':
        return {
          hidden: { opacity: 0, y: 40 },
          visible: { opacity: 1, y: 0 },
        };
      case 'scale':
        return {
          hidden: { opacity: 0, scale: 0.95 },
          visible: { opacity: 1, scale: 1 },
        };
      case 'fade':
      default:
        return {
          hidden: { opacity: 0 },
          visible: { opacity: 1 },
        };
    }
  };

  const variants = getAnimationVariants();

  return (
    <ScrollReveal>
      <motion.section
        className={`content-section ${className}`}
        data-theme={theme}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: '-100px' }}
        transition={{
          duration: 0.6,
          delay,
          ease: [0.4, 0, 0.2, 1],
        }}
        variants={variants}
      >
        {(title || subtitle) && (
          <div className="content-section__header">
            {title && (
              <motion.h2
                className="content-section__title"
                variants={{
                  hidden: { opacity: 0, y: 20 },
                  visible: { opacity: 1, y: 0 },
                }}
                transition={{ delay: delay + 0.1 }}
              >
                {title}
              </motion.h2>
            )}
            {subtitle && (
              <motion.p
                className="content-section__subtitle"
                variants={{
                  hidden: { opacity: 0, y: 20 },
                  visible: { opacity: 1, y: 0 },
                }}
                transition={{ delay: delay + 0.2 }}
              >
                {subtitle}
              </motion.p>
            )}
          </div>
        )}
        <motion.div
          className="content-section__body"
          variants={{
            hidden: { opacity: 0 },
            visible: {
              opacity: 1,
              transition: {
                staggerChildren: 0.1,
                delayChildren: delay + 0.3,
              },
            },
          }}
        >
          {children}
        </motion.div>
      </motion.section>
    </ScrollReveal>
  );
}
