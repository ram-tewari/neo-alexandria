import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { QualityDetails } from '@/features/editor/types';

interface QualityState {
  // Quality data
  qualityData: QualityDetails | null;
  
  // Quality cache (resourceId -> qualityData)
  qualityCache: Record<string, QualityDetails>;
  
  // UI state
  badgeVisibility: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setQualityData: (data: QualityDetails | null) => void;
  toggleBadgeVisibility: () => void;
  setBadgeVisibility: (visible: boolean) => void;
  
  // Data fetching
  fetchQualityData: (resourceId: string) => Promise<void>;
  
  // Cache management
  getCachedQuality: (resourceId: string) => QualityDetails | null;
  setCachedQuality: (resourceId: string, data: QualityDetails) => void;
  clearCache: () => void;
}

export const useQualityStore = create<QualityState>()(
  persist(
    (set, get) => ({
      // Initial state
      qualityData: null,
      qualityCache: {},
      badgeVisibility: true,
      isLoading: false,
      error: null,
      
      // Set quality data
      setQualityData: (data: QualityDetails | null) =>
        set({ qualityData: data }),
      
      // Toggle badge visibility
      toggleBadgeVisibility: () =>
        set((state) => ({ badgeVisibility: !state.badgeVisibility })),
      
      // Set badge visibility
      setBadgeVisibility: (visible: boolean) =>
        set({ badgeVisibility: visible }),
      
      // Fetch quality data for a resource
      fetchQualityData: async (resourceId: string) => {
        // Check cache first
        const cached = get().getCachedQuality(resourceId);
        if (cached) {
          set({ qualityData: cached, isLoading: false });
          return;
        }
        
        set({ isLoading: true, error: null });
        
        try {
          // TODO: Replace with actual API call in Task 3
          // const response = await editorApi.getQualityDetails(resourceId);
          // const qualityData = response.data;
          
          // Simulate API delay
          await new Promise((resolve) => setTimeout(resolve, 300));
          
          // Mock data for now
          const qualityData: QualityDetails | null = null;
          
          // Update state and cache
          set({ qualityData, isLoading: false });
          if (qualityData) {
            get().setCachedQuality(resourceId, qualityData);
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch quality data',
            isLoading: false,
          });
        }
      },
      
      // Get cached quality data for a resource
      getCachedQuality: (resourceId: string) => {
        return get().qualityCache[resourceId] || null;
      },
      
      // Set cached quality data for a resource
      setCachedQuality: (resourceId: string, data: QualityDetails) =>
        set((state) => ({
          qualityCache: {
            ...state.qualityCache,
            [resourceId]: data,
          },
        })),
      
      // Clear all cached quality data
      clearCache: () =>
        set({ qualityCache: {} }),
    }),
    {
      name: 'quality-storage',
      // Persist badge visibility preference and cache
      partialize: (state) => ({
        badgeVisibility: state.badgeVisibility,
        qualityCache: state.qualityCache,
      }),
    }
  )
);
