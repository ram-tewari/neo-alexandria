import { apiClient } from './client';
import {
  SystemHealth,
  PerformanceMetrics,
  WorkerStatus,
  QueueMetrics,
  DatabaseMetrics,
  CacheMetrics,
  Alert,
} from '@/types/monitoring';

export const monitoringApi = {
  getSystemHealth: async (): Promise<SystemHealth> => {
    const response = await apiClient.get<SystemHealth>('/monitoring/health');
    return response.data;
  },

  getPerformanceMetrics: async (): Promise<PerformanceMetrics> => {
    const response = await apiClient.get<PerformanceMetrics>('/monitoring/performance');
    return response.data;
  },

  getWorkerStatus: async (): Promise<WorkerStatus[]> => {
    const response = await apiClient.get<WorkerStatus[]>('/monitoring/workers');
    return response.data;
  },

  getQueueMetrics: async (): Promise<QueueMetrics[]> => {
    const response = await apiClient.get<QueueMetrics[]>('/monitoring/queues');
    return response.data;
  },

  getDatabaseMetrics: async (): Promise<DatabaseMetrics> => {
    const response = await apiClient.get<DatabaseMetrics>('/monitoring/database');
    return response.data;
  },

  getCacheMetrics: async (): Promise<CacheMetrics> => {
    const response = await apiClient.get<CacheMetrics>('/monitoring/cache');
    return response.data;
  },

  getAlerts: async (): Promise<Alert[]> => {
    const response = await apiClient.get<Alert[]>('/monitoring/alerts');
    return response.data;
  },

  acknowledgeAlert: async (alertId: string): Promise<void> => {
    await apiClient.post(`/monitoring/alerts/${alertId}/acknowledge`);
  },
};
