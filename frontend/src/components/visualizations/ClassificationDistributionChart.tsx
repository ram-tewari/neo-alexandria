// Neo Alexandria 2.0 Frontend - Classification Distribution Chart Component
// Interactive bar chart showing resource distribution across classifications

import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface ClassificationData {
  code: string;
  name?: string;
  count: number;
}

interface ClassificationDistributionChartProps {
  /**
   * Classification distribution data
   */
  data: ClassificationData[];
  /**
   * Height of the chart
   * @default 400
   */
  height?: number;
  /**
   * Callback when a bar is clicked
   */
  onBarClick?: (code: string) => void;
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get color for classification bar based on index
 * Uses a gradient of blue shades for visual variety
 */
const getBarColor = (index: number, total: number): string => {
  const colors = [
    '#3B82F6', // Accent blue
    '#60A5FA', // Light blue
    '#2563EB', // Medium blue
    '#1D4ED8', // Dark blue
    '#1E40AF', // Darker blue
    '#4299E1', // Neutral blue
    '#2B6CB0', // Deep blue
    '#2C5282', // Navy blue
  ];
  return colors[index % colors.length];
};

/**
 * Custom tooltip component for the chart
 */
const CustomTooltip: React.FC<any> = ({ active, payload }) => {
  if (!active || !payload || !payload.length) {
    return null;
  }

  const data = payload[0].payload;

  return (
    <div className="bg-[#09090B] border border-[#27272A] rounded-lg p-3 shadow-2xl">
      <div className="text-zinc-100 font-medium mb-1 text-sm">
        {data.code}
      </div>
      {data.name && (
        <div className="text-zinc-500 text-xs mb-2">
          {data.name}
        </div>
      )}
      <div className="text-zinc-300 text-xs font-medium">
        {data.count} {data.count === 1 ? 'resource' : 'resources'}
      </div>
    </div>
  );
};

/**
 * ClassificationDistributionChart - Interactive bar chart for classification distribution
 * 
 * Features:
 * - Bar chart using Recharts library
 * - Classification codes on x-axis
 * - Resource counts on y-axis
 * - Hover tooltips with detailed information
 * - Click to filter by classification
 * - Responsive container that adapts to parent width
 * - Color-coded bars for visual distinction
 * 
 * @example
 * ```tsx
 * <ClassificationDistributionChart 
 *   data={classificationData}
 *   onBarClick={(code) => filterByClassification(code)}
 * />
 * ```
 */
export const ClassificationDistributionChart: React.FC<ClassificationDistributionChartProps> = ({
  data,
  height = 400,
  onBarClick,
  className = '',
}) => {
  // Sort data by count in descending order and limit to top 20
  const sortedData = useMemo(() => {
    return [...data]
      .sort((a, b) => b.count - a.count)
      .slice(0, 20);
  }, [data]);

  // Handle bar click
  const handleBarClick = (data: any) => {
    if (onBarClick && data) {
      onBarClick(data.code);
    }
  };

  // Calculate max value for Y-axis domain
  const maxCount = useMemo(() => {
    return Math.max(...sortedData.map(d => d.count), 0);
  }, [sortedData]);

  return (
    <div className={`classification-distribution-chart ${className}`}>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={sortedData}
          margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#27272A" 
            opacity={0.5}
            vertical={false}
          />
          <XAxis
            dataKey="code"
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fill: '#71717A', fontSize: 11 }}
            stroke="#27272A"
            axisLine={{ stroke: '#27272A' }}
          />
          <YAxis
            tick={{ fill: '#71717A', fontSize: 11 }}
            stroke="#27272A"
            axisLine={{ stroke: '#27272A' }}
            domain={[0, maxCount]}
            label={{
              value: 'Resources',
              angle: -90,
              position: 'insideLeft',
              style: { fill: '#71717A', fontSize: 11 },
            }}
          />
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ fill: 'rgba(59, 130, 246, 0.05)' }}
          />
          <Bar
            dataKey="count"
            onClick={handleBarClick}
            cursor={onBarClick ? 'pointer' : 'default'}
            radius={[2, 2, 0, 0]}
          >
            {sortedData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getBarColor(index, sortedData.length)}
                opacity={0.8}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      
      {data.length > 20 && (
        <div className="text-center text-zinc-600 text-xs mt-3">
          Showing top 20 of {data.length} classifications
        </div>
      )}
    </div>
  );
};

export default ClassificationDistributionChart;
