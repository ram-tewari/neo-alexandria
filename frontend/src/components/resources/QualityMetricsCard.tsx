// Neo Alexandria 2.0 Frontend - Quality Metrics Card Component
// Displays quality score with radial progress and detailed metrics

import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { QualityScoreRadial } from '@/components/visualizations';
import type { Resource } from '@/types/api';
import {
  Award,
  CheckCircle,
  AlertCircle,
  XCircle,
  TrendingUp,
  FileText,
  Eye,
} from 'lucide-react';

interface QualityMetricsCardProps {
  resource: Resource;
}

// Quality level badge
const QualityLevelBadge: React.FC<{ score: number }> = ({ score }) => {
  const getLevel = () => {
    if (score >= 0.8) return { label: 'High Quality', variant: 'success' as const, icon: CheckCircle };
    if (score >= 0.6) return { label: 'Medium Quality', variant: 'warning' as const, icon: AlertCircle };
    return { label: 'Needs Review', variant: 'error' as const, icon: XCircle };
  };

  const level = getLevel();
  const Icon = level.icon;

  return (
    <Badge variant={level.variant} size="md" className="flex items-center gap-1">
      <Icon className="w-3 h-3" />
      {level.label}
    </Badge>
  );
};

export const QualityMetricsCard: React.FC<QualityMetricsCardProps> = ({ resource }) => {
  const qualityScore = Math.round(resource.quality_score * 100);

  // Calculate metadata completeness
  const metadataFields = [
    resource.title,
    resource.description,
    resource.creator,
    resource.publisher,
    resource.language,
    resource.type,
    resource.classification_code,
    resource.subject?.length > 0,
  ];
  const completedFields = metadataFields.filter(Boolean).length;
  const metadataCompleteness = Math.round((completedFields / metadataFields.length) * 100);

  // Mock readability metrics (in production, these would come from the API)
  const readabilityMetrics = {
    flesch_kincaid: 8.5,
    gunning_fog: 10.2,
    automated_readability: 9.1,
  };

  // Generate quality suggestions based on score and completeness
  const suggestions: string[] = [];
  if (!resource.description) {
    suggestions.push('Add a detailed description to improve discoverability');
  }
  if (!resource.creator) {
    suggestions.push('Specify the creator or author information');
  }
  if (!resource.classification_code) {
    suggestions.push('Assign a classification code for better organization');
  }
  if (resource.subject.length < 3) {
    suggestions.push('Add more subject tags to enhance searchability');
  }
  if (qualityScore < 80) {
    suggestions.push('Review and enhance metadata completeness');
  }

  return (
    <Card className="bg-charcoal-grey-800 border-charcoal-grey-700">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Award className="w-5 h-5 text-accent-blue-400" />
          <h2 className="text-lg font-semibold text-charcoal-grey-50">Quality Metrics</h2>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Radial Progress */}
        <div className="flex flex-col items-center">
          <QualityScoreRadial value={qualityScore} />
          <div className="mt-3">
            <QualityLevelBadge score={resource.quality_score} />
          </div>
        </div>

        {/* Metadata Completeness */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-charcoal-grey-400" />
              <span className="text-sm font-medium text-charcoal-grey-50">
                Metadata Completeness
              </span>
            </div>
            <span className="text-sm font-bold text-charcoal-grey-50">
              {metadataCompleteness}%
            </span>
          </div>
          <div className="w-full bg-charcoal-grey-700 rounded-full h-2 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${metadataCompleteness}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className={`h-full rounded-full ${
                metadataCompleteness >= 80
                  ? 'bg-green-500'
                  : metadataCompleteness >= 60
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}
            />
          </div>
          <div className="text-xs text-charcoal-grey-400 mt-1">
            {completedFields} of {metadataFields.length} fields completed
          </div>
        </div>

        {/* Readability Metrics */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Eye className="w-4 h-4 text-charcoal-grey-400" />
            <span className="text-sm font-medium text-charcoal-grey-50">
              Readability Metrics
            </span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-xs text-charcoal-grey-400">Flesch-Kincaid Grade</span>
              <span className="text-sm text-charcoal-grey-50 font-medium">
                {readabilityMetrics.flesch_kincaid}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-charcoal-grey-400">Gunning Fog Index</span>
              <span className="text-sm text-charcoal-grey-50 font-medium">
                {readabilityMetrics.gunning_fog}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-charcoal-grey-400">Automated Readability</span>
              <span className="text-sm text-charcoal-grey-50 font-medium">
                {readabilityMetrics.automated_readability}
              </span>
            </div>
          </div>
          <div className="text-xs text-charcoal-grey-400 mt-2 italic">
            Note: Readability metrics are simulated for demonstration
          </div>
        </div>

        {/* Quality Suggestions */}
        {suggestions.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-4 h-4 text-charcoal-grey-400" />
              <span className="text-sm font-medium text-charcoal-grey-50">
                Improvement Suggestions
              </span>
            </div>
            <div className="space-y-2">
              {suggestions.map((suggestion, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-2 text-xs text-charcoal-grey-300"
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-accent-blue-500 mt-1.5 flex-shrink-0" />
                  <span>{suggestion}</span>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Quality Score Breakdown */}
        <div className="pt-4 border-t border-charcoal-grey-700">
          <div className="text-xs text-charcoal-grey-400 space-y-1">
            <div className="flex justify-between">
              <span>Overall Quality:</span>
              <span className="text-charcoal-grey-300 font-medium">{qualityScore}%</span>
            </div>
            <div className="flex justify-between">
              <span>Metadata Quality:</span>
              <span className="text-charcoal-grey-300 font-medium">{metadataCompleteness}%</span>
            </div>
            <div className="flex justify-between">
              <span>Content Depth:</span>
              <span className="text-charcoal-grey-300 font-medium">
                {resource.description ? 'Good' : 'Limited'}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
