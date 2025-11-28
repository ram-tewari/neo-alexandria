export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down';
  components: ComponentHealth[];
  timestamp: Date;
  uptime: number;
}

export interface ComponentHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  metrics: Record<string, number>;
  lastCheck: Date;
  message?: string;
}

export interface PerformanceMetrics {
  responseTime: number;
  throughput: number;
  errorRate: number;
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
}

export interface WorkerStatus {
  id: string;
  name: string;
  status: 'running' | 'idle' | 'stopped' | 'error';
  tasksProcessed: number;
  currentTask?: string;
  lastActivity: Date;
}

export interface QueueMetrics {
  name: string;
  size: number;
  processing: number;
  completed: number;
  failed: number;
  averageWaitTime: number;
}

export interface DatabaseMetrics {
  connectionPoolSize: number;
  activeConnections: number;
  idleConnections: number;
  queryTime: number;
  slowQueries: number;
}

export interface CacheMetrics {
  hitRate: number;
  missRate: number;
  evictionRate: number;
  size: number;
  maxSize: number;
}

export interface Alert {
  id: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  component: string;
  message: string;
  timestamp: Date;
  acknowledged: boolean;
}

export const HEALTH_STATUS_COLORS = {
  healthy: 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/20',
  degraded: 'text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-900/20',
  down: 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/20',
} as const;
