import { IconName } from '../config/icons';

export interface NavLink {
  path: string;
  label: string;
}

export interface SidebarItem {
  iconName: IconName;
  label: string;
  path?: string;
  badge?: number | string;
  onClick?: () => void;
  children?: SidebarItem[];
}
