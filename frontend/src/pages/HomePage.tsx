// Neo Alexandria 2.0 Frontend - Home Page
// Dashboard with recommendations, quick search, and recent activity

import React from 'react';
import { RecommendationsFeed } from '@/components/home/RecommendationsFeed';
import { QuickSearchPanel } from '@/components/home/QuickSearchPanel';
import { RecentActivityTimeline } from '@/components/home/RecentActivityTimeline';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-black">
      {/* Hero Section - Clean and Minimal */}
      <div className="border-b border-zinc-900">
        <div className="max-w-5xl mx-auto px-6 py-16">
          <h1 className="text-3xl font-semibold text-zinc-100 mb-4">
            Neo Alexandria
          </h1>
          
          <p className="text-base text-zinc-400 mb-3 max-w-2xl">
            Your intelligent knowledge management system
          </p>
          
          <p className="text-sm text-zinc-500 max-w-2xl">
            Discover, organize, and explore your research with AI-powered recommendations,
            advanced search, and interactive knowledge graphs.
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {/* Quick Search Panel */}
        <QuickSearchPanel />

        {/* Recommendations Feed */}
        <RecommendationsFeed />

        {/* Recent Activity Timeline */}
        <RecentActivityTimeline />
      </div>
    </div>
  );
};

export { HomePage };
