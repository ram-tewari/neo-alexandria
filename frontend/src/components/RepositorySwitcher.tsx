import { useEffect } from 'react';
import { Check, ChevronsUpDown, Github, GitlabIcon, FolderOpen, Plus } from 'lucide-react';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { useRepositoryStore, type Repository } from '../stores/repository';
import { motion } from 'framer-motion';

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
  const {
    repositories,
    activeRepository,
    isLoading,
    setActiveRepository,
    fetchRepositories,
  } = useRepositoryStore();

  useEffect(() => {
    fetchRepositories();
  }, [fetchRepositories]);

  const handleSelect = (repo: Repository) => {
    setActiveRepository(repo.id);
  };

  if (isLoading) {
    return (
      <Button variant="outline" disabled className="w-[200px] justify-between">
        <span className="truncate">Loading...</span>
      </Button>
    );
  }

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
