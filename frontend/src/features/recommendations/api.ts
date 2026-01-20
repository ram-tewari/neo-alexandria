/**
 * Recommendations API Client
 * Handles communication with the backend recommendations API
 */

import type { Recommendation } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Get personalized recommendations
 * @param limit - Maximum number of recommendations to return (default: 10)
 * @returns Promise resolving to array of recommendations
 * @throws Error if request fails
 */
export async function getRecommendations(limit: number = 10): Promise<Recommendation[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/recommendations?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch recommendations: ${response.status}`);
    }

    const data = await response.json();
    return data.recommendations || data; // Handle both {recommendations: []} and [] formats
  } catch (error) {
    console.error('Recommendations API error:', error);
    throw error;
  }
}
