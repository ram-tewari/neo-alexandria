/**
 * Quality Store
 * 
 * Manages quality badge visibility and UI state.
 * Quality data is now fetched via TanStack Query hooks (useQualityDetails)
 * instead of being stored in this Zustand store.
 * 
 * This store only manages:
 * - Badge visibility toggle
 * - UI preferences (persisted to localStorage)
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 8.3 Update quality store to use real data
 * Requirements: 5.1, 5.9, 5.10
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface QualityState {
  // UI state
  badgeVisibility: boolean;
  
  // Actions
  toggleBadgeVisibility: () => void;
  setBadgeVisibility: (visible: boolean) => void;
}

/**
 * Quality store for managing UI state
 * 
 * Note: Quality data is now managed by TanStack Query hooks:
 * - useQualityDetails(resourceId) - Fetch quality data from resource metadata
 * - useRecalculateQuality() - Trigger quality recalculation
 * - useQualityOutliers() - Fetch quality outliers
 * - useQualityDegradation() - Fetch quality degradation
 * - useQualityDistribution() - Fetch quality distribution
 * - useQualityTrends() - Fetch quality trends
 * - useQualityDimensions() - Fetch quality dimensions
 * - useQualityReviewQueue() - Fetch quality review queue
 * 
 * @example
 * ```tsx
 * function QualityBadgeToggle() {
 *   const { badgeVisibility, toggleBadgeVisibility } = useQualityStore();
 *   
 *   return (
 *     <button onClick={toggleBadgeVisibility}>
 *       {badgeVisibility ? 'Hide' : 'Show'} Quality Badges
 *     </button>
 *   );
 * }
 * ```
 */
export const useQualityStore = create<QualityState>()(
  persist(
    (set) => ({
      // Initial state
      badgeVisibility: true,
      
      // Toggle badge visibility
      toggleBadgeVisibility: () =>
        set((state) => ({ 
          badgeVisibility: !state.badgeVisibility,
        })),
      
      // Set badge visibility
      setBadgeVisibility: (visible: boolean) =>
        set({ badgeVisibility: visible }),
    }),
    {
      name: 'quality-storage',
      // Persist badge visibility preference
      partialize: (state) => ({
        badgeVisibility: state.badgeVisibility,
      }),
    }
  )
);
