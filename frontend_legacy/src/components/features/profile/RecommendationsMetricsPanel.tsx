import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { recommendationsApi, RecommendationsMetrics } from '@/lib/api/recommendations';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { BarChart2, TrendingUp, Zap, Target } from 'lucide-react';

export const RecommendationsMetricsPanel = () => {
    const [metrics, setMetrics] = useState<RecommendationsMetrics | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                // Mock delay
                await new Promise(resolve => setTimeout(resolve, 1000));
                const data = await recommendationsApi.getMetrics();
                setMetrics(data);
            } catch (err) {
                console.error('Failed to fetch metrics:', err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchMetrics();
    }, []);

    if (isLoading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
                <LoadingSpinner size="md" />
            </div>
        );
    }

    if (!metrics) {
        return (
            <div style={{ padding: '1rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
                Unable to load metrics.
            </div>
        );
    }

    return (
        <div className="metrics-panel">
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--primary-white)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BarChart2 size={20} color="var(--accent)" />
                Performance Metrics
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem' }}>
                <MetricCard
                    label="Click-Through Rate"
                    value={`${(metrics.ctr * 100).toFixed(1)}%`}
                    icon={<Target size={16} color="var(--accent)" />}
                />
                <MetricCard
                    label="Total Interactions"
                    value={metrics.total_interactions.toString()}
                    icon={<Zap size={16} color="var(--accent)" />}
                />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <MetricBar
                    label="Diversity Score"
                    value={metrics.diversity_score}
                    color="var(--secondary)"
                    description="Variety of topics in your feed"
                />
                <MetricBar
                    label="Novelty Score"
                    value={metrics.novelty_score}
                    color="var(--accent)"
                    description="Discovery of non-popular content"
                />
            </div>
        </div>
    );
};

const MetricCard = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div style={{
        background: 'var(--surface-subtle)',
        padding: '1rem',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border)'
    }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            {icon}
            {label}
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            {value}
        </div>
    </div>
);

const MetricBar = ({ label, value, color, description }: { label: string, value: number, color: string, description: string }) => (
    <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <div>
                <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.9rem' }}>{label}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{description}</div>
            </div>
            <div style={{ fontWeight: 700, color }}>{(value * 100).toFixed(0)}%</div>
        </div>
        <div style={{ height: '8px', background: 'var(--surface-subtle)', borderRadius: '4px', overflow: 'hidden' }}>
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value * 100}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                style={{ height: '100%', background: color, borderRadius: '4px' }}
            />
        </div>
    </div>
);
