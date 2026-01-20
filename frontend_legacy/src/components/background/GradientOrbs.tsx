import { motion } from 'framer-motion';
import './GradientOrbs.css';

export const GradientOrbs = () => {
  return (
    <div className="gradient-orbs-container">
      {/* Large purple orb - top left */}
      <motion.div
        className="gradient-orb gradient-orb-purple"
        animate={{
          x: [0, 150, -50, 0],
          y: [0, -80, 40, 0],
          scale: [1, 1.3, 0.9, 1],
        }}
        transition={{
          duration: 30,
          repeat: Infinity,
          ease: "easeInOut",
          times: [0, 0.4, 0.7, 1],
        }}
      />
      
      {/* Pink orb - top right */}
      <motion.div
        className="gradient-orb gradient-orb-pink"
        animate={{
          x: [0, -120, 60, 0],
          y: [0, 100, -40, 0],
          scale: [1, 1.2, 1.1, 1],
        }}
        transition={{
          duration: 28,
          repeat: Infinity,
          ease: "easeInOut",
          times: [0, 0.35, 0.65, 1],
        }}
      />
      
      {/* Blue orb - bottom left */}
      <motion.div
        className="gradient-orb gradient-orb-blue"
        animate={{
          x: [0, -100, 80, 0],
          y: [0, -60, 30, 0],
          scale: [1, 1.25, 0.95, 1],
        }}
        transition={{
          duration: 35,
          repeat: Infinity,
          ease: "easeInOut",
          times: [0, 0.3, 0.7, 1],
        }}
      />
      
      {/* Orange orb - bottom right */}
      <motion.div
        className="gradient-orb gradient-orb-orange"
        animate={{
          x: [0, 90, -70, 0],
          y: [0, 70, -50, 0],
          scale: [1, 1.4, 1.05, 1],
        }}
        transition={{
          duration: 32,
          repeat: Infinity,
          ease: "easeInOut",
          times: [0, 0.45, 0.75, 1],
        }}
      />
    </div>
  );
};
