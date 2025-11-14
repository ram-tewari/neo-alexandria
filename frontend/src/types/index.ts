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
  icon: string;
  label: string;
  path: string;
}

export interface StatData {
  icon: string;
  value: string | number;
  label: string;
  color: 'blue' | 'cyan' | 'purple' | 'teal';
}

export interface Activity {
  icon: string;
  color: string;
  text: string;
  time: string;
}
