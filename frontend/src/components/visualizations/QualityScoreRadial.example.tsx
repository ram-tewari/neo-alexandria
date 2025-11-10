// Neo Alexandria 2.0 Frontend - QualityScoreRadial Component Examples
// Demonstrates various usage patterns of the QualityScoreRadial component

import React from 'react';
import { QualityScoreRadial } from './QualityScoreRadial';

/**
 * Example component showcasing different QualityScoreRadial configurations
 */
export const QualityScoreRadialExamples: React.FC = () => {
  return (
    <div className="p-8 space-y-12 bg-charcoal-grey-900">
      <div>
        <h2 className="text-2xl font-bold text-charcoal-grey-50 mb-6">
          QualityScoreRadial Component Examples
        </h2>
        
        {/* Example 1: High Quality Score (Green) */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-charcoal-grey-200 mb-4">
            High Quality Score (80-100)
          </h3>
          <div className="flex gap-8 flex-wrap">
            <QualityScoreRadial value={85} />
            <QualityScoreRadial value={92} />
            <QualityScoreRadial value={100} />
          </div>
        </div>

        {/* Example 2: Medium Quality Score (Yellow) */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-charcoal-grey-200 mb-4">
            Medium Quality Score (60-79)
          </h3>
          <div className="flex gap-8 flex-wrap">
            <QualityScoreRadial value={60} />
            <QualityScoreRadial value={70} />
            <QualityScoreRadial value={79} />
          </div>
        </div>

        {/* Example 3: Low Quality Score (Red) */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-charcoal-grey-200 mb-4">
            Low Quality Score (0-59)
          </h3>
          <div className="flex gap-8 flex-wrap">
            <QualityScoreRadial value={25} />
            <QualityScoreRadial value={45} />
            <QualityScoreRadial value={59} />
          </div>
        </div>

        {/* Example 4: Different Sizes */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-charcoal-grey-200 mb-4">
            Different Sizes
          </h3>
          <div className="flex gap-8 items-end flex-wrap">
            <QualityScoreRadial value={75} size={80} />
            <QualityScoreRadial value={75} size={120} />
            <QualityScoreRadial value={75} size={160} />
          </div>
        </div>

        {/* Example 5: Custom Stroke Width */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-charcoal-grey-200 mb-4">
            Custom Stroke Width
          </h3>
          <div className="flex gap-8 flex-wrap">
            <QualityScoreRadial value={88} strokeWidth={4} />
            <QualityScoreRadial value={88} strokeWidth={8} />
            <QualityScoreRadial value={88} strokeWidth={12} />
          </div>
        </div>

        {/* Example 6: Without Label */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-charcoal-grey-200 mb-4">
            Without Label
          </h3>
          <div className="flex gap-8 flex-wrap">
            <QualityScoreRadial value={82} showLabel={false} />
          </div>
        </div>

        {/* Example 7: Custom Label */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-charcoal-grey-200 mb-4">
            Custom Label
          </h3>
          <div className="flex gap-8 flex-wrap">
            <QualityScoreRadial value={95} label="Metadata Score" />
            <QualityScoreRadial value={68} label="Content Score" />
            <QualityScoreRadial value={42} label="Completeness" />
          </div>
        </div>

        {/* Example 8: Fast Animation */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-charcoal-grey-200 mb-4">
            Fast Animation (0.5s)
          </h3>
          <div className="flex gap-8 flex-wrap">
            <QualityScoreRadial value={77} animationDuration={0.5} />
          </div>
        </div>

        {/* Example 9: Slow Animation */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-charcoal-grey-200 mb-4">
            Slow Animation (2s)
          </h3>
          <div className="flex gap-8 flex-wrap">
            <QualityScoreRadial value={77} animationDuration={2} />
          </div>
        </div>

        {/* Example 10: In a Card Context */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-charcoal-grey-200 mb-4">
            In a Card Context
          </h3>
          <div className="bg-charcoal-grey-800 border border-charcoal-grey-700 rounded-lg p-6 max-w-sm">
            <h4 className="text-lg font-semibold text-charcoal-grey-50 mb-4">
              Resource Quality
            </h4>
            <div className="flex justify-center">
              <QualityScoreRadial value={87} />
            </div>
            <p className="text-sm text-charcoal-grey-400 mt-4 text-center">
              This resource has excellent quality metrics
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QualityScoreRadialExamples;
