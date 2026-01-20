/**
 * Command Registry Service
 * 
 * Centralized service for managing available commands
 * Singleton pattern for global access
 */

import type { LucideIcon } from 'lucide-react';
import { fuzzySearch, type SearchResult } from '@/utils/fuzzySearch';

export type CommandCategory = 'navigation' | 'action' | 'filter' | 'search' | 'help';

export interface Command {
  id: string;
  label: string;
  description?: string;
  icon: LucideIcon;
  keywords: string[];
  category: CommandCategory;
  action: () => void | Promise<void>;
  shortcut?: string;
  priority?: number;
  enabled?: () => boolean;
}

interface SearchableCommand extends Command {
  searchText: string;
}

type CommandUpdateListener = (commands: Command[]) => void;

class CommandRegistryService {
  private commands: Map<string, Command> = new Map();
  private listeners: Set<CommandUpdateListener> = new Set();

  /**
   * Register a new command
   */
  register(command: Command): void {
    // Validate command structure
    if (!command.id || !command.label || !command.icon || !command.action) {
      console.warn('[CommandRegistry] Invalid command structure:', command);
      return;
    }

    // Check for duplicate ID
    if (this.commands.has(command.id)) {
      console.warn(`[CommandRegistry] Command with ID "${command.id}" already exists. Overwriting.`);
    }

    this.commands.set(command.id, command);
    this.notifyListeners();
  }

  /**
   * Register multiple commands at once
   */
  registerMany(commands: Command[]): void {
    commands.forEach(cmd => this.register(cmd));
  }

  /**
   * Unregister a command by ID
   */
  unregister(commandId: string): void {
    if (this.commands.delete(commandId)) {
      this.notifyListeners();
    }
  }

  /**
   * Get all registered commands
   */
  getAll(): Command[] {
    return Array.from(this.commands.values()).filter(cmd => {
      // Filter out disabled commands
      return cmd.enabled ? cmd.enabled() : true;
    });
  }

  /**
   * Get commands by category
   */
  getByCategory(category: CommandCategory): Command[] {
    return this.getAll().filter(cmd => cmd.category === category);
  }

  /**
   * Search commands with fuzzy matching
   */
  search(query: string, maxResults: number = 10): SearchResult<Command>[] {
    const enabledCommands = this.getAll();
    
    // Convert commands to searchable format
    const searchableCommands: SearchableCommand[] = enabledCommands.map(cmd => ({
      ...cmd,
      searchText: [cmd.label, ...cmd.keywords].join(' '),
    }));

    return fuzzySearch(query, searchableCommands, maxResults);
  }

  /**
   * Get a specific command by ID
   */
  get(commandId: string): Command | undefined {
    return this.commands.get(commandId);
  }

  /**
   * Clear all commands
   */
  clear(): void {
    this.commands.clear();
    this.notifyListeners();
  }

  /**
   * Subscribe to command updates
   */
  subscribe(listener: CommandUpdateListener): () => void {
    this.listeners.add(listener);
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * Notify all listeners of command updates
   */
  private notifyListeners(): void {
    const commands = this.getAll();
    this.listeners.forEach(listener => listener(commands));
  }

  /**
   * Get command count
   */
  get count(): number {
    return this.commands.size;
  }
}

// Export singleton instance
export const commandRegistry = new CommandRegistryService();

// Export type for external use
export type { SearchResult } from '@/utils/fuzzySearch';
