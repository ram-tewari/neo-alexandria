// Neo Alexandria 2.0 Frontend - Recent Activity Timeline Component
// Displays recent resources viewed or modified with timestamps

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Clock, FileText, ExternalLink, Eye } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { AnimatedCard } from '@/components/ui/AnimatedCard';
import { Badge } from '@/components/ui/Badge';
import type { Resource } from '@/types/api';

interface ActivityItem {
  resource: Resource;
  timestamp: Date;
  action: 'viewed' | 'modified';
}

const RecentActivityTimeline: React.FC = () => {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const navigate = useNavigate();

  // Load recent activity from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem('recentActivity');
      if (stored) {
        const parsed = JSON.parse(stored);
        const items = parsed.map((item: any) => ({
          ...item,
          timestamp: new Date(item.timestamp),
        }));
        setActivities(items.slice(0, 20));
      }
    } catch (error) {
      console.error('Error loading recent activity:', error);
    }
  }, []);

  const handleResourceClick = (resourceId: string) => {
    navigate(`/resources/${resourceId}`);
  };

  if (activities.length === 0) {
    return (
      <div className="bg-charcoal-grey-800 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Clock className="w-6 h-6 text-accent-blue-500 mr-2" />
          <h2 className="text-2xl font-bold text-charcoal-grey-50">
            Recent Activity
          </h2>
        </div>
        <div className="text-center py-12">
          <Clock className="w-16 h-16 text-charcoal-grey-600 mx-auto mb-4" />
          <p className="text-charcoal-grey-400 text-lg">
            No recent activity yet.
          </p>
          <p className="text-charcoal-grey-500 text-sm mt-2">
            Start exploring resources to see your activity here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-charcoal-grey-800 rounded-lg p-6">
      <div className="flex items-center mb-6">
        <Clock className="w-6 h-6 text-accent-blue-500 mr-2" />
        <h2 className="text-2xl font-bold text-charcoal-grey-50">
          Recent Activity
        </h2>
      </div>

      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-charcoal-grey-600" />

        {/* Activity Items */}
        <motion.div
          className="space-y-6"
          variants={{
            hidden: { opacity: 0 },
            show: {
              opacity: 1,
              transition: {
                staggerChildren: 0.1,
              },
            },
          }}
          initial="hidden"
          animate="show"
        >
          {activities.map((activity, index) => (
            <motion.div
              key={`${activity.resource.id}-${activity.timestamp.getTime()}`}
              variants={{
                hidden: { opacity: 0, x: -20 },
                show: { opacity: 1, x: 0 },
              }}
              className="relative pl-16"
            >
              {/* Timeline Dot */}
              <div className="absolute left-4 top-4 w-4 h-4 rounded-full bg-accent-blue-500 border-4 border-charcoal-grey-800 z-10" />

              {/* Activity Card */}
              <AnimatedCard
                onClick={() => handleResourceClick(activity.resource.id)}
                className="cursor-pointer bg-charcoal-grey-700 hover:bg-charcoal-grey-600 transition-colors"
              >
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2 flex-1">
                      {activity.action === 'viewed' ? (
                        <Eye className="w-4 h-4 text-neutral-blue-400 flex-shrink-0" />
                      ) : (
                        <FileText className="w-4 h-4 text-accent-blue-400 flex-shrink-0" />
                      )}
                      <span className="text-xs text-charcoal-grey-400">
                        {activity.action === 'viewed' ? 'Viewed' : 'Modified'}{' '}
                        {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
                      </span>
                    </div>
                    <ExternalLink className="w-4 h-4 text-charcoal-grey-500 flex-shrink-0" />
                  </div>

                  <h3 className="text-lg font-semibold text-charcoal-grey-50 mb-2 line-clamp-2">
                    {activity.resource.title}
                  </h3>

                  {activity.resource.description && (
                    <p className="text-sm text-charcoal-grey-300 mb-3 line-clamp-2">
                      {activity.resource.description}
                    </p>
                  )}

                  <div className="flex items-center space-x-2 flex-wrap gap-2">
                    {activity.resource.classification_code && (
                      <Badge variant="default">
                        {activity.resource.classification_code}
                      </Badge>
                    )}
                    {activity.resource.type && (
                      <Badge variant="secondary">
                        {activity.resource.type}
                      </Badge>
                    )}
                    {activity.resource.quality_score !== undefined && (
                      <Badge
                        variant={
                          activity.resource.quality_score >= 0.8
                            ? 'success'
                            : activity.resource.quality_score >= 0.6
                            ? 'warning'
                            : 'default'
                        }
                      >
                        Quality: {Math.round(activity.resource.quality_score * 100)}%
                      </Badge>
                    )}
                  </div>
                </div>
              </AnimatedCard>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {activities.length >= 20 && (
        <div className="mt-6 text-center">
          <button
            onClick={() => navigate('/library')}
            className="text-accent-blue-400 hover:text-accent-blue-300 text-sm font-medium transition-colors"
          >
            View all activity in Library →
          </button>
        </div>
      )}
    </div>
  );
};

// Helper function to save activity (can be called from resource detail pages)
export const saveRecentActivity = (resource: Resource, action: 'viewed' | 'modified') => {
  try {
    const stored = localStorage.getItem('recentActivity');
    const activities: ActivityItem[] = stored ? JSON.parse(stored) : [];

    // Add new activity at the beginning
    const newActivity: ActivityItem = {
      resource,
      timestamp: new Date(),
      action,
    };

    // Remove duplicates and keep only last 50
    const filtered = activities.filter(
      (a) => a.resource.id !== resource.id || a.action !== action
    );
    const updated = [newActivity, ...filtered].slice(0, 50);

    localStorage.setItem('recentActivity', JSON.stringify(updated));
  } catch (error) {
    console.error('Error saving recent activity:', error);
  }
};

export { RecentActivityTimeline };
