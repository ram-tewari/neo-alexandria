// Neo Alexandria 2.0 Frontend - Temporal Trends Chart Component
// Interactive line chart showing resource creation trends over time

import React, { useMemo, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush,
} from 'recharts';
import { format, parseISO } from 'date-fns';

interface TemporalDataPoint {
  date: string; // ISO date string
  [key: string]: number | string; // Dynamic keys for different resource types
}

interface TemporalTrendsChartProps {
  /**
   * Temporal trend data with dates and counts
   */
  data: TemporalDataPoint[];
  /**
   * Series to display (e.g., ['article', 'dataset', 'code'])
   */
  series: string[];
  /**
   * Height of the chart
   * @default 400
   */
  height?: number;
  /**
   * Date format for x-axis
   * @default 'MMM yyyy'
   */
  dateFormat?: string;
  /**
   * Enable zoom and pan with brush
   * @default true
   */
  enableBrush?: boolean;
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Color palette for different series
 */
const seriesColors: Record<string, string> = {
  article: '#3B82F6', // Accent blue
  dataset: '#10B981', // Green
  code: '#8B5CF6', // Purple
  book: '#F59E0B', // Amber
  video: '#EF4444', // Red
  audio: '#EC4899', // Pink
  image: '#14B8A6', // Teal
  other: '#6B7280', // Grey
};

/**
 * Get color for a series, with fallback
 */
const getSeriesColor = (seriesName: string): string => {
  return seriesColors[seriesName.toLowerCase()] || '#6B7280';
};

/**
 * Custom tooltip component
 */
const CustomTooltip: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) {
    return null;
  }

  return (
    <div className="bg-[#09090B] border border-[#27272A] rounded-lg p-3 shadow-2xl">
      <div className="text-zinc-100 font-medium mb-2 text-sm">
        {format(parseISO(label), 'MMMM yyyy')}
      </div>
      <div className="space-y-1.5">
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-zinc-400 text-xs capitalize">
                {entry.name}
              </span>
            </div>
            <span className="text-zinc-200 font-medium text-xs">
              {entry.value}
            </span>
          </div>
        ))}
      </div>
      <div className="mt-2 pt-2 border-t border-[#27272A]">
        <div className="flex items-center justify-between">
          <span className="text-zinc-500 text-xs">Total</span>
          <span className="text-zinc-200 font-medium text-xs">
            {payload.reduce((sum: number, entry: any) => sum + entry.value, 0)}
          </span>
        </div>
      </div>
    </div>
  );
};

/**
 * TemporalTrendsChart - Interactive line chart for temporal trends
 * 
 * Features:
 * - Line chart using Recharts library
 * - Dates on x-axis with formatted labels
 * - Resource creation counts on y-axis
 * - Multiple series for different resource types
 * - Zoom and pan interactions with brush component
 * - Interactive legend to toggle series visibility
 * - Hover tooltips with detailed breakdown
 * - Responsive container that adapts to parent width
 * 
 * @example
 * ```tsx
 * <TemporalTrendsChart 
 *   data={trendsData}
 *   series={['article', 'dataset', 'code']}
 *   enableBrush={true}
 * />
 * ```
 */
export const TemporalTrendsChart: React.FC<TemporalTrendsChartProps> = ({
  data,
  series,
  height = 400,
  dateFormat = 'MMM yyyy',
  enableBrush = true,
  className = '',
}) => {
  const [hiddenSeries, setHiddenSeries] = useState<Set<string>>(new Set());

  // Sort data by date
  const sortedData = useMemo(() => {
    return [...data].sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  }, [data]);

  // Format date for display
  const formatXAxis = (dateString: string) => {
    try {
      return format(parseISO(dateString), dateFormat);
    } catch {
      return dateString;
    }
  };

  // Calculate max value for Y-axis domain
  const maxCount = useMemo(() => {
    let max = 0;
    sortedData.forEach(point => {
      const total = series.reduce((sum, s) => {
        const value = point[s];
        return sum + (typeof value === 'number' ? value : 0);
      }, 0);
      max = Math.max(max, total);
    });
    return max;
  }, [sortedData, series]);

  // Handle legend click to toggle series visibility
  const handleLegendClick = (dataKey: string) => {
    setHiddenSeries(prev => {
      const newSet = new Set(prev);
      if (newSet.has(dataKey)) {
        newSet.delete(dataKey);
      } else {
        newSet.add(dataKey);
      }
      return newSet;
    });
  };

  return (
    <div className={`temporal-trends-chart ${className}`}>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={sortedData}
          margin={{ top: 20, right: 30, left: 20, bottom: enableBrush ? 60 : 20 }}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#27272A" 
            opacity={0.5}
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tickFormatter={formatXAxis}
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
          <Tooltip content={<CustomTooltip />} />
          <Legend
            onClick={(e) => handleLegendClick(e.dataKey as string)}
            wrapperStyle={{ cursor: 'pointer', fontSize: '12px' }}
            formatter={(value: string) => (
              <span className="capitalize text-zinc-400">{value}</span>
            )}
          />
          
          {series.map((seriesName) => (
            <Line
              key={seriesName}
              type="monotone"
              dataKey={seriesName}
              stroke={getSeriesColor(seriesName)}
              strokeWidth={1.5}
              dot={{ r: 3, strokeWidth: 0 }}
              activeDot={{ r: 5, strokeWidth: 0 }}
              hide={hiddenSeries.has(seriesName)}
              name={seriesName}
            />
          ))}
          
          {enableBrush && (
            <Brush
              dataKey="date"
              height={28}
              stroke="#3B82F6"
              fill="#09090B"
              tickFormatter={formatXAxis}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
      
      <div className="text-center text-zinc-600 text-xs mt-3">
        {enableBrush && 'Drag the brush below to zoom into a time range'}
        {!enableBrush && 'Click legend items to toggle series visibility'}
      </div>
    </div>
  );
};

export default TemporalTrendsChart;
