/**
 * Topic Color Palette for Knowledge Graph
 * Using OKLCH color space for perceptually uniform colors
 * All colors meet WCAG AA contrast requirements on dark backgrounds
 */

export interface TopicCategory {
  id: string;
  name: string;
  color: string; // OKLCH format
  description?: string;
}

export const topicColors: Record<string, TopicCategory> = {
  technology: {
    id: 'technology',
    name: 'Technology',
    color: 'oklch(0.7 0.2 230)', // Blue
    description: 'Tech, programming, software, hardware',
  },
  science: {
    id: 'science',
    name: 'Science',
    color: 'oklch(0.7 0.2 180)', // Cyan
    description: 'Scientific research, studies, experiments',
  },
  arts: {
    id: 'arts',
    name: 'Arts & Culture',
    color: 'oklch(0.7 0.2 330)', // Pink/Magenta
    description: 'Art, music, culture, entertainment',
  },
  business: {
    id: 'business',
    name: 'Business',
    color: 'oklch(0.7 0.2 90)', // Yellow-green
    description: 'Business, finance, economics, entrepreneurship',
  },
  health: {
    id: 'health',
    name: 'Health',
    color: 'oklch(0.7 0.2 140)', // Green
    description: 'Health, medicine, wellness, fitness',
  },
  education: {
    id: 'education',
    name: 'Education',
    color: 'oklch(0.7 0.2 50)', // Orange
    description: 'Learning, teaching, courses, tutorials',
  },
  philosophy: {
    id: 'philosophy',
    name: 'Philosophy',
    color: 'oklch(0.7 0.2 290)', // Purple
    description: 'Philosophy, ethics, thought, reasoning',
  },
  history: {
    id: 'history',
    name: 'History',
    color: 'oklch(0.7 0.2 20)', // Red-orange
    description: 'Historical events, periods, civilizations',
  },
  social: {
    id: 'social',
    name: 'Social Sciences',
    color: 'oklch(0.7 0.2 260)', // Blue-purple
    description: 'Psychology, sociology, anthropology',
  },
  uncategorized: {
    id: 'uncategorized',
    name: 'Uncategorized',
    color: 'oklch(0.5 0 0)', // Gray
    description: 'Unclassified content',
  },
};

// Array version for easy iteration
export const topicCategoriesArray: TopicCategory[] = Object.values(topicColors);

// Helper function to get color by category ID
export const getTopicColor = (categoryId: string): string => {
  return topicColors[categoryId]?.color || topicColors.uncategorized.color;
};

// Helper function to get category by ID
export const getTopicCategory = (categoryId: string): TopicCategory => {
  return topicColors[categoryId] || topicColors.uncategorized;
};

// Light mode color adjustments (slightly darker for better contrast)
export const getTopicColorForTheme = (categoryId: string, theme: 'light' | 'dark'): string => {
  const category = topicColors[categoryId] || topicColors.uncategorized;
  
  if (theme === 'light') {
    // For light mode, reduce lightness slightly for better contrast
    return category.color.replace(/oklch\(0\.7/, 'oklch(0.5');
  }
  
  return category.color;
};
