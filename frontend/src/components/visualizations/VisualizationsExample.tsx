// Neo Alexandria 2.0 Frontend - Visualizations Example
// Example usage of all visualization components

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  QualityScoreRadial,
  CitationNetworkGraph,
  ClassificationDistributionChart,
  TemporalTrendsChart,
} from './index';

/**
 * Example component demonstrating all visualization components
 * This can be used as a reference or in a dashboard/analytics page
 */
export const VisualizationsExample: React.FC = () => {
  const navigate = useNavigate();

  // Example data for CitationNetworkGraph
  const citationGraphData = {
    nodes: [
      { id: '1', title: 'Machine Learning Basics', type: 'reference', classification_code: '006.31' },
      { id: '2', title: 'Deep Learning Dataset', type: 'dataset', classification_code: '006.31' },
      { id: '3', title: 'Neural Network Code', type: 'code', classification_code: '006.32' },
      { id: '4', title: 'AI Ethics Paper', type: 'reference', classification_code: '174.9' },
    ],
    edges: [
      { source: '1', target: '2', weight: 0.8, details: { connection_type: 'vector' as const } },
      { source: '1', target: '3', weight: 0.6, details: { connection_type: 'subject' as const } },
      { source: '2', target: '3', weight: 0.9, details: { connection_type: 'classification' as const } },
      { source: '1', target: '4', weight: 0.5, details: { connection_type: 'hybrid' as const } },
    ],
  };

  // Example data for ClassificationDistributionChart
  const classificationData = [
    { code: '006.31', name: 'Machine Learning', count: 45 },
    { code: '006.32', name: 'Neural Networks', count: 38 },
    { code: '174.9', name: 'AI Ethics', count: 22 },
    { code: '510', name: 'Mathematics', count: 31 },
    { code: '004.6', name: 'Computer Networks', count: 18 },
    { code: '005.1', name: 'Programming', count: 27 },
  ];

  // Example data for TemporalTrendsChart
  const temporalData = [
    { date: '2024-01-01', article: 12, dataset: 5, code: 3 },
    { date: '2024-02-01', article: 15, dataset: 7, code: 4 },
    { date: '2024-03-01', article: 18, dataset: 9, code: 6 },
    { date: '2024-04-01', article: 22, dataset: 11, code: 8 },
    { date: '2024-05-01', article: 25, dataset: 13, code: 10 },
    { date: '2024-06-01', article: 28, dataset: 15, code: 12 },
  ];

  return (
    <div className="min-h-screen bg-black">
      <div className="max-w-7xl mx-auto px-6 py-12 space-y-16">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold text-zinc-100">
            Data Visualizations
          </h1>
          <p className="text-sm text-zinc-500">
            Interactive charts and graphs for knowledge exploration
          </p>
        </div>

        {/* Quality Score Radials */}
        <section className="space-y-4">
          <h2 className="text-base font-medium text-zinc-300">
            Quality Score Indicators
          </h2>
          <div className="flex gap-12 flex-wrap">
            <QualityScoreRadial value={85} label="High Quality" />
            <QualityScoreRadial value={72} label="Medium Quality" />
            <QualityScoreRadial value={45} label="Low Quality" />
          </div>
        </section>

        {/* Citation Network Graph */}
        <section className="space-y-4">
          <h2 className="text-base font-medium text-zinc-300">
            Citation Network
          </h2>
          <div className="bg-[#0A0A0A] border border-[#27272A] rounded-lg p-6">
            <CitationNetworkGraph
              data={citationGraphData}
              width={800}
              height={500}
              onNodeClick={(id) => navigate(`/resources/${id}`)}
            />
          </div>
        </section>

        {/* Classification Distribution */}
        <section className="space-y-4">
          <h2 className="text-base font-medium text-zinc-300">
            Classification Distribution
          </h2>
          <div className="bg-[#0A0A0A] border border-[#27272A] rounded-lg p-6">
            <ClassificationDistributionChart
              data={classificationData}
              height={400}
              onBarClick={(code) => console.log('Filter by:', code)}
            />
          </div>
        </section>

        {/* Temporal Trends */}
        <section className="space-y-4">
          <h2 className="text-base font-medium text-zinc-300">
            Resource Creation Trends
          </h2>
          <div className="bg-[#0A0A0A] border border-[#27272A] rounded-lg p-6">
            <TemporalTrendsChart
              data={temporalData}
              series={['article', 'dataset', 'code']}
              height={400}
              enableBrush={true}
            />
          </div>
        </section>
      </div>
    </div>
  );
};

export default VisualizationsExample;
