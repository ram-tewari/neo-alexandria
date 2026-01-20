import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
    recommendationsApi,
    RecommendationItem,
    RecommendationCategory,
    RecommendationFeedbackPayload
} from '@/lib/api/recommendations';
import { RecommendationCard } from './RecommendationCard';
import { Carousel } from '@/components/common/Carousel';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { useToast } from '@/contexts/ToastContext';
import { Button } from '@/components/common/Button';
import { RefreshCw } from 'lucide-react';

interface RecommendationsSectionProps {
    title: string;
    subtitle?: string;
    category: RecommendationCategory;
    gradient?: string;
}

export const RecommendationsSection = ({
    title,
    subtitle,
    category,
    gradient = 'linear-gradient(90deg, #FF0080 0%, #7928CA 100%)'
}: RecommendationsSectionProps) => {
    const [items, setItems] = useState<RecommendationItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { showToast } = useToast();

    const fetchRecommendations = async () => {
        setIsLoading(true);
        setError(null);
        try {
            // Mock delay for effect
            await new Promise(resolve => setTimeout(resolve, 800));
            const data = await recommendationsApi.getRecommendations(category);
            setItems(data);
        } catch (err) {
            console.error(`Failed to fetch recommendations for ${category}:`, err);
            setError('Failed to load recommendations');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchRecommendations();
    }, [category]);

    const handleFeedback = async (payload: RecommendationFeedbackPayload) => {
        try {
            await recommendationsApi.sendFeedback(payload);
            showToast({ message: 'Thanks for your feedback!', variant: 'success' });
        } catch (err) {
            console.error('Failed to send feedback:', err);
            showToast({ message: 'Failed to send feedback', variant: 'error' });
        }
    };

    const handleInteraction = async (id: string, type: 'view' | 'click' | 'open_detail') => {
        try {
            await recommendationsApi.trackInteraction({
                resource_id: id,
                event_type: type
            });
        } catch (err) {
            console.error('Failed to track interaction:', err);
        }
    };

    if (error) {
        return (
            <div style={{ marginBottom: '3rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary-white)' }}>{title}</h2>
                </div>
                <div style={{
                    padding: '2rem',
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--destructive)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '1rem'
                }}>
                    <p>{error}</p>
                    <Button variant="secondary" size="sm" onClick={fetchRecommendations}>
                        <RefreshCw size={16} style={{ marginRight: '8px' }} />
                        Retry
                    </Button>
                </div>
            </div>
        );
    }

    if (!isLoading && items.length === 0) {
        return (
            <div style={{ marginBottom: '3rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary-white)' }}>{title}</h2>
                </div>
                <div style={{
                    padding: '3rem',
                    textAlign: 'center',
                    color: 'var(--text-secondary)',
                    background: 'var(--surface-subtle)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px dashed var(--border)'
                }}>
                    <p>No recommendations found for this category yet.</p>
                </div>
            </div>
        );
    }

    return (
        <div style={{ marginBottom: '3rem' }}>
            <div style={{ marginBottom: '1.5rem' }}>
                <h2 style={{
                    fontSize: '1.5rem',
                    fontWeight: '700',
                    color: 'var(--primary-white)',
                    display: 'inline-block',
                    position: 'relative',
                    marginBottom: '0.5rem'
                }}>
                    {title}
                    <span style={{
                        position: 'absolute',
                        bottom: '-4px',
                        left: 0,
                        width: '100%',
                        height: '3px',
                        background: gradient,
                        borderRadius: '2px'
                    }} />
                </h2>
                {subtitle && (
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>{subtitle}</p>
                )}
            </div>

            {isLoading ? (
                <div style={{ display: 'flex', gap: '20px', overflow: 'hidden' }}>
                    {[1, 2, 3].map((i) => (
                        <div key={i} style={{
                            width: '380px',
                            height: '280px',
                            background: 'var(--surface-subtle)',
                            borderRadius: 'var(--radius-lg)',
                            flexShrink: 0,
                            animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
                        }} />
                    ))}
                </div>
            ) : (
                <Carousel speed={25} pauseOnHover={true}>
                    {items.map((item, index) => (
                        <div key={item.id} style={{ width: '380px', paddingRight: '20px' }}>
                            <RecommendationCard
                                item={item}
                                onFeedback={handleFeedback}
                                onInteraction={handleInteraction}
                                delay={index * 0.1}
                            />
                        </div>
                    ))}
                </Carousel>
            )}
        </div>
    );
};
