// Neo Alexandria 2.0 Frontend - Class Name Utility
// Utility for merging Tailwind CSS classes with clsx and tailwind-merge

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merges class names with tailwind-merge to handle Tailwind CSS conflicts
 * Combines clsx for conditional classes with tailwind-merge for proper Tailwind resolution
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
