import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface WorkbenchState {
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
}

export const useWorkbenchStore = create<WorkbenchState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      sidebarCollapsed: false,
      
      toggleSidebar: () =>
        set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      
      setSidebarOpen: (open: boolean) =>
        set({ sidebarOpen: open }),
      
      setSidebarCollapsed: (collapsed: boolean) =>
        set({ sidebarCollapsed: collapsed }),
    }),
    {
      name: 'workbench-storage',
      partialize: (state) => ({
        sidebarOpen: state.sidebarOpen,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);
