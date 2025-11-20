/**
 * Fuzzy Search Utility
 * 
 * Lightweight fuzzy matching algorithm optimized for command palette use case
 */

export interface MatchRange {
  start: number;
  end: number;
}

export interface SearchResult<T> {
  item: T;
  score: number;
  matches: MatchRange[];
}

interface SearchableItem {
  searchText: string;
  priority?: number;
}

/**
 * Calculate fuzzy match score for a query against text
 * Returns score (0-100) and match positions
 */
export function fuzzyMatch(query: string, text: string): { score: number; matches: MatchRange[] } {
  if (!query) return { score: 0, matches: [] };
  
  const queryLower = query.toLowerCase();
  const textLower = text.toLowerCase();
  const matches: MatchRange[] = [];
  
  let score = 0;
  let queryIndex = 0;
  let consecutiveMatches = 0;
  let lastMatchIndex = -1;
  
  for (let i = 0; i < textLower.length && queryIndex < queryLower.length; i++) {
    if (textLower[i] === queryLower[queryIndex]) {
      // Character match found
      const isConsecutive = i === lastMatchIndex + 1;
      const isWordBoundary = i === 0 || textLower[i - 1] === ' ' || textLower[i - 1] === '-';
      
      // Scoring
      if (isConsecutive) {
        consecutiveMatches++;
        score += 10 + consecutiveMatches; // Bonus for consecutive matches
      } else {
        consecutiveMatches = 0;
        score += isWordBoundary ? 5 : 1; // Bonus for word boundary matches
      }
      
      // Track match position
      if (matches.length === 0 || !isConsecutive) {
        matches.push({ start: i, end: i + 1 });
      } else {
        matches[matches.length - 1].end = i + 1;
      }
      
      lastMatchIndex = i;
      queryIndex++;
    }
  }
  
  // If we didn't match all query characters, return 0 score
  if (queryIndex < queryLower.length) {
    return { score: 0, matches: [] };
  }
  
  // Bonus for exact match
  if (textLower === queryLower) {
    score += 50;
  }
  
  // Bonus for match at start
  if (textLower.startsWith(queryLower)) {
    score += 25;
  }
  
  return { score, matches };
}

/**
 * Search through items with fuzzy matching
 * Returns sorted results with scores and match positions
 */
export function fuzzySearch<T extends SearchableItem>(
  query: string,
  items: T[],
  maxResults: number = 10
): SearchResult<T>[] {
  if (!query.trim()) {
    // Return all items with default score when query is empty
    return items.slice(0, maxResults).map(item => ({
      item,
      score: item.priority || 50,
      matches: [],
    }));
  }
  
  const results: SearchResult<T>[] = [];
  
  for (const item of items) {
    const { score, matches } = fuzzyMatch(query, item.searchText);
    
    if (score > 0) {
      // Apply priority multiplier
      const finalScore = score * (item.priority ? item.priority / 50 : 1);
      
      results.push({
        item,
        score: finalScore,
        matches,
      });
    }
  }
  
  // Sort by score descending
  results.sort((a, b) => b.score - a.score);
  
  // Return top N results
  return results.slice(0, maxResults);
}

/**
 * Highlight matched characters in text
 * Returns array of text segments with match flags
 */
export function highlightMatches(text: string, matches: MatchRange[]): Array<{ text: string; isMatch: boolean }> {
  if (matches.length === 0) {
    return [{ text, isMatch: false }];
  }
  
  const segments: Array<{ text: string; isMatch: boolean }> = [];
  let lastIndex = 0;
  
  for (const match of matches) {
    // Add non-matched text before this match
    if (match.start > lastIndex) {
      segments.push({
        text: text.substring(lastIndex, match.start),
        isMatch: false,
      });
    }
    
    // Add matched text
    segments.push({
      text: text.substring(match.start, match.end),
      isMatch: true,
    });
    
    lastIndex = match.end;
  }
  
  // Add remaining non-matched text
  if (lastIndex < text.length) {
    segments.push({
      text: text.substring(lastIndex),
      isMatch: false,
    });
  }
  
  return segments;
}
