import { create } from 'zustand';
import type { Resource, IngestionStatus } from '@/types/api';

/**
 * Repository Store for Neo Alexandria 2.0
 * 
 * Manages repository/resource state for the workbench.
 * Updated in Phase 2.5 to use real backend data via useResources hook.
 * 
 * Note: This store maintains UI state (active repository, selection).
 * Data fetching is handled by TanStack Query hooks in useWorkbenchData.ts.
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 3.3 Update workbench store to use real data
 * Requirements: 2.2, 2.5, 2.6
 */

export interface Repository {
  id: string;
  name: string;
  source: 'github' | 'gitlab' | 'local';
  url?: string;
  description?: string;
  language?: string;
  stars?: number;
  lastUpdated: Date;
  status: 'ready' | 'indexing' | 'error';
  stats?: {
    files: number;
    lines: number;
    size: number;
  };
}

interface RepositoryState {
  // UI State
  activeRepositoryId: string | null;
  
  // Actions
  setActiveRepository: (id: string | null) => void;
  clearActiveRepository: () => void;
}

/**
 * Maps backend Resource to frontend Repository interface
 * 
 * @param resource - Backend resource object
 * @returns Frontend repository object
 */
export function mapResourceToRepository(resource: Resource): Repository {
  // Determine source from URL or file path
  let source: 'github' | 'gitlab' | 'local' = 'local';
  if (resource.url) {
    if (resource.url.includes('github.com')) {
      source = 'github';
    } else if (resource.url.includes('gitlab.com')) {
      source = 'gitlab';
    }
  }
  
  // Map ingestion status to repository status
  const statusMap: Record<IngestionStatus, 'ready' | 'indexing' | 'error'> = {
    completed: 'ready',
    processing: 'indexing',
    pending: 'indexing',
    failed: 'error',
  };
  
  return {
    id: resource.id,
    name: resource.title,
    source,
    url: resource.url,
    description: resource.description,
    language: resource.language,
    lastUpdated: new Date(resource.updated_at),
    status: statusMap[resource.ingestion_status],
    // Note: Backend doesn't provide stars or stats yet
    // These could be added in future backend updates
  };
}

/**
 * Repository Store
 * 
 * Manages active repository selection for the workbench.
 * Data fetching is delegated to TanStack Query hooks.
 * 
 * @example
 * ```tsx
 * function RepositorySwitcher() {
 *   const { data: resources, isLoading, error } = useResources();
 *   const { activeRepositoryId, setActiveRepository } = useRepositoryStore();
 *   
 *   const repositories = resources?.map(mapResourceToRepository) || [];
 *   const activeRepo = repositories.find(r => r.id === activeRepositoryId);
 *   
 *   return (
 *     <Select value={activeRepositoryId} onChange={setActiveRepository}>
 *       {repositories.map(repo => (
 *         <option key={repo.id} value={repo.id}>{repo.name}</option>
 *       ))}
 *     </Select>
 *   );
 * }
 * ```
 */
export const useRepositoryStore = create<RepositoryState>((set) => ({
  activeRepositoryId: null,
  
  setActiveRepository: (id: string | null) => {
    set({ activeRepositoryId: id });
  },
  
  clearActiveRepository: () => {
    set({ activeRepositoryId: null });
  },
}));
