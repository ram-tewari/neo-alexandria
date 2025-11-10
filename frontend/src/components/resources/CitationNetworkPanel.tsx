// Neo Alexandria 2.0 Frontend - Citation Network Panel Component
// Displays inbound and outbound citations with importance scores

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { useCitations } from '@/hooks/useCitations';
import type { Citation } from '@/services/api/citations';
import {
  Quote,
  ArrowRight,
  ArrowLeft,
  ExternalLink,
  FileCode,
  Database,
  BookOpen,
  RefreshCw,
} from 'lucide-react';

interface CitationNetworkPanelProps {
  resourceId: string;
}

type TabType = 'inbound' | 'outbound';

// Citation type icons
const CITATION_TYPE_ICONS: Record<Citation['citation_type'], React.ReactNode> = {
  reference: <Quote className="w-4 h-4" />,
  dataset: <Database className="w-4 h-4" />,
  code: <FileCode className="w-4 h-4" />,
  general: <BookOpen className="w-4 h-4" />,
};

// Citation type colors
const CITATION_TYPE_COLORS: Record<Citation['citation_type'], string> = {
  reference: 'bg-accent-blue-500/20 text-accent-blue-400 border-accent-blue-500/30',
  dataset: 'bg-green-500/20 text-green-400 border-green-500/30',
  code: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  general: 'bg-neutral-blue-500/20 text-neutral-blue-400 border-neutral-blue-500/30',
};

// Get importance score color
const getImportanceColor = (score?: number): string => {
  if (!score) return 'text-charcoal-grey-400';
  if (score >= 0.8) return 'text-green-400';
  if (score >= 0.5) return 'text-yellow-400';
  return 'text-charcoal-grey-400';
};

// Citation item component
const CitationItem: React.FC<{
  citation: Citation;
  direction: 'inbound' | 'outbound';
  onNavigate: (id: string) => void;
}> = ({ citation, direction, onNavigate }) => {
  const hasTargetResource = !!citation.target_resource_id;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="bg-charcoal-grey-700 border border-charcoal-grey-600 rounded-lg p-4 hover:border-charcoal-grey-500 transition-colors"
    >
      <div className="flex items-start gap-3">
        {/* Direction Icon */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          direction === 'inbound' ? 'bg-green-500/20' : 'bg-accent-blue-500/20'
        }`}>
          {direction === 'inbound' ? (
            <ArrowLeft className="w-4 h-4 text-green-400" />
          ) : (
            <ArrowRight className="w-4 h-4 text-accent-blue-400" />
          )}
        </div>

        {/* Citation Content */}
        <div className="flex-1 min-w-0">
          {/* Citation Type Badge */}
          <div className="flex items-center gap-2 mb-2">
            <Badge
              variant="outline"
              size="sm"
              className={CITATION_TYPE_COLORS[citation.citation_type]}
            >
              <span className="flex items-center gap-1">
                {CITATION_TYPE_ICONS[citation.citation_type]}
                {citation.citation_type}
              </span>
            </Badge>

            {/* Importance Score */}
            {citation.importance_score !== undefined && (
              <div className={`text-xs font-medium ${getImportanceColor(citation.importance_score)}`}>
                Importance: {Math.round(citation.importance_score * 100)}%
              </div>
            )}
          </div>

          {/* Target URL */}
          <div className="mb-2">
            <a
              href={citation.target_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-accent-blue-400 hover:text-accent-blue-300 transition-colors break-all flex items-center gap-1 group"
            >
              <span className="truncate">{citation.target_url}</span>
              <ExternalLink className="w-3 h-3 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
            </a>
          </div>

          {/* Context Snippet */}
          {citation.context_snippet && (
            <div className="text-sm text-charcoal-grey-300 bg-charcoal-grey-800 rounded p-2 mb-2 italic border-l-2 border-charcoal-grey-600">
              "{citation.context_snippet}"
            </div>
          )}

          {/* Navigate Button */}
          {hasTargetResource && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onNavigate(citation.target_resource_id!)}
              className="mt-2"
            >
              View Resource
            </Button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export const CitationNetworkPanel: React.FC<CitationNetworkPanelProps> = ({ resourceId }) => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('outbound');
  
  const { data: citationData, isLoading, error, refetch } = useCitations(resourceId);

  const inboundCitations = citationData?.inbound || [];
  const outboundCitations = citationData?.outbound || [];
  const activeCitations = activeTab === 'inbound' ? inboundCitations : outboundCitations;

  const handleNavigate = (id: string) => {
    navigate(`/resources/${id}`);
  };

  return (
    <Card className="bg-charcoal-grey-800 border-charcoal-grey-700">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Quote className="w-5 h-5 text-accent-blue-400" />
            <h2 className="text-xl font-semibold text-charcoal-grey-50">Citation Network</h2>
          </div>

          <Button
            variant="outline"
            size="sm"
            icon={<RefreshCw />}
            onClick={() => refetch()}
            loading={isLoading}
          >
            Refresh
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-charcoal-grey-700">
          <button
            onClick={() => setActiveTab('outbound')}
            className={`px-4 py-2 text-sm font-medium transition-colors relative ${
              activeTab === 'outbound'
                ? 'text-accent-blue-400'
                : 'text-charcoal-grey-400 hover:text-charcoal-grey-300'
            }`}
          >
            <span className="flex items-center gap-2">
              <ArrowRight className="w-4 h-4" />
              Outbound Citations
              {outboundCitations.length > 0 && (
                <Badge variant="info" size="sm">
                  {outboundCitations.length}
                </Badge>
              )}
            </span>
            {activeTab === 'outbound' && (
              <motion.div
                layoutId="activeTab"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent-blue-500"
              />
            )}
          </button>

          <button
            onClick={() => setActiveTab('inbound')}
            className={`px-4 py-2 text-sm font-medium transition-colors relative ${
              activeTab === 'inbound'
                ? 'text-accent-blue-400'
                : 'text-charcoal-grey-400 hover:text-charcoal-grey-300'
            }`}
          >
            <span className="flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Inbound Citations
              {inboundCitations.length > 0 && (
                <Badge variant="info" size="sm">
                  {inboundCitations.length}
                </Badge>
              )}
            </span>
            {activeTab === 'inbound' && (
              <motion.div
                layoutId="activeTab"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent-blue-500"
              />
            )}
          </button>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="py-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-blue-500 mx-auto mb-4" />
            <div className="text-charcoal-grey-400">Loading citations...</div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="py-12 text-center">
            <Quote className="w-12 h-12 text-charcoal-grey-400 mx-auto mb-4" />
            <div className="text-charcoal-grey-50 font-medium mb-2">Failed to load citations</div>
            <div className="text-charcoal-grey-400 text-sm mb-4">
              {error instanceof Error ? error.message : 'An error occurred'}
            </div>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              Try Again
            </Button>
          </div>
        )}

        {/* Citations List */}
        {!isLoading && !error && (
          <AnimatePresence mode="wait">
            {activeCitations.length > 0 ? (
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: activeTab === 'inbound' ? -20 : 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: activeTab === 'inbound' ? 20 : -20 }}
                transition={{ duration: 0.2 }}
                className="space-y-3"
              >
                {activeCitations.map((citation) => (
                  <CitationItem
                    key={citation.id}
                    citation={citation}
                    direction={activeTab}
                    onNavigate={handleNavigate}
                  />
                ))}
              </motion.div>
            ) : (
              <motion.div
                key={`${activeTab}-empty`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="py-12 text-center"
              >
                <Quote className="w-12 h-12 text-charcoal-grey-400 mx-auto mb-4" />
                <div className="text-charcoal-grey-50 font-medium mb-2">
                  No {activeTab} citations
                </div>
                <div className="text-charcoal-grey-400 text-sm">
                  {activeTab === 'outbound'
                    ? 'This resource does not cite any other resources.'
                    : 'This resource is not cited by any other resources yet.'}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        )}

        {/* Summary */}
        {!isLoading && !error && (inboundCitations.length > 0 || outboundCitations.length > 0) && (
          <div className="mt-6 pt-4 border-t border-charcoal-grey-700">
            <div className="text-sm text-charcoal-grey-400">
              <span className="font-medium text-charcoal-grey-300">Citation Summary:</span>{' '}
              This resource cites {outboundCitations.length} other{' '}
              {outboundCitations.length === 1 ? 'resource' : 'resources'} and is cited by{' '}
              {inboundCitations.length} {inboundCitations.length === 1 ? 'resource' : 'resources'}.
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
