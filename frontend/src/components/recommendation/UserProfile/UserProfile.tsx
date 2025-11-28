import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Save, Plus, X, BarChart3, TrendingUp, Target } from 'lucide-react';
import { useUserPreferences, useUpdatePreferences, useRecommendationMetrics } from '@/hooks/useRecommendations';
import { UserPreferences } from '@/types/recommendation';
import { useReducedMotion } from '@/hooks/useReducedMotion';

interface UserProfileProps {
  onClose?: () => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ onClose }) => {
  const { data: preferences, isLoading } = useUserPreferences();
  const { data: metrics } = useRecommendationMetrics();
  const updatePreferences = useUpdatePreferences();
  const prefersReducedMotion = useReducedMotion();

  const [localPreferences, setLocalPreferences] = useState<UserPreferences>({
    interests: [],
    diversity: 0.5,
    novelty: 0.5,
    recency: 0.5,
    domains: [],
  });
  const [newInterest, setNewInterest] = useState('');
  const [newDomain, setNewDomain] = useState('');

  React.useEffect(() => {
    if (preferences) {
      setLocalPreferences(preferences);
    }
  }, [preferences]);

  const handleSave = () => {
    updatePreferences.mutate(localPreferences);
  };

  const addInterest = () => {
    if (newInterest.trim() && !localPreferences.interests.includes(newInterest.trim())) {
      setLocalPreferences(prev => ({
        ...prev,
        interests: [...prev.interests, newInterest.trim()]
      }));
      setNewInterest('');
    }
  };

  const removeInterest = (interest: string) => {
    setLocalPreferences(prev => ({
      ...prev,
      interests: prev.interests.filter(i => i !== interest)
    }));
  };

  const addDomain = () => {
    if (newDomain.trim() && !localPreferences.domains.includes(newDomain.trim())) {
      setLocalPreferences(prev => ({
        ...prev,
        domains: [...prev.domains, newDomain.trim()]
      }));
      setNewDomain('');
    }
  };

  const removeDomain = (domain: string) => {
    setLocalPreferences(prev => ({
      ...prev,
      domains: prev.domains.filter(d => d !== domain)
    }));
  };

  const getSliderColor = (value: number) => {
    if (value < 0.3) return 'accent-blue-500';
    if (value < 0.7) return 'accent-yellow-500';
    return 'accent-green-500';
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl mx-auto overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Recommendation Preferences
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Customize your personalized recommendations
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      <div className="p-6 space-y-8">
        {/* Interests Section */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Research Interests
            </h3>
          </div>
          
          <div className="flex items-center gap-2 mb-3">
            <input
              type="text"
              value={newInterest}
              onChange={(e) => setNewInterest(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addInterest()}
              placeholder="Add an interest..."
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <button
              onClick={addInterest}
              className="p-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
              aria-label="Add interest"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {localPreferences.interests.map((interest, index) => (
              <motion.span
                key={interest}
                initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 rounded-full text-sm"
              >
                {interest}
                <button
                  onClick={() => removeInterest(interest)}
                  className="hover:text-primary-900 dark:hover:text-primary-100"
                  aria-label={`Remove ${interest}`}
                >
                  <X className="w-3 h-3" />
                </button>
              </motion.span>
            ))}
          </div>
        </div>

        {/* Research Domains */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Research Domains
          </h3>
          
          <div className="flex items-center gap-2 mb-3">
            <input
              type="text"
              value={newDomain}
              onChange={(e) => setNewDomain(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addDomain()}
              placeholder="Add a domain (e.g., Computer Science)..."
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <button
              onClick={addDomain}
              className="p-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
              aria-label="Add domain"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {localPreferences.domains.map((domain) => (
              <motion.span
                key={domain}
                initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-full text-sm"
              >
                {domain}
                <button
                  onClick={() => removeDomain(domain)}
                  className="hover:text-blue-900 dark:hover:text-blue-100"
                  aria-label={`Remove ${domain}`}
                >
                  <X className="w-3 h-3" />
                </button>
              </motion.span>
            ))}
          </div>
        </div>

        {/* Preference Sliders */}
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Recommendation Tuning
          </h3>

          {/* Diversity Slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Diversity
              </label>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {Math.round(localPreferences.diversity * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={localPreferences.diversity}
              onChange={(e) => setLocalPreferences(prev => ({
                ...prev,
                diversity: parseFloat(e.target.value)
              }))}
              className={`w-full h-2 rounded-lg appearance-none cursor-pointer ${getSliderColor(localPreferences.diversity)}`}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Lower: Similar topics • Higher: Varied topics
            </p>
          </div>

          {/* Novelty Slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Novelty
              </label>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {Math.round(localPreferences.novelty * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={localPreferences.novelty}
              onChange={(e) => setLocalPreferences(prev => ({
                ...prev,
                novelty: parseFloat(e.target.value)
              }))}
              className={`w-full h-2 rounded-lg appearance-none cursor-pointer ${getSliderColor(localPreferences.novelty)}`}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Lower: Familiar content • Higher: Exploratory content
            </p>
          </div>

          {/* Recency Slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Recency
              </label>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {Math.round(localPreferences.recency * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={localPreferences.recency}
              onChange={(e) => setLocalPreferences(prev => ({
                ...prev,
                recency: parseFloat(e.target.value)
              }))}
              className={`w-full h-2 rounded-lg appearance-none cursor-pointer ${getSliderColor(localPreferences.recency)}`}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Lower: Classic papers • Higher: Recent publications
            </p>
          </div>
        </div>

        {/* Performance Metrics */}
        {metrics && (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Recommendation Performance
              </h3>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Math.round(metrics.clickThroughRate * 100)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Click-through Rate
                </div>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Math.round(metrics.diversityScore * 100)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Diversity Score
                </div>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Math.round(metrics.noveltyScore * 100)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Novelty Score
                </div>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {metrics.totalRecommendations}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Total Recommendations
                </div>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {metrics.totalClicks}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Total Clicks
                </div>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Math.round(metrics.userSatisfaction * 100)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Satisfaction
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50">
        {onClose && (
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
          >
            Cancel
          </button>
        )}
        <motion.button
          whileHover={prefersReducedMotion ? {} : { scale: 1.05 }}
          whileTap={prefersReducedMotion ? {} : { scale: 0.95 }}
          onClick={handleSave}
          disabled={updatePreferences.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {updatePreferences.isPending ? 'Saving...' : 'Save Preferences'}
        </motion.button>
      </div>
    </motion.div>
  );
};
