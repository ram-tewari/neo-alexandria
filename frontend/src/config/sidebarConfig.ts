import type { SidebarSection } from '../types';

export const sidebarSections: SidebarSection[] = [
  {
    id: 'main',
    label: 'MAIN',
    items: [
      { iconName: 'home', label: 'Home', path: '/' },
      { iconName: 'activity', label: 'Activity', path: '/activity' },
      { iconName: 'workspaces', label: 'Workspaces', path: '/workspaces' },
      { iconName: 'discover', label: 'Discover', path: '/discover' },
    ],
  },
  {
    id: 'tools',
    label: 'TOOLS',
    items: [
      { iconName: 'notes', label: 'Notes', path: '/notes' },
      { iconName: 'tasks', label: 'Tasks', path: '/tasks' },
      { iconName: 'highlights', label: 'Highlights', path: '/highlights' },
      { iconName: 'tags', label: 'Tags Manager', path: '/tags' },
      { iconName: 'import', label: 'Import & Export', path: '/import-export' },
    ],
  },
  {
    id: 'collections',
    label: 'COLLECTIONS',
    collapsible: true,
    defaultOpen: true,
    items: [
      { iconName: 'library', label: 'All Collections', path: '/collections' },
      { iconName: 'favorites', label: 'Favorites', path: '/favorites' },
      { iconName: 'recent', label: 'Recent', path: '/recent' },
      { iconName: 'readLater', label: 'Read Later', path: '/read-later' },
      { iconName: 'playlists', label: 'Playlists', path: '/playlists' },
      { iconName: 'archived', label: 'Archived', path: '/archived' },
      { iconName: 'shared', label: 'Shared with Me', path: '/shared' },
    ],
  },
  {
    id: 'insights',
    label: 'INSIGHTS',
    collapsible: true,
    defaultOpen: false,
    items: [
      { iconName: 'statistics', label: 'Statistics', path: '/statistics' },
      { iconName: 'trends', label: 'Usage Trends', path: '/trends' },
      { iconName: 'recommendations', label: 'Recommendations', path: '/recommendations' },
      { iconName: 'breakdown', label: 'Content Breakdown', path: '/breakdown' },
    ],
  },
  {
    id: 'system',
    label: 'SYSTEM',
    items: [
      { iconName: 'settings', label: 'Settings', path: '/settings' },
      { iconName: 'profile', label: 'Profile', path: '/profile' },
      { iconName: 'themes', label: 'Themes', path: '/themes' },
      { iconName: 'help', label: 'Help Center', path: '/help' },
      { iconName: 'feedback', label: 'Feedback', path: '/feedback' },
      { iconName: 'about', label: 'About', path: '/about' },
    ],
  },
];
