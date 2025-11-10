// Neo Alexandria 2.0 Frontend - Version History Timeline Component
// Displays resource version history with visual timeline

import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Clock, Edit, Plus, CheckCircle, AlertCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface VersionHistoryTimelineProps {
  resourceId: string;
}

interface VersionEvent {
  id: string;
  type: 'created' | 'updated' | 'classified' | 'quality_updated';
  timestamp: string;
  description: string;
  details?: Record<string, any>;
}

// Event type icons
const EVENT_TYPE_ICONS: Record<VersionEvent['type'], React.ReactNode> = {
  created: <Plus className="w-4 h-4" />,
  updated: <Edit className="w-4 h-4" />,
  classified: <CheckCircle className="w-4 h-4" />,
  quality_updated: <AlertCircle className="w-4 h-4" />,
};

// Event type colors
const EVENT_TYPE_COLORS: Record<VersionEvent['type'], string> = {
  created: 'bg-green-500',
  updated: 'bg-accent-blue-500',
  classified: 'bg-purple-500',
  quality_updated: 'bg-yellow-500',
};

// Event type labels
const EVENT_TYPE_LABELS: Record<VersionEvent['type'], string> = {
  created: 'Created',
  updated: 'Updated',
  classified: 'Classified',
  quality_updated: 'Quality Updated',
};

export const VersionHistoryTimeline: React.FC<VersionHistoryTimelineProps> = ({ resourceId }) => {
  // TODO: In production, this would fetch from an API endpoint
  // For now, we'll generate mock data based on the resource
  // Since we don't have a version history API yet, we'll show a placeholder
  
  // Mock version events (in production, fetch from API)
  const versionEvents: VersionEvent[] = [
    {
      id: '1',
      type: 'created',
      timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      description: 'Resource created and ingestion started',
    },
    {
      id: '2',
      type: 'quality_updated',
      timestamp: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
      description: 'Quality score calculated',
      details: { quality_score: 0.85 },
    },
    {
      id: '3',
      type: 'classified',
      timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      description: 'Classification assigned',
      details: { classification_code: '000' },
    },
    {
      id: '4',
      type: 'updated',
      timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      description: 'Metadata updated',
      details: { fields: ['title', 'description'] },
    },
  ];

  // Sort events by timestamp (newest first)
  const sortedEvents = [...versionEvents].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return (
    <Card className="bg-charcoal-grey-800 border-charcoal-grey-700">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-accent-blue-400" />
          <h2 className="text-lg font-semibold text-charcoal-grey-50">Version History</h2>
        </div>
      </CardHeader>

      <CardContent>
        {sortedEvents.length > 0 ? (
          <div className="relative">
            {/* Timeline Line */}
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-charcoal-grey-700" />

            {/* Timeline Events */}
            <div className="space-y-4">
              {sortedEvents.map((event, index) => (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="relative pl-10"
                >
                  {/* Event Icon */}
                  <div
                    className={`absolute left-0 w-8 h-8 rounded-full ${EVENT_TYPE_COLORS[event.type]} flex items-center justify-center text-white shadow-lg`}
                  >
                    {EVENT_TYPE_ICONS[event.type]}
                  </div>

                  {/* Event Content */}
                  <div className="bg-charcoal-grey-700 border border-charcoal-grey-600 rounded-lg p-3">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <Badge
                        variant="outline"
                        size="sm"
                        className="text-charcoal-grey-300 border-charcoal-grey-500"
                      >
                        {EVENT_TYPE_LABELS[event.type]}
                      </Badge>
                      <div className="text-xs text-charcoal-grey-400">
                        {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                      </div>
                    </div>

                    <div className="text-sm text-charcoal-grey-50 mb-1">
                      {event.description}
                    </div>

                    {/* Event Details */}
                    {event.details && (
                      <div className="mt-2 text-xs text-charcoal-grey-400 space-y-1">
                        {Object.entries(event.details).map(([key, value]) => (
                          <div key={key}>
                            <span className="font-medium text-charcoal-grey-300">
                              {key.replace(/_/g, ' ')}:
                            </span>{' '}
                            {Array.isArray(value) ? value.join(', ') : String(value)}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Timestamp */}
                    <div className="text-xs text-charcoal-grey-500 mt-2">
                      {new Date(event.timestamp).toLocaleString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        ) : (
          <div className="py-8 text-center">
            <Clock className="w-12 h-12 text-charcoal-grey-400 mx-auto mb-4" />
            <div className="text-charcoal-grey-50 font-medium mb-2">No Version History</div>
            <div className="text-charcoal-grey-400 text-sm">
              Version history will appear here as changes are made to this resource.
            </div>
          </div>
        )}

        {/* Note about version history */}
        <div className="mt-4 pt-4 border-t border-charcoal-grey-700">
          <div className="text-xs text-charcoal-grey-400 italic">
            Note: Version history tracking is currently in development. The timeline above shows
            simulated events for demonstration purposes.
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
