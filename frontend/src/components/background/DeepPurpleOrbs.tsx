/**
 * Deep Purple Orbs Background
 * 
 * Dramatic animated purple orbs with deep purple theme
 */
import { motion } from 'framer-motion';
import './DeepPurpleOrbs.css';

export const DeepPurpleOrbs = () => {
  return (
    <div className="deep-purple-orbs">
      {/* Large Deep Purple Orb */}
      <motion.div
        className="deep-purple-orb deep-purple-orb--large"
        animate={{
          x: [0, 200, -80, 0],
          y: [0, -150, 80, 0],
          scale: [1, 1.4, 0.8, 1],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: [0.45, 0, 0.55, 1]
        }}
      />
      
      {/* Medium Vibrant Purple Orb */}
      <motion.div
        className="deep-purple-orb deep-purple-orb--medium"
        animate={{
          x: [0, -150, 100, 0],
          y: [0, 120, -80, 0],
          scale: [1, 0.7, 1.5, 1],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: [0.45, 0, 0.55, 1],
          delay: 1.5
        }}
      />
      
      {/* Small Bright Purple Orb */}
      <motion.div
        className="deep-purple-orb deep-purple-orb--small"
        animate={{
          x: [0, 80, -60, 0],
          y: [0, -100, 60, 0],
          scale: [1, 1.6, 0.6, 1],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: [0.45, 0, 0.55, 1],
          delay: 3
        }}
      />
      
      {/* Extra Large Background Orb */}
      <motion.div
        className="deep-purple-orb deep-purple-orb--xlarge"
        animate={{
          x: [0, -120, 150, 0],
          y: [0, 150, -120, 0],
          scale: [1, 1.3, 0.85, 1],
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: [0.45, 0, 0.55, 1],
          delay: 0.5
        }}
      />
      
      {/* Accent Orb */}
      <motion.div
        className="deep-purple-orb deep-purple-orb--accent"
        animate={{
          x: [0, 120, -90, 0],
          y: [0, -70, 90, 0],
          scale: [1, 1.2, 0.9, 1],
        }}
        transition={{
          duration: 14,
          repeat: Infinity,
          ease: [0.45, 0, 0.55, 1],
          delay: 2.5
        }}
      />
    </div>
  );
};
