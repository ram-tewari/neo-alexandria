import { create } from 'zustand';

export interface Command {
  id: string;
  label: string;
  icon?: React.ReactNode;
  shortcut?: string;
  action: () => void;
  category: 'navigation' | 'search' | 'action';
}

interface CommandStore {
  isOpen: boolean;
  commands: Command[];
  recentCommands: string[];
  openPalette: () => void;
  closePalette: () => void;
  togglePalette: () => void;
  registerCommand: (command: Command) => void;
  unregisterCommand: (id: string) => void;
  addRecentCommand: (id: string) => void;
}

export const useCommandStore = create<CommandStore>((set) => ({
  isOpen: false,
  commands: [],
  recentCommands: [],

  openPalette: () => set({ isOpen: true }),
  closePalette: () => set({ isOpen: false }),
  togglePalette: () => set((state) => ({ isOpen: !state.isOpen })),

  registerCommand: (command) =>
    set((state) => ({
      commands: [...state.commands.filter((c) => c.id !== command.id), command],
    })),

  unregisterCommand: (id) =>
    set((state) => ({
      commands: state.commands.filter((c) => c.id !== id),
    })),

  addRecentCommand: (id) =>
    set((state) => ({
      recentCommands: [id, ...state.recentCommands.filter((cid) => cid !== id)].slice(0, 5),
    })),
}));
