import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from '@tanstack/react-router';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from './ui/command';
import { useCommandPaletteStore } from '../stores/command';
import { useWorkbenchStore } from '../stores/workbench';
import { useThemeStore } from '../stores/theme';
import { navigationItems } from '../layouts/navigation-config';
import {
  Moon,
  Sun,
  Monitor,
  PanelLeftClose,
  PanelLeft,
} from 'lucide-react';

export function CommandPalette() {
  const { isOpen, close, commands, recentCommands, executeCommand, registerCommands } =
    useCommandPaletteStore();
  const { sidebarOpen, toggleSidebar } = useWorkbenchStore();
  const { setTheme } = useThemeStore();
  const navigate = useNavigate();
  const [search, setSearch] = useState('');

  // Register built-in commands
  useEffect(() => {
    const builtInCommands = [
      // Navigation commands
      ...navigationItems.map((item) => ({
        id: `nav-${item.id}`,
        label: `Go to ${item.label}`,
        description: item.description,
        icon: item.icon,
        action: () => navigate({ to: item.path }),
        category: 'navigation' as const,
        keywords: [item.label.toLowerCase(), 'navigate', 'go'],
      })),
      
      // Action commands
      {
        id: 'toggle-sidebar',
        label: sidebarOpen ? 'Close Sidebar' : 'Open Sidebar',
        description: 'Toggle the navigation sidebar',
        icon: sidebarOpen ? PanelLeftClose : PanelLeft,
        shortcut: ['⌘', 'B'],
        action: () => toggleSidebar(),
        category: 'actions' as const,
        keywords: ['sidebar', 'navigation', 'toggle'],
      },
      
      // Theme commands
      {
        id: 'theme-light',
        label: 'Light Theme',
        description: 'Switch to light theme',
        icon: Sun,
        action: () => setTheme('light'),
        category: 'settings' as const,
        keywords: ['theme', 'light', 'appearance'],
      },
      {
        id: 'theme-dark',
        label: 'Dark Theme',
        description: 'Switch to dark theme',
        icon: Moon,
        action: () => setTheme('dark'),
        category: 'settings' as const,
        keywords: ['theme', 'dark', 'appearance'],
      },
      {
        id: 'theme-system',
        label: 'System Theme',
        description: 'Use system theme preference',
        icon: Monitor,
        action: () => setTheme('system'),
        category: 'settings' as const,
        keywords: ['theme', 'system', 'appearance', 'auto'],
      },
      
      // Settings command (commented out until settings route is created)
      // {
      //   id: 'open-settings',
      //   label: 'Open Settings',
      //   description: 'Open application settings',
      //   icon: Settings,
      //   shortcut: ['⌘', ','],
      //   action: () => navigate({ to: '/settings' }),
      //   category: 'settings' as const,
      //   keywords: ['settings', 'preferences', 'config'],
      // },
    ];

    registerCommands(builtInCommands);
  }, [navigate, toggleSidebar, setTheme, sidebarOpen, registerCommands]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        useCommandPaletteStore.getState().toggle();
      }
      
      if (e.key === 'p' && e.shiftKey && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        useCommandPaletteStore.getState().open();
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  const handleSelect = useCallback(
    async (commandId: string) => {
      try {
        await executeCommand(commandId);
        setSearch('');
      } catch (error) {
        console.error('Failed to execute command:', error);
      }
    },
    [executeCommand]
  );

  // Group commands by category
  const navigationCommands = commands.filter((c) => c.category === 'navigation');
  const actionCommands = commands.filter((c) => c.category === 'actions');
  const settingsCommands = commands.filter((c) => c.category === 'settings');
  
  // Get recent commands
  const recentCommandsList = recentCommands
    .map((id) => commands.find((c) => c.id === id))
    .filter(Boolean);

  return (
    <CommandDialog open={isOpen} onOpenChange={close}>
      <CommandInput
        placeholder="Type a command or search..."
        value={search}
        onValueChange={setSearch}
      />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        {recentCommandsList.length > 0 && (
          <>
            <CommandGroup heading="Recent">
              {recentCommandsList.map((command) => {
                if (!command) return null;
                const Icon = command.icon;
                return (
                  <CommandItem
                    key={command.id}
                    value={command.label}
                    onSelect={() => handleSelect(command.id)}
                  >
                    {Icon && <Icon className="mr-2 h-4 w-4" />}
                    <span>{command.label}</span>
                    {command.description && (
                      <span className="ml-2 text-xs text-muted-foreground">
                        {command.description}
                      </span>
                    )}
                    {command.shortcut && (
                      <CommandShortcut>
                        {command.shortcut.join(' ')}
                      </CommandShortcut>
                    )}
                  </CommandItem>
                );
              })}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        {navigationCommands.length > 0 && (
          <CommandGroup heading="Navigation">
            {navigationCommands.map((command) => {
              const Icon = command.icon;
              return (
                <CommandItem
                  key={command.id}
                  value={command.label}
                  keywords={command.keywords}
                  onSelect={() => handleSelect(command.id)}
                >
                  {Icon && <Icon className="mr-2 h-4 w-4" />}
                  <span>{command.label}</span>
                  {command.description && (
                    <span className="ml-2 text-xs text-muted-foreground">
                      {command.description}
                    </span>
                  )}
                </CommandItem>
              );
            })}
          </CommandGroup>
        )}

        {actionCommands.length > 0 && (
          <CommandGroup heading="Actions">
            {actionCommands.map((command) => {
              const Icon = command.icon;
              return (
                <CommandItem
                  key={command.id}
                  value={command.label}
                  keywords={command.keywords}
                  onSelect={() => handleSelect(command.id)}
                >
                  {Icon && <Icon className="mr-2 h-4 w-4" />}
                  <span>{command.label}</span>
                  {command.shortcut && (
                    <CommandShortcut>
                      {command.shortcut.join(' ')}
                    </CommandShortcut>
                  )}
                </CommandItem>
              );
            })}
          </CommandGroup>
        )}

        {settingsCommands.length > 0 && (
          <CommandGroup heading="Settings">
            {settingsCommands.map((command) => {
              const Icon = command.icon;
              return (
                <CommandItem
                  key={command.id}
                  value={command.label}
                  keywords={command.keywords}
                  onSelect={() => handleSelect(command.id)}
                >
                  {Icon && <Icon className="mr-2 h-4 w-4" />}
                  <span>{command.label}</span>
                  {command.shortcut && (
                    <CommandShortcut>
                      {command.shortcut.join(' ')}
                    </CommandShortcut>
                  )}
                </CommandItem>
              );
            })}
          </CommandGroup>
        )}
      </CommandList>
    </CommandDialog>
  );
}
