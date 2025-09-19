// Neo Alexandria 2.0 Frontend - Formatting Utilities
// Utility functions for formatting dates, numbers, and text

import { format, formatDistanceToNow, parseISO, isValid } from 'date-fns';

/**
 * Format a date string or Date object to a human-readable format
 */
export function formatDate(date: string | Date | null | undefined, formatString: string = 'MMM d, yyyy'): string {
  if (!date) return '';
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(dateObj)) return '';
    return format(dateObj, formatString);
  } catch {
    return '';
  }
}

/**
 * Format a date to show relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: string | Date | null | undefined): string {
  if (!date) return '';
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(dateObj)) return '';
    return formatDistanceToNow(dateObj, { addSuffix: true });
  } catch {
    return '';
  }
}

/**
 * Format a date with both absolute and relative time
 */
export function formatDateWithRelative(date: string | Date | null | undefined): string {
  const absolute = formatDate(date);
  const relative = formatRelativeTime(date);
  return relative ? `${absolute} (${relative})` : absolute;
}

/**
 * Format a quality score as a percentage
 */
export function formatQualityScore(score: number | null | undefined): string {
  if (score === null || score === undefined) return 'N/A';
  return `${Math.round(score * 100)}%`;
}

/**
 * Format a quality score with color class
 */
export function getQualityScoreColor(score: number | null | undefined): string {
  if (score === null || score === undefined) return 'text-gray-500';
  
  if (score >= 0.8) return 'text-green-600';
  if (score >= 0.6) return 'text-yellow-600';
  if (score >= 0.4) return 'text-orange-600';
  return 'text-red-600';
}

/**
 * Format a quality score with badge style
 */
export function getQualityBadgeClass(score: number | null | undefined): string {
  if (score === null || score === undefined) return 'bg-gray-100 text-gray-600';
  
  if (score >= 0.8) return 'bg-green-100 text-green-800';
  if (score >= 0.6) return 'bg-yellow-100 text-yellow-800';
  if (score >= 0.4) return 'bg-orange-100 text-orange-800';
  return 'bg-red-100 text-red-800';
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string | null | undefined, maxLength: number = 100): string {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
}

/**
 * Format a list of subjects/tags
 */
export function formatSubjects(subjects: string[]): string {
  if (!subjects || subjects.length === 0) return '';
  if (subjects.length <= 3) return subjects.join(', ');
  return `${subjects.slice(0, 3).join(', ')} +${subjects.length - 3} more`;
}

/**
 * Format file size in human-readable format
 */
export function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes || bytes === 0) return '0 B';
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const unitIndex = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = bytes / Math.pow(1024, unitIndex);
  
  return `${size.toFixed(1)} ${units[unitIndex]}`;
}

/**
 * Format a number with thousands separators
 */
export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return '0';
  return num.toLocaleString();
}

/**
 * Get a color class for read status
 */
export function getReadStatusColor(status: string): string {
  switch (status) {
    case 'completed':
      return 'text-green-600 bg-green-100';
    case 'in_progress':
      return 'text-blue-600 bg-blue-100';
    case 'archived':
      return 'text-gray-600 bg-gray-100';
    case 'unread':
    default:
      return 'text-orange-600 bg-orange-100';
  }
}

/**
 * Format read status for display
 */
export function formatReadStatus(status: string): string {
  switch (status) {
    case 'in_progress':
      return 'In Progress';
    case 'completed':
      return 'Completed';
    case 'archived':
      return 'Archived';
    case 'unread':
    default:
      return 'Unread';
  }
}

/**
 * Extract domain from URL
 */
export function extractDomain(url: string | null | undefined): string {
  if (!url) return '';
  
  try {
    const urlObj = new URL(url);
    return urlObj.hostname.replace(/^www\./, '');
  } catch {
    return '';
  }
}

/**
 * Generate initials from a name or title
 */
export function generateInitials(name: string | null | undefined): string {
  if (!name) return '?';
  
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
    .substring(0, 2);
}

/**
 * Format classification code for display
 */
export function formatClassificationCode(code: string | null | undefined): string {
  if (!code) return 'Unclassified';
  
  // Format UDC-style codes (e.g., "004" -> "004 - Computer Science")
  const codeMap: Record<string, string> = {
    '000': 'General Knowledge',
    '001': 'Knowledge Organization',
    '004': 'Computer Science',
    '100': 'Philosophy',
    '200': 'Religion',
    '300': 'Social Sciences',
    '400': 'Language',
    '500': 'Pure Sciences',
    '600': 'Applied Sciences',
    '700': 'Arts & Recreation',
    '800': 'Literature',
    '900': 'History & Geography',
  };
  
  const name = codeMap[code] || 'Specialized Topic';
  return `${code} - ${name}`;
}

/**
 * Highlight search terms in text
 */
export function highlightSearchTerms(text: string, searchTerm: string): string {
  if (!searchTerm || !text) return text;
  
  const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
}

/**
 * Get a consistent color for a string (useful for avatars, tags, etc.)
 */
export function getStringColor(str: string): string {
  const colors = [
    'bg-red-100 text-red-700',
    'bg-blue-100 text-blue-700',
    'bg-green-100 text-green-700',
    'bg-yellow-100 text-yellow-700',
    'bg-purple-100 text-purple-700',
    'bg-pink-100 text-pink-700',
    'bg-indigo-100 text-indigo-700',
    'bg-teal-100 text-teal-700',
  ];
  
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  return colors[Math.abs(hash) % colors.length];
}
