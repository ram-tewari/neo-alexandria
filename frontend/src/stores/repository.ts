import { create } from 'zustand';

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
  repositories: Repository[];
  activeRepository: Repository | null;
  isLoading: boolean;
  error: string | null;
  
  setRepositories: (repositories: Repository[]) => void;
  setActiveRepository: (id: string) => void;
  fetchRepositories: () => Promise<void>;
}

// Mock data for development
const mockRepositories: Repository[] = [
  {
    id: '1',
    name: 'neo-alexandria-2.0',
    source: 'github',
    url: 'https://github.com/example/neo-alexandria-2.0',
    description: 'Advanced knowledge management system',
    language: 'TypeScript',
    stars: 42,
    lastUpdated: new Date('2024-01-15'),
    status: 'ready',
    stats: {
      files: 156,
      lines: 12450,
      size: 2048000,
    },
  },
  {
    id: '2',
    name: 'react',
    source: 'github',
    url: 'https://github.com/facebook/react',
    description: 'A declarative, efficient, and flexible JavaScript library',
    language: 'JavaScript',
    stars: 220000,
    lastUpdated: new Date('2024-01-20'),
    status: 'ready',
    stats: {
      files: 892,
      lines: 45230,
      size: 8192000,
    },
  },
  {
    id: '3',
    name: 'local-project',
    source: 'local',
    description: 'Local development project',
    language: 'Python',
    lastUpdated: new Date('2024-01-22'),
    status: 'indexing',
    stats: {
      files: 45,
      lines: 3200,
      size: 512000,
    },
  },
];

export const useRepositoryStore = create<RepositoryState>((set, get) => ({
  repositories: [],
  activeRepository: null,
  isLoading: false,
  error: null,
  
  setRepositories: (repositories: Repository[]) =>
    set({ repositories }),
  
  setActiveRepository: (id: string) => {
    const repository = get().repositories.find((r) => r.id === id);
    if (repository) {
      set({ activeRepository: repository });
    }
  },
  
  fetchRepositories: async () => {
    set({ isLoading: true, error: null });
    
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/repositories');
      // const data = await response.json();
      
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 500));
      
      // Use mock data for now
      set({
        repositories: mockRepositories,
        activeRepository: mockRepositories[0],
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch repositories',
        isLoading: false,
      });
    }
  },
}));
