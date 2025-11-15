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
  SidebarRail,
  Tooltip,
  useSidebar,
} from '../ui/sidebar';
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '../ui/collapsible';
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
    <Sidebar collapsible="icon">
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
                    <Tooltip content={item.label} side="right">
                      <SidebarMenuButton asChild isActive={isActive}>
                        <motion.a
                          href="#"
                          onClick={(e) => {
                            e.preventDefault();
                            handleNavigation(item.path);
                          }}
                          className="sidebar-menu-link"
                          aria-current={isActive ? 'page' : undefined}
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
                    </Tooltip>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarSeparator />

        <Collapsible defaultOpen className="group/collapsible">
          <SidebarGroup>
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="sidebar-group-label-wrapper">
                <span className="sidebar-group-label">Collections</span>
                <Icon icon={icons.chevronDown} size={16} className="chevron-icon ml-auto" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {collections.map((item) => {
                    const IconComponent = icons[item.iconName];
                    const isActive = location.pathname === item.path;

                    return (
                      <SidebarMenuItem key={item.path}>
                        <Tooltip content={item.label} side="right">
                          <SidebarMenuButton asChild isActive={isActive}>
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
                        </Tooltip>
                      </SidebarMenuItem>
                    );
                  })}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </SidebarGroup>
        </Collapsible>
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  );
}
