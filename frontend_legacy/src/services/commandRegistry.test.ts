/**
 * Command Registry Service Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { commandRegistry, type Command } from './commandRegistry';
import { Home, Library, Plus } from 'lucide-react';

// Mock commands for testing
const mockCommand1: Command = {
  id: 'test-1',
  label: 'Test Command 1',
  icon: Home,
  keywords: ['test', 'one'],
  category: 'action',
  action: vi.fn(),
  priority: 80,
};

const mockCommand2: Command = {
  id: 'test-2',
  label: 'Test Command 2',
  icon: Library,
  keywords: ['test', 'two'],
  category: 'navigation',
  action: vi.fn(),
  priority: 60,
};

const mockCommand3: Command = {
  id: 'test-3',
  label: 'Another Command',
  icon: Plus,
  keywords: ['another', 'different'],
  category: 'action',
  action: vi.fn(),
  enabled: () => false, // Disabled command
};

describe('CommandRegistry', () => {
  beforeEach(() => {
    // Clear registry before each test
    commandRegistry.clear();
  });

  describe('register', () => {
    it('should register a valid command', () => {
      commandRegistry.register(mockCommand1);
      expect(commandRegistry.count).toBe(1);
      expect(commandRegistry.get('test-1')).toBe(mockCommand1);
    });

    it('should warn and overwrite duplicate command IDs', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      
      commandRegistry.register(mockCommand1);
      commandRegistry.register({ ...mockCommand1, label: 'Updated' });
      
      expect(consoleSpy).toHaveBeenCalled();
      expect(commandRegistry.count).toBe(1);
      expect(commandRegistry.get('test-1')?.label).toBe('Updated');
      
      consoleSpy.mockRestore();
    });

    it('should warn for invalid command structure', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      
      // @ts-expect-error Testing invalid command
      commandRegistry.register({ id: 'invalid' });
      
      expect(consoleSpy).toHaveBeenCalled();
      expect(commandRegistry.count).toBe(0);
      
      consoleSpy.mockRestore();
    });
  });

  describe('registerMany', () => {
    it('should register multiple commands at once', () => {
      commandRegistry.registerMany([mockCommand1, mockCommand2]);
      expect(commandRegistry.count).toBe(2);
    });
  });

  describe('unregister', () => {
    it('should remove a command by ID', () => {
      commandRegistry.register(mockCommand1);
      commandRegistry.unregister('test-1');
      expect(commandRegistry.count).toBe(0);
      expect(commandRegistry.get('test-1')).toBeUndefined();
    });

    it('should handle unregistering non-existent command', () => {
      commandRegistry.unregister('non-existent');
      expect(commandRegistry.count).toBe(0);
    });
  });

  describe('getAll', () => {
    it('should return all registered commands', () => {
      commandRegistry.registerMany([mockCommand1, mockCommand2]);
      const commands = commandRegistry.getAll();
      expect(commands.length).toBe(2);
    });

    it('should filter out disabled commands', () => {
      commandRegistry.registerMany([mockCommand1, mockCommand3]);
      const commands = commandRegistry.getAll();
      expect(commands.length).toBe(1);
      expect(commands[0].id).toBe('test-1');
    });

    it('should return empty array when no commands registered', () => {
      const commands = commandRegistry.getAll();
      expect(commands).toEqual([]);
    });
  });

  describe('getByCategory', () => {
    it('should return commands filtered by category', () => {
      commandRegistry.registerMany([mockCommand1, mockCommand2]);
      const actionCommands = commandRegistry.getByCategory('action');
      expect(actionCommands.length).toBe(1);
      expect(actionCommands[0].category).toBe('action');
    });

    it('should return empty array for category with no commands', () => {
      commandRegistry.register(mockCommand1);
      const filterCommands = commandRegistry.getByCategory('filter');
      expect(filterCommands).toEqual([]);
    });
  });

  describe('search', () => {
    beforeEach(() => {
      commandRegistry.registerMany([mockCommand1, mockCommand2]);
    });

    it('should return all commands when query is empty', () => {
      const results = commandRegistry.search('');
      expect(results.length).toBe(2);
    });

    it('should filter commands based on query', () => {
      const results = commandRegistry.search('Command 1');
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].item.id).toBe('test-1');
    });

    it('should search through keywords', () => {
      const results = commandRegistry.search('one');
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].item.id).toBe('test-1');
    });

    it('should respect maxResults parameter', () => {
      const results = commandRegistry.search('test', 1);
      expect(results.length).toBe(1);
    });

    it('should return results sorted by score', () => {
      const results = commandRegistry.search('test');
      for (let i = 1; i < results.length; i++) {
        expect(results[i - 1].score).toBeGreaterThanOrEqual(results[i].score);
      }
    });

    it('should return empty array when no matches found', () => {
      const results = commandRegistry.search('nonexistent');
      expect(results).toEqual([]);
    });
  });

  describe('get', () => {
    it('should return command by ID', () => {
      commandRegistry.register(mockCommand1);
      const command = commandRegistry.get('test-1');
      expect(command).toBe(mockCommand1);
    });

    it('should return undefined for non-existent ID', () => {
      const command = commandRegistry.get('non-existent');
      expect(command).toBeUndefined();
    });
  });

  describe('clear', () => {
    it('should remove all commands', () => {
      commandRegistry.registerMany([mockCommand1, mockCommand2]);
      commandRegistry.clear();
      expect(commandRegistry.count).toBe(0);
      expect(commandRegistry.getAll()).toEqual([]);
    });
  });

  describe('subscribe', () => {
    it('should notify listeners on command registration', () => {
      const listener = vi.fn();
      commandRegistry.subscribe(listener);
      
      commandRegistry.register(mockCommand1);
      
      expect(listener).toHaveBeenCalledWith([mockCommand1]);
    });

    it('should notify listeners on command unregistration', () => {
      const listener = vi.fn();
      commandRegistry.register(mockCommand1);
      commandRegistry.subscribe(listener);
      
      commandRegistry.unregister('test-1');
      
      expect(listener).toHaveBeenCalledWith([]);
    });

    it('should return unsubscribe function', () => {
      const listener = vi.fn();
      const unsubscribe = commandRegistry.subscribe(listener);
      
      unsubscribe();
      commandRegistry.register(mockCommand1);
      
      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('count', () => {
    it('should return correct command count', () => {
      expect(commandRegistry.count).toBe(0);
      
      commandRegistry.register(mockCommand1);
      expect(commandRegistry.count).toBe(1);
      
      commandRegistry.register(mockCommand2);
      expect(commandRegistry.count).toBe(2);
      
      commandRegistry.unregister('test-1');
      expect(commandRegistry.count).toBe(1);
    });
  });
});
