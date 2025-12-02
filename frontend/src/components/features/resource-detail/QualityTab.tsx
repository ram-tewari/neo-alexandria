import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { qualityApi } from '../../../lib/api/quality';
import { QualityChart } from '../../ui/QualityChart';
import { Card } from '../../ui/Card/Card';
import { Skeleton } from '../../ui/Skeleton/Skeleton';
import './QualityTab.css';

interface QualityTabProps {
  resourceId: string;
}

/**
 * QualityTab - Displays resource quality metrics with visualization
 * 
 * Features:
 * - Overall quality score with radial chart
 * - Dimension breakdown with animated progress bars
 * - Outlier warning if applicable
 * - Loading and error states
 */
export const QualityTab: React.FC<QualityTabProps> = ({ resourceId }) => {
  const { data: quality, isLoading, error } = useQuery({
    queryKey: ['resource-quality', resourceId],
    queryFn: () => qualityApi.getDetails(resourceId),
  });

  if (isLoading) {
    return (
      <div
        role="tabpanel"
        id="panel-quality"
        aria-labelledby="tab-quality"
        className="quality-tab"
      >
        <div className="quality-tab-loading">
          <Skeleton width="192px" height="192px" className="quality-chart-skeleton" />
          <div className="quality-dimensions-skeleton">
            <Skeleton width="100%" height="100px" />
            <Skeleton width="100%" height="100px" />
            <Skeleton width="100%" height="100px" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        role="tabpanel"
        id="panel-quality"
        aria-labelledby="tab-quality"
        className="quality-tab"
      >
        <div className="quality-tab-error">
          <p>Failed to load quality data. Please try again later.</p>
        </div>
      </div>
    );
  }

  if (!quality) {
    return (
      <div
        role="tabpanel"
        id="panel-quality"
        aria-labelledby="tab-quality"
        className="quality-tab"
      >
        <div className="quality-tab-empty">
          <p>Quality analysis pending...</p>
        </div>
      </div>
    );
  }

  return (
    <div
      role="tabpanel"
      id="panel-quality"
      aria-labelledby="tab-quality"
      className="quality-tab"
    >
      {/* Overall Score Chart */}
      <div className="quality-chart-container">
        <QualityChart score={quality.overall_score} />
      </div>

      {/* Dimension Breakdown */}
      <div className="quality-dimensions">
        {quality.dimensions.map((dimension, index) => (
          <Card key={dimension.name} className="quality-dimension-card">
            <div className="quality-dimension-header">
              <span className="quality-dimension-name">{dimension.name}</span>
              <span className="quality-dimension-score">
                {Math.round(dimension.score * 100)}%
              </span>
            </div>
            <div className="quality-dimension-bar-container">
              <motion.div
                className="quality-dimension-bar"
                initial={{ width: 0 }}
                animate={{ width: `${dimension.score * 100}%` }}
                transition={{ duration: 0.8, delay: 0.2 + index * 0.1 }}
              />
            </div>
          </Card>
        ))}
      </div>

      {/* Outlier Warning */}
      {quality.is_outlier && (
        <Card className="quality-outlier-warning">
          <div className="quality-outlier-content">
            <svg 
              className="quality-outlier-icon" 
              width="20" 
              height="20" 
              viewBox="0 0 20 20" 
              fill="none"
            >
              <path
                d="M10 0L12.2451 7.75486H20L13.8775 12.2451L16.1225 20L10 15.5098L3.87746 20L6.12254 12.2451L0 7.75486H7.75486L10 0Z"
                fill="currentColor"
              />
            </svg>
            <div className="quality-outlier-text">
              <h4 className="quality-outlier-title">Quality Outlier Detected</h4>
              <p className="quality-outlier-description">
                This resource has significantly lower quality metrics compared to similar resources.
                Consider reviewing or updating the content.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};
