import { create } from 'zustand';

interface NavigationState {
  currentPage: string;
  sidebarOpen: boolean;
  scrolled: boolean;
  setCurrentPage: (page: string) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setScrolled: (scrolled: boolean) => void;
}

export const useNavigationStore = create<NavigationState>((set) => ({
  currentPage: 'dashboard',
  sidebarOpen: true,
  scrolled: false,
  setCurrentPage: (page) => set({ currentPage: page }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setScrolled: (scrolled) => set({ scrolled }),
}));
