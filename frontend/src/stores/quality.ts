import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { QualityDetails } from '@/features/editor/types';
import { editorApi } from '@/lib/api/editor';

interface QualityState {
  // Quality data
  qualityData: QualityDetails | null;
  
  // Quality cache (resourceId -> qualityData)
  qualityCache: Record<string, QualityDetails>;
  
  // UI state
  badgeVisibility: boolean;
  isLoading: boolean;
  error: string | null;
  hideBadgesDueToError: boolean; // Auto-hide badges when API fails
  
  // Actions
  setQualityData: (data: QualityDetails | null) => void;
  toggleBadgeVisibility: () => void;
  setBadgeVisibility: (visible: boolean) => void;
  clearError: () => void;
  
  // Data fetching with error handling
  fetchQualityData: (resourceId: string) => Promise<void>;
  
  // Retry failed operations
  retryLastOperation: () => Promise<void>;
  
  // Cache management
  getCachedQuality: (resourceId: string) => QualityDetails | null;
  setCachedQuality: (resourceId: string, data: QualityDetails) => void;
  clearCache: () => void;
}

// Store last operation for retry functionality
let lastQualityOperation: (() => Promise<void>) | null = null;

export const useQualityStore = create<QualityState>()(
  persist(
    (set, get) => ({
      // Initial state
      qualityData: null,
      qualityCache: {},
      badgeVisibility: true,
      isLoading: false,
      error: null,
      hideBadgesDueToError: false,
      
      // Set quality data
      setQualityData: (data: QualityDetails | null) =>
        set({ qualityData: data }),
      
      // Toggle badge visibility
      toggleBadgeVisibility: () =>
        set((state) => ({ 
          badgeVisibility: !state.badgeVisibility,
          // Clear error flag when manually toggling
          hideBadgesDueToError: false,
        })),
      
      // Set badge visibility
      setBadgeVisibility: (visible: boolean) =>
        set({ 
          badgeVisibility: visible,
          // Clear error flag when manually setting
          hideBadgesDueToError: false,
        }),
      
      // Clear error
      clearError: () =>
        set({ error: null, hideBadgesDueToError: false }),
      
      // Fetch quality data for a resource with graceful error handling
      fetchQualityData: async (resourceId: string) => {
        const operation = async () => {
          // Check cache first
          const cached = get().getCachedQuality(resourceId);
          if (cached) {
            set({ 
              qualityData: cached, 
              isLoading: false,
              hideBadgesDueToError: false,
            });
            return;
          }
          
          set({ isLoading: true, error: null, hideBadgesDueToError: false });
          
          try {
            const response = await editorApi.getQualityDetails(resourceId);
            const qualityData = response.data;
            
            // Update state and cache
            set({ 
              qualityData, 
              isLoading: false,
              hideBadgesDueToError: false,
            });
            get().setCachedQuality(resourceId, qualityData);
          } catch (error) {
            // Gracefully handle error by hiding badges
            set({
              qualityData: null,
              error: error instanceof Error 
                ? error.message 
                : 'Failed to fetch quality data',
              hideBadgesDueToError: true, // Auto-hide badges on error
              isLoading: false,
            });
          }
        };
        
        lastQualityOperation = operation;
        await operation();
      },
      
      // Retry last failed operation
      retryLastOperation: async () => {
        if (lastQualityOperation) {
          await lastQualityOperation();
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
