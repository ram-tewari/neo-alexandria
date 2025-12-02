/**
 * Mock data for development and testing
 */

import type { Resource, Collection } from './types';

/**
 * Simulate network delay
 */
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Mock resources data
 */
export const mockResources: Resource[] = [
  {
    id: '1',
    title: 'Introduction to React Hooks',
    url: 'https://example.com/react-hooks',
    resource_type: 'article',
    description: 'A comprehensive guide to React Hooks and their usage patterns',
    tags: ['react', 'javascript', 'frontend'],
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
  },
  {
    id: '2',
    title: 'TypeScript Best Practices',
    url: 'https://example.com/typescript-best-practices',
    resource_type: 'video',
    description: 'Learn TypeScript best practices for building scalable applications',
    tags: ['typescript', 'javascript', 'programming'],
    created_at: '2024-01-16T14:30:00Z',
    updated_at: '2024-01-16T14:30:00Z',
  },
  {
    id: '3',
    title: 'Clean Code: A Handbook of Agile Software Craftsmanship',
    url: 'https://example.com/clean-code',
    resource_type: 'book',
    description: 'Essential reading for software developers who want to write better code',
    tags: ['programming', 'software-engineering', 'best-practices'],
    created_at: '2024-01-17T09:15:00Z',
    updated_at: '2024-01-17T09:15:00Z',
  },
  {
    id: '4',
    title: 'Machine Learning Fundamentals',
    url: 'https://example.com/ml-fundamentals',
    resource_type: 'paper',
    description: 'Research paper on fundamental concepts in machine learning',
    tags: ['machine-learning', 'ai', 'research'],
    created_at: '2024-01-18T16:45:00Z',
    updated_at: '2024-01-18T16:45:00Z',
  },
  {
    id: '5',
    title: 'CSS Grid Layout Guide',
    url: 'https://example.com/css-grid',
    resource_type: 'article',
    description: 'Complete guide to CSS Grid layout with practical examples',
    tags: ['css', 'frontend', 'web-design'],
    created_at: '2024-01-19T11:20:00Z',
    updated_at: '2024-01-19T11:20:00Z',
  },
  {
    id: '6',
    title: 'Advanced Node.js Patterns',
    url: 'https://example.com/nodejs-patterns',
    resource_type: 'video',
    description: 'Deep dive into advanced Node.js design patterns and architectures',
    tags: ['nodejs', 'javascript', 'backend'],
    created_at: '2024-01-20T13:00:00Z',
    updated_at: '2024-01-20T13:00:00Z',
  },
];

/**
 * Mock collections data
 */
export const mockCollections: Collection[] = [
  {
    id: '1',
    name: 'Frontend Development',
    description: 'Resources for modern frontend development',
    resource_count: 12,
    created_at: '2024-01-10T10:00:00Z',
    updated_at: '2024-01-20T15:30:00Z',
  },
  {
    id: '2',
    name: 'Machine Learning',
    description: 'ML and AI research papers and tutorials',
    resource_count: 8,
    created_at: '2024-01-12T14:00:00Z',
    updated_at: '2024-01-18T16:45:00Z',
  },
  {
    id: '3',
    name: 'Software Engineering',
    description: 'Best practices and patterns for software development',
    resource_count: 15,
    created_at: '2024-01-08T09:00:00Z',
    updated_at: '2024-01-19T12:00:00Z',
  },
];

/**
 * Mock API client with simulated latency
 */
export const mockApiClient = {
  resources: {
    list: async (params?: any) => {
      await delay(300); // Simulate network latency
      return {
        resources: mockResources,
        total: mockResources.length,
        page: params?.page || 1,
        page_size: params?.page_size || 20,
      };
    },
    get: async (id: string) => {
      await delay(200);
      const resource = mockResources.find((r) => r.id === id);
      if (!resource) throw new Error('Resource not found');
      return resource;
    },
    create: async (data: any) => {
      await delay(400);
      const newResource: Resource = {
        id: String(mockResources.length + 1),
        ...data,
        tags: data.tags || [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      return newResource;
    },
    update: async (id: string, data: any) => {
      await delay(400);
      const resource = mockResources.find((r) => r.id === id);
      if (!resource) throw new Error('Resource not found');
      return {
        ...resource,
        ...data,
        updated_at: new Date().toISOString(),
      };
    },
    delete: async (id: string) => {
      await delay(300);
      const index = mockResources.findIndex((r) => r.id === id);
      if (index === -1) throw new Error('Resource not found');
    },
  },
  collections: {
    list: async () => {
      await delay(250);
      return mockCollections;
    },
    get: async (id: string) => {
      await delay(200);
      const collection = mockCollections.find((c) => c.id === id);
      if (!collection) throw new Error('Collection not found');
      return collection;
    },
  },
  search: async (query: string) => {
    await delay(300);
    const filtered = mockResources.filter(
      (r) =>
        r.title.toLowerCase().includes(query.toLowerCase()) ||
        r.description?.toLowerCase().includes(query.toLowerCase()) ||
        r.tags.some((tag) => tag.toLowerCase().includes(query.toLowerCase()))
    );
    return {
      resources: filtered,
      total: filtered.length,
      page: 1,
      page_size: 20,
    };
  },
};
