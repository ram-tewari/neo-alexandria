import { Check, ChevronsUpDown, Github, GitlabIcon, FolderOpen, Plus, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { useRepositoryStore, mapResourceToRepository, type Repository } from '../stores/repository';
import { useResources } from '../lib/hooks/useWorkbenchData';
import { motion } from 'framer-motion';
import { Alert, AlertDescription } from './ui/alert';

/**
 * Repository Switcher Component
 * 
 * Displays a dropdown menu for switching between repositories/resources.
 * Updated in Phase 2.5 to use real backend data via TanStack Query.
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 3.3 Update workbench store to use real data
 * Requirements: 2.2, 2.5, 2.6
 */

const sourceIcons = {
  github: Github,
  gitlab: GitlabIcon,
  local: FolderOpen,
};

const statusColors = {
  ready: 'bg-green-500',
  indexing: 'bg-yellow-500',
  error: 'bg-red-500',
};

export function RepositorySwitcher() {
  // Fetch resources from backend using TanStack Query
  const { data: resources, isLoading, error, refetch } = useResources({
    limit: 50, // Show up to 50 repositories in the switcher
  });
  
  // Get active repository ID from store
  const { activeRepositoryId, setActiveRepository } = useRepositoryStore();

  // Map backend resources to frontend repositories
  const repositories = resources?.map(mapResourceToRepository) || [];
  const activeRepository = repositories.find(r => r.id === activeRepositoryId);

  const handleSelect = (repo: Repository) => {
    setActiveRepository(repo.id);
  };

  // Loading state
  if (isLoading) {
    return (
      <Button variant="outline" disabled className="w-[200px] justify-between">
        <span className="truncate">Loading...</span>
      </Button>
    );
  }

  // Error state
  if (error) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" className="w-[200px] justify-between text-destructive">
            <div className="flex items-center gap-2 truncate">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span className="truncate">Error loading</span>
            </div>
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-[250px]" align="start">
          <div className="p-2">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Failed to load repositories. {error.message}
              </AlertDescription>
            </Alert>
            <Button 
              variant="outline" 
              size="sm" 
              className="w-full mt-2"
              onClick={() => refetch()}
            >
              Retry
            </Button>
          </div>
        </DropdownMenuContent>
      </DropdownMenu>
    );
  }

  // Empty state
  if (repositories.length === 0) {
    return (
      <Button variant="outline" className="w-[200px] justify-between">
        <span className="truncate text-muted-foreground">No repositories</span>
        <Plus className="ml-2 h-4 w-4" />
      </Button>
    );
  }

  const SourceIcon = activeRepository
    ? sourceIcons[activeRepository.source]
    : FolderOpen;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          className="w-[200px] justify-between"
        >
          <div className="flex items-center gap-2 truncate">
            <SourceIcon className="h-4 w-4 shrink-0" />
            <span className="truncate">
              {activeRepository?.name || 'Select repository'}
            </span>
          </div>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[250px]" align="start">
        <DropdownMenuLabel>Repositories</DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        {repositories.map((repo, index) => {
          const Icon = sourceIcons[repo.source];
          const isActive = activeRepository?.id === repo.id;
          
          return (
            <motion.div
              key={repo.id}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <DropdownMenuItem
                onSelect={() => handleSelect(repo)}
                className="flex items-center gap-2 cursor-pointer"
              >
                <Icon className="h-4 w-4 shrink-0" />
                <div className="flex-1 truncate">
                  <div className="flex items-center gap-2">
                    <span className="truncate">{repo.name}</span>
                    <div
                      className={`h-2 w-2 rounded-full ${statusColors[repo.status]}`}
                      title={repo.status}
                    />
                  </div>
                  {repo.description && (
                    <p className="text-xs text-muted-foreground truncate">
                      {repo.description}
                    </p>
                  )}
                </div>
                {isActive && <Check className="h-4 w-4 shrink-0" />}
              </DropdownMenuItem>
            </motion.div>
          );
        })}
        
        <DropdownMenuSeparator />
        <DropdownMenuItem className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          <span>Add repository</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
