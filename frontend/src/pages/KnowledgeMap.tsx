// Neo Alexandria 2.0 Frontend - Knowledge Map Page
// Interactive mind-map style visualization of knowledge domains

import React, { useState, useMemo } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useResources, useClassificationTree } from '@/hooks/useApi';
import { 
  Map, 
  Layers, 
  Filter, 
  Search, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw,
  Download,
  Eye,
  EyeOff,
  Star,
  BookOpen,
  Tag
} from 'lucide-react';
import { cn } from '@/utils/cn';

interface KnowledgeMapProps {}

const KnowledgeMap: React.FC<KnowledgeMapProps> = () => {
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'domains' | 'resources' | 'hybrid'>('domains');
  const [zoomLevel, setZoomLevel] = useState(1);
  const [showConnections, setShowConnections] = useState(true);
  const [filterByQuality, setFilterByQuality] = useState(false);

  // Fetch data
  const { data: resourcesData, isLoading: resourcesLoading } = useResources({ limit: 100 });
  const { data: classificationData, isLoading: classificationLoading } = useClassificationTree();

  const isLoading = resourcesLoading || classificationLoading;

  // Process data for map visualization
  const mapData = useMemo(() => {
    if (!resourcesData?.items || !classificationData?.tree) {
      return { domains: [], connections: [] };
    }

    const resources = resourcesData.items;
    const classificationTree = classificationData.tree;

    // Group resources by classification
    const domainMap = new Map();
    
    classificationTree.forEach(domain => {
      const domainResources = resources.filter(r => r.classification_code === domain.code);
      if (domainResources.length > 0) {
        domainMap.set(domain.code, {
          ...domain,
          resources: domainResources,
          resourceCount: domainResources.length,
          avgQuality: domainResources.reduce((sum, r) => sum + r.quality_score, 0) / domainResources.length,
          topics: [...new Set(domainResources.flatMap(r => r.subject || []))],
        });
      }
    });

    // Create connections between domains based on shared topics
    const connections = [];
    const domains = Array.from(domainMap.values());
    
    for (let i = 0; i < domains.length; i++) {
      for (let j = i + 1; j < domains.length; j++) {
        const domain1 = domains[i];
        const domain2 = domains[j];
        const sharedTopics = domain1.topics.filter(topic => 
          domain2.topics.includes(topic)
        );
        
        if (sharedTopics.length > 0) {
          connections.push({
            source: domain1.code,
            target: domain2.code,
            strength: sharedTopics.length / Math.max(domain1.topics.length, domain2.topics.length),
            sharedTopics,
          });
        }
      }
    }

    return { domains, connections };
  }, [resourcesData, classificationData]);

  const handleDomainClick = (domainCode: string) => {
    setSelectedDomain(selectedDomain === domainCode ? null : domainCode);
  };

  const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 0.2, 2));
  const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 0.2, 0.5));
  const handleReset = () => {
    setZoomLevel(1);
    setSelectedDomain(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner text="Loading knowledge map..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">
            Knowledge Map
          </h1>
          <p className="text-secondary-600">
            Explore your knowledge domains and their relationships
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant={viewMode === 'domains' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setViewMode('domains')}
            icon={<Layers className="w-4 h-4" />}
          >
            Domains
          </Button>
          <Button
            variant={viewMode === 'resources' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setViewMode('resources')}
            icon={<BookOpen className="w-4 h-4" />}
          >
            Resources
          </Button>
          <Button
            variant={viewMode === 'hybrid' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setViewMode('hybrid')}
            icon={<Map className="w-4 h-4" />}
          >
            Hybrid
          </Button>
        </div>
      </div>

      {/* Controls */}
      <Card variant="glass">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleZoomOut}
                  icon={<ZoomOut className="w-4 h-4" />}
                />
                <span className="text-sm text-secondary-600 w-16 text-center">
                  {Math.round(zoomLevel * 100)}%
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleZoomIn}
                  icon={<ZoomIn className="w-4 h-4" />}
                />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleReset}
                  icon={<RotateCcw className="w-4 h-4" />}
                />
              </div>

              <div className="flex items-center space-x-2">
                <Button
                  variant={showConnections ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setShowConnections(!showConnections)}
                  icon={showConnections ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                >
                  Connections
                </Button>
                
                <Button
                  variant={filterByQuality ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setFilterByQuality(!filterByQuality)}
                  icon={<Star className="w-4 h-4" />}
                >
                  High Quality
                </Button>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Button variant="glass" size="sm" icon={<Download className="w-4 h-4" />}>
                Export Map
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Map Visualization */}
      <Card variant="glass">
        <CardContent className="p-0">
          <div className="h-[600px] relative rounded-xl overflow-hidden bg-gradient-to-br from-slate-50 to-slate-100">
            <div 
              className="w-full h-full transform transition-transform duration-300"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              <KnowledgeMapVisualization
                data={mapData}
                viewMode={viewMode}
                selectedDomain={selectedDomain}
                showConnections={showConnections}
                filterByQuality={filterByQuality}
                onDomainClick={handleDomainClick}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Map Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="glass">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600 mb-1">
              {mapData.domains.length}
            </div>
            <div className="text-sm text-gray-700">Knowledge Domains</div>
          </CardContent>
        </Card>
        
        <Card variant="glass">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600 mb-1">
              {mapData.domains.reduce((sum, d) => sum + d.resourceCount, 0)}
            </div>
            <div className="text-sm text-gray-700">Total Resources</div>
          </CardContent>
        </Card>
        
        <Card variant="glass">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600 mb-1">
              {mapData.connections.length}
            </div>
            <div className="text-sm text-gray-700">Domain Connections</div>
          </CardContent>
        </Card>
        
        <Card variant="glass">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600 mb-1">
              {mapData.domains.length > 0 ? 
                Math.round(mapData.domains.reduce((sum, d) => sum + d.avgQuality, 0) / mapData.domains.length * 100) : 
                0
              }%
            </div>
            <div className="text-sm text-gray-700">Avg. Quality</div>
          </CardContent>
        </Card>
      </div>

      {/* Selected Domain Details */}
      {selectedDomain && (
        <Card variant="glass">
          <CardHeader>
            <h3 className="text-lg font-semibold">
              {mapData.domains.find(d => d.code === selectedDomain)?.name}
            </h3>
          </CardHeader>
          <CardContent>
            <DomainDetails 
              domain={mapData.domains.find(d => d.code === selectedDomain)!}
              connections={mapData.connections.filter(c => 
                c.source === selectedDomain || c.target === selectedDomain
              )}
              allDomains={mapData.domains}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Knowledge Map Visualization Component
interface KnowledgeMapVisualizationProps {
  data: { domains: any[]; connections: any[] };
  viewMode: 'domains' | 'resources' | 'hybrid';
  selectedDomain: string | null;
  showConnections: boolean;
  filterByQuality: boolean;
  onDomainClick: (domainCode: string) => void;
}

const KnowledgeMapVisualization: React.FC<KnowledgeMapVisualizationProps> = ({
  data,
  viewMode,
  selectedDomain,
  showConnections,
  filterByQuality,
  onDomainClick,
}) => {
  const { domains, connections } = data;

  // Calculate positions for domains in a circular layout
  const positionedDomains = useMemo(() => {
    if (domains.length === 0) return [];

    const centerX = 300;
    const centerY = 300;
    const radius = Math.min(200, 150 + domains.length * 10);

    return domains.map((domain, index) => {
      const angle = (2 * Math.PI * index) / domains.length;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      return {
        ...domain,
        x,
        y,
        size: Math.max(20, Math.min(60, domain.resourceCount * 2)),
      };
    });
  }, [domains]);

  if (domains.length === 0) {
    return (
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <Map className="w-16 h-16 mx-auto mb-4 text-secondary-300" />
          <h3 className="text-lg font-medium text-secondary-900 mb-2">
            No Knowledge Domains Found
          </h3>
          <p className="text-secondary-600">
            Add resources with classifications to see your knowledge map.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full relative">
      {/* SVG for connections */}
      <svg className="absolute inset-0 w-full h-full">
        {showConnections && connections.map((connection, index) => {
          const sourceDomain = positionedDomains.find(d => d.code === connection.source);
          const targetDomain = positionedDomains.find(d => d.code === connection.target);
          
          if (!sourceDomain || !targetDomain) return null;

          return (
            <line
              key={index}
              x1={sourceDomain.x}
              y1={sourceDomain.y}
              x2={targetDomain.x}
              y2={targetDomain.y}
              stroke="rgba(59, 130, 246, 0.4)"
              strokeWidth={Math.max(1, connection.strength * 3)}
              className="transition-opacity duration-200"
            />
          );
        })}
      </svg>

      {/* Domain nodes */}
      {positionedDomains.map((domain) => {
        const isSelected = selectedDomain === domain.code;
        const isHighQuality = domain.avgQuality > 0.7;
        const shouldShow = !filterByQuality || isHighQuality;

        if (!shouldShow) return null;

        return (
          <div
            key={domain.code}
            className={cn(
              "absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-200",
              "hover:scale-110",
              isSelected && "scale-110"
            )}
            style={{
              left: domain.x,
              top: domain.y,
              width: domain.size,
              height: domain.size,
            }}
            onClick={() => onDomainClick(domain.code)}
          >
            <div
              className={cn(
                "w-full h-full rounded-full flex items-center justify-center text-white font-medium text-xs shadow-lg",
                isSelected 
                  ? "bg-primary-600 ring-4 ring-primary-200" 
                  : isHighQuality 
                    ? "bg-green-500" 
                    : "bg-blue-500"
              )}
            >
              {domain.code}
            </div>
            
            {/* Domain label */}
            <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 text-center">
              <div className="bg-white rounded px-2 py-1 shadow-sm border text-xs font-medium text-gray-900 whitespace-nowrap">
                {domain.name}
              </div>
              <div className="text-xs text-gray-700 mt-1">
                {domain.resourceCount} resources
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

// Domain Details Component
interface DomainDetailsProps {
  domain: any;
  connections: any[];
  allDomains: any[];
}

const DomainDetails: React.FC<DomainDetailsProps> = ({ domain, connections, allDomains }) => {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 className="font-medium text-gray-900 mb-2">Domain Information</h4>
          <div className="space-y-2 text-sm text-gray-800">
            <div><span className="font-medium text-gray-900">Code:</span> {domain.code}</div>
            <div><span className="font-medium text-gray-900">Resources:</span> {domain.resourceCount}</div>
            <div><span className="font-medium text-gray-900">Avg. Quality:</span> {Math.round(domain.avgQuality * 100)}%</div>
            <div><span className="font-medium text-gray-900">Topics:</span> {domain.topics.length}</div>
          </div>
        </div>

        <div>
          <h4 className="font-medium text-gray-900 mb-2">Connected Domains</h4>
          <div className="space-y-1 text-sm">
            {connections.length > 0 ? (
              connections.map((conn, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-gray-700">
                    {conn.source === domain.code ? 
                      allDomains.find(d => d.code === conn.target)?.name || 'Unknown' :
                      allDomains.find(d => d.code === conn.source)?.name || 'Unknown'
                    }
                  </span>
                  <span className="text-blue-600 font-medium">
                    {Math.round(conn.strength * 100)}%
                  </span>
                </div>
              ))
            ) : (
              <div className="text-gray-600">No connections found</div>
            )}
          </div>
        </div>
      </div>

      {domain.topics.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-900 mb-2">Key Topics</h4>
          <div className="flex flex-wrap gap-2">
            {domain.topics.slice(0, 10).map((topic: string, index: number) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
              >
                <Tag className="w-3 h-3 mr-1" />
                {topic}
              </span>
            ))}
            {domain.topics.length > 10 && (
              <span className="text-xs text-gray-600">
                +{domain.topics.length - 10} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export { KnowledgeMap };
