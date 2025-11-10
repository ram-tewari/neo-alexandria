// Neo Alexandria 2.0 Frontend - Home Page
// Dashboard with recommendations, quick search, and recent activity

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { RecommendationsFeed } from '@/components/home/RecommendationsFeed';
import { QuickSearchPanel } from '@/components/home/QuickSearchPanel';
import { RecentActivityTimeline } from '@/components/home/RecentActivityTimeline';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section with Animated Background */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="relative overflow-hidden bg-gradient-to-br from-charcoal-grey-900 via-charcoal-grey-800 to-neutral-blue-900 py-20 px-4"
      >
        {/* Animated Background Gradient */}
        <motion.div
          className="absolute inset-0 opacity-30"
          animate={{
            background: [
              'radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)',
              'radial-gradient(circle at 80% 50%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)',
              'radial-gradient(circle at 50% 80%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)',
              'radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)',
            ],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: 'linear',
          }}
        />

        {/* Hero Content with Stagger Animation */}
        <motion.div
          className="relative z-10 max-w-4xl mx-auto text-center"
          initial="hidden"
          animate="visible"
          variants={{
            hidden: { opacity: 0 },
            visible: {
              opacity: 1,
              transition: {
                staggerChildren: 0.2,
              },
            },
          }}
        >
          <motion.div
            variants={{
              hidden: { opacity: 0, y: 20 },
              visible: { opacity: 1, y: 0 },
            }}
            className="flex items-center justify-center mb-6"
          >
            <Sparkles className="w-12 h-12 text-accent-blue-400 mr-3" />
            <h1 className="text-5xl md:text-6xl font-bold text-charcoal-grey-50">
              Neo Alexandria
            </h1>
          </motion.div>

          <motion.p
            variants={{
              hidden: { opacity: 0, y: 20 },
              visible: { opacity: 1, y: 0 },
            }}
            className="text-xl md:text-2xl text-charcoal-grey-300 mb-8"
          >
            Your intelligent knowledge management system
          </motion.p>

          <motion.p
            variants={{
              hidden: { opacity: 0, y: 20 },
              visible: { opacity: 1, y: 0 },
            }}
            className="text-lg text-charcoal-grey-400 max-w-2xl mx-auto"
          >
            Discover, organize, and explore your research with AI-powered recommendations,
            advanced search, and interactive knowledge graphs.
          </motion.p>
        </motion.div>
      </motion.div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12 space-y-12">
        {/* Quick Search Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          <QuickSearchPanel />
        </motion.div>

        {/* Recommendations Feed */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <RecommendationsFeed />
        </motion.div>

        {/* Recent Activity Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.5 }}
        >
          <RecentActivityTimeline />
        </motion.div>
      </div>
    </div>
  );
};

export { HomePage };
