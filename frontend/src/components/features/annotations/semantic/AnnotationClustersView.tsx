import React, { useState } from 'react';
import type { AnnotationCluster } from '../../../../types/annotations';
import './AnnotationClustersView.css';

interface AnnotationClustersViewProps {
    clusters: AnnotationCluster[];
    onClusterSelect?: (clusterId: string | null) => void;
}

/**
 * AnnotationClustersView - Simple cluster visualization
 * 
 * Features:
 * - Display clusters as color-coded groups
 * - Each cluster shows topic label and annotation count
 * - Click cluster to filter results
 * - Visual grouping using cards
 * - Legend showing cluster colors
 */
export const AnnotationClustersView: React.FC<AnnotationClustersViewProps> = ({
    clusters,
    onClusterSelect,
}) => {
    const [selectedCluster, setSelectedCluster] = useState<string | null>(null);

    const handleClusterClick = (clusterId: string) => {
        const newSelection = selectedCluster === clusterId ? null : clusterId;
        setSelectedCluster(newSelection);
        onClusterSelect?.(newSelection);
    };

    if (clusters.length === 0) return null;

    return (
        <div className="annotation-clusters-view">
            <h3 className="annotation-clusters-title">Concept Clusters</h3>
            <div className="annotation-clusters-grid">
                {clusters.map((cluster) => (
                    <div
                        key={cluster.id}
                        className={`annotation-cluster-card ${selectedCluster === cluster.id ? 'active' : ''
                            }`}
                        onClick={() => handleClusterClick(cluster.id)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                handleClusterClick(cluster.id);
                            }
                        }}
                        style={{ borderColor: cluster.color }}
                    >
                        <div className="annotation-cluster-label">{cluster.label}</div>
                        <div className="annotation-cluster-keywords">
                            {cluster.topicKeywords.slice(0, 3).join(', ')}
                        </div>
                        <div className="annotation-cluster-count">
                            {cluster.annotationCount} annotation{cluster.annotationCount !== 1 ? 's' : ''}
                        </div>
                    </div>
                ))}
            </div>
            <div className="annotation-clusters-legend">
                Click a cluster to filter results by topic
            </div>
        </div>
    );
};
