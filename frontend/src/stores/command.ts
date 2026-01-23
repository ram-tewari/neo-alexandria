import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { LucideIcon } from 'lucide-react';

export type CommandCategory = 'navigation' | 'actions' | 'settings';

export interface Command {
  id: string;
  label: string;
  description?: string;
  icon?: LucideIcon;
  shortcut?: string[];
  action: () => void | Promise<void>;
  category: CommandCategory;
  keywords?: string[];
}

interface CommandPaletteState {
  isOpen: boolean;
  commands: Command[];
  recentCommands: string[]; // Store command IDs
  
  open: () => void;
  close: () => void;
  toggle: () => void;
  registerCommand: (command: Command) => void;
  registerCommands: (commands: Command[]) => void;
  unregisterCommand: (id: string) => void;
  executeCommand: (id: string) => Promise<void>;
  addToRecent: (id: string) => void;
}

const MAX_RECENT_COMMANDS = 5;

export const useCommandPaletteStore = create<CommandPaletteState>()(
  persist(
    (set, get) => ({
      isOpen: false,
      commands: [],
      recentCommands: [],
      
      open: () => set({ isOpen: true }),
      
      close: () => set({ isOpen: false }),
      
      toggle: () => set((state) => ({ isOpen: !state.isOpen })),
      
      registerCommand: (command: Command) =>
        set((state) => ({
          commands: [...state.commands.filter((c) => c.id !== command.id), command],
        })),
      
      registerCommands: (commands: Command[]) =>
        set((state) => {
          const existingIds = new Set(state.commands.map((c) => c.id));
          const newCommands = commands.filter((c) => !existingIds.has(c.id));
          return { commands: [...state.commands, ...newCommands] };
        }),
      
      unregisterCommand: (id: string) =>
        set((state) => ({
          commands: state.commands.filter((c) => c.id !== id),
        })),
      
      executeCommand: async (id: string) => {
        const command = get().commands.find((c) => c.id === id);
        if (!command) {
          console.error(`Command not found: ${id}`);
          return;
        }
        
        try {
          await command.action();
          get().addToRecent(id);
          get().close();
        } catch (error) {
          console.error(`Error executing command ${id}:`, error);
          throw error;
        }
      },
      
      addToRecent: (id: string) =>
        set((state) => {
          const filtered = state.recentCommands.filter((cmdId) => cmdId !== id);
          const updated = [id, ...filtered].slice(0, MAX_RECENT_COMMANDS);
          return { recentCommands: updated };
        }),
    }),
    {
      name: 'command-palette-storage',
      partialize: (state) => ({
        recentCommands: state.recentCommands,
      }),
    }
  )
);
