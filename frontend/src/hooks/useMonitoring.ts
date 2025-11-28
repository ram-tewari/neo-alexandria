import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { monitoringApi } from '@/services/api/monitoring';

export const useSystemHealth = () => {
  return useQuery({
    queryKey: ['monitoring', 'health'],
    queryFn: monitoringApi.getSystemHealth,
    refetchInterval: 30000, // Refresh every 30 seconds
    staleTime: 0,
  });
};

export const usePerformanceMetrics = () => {
  return useQuery({
    queryKey: ['monitoring', 'performance'],
    queryFn: monitoringApi.getPerformanceMetrics,
    refetchInterval: 10000, // Refresh every 10 seconds
    staleTime: 0,
  });
};

export const useWorkerStatus = () => {
  return useQuery({
    queryKey: ['monitoring', 'workers'],
    queryFn: monitoringApi.getWorkerStatus,
    refetchInterval: 15000, // Refresh every 15 seconds
    staleTime: 0,
  });
};

export const useQueueMetrics = () => {
  return useQuery({
    queryKey: ['monitoring', 'queues'],
    queryFn: monitoringApi.getQueueMetrics,
    refetchInterval: 10000,
    staleTime: 0,
  });
};

export const useDatabaseMetrics = () => {
  return useQuery({
    queryKey: ['monitoring', 'database'],
    queryFn: monitoringApi.getDatabaseMetrics,
    refetchInterval: 30000,
    staleTime: 0,
  });
};

export const useCacheMetrics = () => {
  return useQuery({
    queryKey: ['monitoring', 'cache'],
    queryFn: monitoringApi.getCacheMetrics,
    refetchInterval: 15000,
    staleTime: 0,
  });
};

export const useAlerts = () => {
  return useQuery({
    queryKey: ['monitoring', 'alerts'],
    queryFn: monitoringApi.getAlerts,
    refetchInterval: 20000,
    staleTime: 0,
  });
};

export const useAcknowledgeAlert = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: string) => monitoringApi.acknowledgeAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring', 'alerts'] });
    },
  });
};
