import { IconName } from '../config/icons';

export interface Resource {
  title: string;
  description: string;
  author: string;
  readTime: number;
  rating: number;
  tags: string[];
  type: 'article' | 'video' | 'book' | 'paper';
}

export interface NavLink {
  path: string;
  label: string;
}

export interface SidebarItem {
  iconName: IconName;
  label: string;
  path: string;
}

export interface StatData {
  iconName: IconName;
  value: number;
  label: string;
  color: 'blue' | 'cyan' | 'purple' | 'teal';
}

export interface Activity {
  iconName: IconName;
  color: string;
  text: string;
  time: string;
}
