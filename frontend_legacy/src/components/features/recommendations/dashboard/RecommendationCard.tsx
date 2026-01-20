import { memo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RecommendationItem, RecommendationFeedbackPayload } from '@/lib/api/recommendations';
import { cardHoverVariants } from '@/animations/variants';
import { Icon } from '@/components/common/Icon';
import { icons } from '@/config/icons';
import { Tag } from '@/components/common/Tag';
import { ThumbsUp, ThumbsDown, Sparkles } from 'lucide-react';
import '@/components/cards/ResourceCard.css'; // Reuse existing card styles

interface RecommendationCardProps {
    item: RecommendationItem;
    onFeedback: (payload: RecommendationFeedbackPayload) => void;
    onInteraction: (id: string, type: 'view' | 'click' | 'open_detail') => void;
    delay?: number;
}

export const RecommendationCard = memo(({
    item,
    onFeedback,
    onInteraction,
    delay = 0
}: RecommendationCardProps) => {
    const [showActions, setShowActions] = useState(false);
    const [feedbackState, setFeedbackState] = useState<'none' | 'up' | 'down'>('none');
    const [showExplanation, setShowExplanation] = useState(false);

    const handleFeedback = (type: 'thumbs_up' | 'thumbs_down') => {
        if (feedbackState === 'none') {
            setFeedbackState(type === 'thumbs_up' ? 'up' : 'down');
            onFeedback({
                resource_id: item.id,
                feedback_type: type,
                section: item.category
            });
        }
    };

    const handleClick = () => {
        onInteraction(item.id, 'click');
        // Navigate or open detail would go here
    };

    const getTypeColor = () => {
        switch (item.type) {
            case 'article': return 'rgba(59, 130, 246, 0.2)';
            case 'video': return 'rgba(6, 182, 212, 0.2)';
            case 'book': return 'var(--accent-subtle)';
            case 'paper': return 'rgba(20, 184, 166, 0.2)';
            default: return 'rgba(59, 130, 246, 0.2)';
        }
    };

    const getQualityColor = (score: number) => {
        if (score >= 0.8) return 'oklch(0.7 0.2 120)';
        if (score >= 0.6) return 'oklch(0.7 0.2 200)';
        if (score >= 0.4) return 'oklch(0.7 0.2 50)';
        return 'var(--destructive)';
    };

    return (
        <motion.div
            className="card resource-card resource-card--grid"
            variants={cardHoverVariants}
            initial="rest"
            whileHover="hover"
            whileTap={{ scale: 0.98 }}
            style={{ animationDelay: `${delay}s`, position: 'relative' }}
            onHoverStart={() => setShowActions(true)}
            onHoverEnd={() => {
                setShowActions(false);
                setShowExplanation(false);
            }}
            onClick={handleClick}
        >
            {/* Recommendation Badge */}
            <div style={{
                position: 'absolute',
                top: '-10px',
                right: '-10px',
                background: 'var(--accent)',
                borderRadius: '50%',
                padding: '6px',
                zIndex: 10,
                boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
            }}
                onMouseEnter={() => setShowExplanation(true)}
                onMouseLeave={() => setShowExplanation(false)}
            >
                <Sparkles size={16} color="white" />
            </div>

            {/* Explanation Tooltip */}
            <AnimatePresence>
                {showExplanation && (
                    <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.9 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.9 }}
                        style={{
                            position: 'absolute',
                            top: '30px',
                            right: '-20px',
                            width: '250px',
                            background: 'var(--surface-elevated)',
                            border: '1px solid var(--border)',
                            borderRadius: 'var(--radius-md)',
                            padding: '12px',
                            zIndex: 20,
                            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
                            fontSize: '0.875rem',
                            color: 'var(--text-secondary)'
                        }}
                    >
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
                            Why this?
                        </div>
                        {item.explanation.reason}
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="resource-header">
                <div className="resource-type-icon" style={{ background: getTypeColor() }}>
                    <Icon icon={item.type === 'video' ? icons.video : item.type === 'book' ? icons.book : item.type === 'paper' ? icons.paper : icons.article} size={20} />
                </div>
                <div className="resource-rating" style={{ color: getQualityColor(item.quality_score || 0) }}>
                    <Icon icon={icons.star} size={16} />
                    <span>{((item.quality_score || 0) * 100).toFixed(0)}%</span>
                </div>
            </div>

            <h3 className="resource-title">{item.title}</h3>
            <p className="resource-description">{item.description || 'No description available'}</p>

            <div className="resource-tags">
                {(item.subject || []).slice(0, 3).map((tag, i) => (
                    <Tag key={i} label={tag} variant={i % 3 === 0 ? 'blue' : i % 3 === 1 ? 'cyan' : 'purple'} />
                ))}
            </div>

            <div className="resource-meta">
                {item.creator && (
                    <div className="resource-author">
                        <Icon icon={icons.user} size={16} />
                        <span>{item.creator}</span>
                    </div>
                )}
            </div>

            <AnimatePresence>
                {(showActions || feedbackState !== 'none') && (
                    <motion.div
                        className="resource-actions-overlay"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        style={{
                            background: 'linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.6) 50%, transparent 100%)',
                            display: 'flex',
                            alignItems: 'flex-end',
                            padding: '16px'
                        }}
                    >
                        <div style={{ display: 'flex', gap: '12px', width: '100%', justifyContent: 'center' }}>
                            <button
                                onClick={(e) => { e.stopPropagation(); handleFeedback('thumbs_up'); }}
                                style={{
                                    background: feedbackState === 'up' ? 'var(--accent)' : 'rgba(255,255,255,0.1)',
                                    border: 'none',
                                    borderRadius: '50%',
                                    width: '40px',
                                    height: '40px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                <ThumbsUp size={20} color={feedbackState === 'up' ? 'white' : 'var(--text-secondary)'} />
                            </button>
                            <button
                                onClick={(e) => { e.stopPropagation(); handleFeedback('thumbs_down'); }}
                                style={{
                                    background: feedbackState === 'down' ? 'var(--destructive)' : 'rgba(255,255,255,0.1)',
                                    border: 'none',
                                    borderRadius: '50%',
                                    width: '40px',
                                    height: '40px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                <ThumbsDown size={20} color={feedbackState === 'down' ? 'white' : 'var(--text-secondary)'} />
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
});
