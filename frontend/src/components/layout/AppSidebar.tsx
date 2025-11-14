import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarSeparator,
  useSidebar,
} from '../ui/sidebar';
import { Icon } from '../common/Icon';
import { icons } from '../../config/icons';
import type { SidebarItem } from '../../types';

const mainItems: SidebarItem[] = [
  { iconName: 'dashboard', label: 'Dashboard', path: '/' },
  { iconName: 'library', label: 'Library', path: '/library' },
  { iconName: 'search', label: 'Search', path: '/search' },
  { iconName: 'graph', label: 'Knowledge Graph', path: '/graph' },
];

const collections: SidebarItem[] = [
  { iconName: 'favorites', label: 'Favorites', path: '/favorites' },
  { iconName: 'recent', label: 'Recent', path: '/recent' },
  { iconName: 'readLater', label: 'Read Later', path: '/read-later' },
];

export function AppSidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile, setOpenMobile } = useSidebar();

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setOpenMobile(false);
    }
  };

  return (
    <Sidebar collapsible="offcanvas">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Main</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainItems.map((item) => {
                const IconComponent = icons[item.iconName];
                const isActive = location.pathname === item.path;

                return (
                  <SidebarMenuItem key={item.path}>
                    <SidebarMenuButton
                      asChild
                      isActive={isActive}
                    >
                      <motion.a
                        href="#"
                        onClick={(e) => {
                          e.preventDefault();
                          handleNavigation(item.path);
                        }}
                        className="sidebar-menu-link"
                        whileHover={{ x: 4 }}
                        whileTap={{ scale: 0.98 }}
                        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                      >
                        <motion.div
                          className="sidebar-item-glow"
                          initial={{ opacity: 0 }}
                          whileHover={{ opacity: 1 }}
                          transition={{ duration: 0.3 }}
                        />
                        <Icon icon={IconComponent} size={20} />
                        <span>{item.label}</span>
                      </motion.a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarSeparator />

        <SidebarGroup>
          <SidebarGroupLabel>Collections</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {collections.map((item) => {
                const IconComponent = icons[item.iconName];
                const isActive = location.pathname === item.path;

                return (
                  <SidebarMenuItem key={item.path}>
                    <SidebarMenuButton
                      asChild
                      isActive={isActive}
                    >
                      <motion.a
                        href="#"
                        onClick={(e) => {
                          e.preventDefault();
                          handleNavigation(item.path);
                        }}
                        className="sidebar-menu-link"
                        whileHover={{ x: 4 }}
                        whileTap={{ scale: 0.98 }}
                        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                      >
                        <motion.div
                          className="sidebar-item-glow"
                          initial={{ opacity: 0 }}
                          whileHover={{ opacity: 1 }}
                          transition={{ duration: 0.3 }}
                        />
                        <Icon icon={IconComponent} size={20} />
                        <span>{item.label}</span>
                      </motion.a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
