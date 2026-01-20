import { useState } from 'react';
import { motion } from 'framer-motion';
import { HelpCircle } from 'lucide-react';

interface PreferenceSlidersProps {
    preferences: {
        diversity: number;
        novelty: number;
        recency: number;
    };
    onChange: (key: 'diversity' | 'novelty' | 'recency', value: number) => void;
}

export const PreferenceSliders = ({ preferences, onChange }: PreferenceSlidersProps) => {
    return (
        <div className="preference-sliders" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <SliderItem
                label="Diversity"
                value={preferences.diversity}
                onChange={(val) => onChange('diversity', val)}
                description="Mix of different topics and sources"
                lowLabel="Focused"
                highLabel="Eclectic"
            />
            <SliderItem
                label="Novelty"
                value={preferences.novelty}
                onChange={(val) => onChange('novelty', val)}
                description="Balance between popular and obscure content"
                lowLabel="Popular"
                highLabel="Niche"
            />
            <SliderItem
                label="Recency"
                value={preferences.recency}
                onChange={(val) => onChange('recency', val)}
                description="Importance of publication date"
                lowLabel="All Time"
                highLabel="Latest"
            />
        </div>
    );
};

interface SliderItemProps {
    label: string;
    value: number;
    onChange: (value: number) => void;
    description: string;
    lowLabel: string;
    highLabel: string;
}

const SliderItem = ({ label, value, onChange, description, lowLabel, highLabel }: SliderItemProps) => {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <div className="slider-item">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <label style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{label}</label>
                    <div
                        style={{ position: 'relative', cursor: 'help' }}
                        onMouseEnter={() => setIsHovered(true)}
                        onMouseLeave={() => setIsHovered(false)}
                    >
                        <HelpCircle size={14} color="var(--text-secondary)" />
                        {isHovered && (
                            <div style={{
                                position: 'absolute',
                                bottom: '100%',
                                left: '50%',
                                transform: 'translateX(-50%)',
                                background: 'var(--surface-elevated)',
                                border: '1px solid var(--border)',
                                padding: '8px',
                                borderRadius: '4px',
                                width: '200px',
                                fontSize: '0.75rem',
                                zIndex: 10,
                                marginBottom: '8px',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                            }}>
                                {description}
                            </div>
                        )}
                    </div>
                </div>
                <span style={{
                    color: 'var(--accent)',
                    fontWeight: 600,
                    fontSize: '0.875rem',
                    background: 'var(--surface-subtle)',
                    padding: '2px 8px',
                    borderRadius: '12px'
                }}>
                    {value}%
                </span>
            </div>

            <div style={{ position: 'relative', height: '24px', display: 'flex', alignItems: 'center' }}>
                <input
                    type="range"
                    min="0"
                    max="100"
                    value={value}
                    onChange={(e) => onChange(parseInt(e.target.value))}
                    style={{
                        width: '100%',
                        height: '4px',
                        background: `linear-gradient(to right, var(--accent) ${value}%, var(--surface-subtle) ${value}%)`,
                        borderRadius: '2px',
                        appearance: 'none',
                        outline: 'none',
                        cursor: 'pointer'
                    }}
                />
                <style>{`
          input[type=range]::-webkit-slider-thumb {
            -webkit-appearance: none;
            height: 16px;
            width: 16px;
            border-radius: 50%;
            background: var(--primary-white);
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            border: 2px solid var(--accent);
            margin-top: -6px;
          }
          input[type=range]::-webkit-slider-runnable-track {
            width: 100%;
            height: 4px;
            cursor: pointer;
            background: transparent;
            border-radius: 2px;
          }
        `}</style>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                <span>{lowLabel}</span>
                <span>{highLabel}</span>
            </div>
        </div>
    );
};
