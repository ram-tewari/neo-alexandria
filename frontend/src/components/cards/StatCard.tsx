import { memo } from 'react';
import type { StatData } from '../../types';
import './StatCard.css';

interface StatCardProps extends StatData {
  delay?: number;
}

export const StatCard = memo(({ icon, value, label, color, delay = 0 }: StatCardProps) => {
  return (
    <div className="card stat-card fade-in" style={{ animationDelay: `${delay}s` }}>
      <div className={`stat-icon-wrapper ${color}`}>
        <i className={`${icon} stat-icon`} style={{ color: 'var(--accent-blue-light)' }}></i>
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
});
