import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { profileApi, UserProfile } from '@/lib/api/profile';
import { InterestTagsEditor } from './InterestTagsEditor';
import { PreferenceSliders } from './PreferenceSliders';
import { RecommendationsMetricsPanel } from './RecommendationsMetricsPanel';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/common/Button';
import { useToast } from '@/contexts/ToastContext';
import { Save, User, Sparkles } from 'lucide-react';
import { pageVariants } from '@/animations/variants';
import { GradientOrbs } from '@/components/background/GradientOrbs';

export const ProfilePage = () => {
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const { showToast } = useToast();

    // Mock suggestions
    const tagSuggestions = ['Machine Learning', 'React', 'System Design', 'History', 'Physics', 'UX Design'];
    const domainSuggestions = ['Computer Science', 'Mathematics', 'Biology', 'Economics', 'Psychology'];

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                // Mock delay
                await new Promise(resolve => setTimeout(resolve, 800));
                const data = await profileApi.getProfile();
                setProfile(data);
            } catch (err) {
                console.error('Failed to load profile:', err);
                showToast({ message: 'Failed to load profile', variant: 'error' });
            } finally {
                setIsLoading(false);
            }
        };

        fetchProfile();
    }, [showToast]);

    const handleSave = async () => {
        if (!profile) return;

        setIsSaving(true);
        try {
            await profileApi.updateProfile({
                interest_tags: profile.interest_tags,
                research_domains: profile.research_domains,
                preferences: profile.preferences
            });
            showToast({ message: 'Profile updated successfully', variant: 'success' });
        } catch (err) {
            console.error('Failed to update profile:', err);
            showToast({ message: 'Failed to update profile', variant: 'error' });
        } finally {
            setIsSaving(false);
        }
    };

    const updatePreferences = useCallback((key: 'diversity' | 'novelty' | 'recency', value: number) => {
        setProfile(prev => prev ? ({
            ...prev,
            preferences: {
                ...prev.preferences,
                [key]: value
            }
        }) : null);
    }, []);

    if (isLoading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                minHeight: '80vh'
            }}>
                <LoadingSpinner size="lg" />
            </div>
        );
    }

    if (!profile) return null;

    return (
        <motion.div
            className="profile-page"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            style={{ paddingBottom: '4rem' }}
        >
            <GradientOrbs />

            <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 2rem' }}>
                <div className="page-header" style={{ marginBottom: '3rem', paddingTop: '2rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <h1 style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--primary-white)', marginBottom: '0.5rem' }}>
                                Profile & Preferences
                            </h1>
                            <p style={{ color: 'var(--text-secondary)' }}>
                                Manage your identity and tune your recommendation engine.
                            </p>
                        </div>
                        <div style={{ minWidth: '120px' }}>
                            <Button
                                variant="primary"
                                onClick={handleSave}
                                disabled={isSaving}
                            >
                                {isSaving ? <LoadingSpinner size="sm" /> : (
                                    <>
                                        <Save size={18} style={{ marginRight: '8px' }} />
                                        Save Changes
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '3rem' }}>
                    {/* Left Column: Settings */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}>

                        {/* Identity Section */}
                        <section>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--primary-white)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <User color="var(--accent)" />
                                Identity
                            </h2>
                            <div style={{
                                background: 'var(--surface-card)',
                                padding: '2rem',
                                borderRadius: 'var(--radius-lg)',
                                border: '1px solid var(--border)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '2rem'
                            }}>
                                <div style={{
                                    width: '80px',
                                    height: '80px',
                                    borderRadius: '50%',
                                    background: 'var(--surface-elevated)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    border: '2px solid var(--accent)'
                                }}>
                                    <User size={40} color="var(--text-secondary)" />
                                </div>
                                <div>
                                    <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                                        {profile.name}
                                    </h3>
                                    <p style={{ color: 'var(--text-secondary)' }}>{profile.email}</p>
                                </div>
                            </div>
                        </section>

                        {/* Interests Section */}
                        <section>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--primary-white)', marginBottom: '1.5rem' }}>
                                Interests & Domains
                            </h2>
                            <div style={{
                                background: 'var(--surface-card)',
                                padding: '2rem',
                                borderRadius: 'var(--radius-lg)',
                                border: '1px solid var(--border)',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '2rem'
                            }}>
                                <InterestTagsEditor
                                    label="Research Domains"
                                    tags={profile.research_domains}
                                    onChange={(tags) => setProfile({ ...profile, research_domains: tags })}
                                    suggestions={domainSuggestions}
                                    placeholder="Add a domain (e.g. Computer Science)"
                                />
                                <InterestTagsEditor
                                    label="Specific Interests"
                                    tags={profile.interest_tags}
                                    onChange={(tags) => setProfile({ ...profile, interest_tags: tags })}
                                    suggestions={tagSuggestions}
                                    placeholder="Add an interest (e.g. Neural Networks)"
                                />
                            </div>
                        </section>

                        {/* Tuning Section */}
                        <section>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--primary-white)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <Sparkles color="var(--accent)" />
                                Discovery Tuning
                            </h2>
                            <div style={{
                                background: 'var(--surface-card)',
                                padding: '2rem',
                                borderRadius: 'var(--radius-lg)',
                                border: '1px solid var(--border)'
                            }}>
                                <PreferenceSliders
                                    preferences={profile.preferences}
                                    onChange={updatePreferences}
                                />
                            </div>
                        </section>
                    </div>

                    {/* Right Column: Preview & Metrics */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

                        {/* Live Preview Panel */}
                        <div style={{
                            background: 'var(--surface-elevated)',
                            padding: '1.5rem',
                            borderRadius: 'var(--radius-lg)',
                            border: '1px solid var(--border)',
                            position: 'sticky',
                            top: '2rem'
                        }}>
                            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--primary-white)', marginBottom: '1rem' }}>
                                Live Preview
                            </h3>
                            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                                Based on your current settings, your feed will look like:
                            </p>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                <div style={{
                                    padding: '1rem',
                                    background: 'var(--surface-subtle)',
                                    borderRadius: 'var(--radius-md)',
                                    borderLeft: '3px solid var(--accent)'
                                }}>
                                    <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
                                        {profile.preferences.diversity > 70 ? 'Highly Diverse Mix' : 'Focused Topics'}
                                    </div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                        {profile.preferences.diversity > 70
                                            ? 'Expect resources from adjacent fields and new domains.'
                                            : 'Strictly aligned with your specific interest tags.'}
                                    </div>
                                </div>

                                <div style={{
                                    padding: '1rem',
                                    background: 'var(--surface-subtle)',
                                    borderRadius: 'var(--radius-md)',
                                    borderLeft: '3px solid var(--secondary)'
                                }}>
                                    <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
                                        {profile.preferences.novelty > 70 ? 'Hidden Gems' : 'Popular Hits'}
                                    </div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                        {profile.preferences.novelty > 70
                                            ? 'Surfacing less-cited but high-potential papers.'
                                            : 'Focusing on highly-cited, established works.'}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Metrics Panel */}
                        <div style={{
                            background: 'var(--surface-elevated)',
                            padding: '1.5rem',
                            borderRadius: 'var(--radius-lg)',
                            border: '1px solid var(--border)'
                        }}>
                            <RecommendationsMetricsPanel />
                        </div>

                    </div>
                </div>
            </div>
        </motion.div>
    );
};
