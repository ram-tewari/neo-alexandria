/**
 * Fuzzy Search Utility Tests
 */

import { describe, it, expect } from 'vitest';
import { fuzzyMatch, fuzzySearch, highlightMatches } from './fuzzySearch';

describe('fuzzyMatch', () => {
  it('should return 0 score for empty query', () => {
    const result = fuzzyMatch('', 'test');
    expect(result.score).toBe(0);
    expect(result.matches).toEqual([]);
  });

  it('should return high score for exact match', () => {
    const result = fuzzyMatch('test', 'test');
    expect(result.score).toBeGreaterThan(50);
    expect(result.matches.length).toBeGreaterThan(0);
  });

  it('should match case-insensitively', () => {
    const result1 = fuzzyMatch('TEST', 'test');
    const result2 = fuzzyMatch('test', 'TEST');
    expect(result1.score).toBeGreaterThan(0);
    expect(result2.score).toBeGreaterThan(0);
  });

  it('should match partial queries', () => {
    const result = fuzzyMatch('tst', 'test');
    expect(result.score).toBeGreaterThan(0);
    expect(result.matches.length).toBeGreaterThan(0);
  });

  it('should give higher score for consecutive matches', () => {
    const consecutive = fuzzyMatch('tes', 'test');
    const nonConsecutive = fuzzyMatch('tst', 'test');
    expect(consecutive.score).toBeGreaterThan(nonConsecutive.score);
  });

  it('should give bonus for word boundary matches', () => {
    const result = fuzzyMatch('gd', 'Go to Dashboard');
    expect(result.score).toBeGreaterThan(0);
  });

  it('should return 0 score when not all characters match', () => {
    const result = fuzzyMatch('xyz', 'test');
    expect(result.score).toBe(0);
    expect(result.matches).toEqual([]);
  });

  it('should track match positions correctly', () => {
    const result = fuzzyMatch('te', 'test');
    expect(result.matches).toEqual([{ start: 0, end: 2 }]);
  });

  it('should handle multiple match ranges', () => {
    const result = fuzzyMatch('td', 'test dashboard');
    expect(result.matches.length).toBe(2);
  });
});

describe('fuzzySearch', () => {
  const items = [
    { searchText: 'Go to Dashboard', priority: 80 },
    { searchText: 'Go to Library', priority: 70 },
    { searchText: 'Add New Resource', priority: 60 },
    { searchText: 'Create Collection', priority: 50 },
    { searchText: 'Filter Unread', priority: 40 },
  ];

  it('should return all items when query is empty', () => {
    const results = fuzzySearch('', items, 10);
    expect(results.length).toBe(5);
  });

  it('should filter items based on query', () => {
    const results = fuzzySearch('dash', items);
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].item.searchText).toContain('Dashboard');
  });

  it('should respect maxResults parameter', () => {
    const results = fuzzySearch('go', items, 1);
    expect(results.length).toBe(1);
  });

  it('should sort results by score descending', () => {
    const results = fuzzySearch('go', items);
    for (let i = 1; i < results.length; i++) {
      expect(results[i - 1].score).toBeGreaterThanOrEqual(results[i].score);
    }
  });

  it('should apply priority multiplier', () => {
    const highPriority = { searchText: 'test', priority: 100 };
    const lowPriority = { searchText: 'test', priority: 10 };
    const results = fuzzySearch('test', [lowPriority, highPriority]);
    expect(results[0].item).toBe(highPriority);
  });

  it('should return empty array when no matches found', () => {
    const results = fuzzySearch('xyz', items);
    expect(results).toEqual([]);
  });

  it('should handle items without priority', () => {
    const noPriorityItems = [{ searchText: 'test' }];
    const results = fuzzySearch('test', noPriorityItems);
    expect(results.length).toBe(1);
  });
});

describe('highlightMatches', () => {
  it('should return single segment when no matches', () => {
    const segments = highlightMatches('test', []);
    expect(segments).toEqual([{ text: 'test', isMatch: false }]);
  });

  it('should highlight matched characters', () => {
    const segments = highlightMatches('test', [{ start: 0, end: 2 }]);
    expect(segments).toEqual([
      { text: 'te', isMatch: true },
      { text: 'st', isMatch: false },
    ]);
  });

  it('should handle multiple match ranges', () => {
    const segments = highlightMatches('test', [
      { start: 0, end: 1 },
      { start: 2, end: 3 },
    ]);
    expect(segments.length).toBe(4);
    expect(segments[0]).toEqual({ text: 't', isMatch: true });
    expect(segments[1]).toEqual({ text: 'e', isMatch: false });
    expect(segments[2]).toEqual({ text: 's', isMatch: true });
    expect(segments[3]).toEqual({ text: 't', isMatch: false });
  });

  it('should handle match at start', () => {
    const segments = highlightMatches('test', [{ start: 0, end: 4 }]);
    expect(segments).toEqual([{ text: 'test', isMatch: true }]);
  });

  it('should handle match at end', () => {
    const segments = highlightMatches('test', [{ start: 2, end: 4 }]);
    expect(segments).toEqual([
      { text: 'te', isMatch: false },
      { text: 'st', isMatch: true },
    ]);
  });
});
