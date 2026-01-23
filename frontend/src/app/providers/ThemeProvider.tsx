import { useEffect } from 'react';
import { useThemeStore } from '../../stores/theme';

interface ThemeProviderProps {
  children: React.ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const { theme, resolvedTheme, setTheme } = useThemeStore();

  useEffect(() => {
    // Initialize theme on mount
    const root = document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(resolvedTheme);

    // Re-apply theme when it changes (handles hydration)
    setTheme(theme);
  }, [theme, resolvedTheme, setTheme]);

  return <>{children}</>;
}
