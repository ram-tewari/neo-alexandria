import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import './QualityChart.css';

interface QualityChartProps {
  score: number;
  size?: number;
}

/**
 * QualityChart - Radial chart displaying quality score with animated sweep
 * 
 * Features:
 * - Animated stroke sweep on mount
 * - Displays score percentage in center
 * - Responsive sizing
 */
export const QualityChart: React.FC<QualityChartProps> = ({ 
  score, 
  size = 192 
}) => {
  const [animatedScore, setAnimatedScore] = useState(0);
  
  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 100);
    return () => clearTimeout(timer);
  }, [score]);
  
  const radius = (size / 2) - 12; // Account for stroke width
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animatedScore * circumference);
  
  return (
    <div className="quality-chart" style={{ width: size, height: size }}>
      <svg 
        className="quality-chart-svg" 
        width={size} 
        height={size}
        viewBox={`0 0 ${size} ${size}`}
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          className="quality-chart-background"
          strokeWidth="12"
          fill="none"
        />
        {/* Progress circle with animated sweep */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          className="quality-chart-progress"
          strokeWidth="12"
          fill="none"
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{
            strokeDasharray: circumference,
            transform: 'rotate(-90deg)',
            transformOrigin: '50% 50%',
          }}
        />
      </svg>
      <div className="quality-chart-label">
        <span className="quality-chart-score">
          {Math.round(animatedScore * 100)}
        </span>
        <span className="quality-chart-text">Quality Score</span>
      </div>
    </div>
  );
};
