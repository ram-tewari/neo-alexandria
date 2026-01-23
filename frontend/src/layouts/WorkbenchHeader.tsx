import { Menu, Search, User } from 'lucide-react';
import { Button } from '../components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import { ThemeToggle } from '../components/ThemeToggle';
import { RepositorySwitcher } from '../components/RepositorySwitcher';
import { useCommandPaletteStore } from '../stores/command';
import { useWorkbenchStore } from '../stores/workbench';

export function WorkbenchHeader() {
  const { open: openCommandPalette } = useCommandPaletteStore();
  const { toggleSidebar } = useWorkbenchStore();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center gap-4 px-4">
        {/* Mobile menu button */}
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={toggleSidebar}
          aria-label="Toggle menu"
        >
          <Menu className="h-5 w-5" />
        </Button>

        {/* Repository Switcher */}
        <RepositorySwitcher />

        {/* Spacer */}
        <div className="flex-1" />

        {/* Command Palette Trigger */}
        <Button
          variant="outline"
          className="hidden md:flex items-center gap-2 w-[200px] justify-between text-muted-foreground"
          onClick={openCommandPalette}
        >
          <div className="flex items-center gap-2">
            <Search className="h-4 w-4" />
            <span className="text-sm">Search...</span>
          </div>
          <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
            <span className="text-xs">⌘</span>K
          </kbd>
        </Button>

        {/* Mobile search button */}
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={openCommandPalette}
          aria-label="Search"
        >
          <Search className="h-5 w-5" />
        </Button>

        {/* Theme Toggle */}
        <ThemeToggle />

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" aria-label="User menu">
              <User className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Log out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
