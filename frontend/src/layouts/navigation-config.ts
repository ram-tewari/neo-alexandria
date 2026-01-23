import {
  FolderGit2,
  Brain,
  Library,
  ListTodo,
  BookOpen,
  Activity,
  type LucideIcon,
} from 'lucide-react';

export interface NavigationItem {
  id: string;
  label: string;
  icon: LucideIcon;
  path: string;
  description?: string;
}

export const navigationItems: NavigationItem[] = [
  {
    id: 'repositories',
    label: 'Repositories',
    icon: FolderGit2,
    path: '/repositories',
    description: 'Manage code repositories',
  },
  {
    id: 'cortex',
    label: 'Cortex',
    icon: Brain,
    path: '/cortex',
    description: 'AI-powered insights',
  },
  {
    id: 'library',
    label: 'Library',
    icon: Library,
    path: '/library',
    description: 'Browse your knowledge base',
  },
  {
    id: 'planner',
    label: 'Planner',
    icon: ListTodo,
    path: '/planner',
    description: 'Plan and organize tasks',
  },
  {
    id: 'wiki',
    label: 'Wiki',
    icon: BookOpen,
    path: '/wiki',
    description: 'Documentation and notes',
  },
  {
    id: 'ops',
    label: 'Ops',
    icon: Activity,
    path: '/ops',
    description: 'System operations',
  },
];
