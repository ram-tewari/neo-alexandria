/**
 * Built-in Commands
 * 
 * Default commands registered with the command registry
 */

import { commandRegistry, type Command } from './commandRegistry';
import { icons } from '@/config/icons';

export function registerBuiltInCommands(navigate: (path: string) => void) {
  const commands: Command[] = [
    // Navigation Commands
    {
      id: 'nav-dashboard',
      label: 'Go to Dashboard',
      description: 'Navigate to the main dashboard',
      icon: icons.dashboard,
      keywords: ['dashboard', 'home', 'overview', 'main'],
      category: 'navigation',
      action: () => navigate('/'),
      shortcut: 'G D',
      priority: 90,
    },
    {
      id: 'nav-library',
      label: 'Go to Library',
      description: 'Browse your resource library',
      icon: icons.library,
      keywords: ['library', 'resources', 'browse', 'collection'],
      category: 'navigation',
      action: () => navigate('/library'),
      shortcut: 'G L',
      priority: 85,
    },
    {
      id: 'nav-graph',
      label: 'Go to Knowledge Graph',
      description: 'Explore connections in the knowledge graph',
      icon: icons.graph,
      keywords: ['graph', 'network', 'connections', 'visualization'],
      category: 'navigation',
      action: () => navigate('/graph'),
      shortcut: 'G G',
      priority: 80,
    },
    {
      id: 'nav-collections',
      label: 'Go to Collections',
      description: 'View and manage your collections',
      icon: icons.library,
      keywords: ['collections', 'folders', 'organize'],
      category: 'navigation',
      action: () => navigate('/collections'),
      priority: 75,
    },
    
    // Action Commands
    {
      id: 'action-add-resource',
      label: 'Add New Resource',
      description: 'Create a new resource in your library',
      icon: icons.add,
      keywords: ['add', 'new', 'create', 'resource', 'article'],
      category: 'action',
      action: () => {
        // TODO: Implement add resource modal
        console.log('Add resource action');
      },
      shortcut: 'N',
      priority: 70,
    },
    {
      id: 'action-create-collection',
      label: 'Create Collection',
      description: 'Create a new collection to organize resources',
      icon: icons.library,
      keywords: ['collection', 'folder', 'organize', 'group'],
      category: 'action',
      action: () => {
        // TODO: Implement create collection modal
        console.log('Create collection action');
      },
      priority: 65,
    },
    {
      id: 'action-import',
      label: 'Import Resources',
      description: 'Import resources from external sources',
      icon: icons.add,
      keywords: ['import', 'upload', 'add', 'bulk'],
      category: 'action',
      action: () => {
        // TODO: Implement import modal
        console.log('Import resources action');
      },
      priority: 60,
    },
    
    // Filter Commands
    {
      id: 'filter-unread',
      label: 'Filter: Unread',
      description: 'Show only unread resources',
      icon: icons.filter,
      keywords: ['filter', 'unread', 'status', 'pending'],
      category: 'filter',
      action: () => {
        // TODO: Implement filter logic
        console.log('Filter unread action');
      },
      priority: 55,
    },
    {
      id: 'filter-completed',
      label: 'Filter: Completed',
      description: 'Show only completed resources',
      icon: icons.check,
      keywords: ['filter', 'completed', 'read', 'done', 'finished'],
      category: 'filter',
      action: () => {
        // TODO: Implement filter logic
        console.log('Filter completed action');
      },
      priority: 50,
    },
    {
      id: 'filter-favorites',
      label: 'Filter: Favorites',
      description: 'Show only favorited resources',
      icon: icons.star,
      keywords: ['filter', 'favorites', 'starred', 'bookmarked'],
      category: 'filter',
      action: () => {
        // TODO: Implement filter logic
        console.log('Filter favorites action');
      },
      priority: 50,
    },
    
    // Search Commands
    {
      id: 'search-resources',
      label: 'Search Resources',
      description: 'Search through all your resources',
      icon: icons.search,
      keywords: ['search', 'find', 'query', 'lookup'],
      category: 'search',
      action: () => {
        // TODO: Implement search modal
        console.log('Search resources action');
      },
      shortcut: '/',
      priority: 80,
    },
    
    // Help Commands
    {
      id: 'help-shortcuts',
      label: 'Keyboard Shortcuts',
      description: 'View all available keyboard shortcuts',
      icon: icons.help,
      keywords: ['help', 'shortcuts', 'keyboard', 'commands', 'hotkeys'],
      category: 'help',
      action: () => {
        // TODO: Implement shortcuts modal
        console.log('Show shortcuts action');
      },
      shortcut: '?',
      priority: 40,
    },
    {
      id: 'help-guide',
      label: 'User Guide',
      description: 'Learn how to use the application',
      icon: icons.help,
      keywords: ['help', 'guide', 'tutorial', 'documentation', 'learn'],
      category: 'help',
      action: () => {
        // TODO: Implement user guide
        console.log('Show user guide action');
      },
      priority: 35,
    },
  ];

  // Register all commands
  commandRegistry.registerMany(commands);
}

export function unregisterBuiltInCommands() {
  const commandIds = [
    'nav-dashboard',
    'nav-library',
    'nav-graph',
    'nav-collections',
    'action-add-resource',
    'action-create-collection',
    'action-import',
    'filter-unread',
    'filter-completed',
    'filter-favorites',
    'search-resources',
    'help-shortcuts',
    'help-guide',
  ];

  commandIds.forEach(id => commandRegistry.unregister(id));
}
