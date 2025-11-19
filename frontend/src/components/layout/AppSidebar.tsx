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
import { SidebarCollapseButton } from '../ui/SidebarCollapseButton';
import { Icon } from '../common/Icon';
import { icons } from '../../config/icons';
import { sidebarSections } from '../../config/sidebarConfig';
import type { SidebarItem, SidebarSection } from '../../types';

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

  const renderSidebarItem = (item: SidebarItem) => {
    const IconComponent = icons[item.iconName];
    const isActive = item.path ? location.pathname === item.path : false;

    return (
      <SidebarMenuItem key={item.path || item.label}>
        <Tooltip content={item.label} side="right">
          <SidebarMenuButton asChild isActive={isActive}>
            <motion.a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                if (item.path) {
                  handleNavigation(item.path);
                } else if (item.onClick) {
                  item.onClick();
                }
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
              {item.badge && (
                <span className="sidebar-badge">{item.badge}</span>
              )}
            </motion.a>
          </SidebarMenuButton>
        </Tooltip>
      </SidebarMenuItem>
    );
  };

  const renderSection = (section: SidebarSection, index: number) => {
    if (section.collapsible) {
      return (
        <Collapsible key={section.id} defaultOpen={section.defaultOpen} className="group/collapsible">
          <SidebarGroup>
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="sidebar-group-label-wrapper">
                <span className="sidebar-group-label">{section.label}</span>
                <Icon icon={icons.chevronDown} size={16} className="chevron-icon ml-auto" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {section.items.map(renderSidebarItem)}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </SidebarGroup>
        </Collapsible>
      );
    }

    return (
      <SidebarGroup key={section.id}>
        <SidebarGroupLabel>{section.label}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            {section.items.map(renderSidebarItem)}
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    );
  };

  return (
    <Sidebar collapsible="icon">
      <SidebarContent>
        {sidebarSections.map((section, index) => (
          <div key={section.id}>
            {renderSection(section, index)}
            {index < sidebarSections.length - 1 && <SidebarSeparator />}
          </div>
        ))}
      </SidebarContent>
      <div style={{ padding: '0.5rem', borderTop: '1px solid var(--border-subtle)' }}>
        <SidebarCollapseButton showKeyboardHint={true} />
      </div>
      <SidebarRail />
    </Sidebar>
  );
}
