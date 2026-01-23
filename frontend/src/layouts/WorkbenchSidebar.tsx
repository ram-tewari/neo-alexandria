import { Link, useRouterState } from '@tanstack/react-router';
import { ChevronLeft, ChevronRight, Brain } from 'lucide-react';
import { Button } from '../components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '../components/ui/tooltip';
import { useWorkbenchStore } from '../stores/workbench';
import { navigationItems } from './navigation-config';
import { motion } from 'framer-motion';

export function WorkbenchSidebar() {
  const { sidebarCollapsed, setSidebarCollapsed } = useWorkbenchStore();
  const router = useRouterState();
  const currentPath = router.location.pathname;

  const isActive = (path: string) => {
    return currentPath === path || currentPath.startsWith(path + '/');
  };

  return (
    <div className="flex h-full flex-col">
      {/* Logo/Brand */}
      <div className="flex h-16 items-center border-b px-4">
        {!sidebarCollapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2"
          >
            <Brain className="h-6 w-6 text-primary" />
            <span className="text-lg font-semibold">Neo Alexandria</span>
          </motion.div>
        )}
        {sidebarCollapsed && (
          <Brain className="h-6 w-6 text-primary mx-auto" />
        )}
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 space-y-1 p-2 overflow-y-auto">
        {navigationItems.map((item, index) => {
          const Icon = item.icon;
          const active = isActive(item.path);

          const navItem = (
            <Link
              to={item.path}
              key={item.id}
              className="block"
            >
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Button
                  variant={active ? 'secondary' : 'ghost'}
                  className={`
                    w-full justify-start gap-3
                    ${sidebarCollapsed ? 'px-2' : 'px-3'}
                    ${active ? 'bg-secondary' : ''}
                  `}
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  {!sidebarCollapsed && (
                    <span className="truncate">{item.label}</span>
                  )}
                </Button>
              </motion.div>
            </Link>
          );

          if (sidebarCollapsed) {
            return (
              <Tooltip key={item.id}>
                <TooltipTrigger asChild>
                  {navItem}
                </TooltipTrigger>
                <TooltipContent side="right">
                  <p>{item.label}</p>
                  {item.description && (
                    <p className="text-xs text-muted-foreground">
                      {item.description}
                    </p>
                  )}
                </TooltipContent>
              </Tooltip>
            );
          }

          return navItem;
        })}
      </nav>

      {/* Toggle Button */}
      <div className="border-t p-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="w-full justify-center"
          aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeft className="h-4 w-4" />
              <span className="ml-2">Collapse</span>
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
