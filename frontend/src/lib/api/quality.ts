/**
 * Quality API Client
 * Provides typed methods for quality-related operations
 */

import { QualityDetails } from './types';
import { apiRequest } from './apiUtils';

/**
 * Quality API Client
 */
export const qualityApi = {
  /**
   * Get detailed quality information for a resource
   */
  async getDetails(resourceId: string): Promise<QualityDetails> {
    return apiRequest<QualityDetails>(`/resources/${resourceId}/quality-details`);
  },
};

export default qualityApi;
