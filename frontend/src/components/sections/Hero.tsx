/**
 * Hero Section Component
 * Impactful landing section with animated backgrounds
 * Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 3.4, 3.5
 */

import React, { useEffect, useState } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useTheme } from '../../contexts/ThemeContext';
import './Hero.css';

export interface HeroProps {
  title: string;
  subtitle?: string;
  cta?: React.ReactNode;
  backgroundAnimation?: boolean;
}

/**
 * Hero Section Component
 * Features:
 * - Large, bold typography
 * - Animated background accents using theme colors
 * - Staggered intro animation sequence
 * - Parallax effect on scroll (light mode)
 * - Glow effects (dark mode)
 */
export function Hero({
  title,
  subtitle,
  cta,
  backgroundAnimation = true,
}: HeroProps) {
  const { theme } = useTheme();
  
  // Scroll-based parallax for light mode
  const { scrollY } = useScroll();
  const parallaxY = useTransform(scrollY, [0, 500], [0, 150]);

  // Animation variants for staggered intro
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: [0.4, 0, 0.2, 1],
      },
    },
  };

  return (
    <motion.section
      className="hero"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      data-theme={theme}
    >
      {/* Animated Background Accents */}
      {backgroundAnimation && (
        <div className="hero__background">
          {theme === 'light' ? (
            // Parallax effect for light mode
            <motion.div
              className="hero__background-accent hero__background-accent--light"
              style={{ y: parallaxY }}
              aria-hidden="true"
            />
          ) : (
            // Glow effects for dark mode
            <>
              <motion.div
                className="hero__background-accent hero__background-accent--dark hero__background-accent--glow-1"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.3, 0.5, 0.3],
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
                aria-hidden="true"
              />
              <motion.div
                className="hero__background-accent hero__background-accent--dark hero__background-accent--glow-2"
                animate={{
                  scale: [1, 1.3, 1],
                  opacity: [0.2, 0.4, 0.2],
                }}
                transition={{
                  duration: 5,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  delay: 1,
                }}
                aria-hidden="true"
              />
            </>
          )}
        </div>
      )}

      {/* Content */}
      <div className="hero__content">
        <motion.h1
          className="hero__title"
          variants={itemVariants}
        >
          {title}
        </motion.h1>

        {subtitle && (
          <motion.p
            className="hero__subtitle"
            variants={itemVariants}
          >
            {subtitle}
          </motion.p>
        )}

        {cta && (
          <motion.div
            className="hero__cta"
            variants={itemVariants}
          >
            {cta}
          </motion.div>
        )}
      </div>
    </motion.section>
  );
}
