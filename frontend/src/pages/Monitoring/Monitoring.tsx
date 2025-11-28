import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Database, Zap, HardDrive, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { useSystemHealth, usePerformanceMetrics, useWorkerStatus, useQueueMetrics, useDatabaseMetrics, useCacheMetrics, useAlerts, useAcknowledgeAlert } from '@/hooks/useMonitoring';
import { HEALTH_STATUS_COLORS } from '@/types/monitoring';
import { useReducedMotion } from '@/hooks/useReducedMotion';

export const Monitoring: React.FC = () => {
  const { data: health } = useSystemHealth();
  const { data: performance } = usePerformanceMetrics();
  const { data: workers = [] } = useWorkerStatus();
  const { data: queues = [] } = useQueueMetrics();
  const { data: database } = useDatabaseMetrics();
  const { data: cache } = useCacheMetrics();
  const { data: alerts = [] } = useAlerts();
  const acknowledgeAlert = useAcknowledgeAlert();
  const prefersReducedMotion = useReducedMotion();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5" />;
      case 'degraded':
        return <AlertTriangle className="w-5 h-5" />;
      case 'down':
        return <XCircle className="w-5 h-5" />;
      default:
        return <Activity className="w-5 h-5" />;
    }
  };

  return (
    <div className="h-full overflow-y-auto bg-white dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">System Monitoring</h2>
          <p className="text-gray-600 dark:text-gray-400">Real-time system health and performance</p>
        </div>

        {/* System Health */}
        {health && (
          <motion.div
            initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-6 rounded-lg border-2 ${HEALTH_STATUS_COLORS[health.status]}`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {getStatusIcon(health.status)}
                <div>
                  <h3 className="text-lg font-semibold">System Status: {health.status.toUpperCase()}</h3>
                  <p className="text-sm opacity-80">Uptime: {Math.floor(health.uptime / 3600)}h {Math.floor((health.uptime % 3600) / 60)}m</p>
                </div>
              </div>
              <div className="text-sm opacity-80">
                Last updated: {new Date(health.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </motion.div>
        )}

        {/* Performance Metrics */}
        {performance && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <motion.div
              initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Response Time</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{performance.responseTime}ms</div>
            </motion.div>
            <motion.div
              initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Throughput</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{performance.throughput}/s</div>
            </motion.div>
            <motion.div
              initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Error Rate</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{(performance.errorRate * 100).toFixed(2)}%</div>
            </motion.div>
            <motion.div
              initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 }}
              className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">CPU Usage</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{Math.round(performance.cpuUsage)}%</div>
            </motion.div>
            <motion.div
              initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 }}
              className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Memory</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{Math.round(performance.memoryUsage)}%</div>
            </motion.div>
            <motion.div
              initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 }}
              className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Disk</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{Math.round(performance.diskUsage)}%</div>
            </motion.div>
          </div>
        )}

        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-5 h-5 text-orange-600 dark:text-orange-400" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Active Alerts ({alerts.filter(a => !a.acknowledged).length})</h3>
            </div>
            <div className="space-y-2">
              {alerts.filter(a => !a.acknowledged).map((alert) => (
                <div key={alert.id} className="flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-900/10 rounded border border-orange-200 dark:border-orange-800">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-orange-700 dark:text-orange-300">{alert.severity.toUpperCase()}</span>
                      <span className="text-xs text-gray-600 dark:text-gray-400">{alert.component}</span>
                    </div>
                    <p className="text-sm text-gray-900 dark:text-white">{alert.message}</p>
                  </div>
                  <button
                    onClick={() => acknowledgeAlert.mutate(alert.id)}
                    className="ml-4 px-3 py-1 text-xs bg-orange-600 hover:bg-orange-700 text-white rounded transition-colors"
                  >
                    Acknowledge
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Components Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Workers */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Zap className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Workers ({workers.length})</h3>
            </div>
            <div className="space-y-2">
              {workers.map((worker) => (
                <div key={worker.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">{worker.name}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      {worker.tasksProcessed} tasks • {worker.currentTask || 'Idle'}
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded ${
                    worker.status === 'running' ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300' :
                    worker.status === 'idle' ? 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300' :
                    'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300'
                  }`}>
                    {worker.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Queues */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Queues</h3>
            </div>
            <div className="space-y-3">
              {queues.map((queue) => (
                <div key={queue.name} className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900 dark:text-white">{queue.name}</span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">{queue.size} pending</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">Processing: </span>
                      <span className="font-medium text-gray-900 dark:text-white">{queue.processing}</span>
                    </div>
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">Completed: </span>
                      <span className="font-medium text-gray-900 dark:text-white">{queue.completed}</span>
                    </div>
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">Failed: </span>
                      <span className="font-medium text-gray-900 dark:text-white">{queue.failed}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Database */}
          {database && (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Database className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Database</h3>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Pool Size</span>
                  <span className="font-medium text-gray-900 dark:text-white">{database.connectionPoolSize}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Active Connections</span>
                  <span className="font-medium text-gray-900 dark:text-white">{database.activeConnections}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Idle Connections</span>
                  <span className="font-medium text-gray-900 dark:text-white">{database.idleConnections}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Avg Query Time</span>
                  <span className="font-medium text-gray-900 dark:text-white">{database.queryTime}ms</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Slow Queries</span>
                  <span className="font-medium text-gray-900 dark:text-white">{database.slowQueries}</span>
                </div>
              </div>
            </div>
          )}

          {/* Cache */}
          {cache && (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center gap-2 mb-4">
                <HardDrive className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Cache</h3>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Hit Rate</span>
                  <span className="font-medium text-green-600 dark:text-green-400">{(cache.hitRate * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Miss Rate</span>
                  <span className="font-medium text-orange-600 dark:text-orange-400">{(cache.missRate * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Eviction Rate</span>
                  <span className="font-medium text-gray-900 dark:text-white">{(cache.evictionRate * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Size</span>
                  <span className="font-medium text-gray-900 dark:text-white">{cache.size} / {cache.maxSize}</span>
                </div>
                <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-600 dark:bg-primary-500"
                    style={{ width: `${(cache.size / cache.maxSize) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
