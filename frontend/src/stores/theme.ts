import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Theme = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

interface ThemeState {
  theme: Theme;
  resolvedTheme: ResolvedTheme;
  setTheme: (theme: Theme) => void;
  setResolvedTheme: (theme: ResolvedTheme) => void;
}

// Helper to get system preference
const getSystemTheme = (): ResolvedTheme => {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

// Helper to resolve theme
const resolveTheme = (theme: Theme): ResolvedTheme => {
  if (theme === 'system') {
    return getSystemTheme();
  }
  return theme;
};

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: 'system',
      resolvedTheme: getSystemTheme(),
      
      setTheme: (theme: Theme) => {
        const resolved = resolveTheme(theme);
        set({ theme, resolvedTheme: resolved });
        
        // Apply theme to document
        if (typeof document !== 'undefined') {
          document.documentElement.classList.remove('light', 'dark');
          document.documentElement.classList.add(resolved);
        }
      },
      
      setResolvedTheme: (resolvedTheme: ResolvedTheme) =>
        set({ resolvedTheme }),
    }),
    {
      name: 'theme-storage',
      partialize: (state) => ({
        theme: state.theme,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          // Re-apply theme after hydration
          const resolved = resolveTheme(state.theme);
          state.setResolvedTheme(resolved);
          
          if (typeof document !== 'undefined') {
            document.documentElement.classList.remove('light', 'dark');
            document.documentElement.classList.add(resolved);
          }
        }
      },
    }
  )
);

// Listen for system theme changes
if (typeof window !== 'undefined') {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    const store = useThemeStore.getState();
    if (store.theme === 'system') {
      const newTheme = e.matches ? 'dark' : 'light';
      store.setResolvedTheme(newTheme);
      document.documentElement.classList.remove('light', 'dark');
      document.documentElement.classList.add(newTheme);
    }
  });
}
