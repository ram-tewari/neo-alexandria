import { motion } from 'framer-motion';
import './GradientOrbs.css';

export const GradientOrbs = () => {
  return (
    <div className="gradient-orbs-container">
      {/* Large purple orb - top left */}
      <motion.div
        className="gradient-orb gradient-orb-purple"
        animate={{
          x: [0, 100, 0],
          y: [0, -50, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      
      {/* Pink orb - top right */}
      <motion.div
        className="gradient-orb gradient-orb-pink"
        animate={{
          x: [0, -80, 0],
          y: [0, 60, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      
      {/* Blue orb - bottom */}
      <motion.div
        className="gradient-orb gradient-orb-blue"
        animate={{
          x: [0, -60, 0],
          y: [0, -40, 0],
          scale: [1, 1.15, 1],
        }}
        transition={{
          duration: 22,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      
      {/* Orange orb - center */}
      <motion.div
        className="gradient-orb gradient-orb-orange"
        animate={{
          x: [0, 70, 0],
          y: [0, 50, 0],
          scale: [1, 1.3, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    </div>
  );
};
