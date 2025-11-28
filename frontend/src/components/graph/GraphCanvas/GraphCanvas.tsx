import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { GraphNode, GraphEdge, GraphLayout, NODE_COLORS, EDGE_COLORS } from '@/types/graph';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  layout: GraphLayout['type'];
  onNodeClick?: (id: string) => void;
  onNodeExpand?: (id: string) => void;
  selectedNodeId?: string;
  highlightedPaths?: string[][];
}

export const GraphCanvas: React.FC<GraphCanvasProps> = ({
  nodes,
  edges,
  layout,
  onNodeClick,
  onNodeExpand,
  selectedNodeId,
  highlightedPaths = [],
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const simulationRef = useRef<d3.Simulation<GraphNode, GraphEdge> | null>(null);

  useEffect(() => {
    const updateDimensions = () => {
      if (svgRef.current) {
        const { width, height } = svgRef.current.getBoundingClientRect();
        setDimensions({ width, height });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const { width, height } = dimensions;

    // Create zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    const g = svg.append('g');

    // Create force simulation
    const simulation = d3.forceSimulation<GraphNode>(nodes)
      .force('link', d3.forceLink<GraphNode, GraphEdge>(edges)
        .id(d => d.id)
        .distance(d => 100 / (d.weight || 1))
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    simulationRef.current = simulation;

    // Check if edge is in highlighted path
    const isEdgeHighlighted = (edge: GraphEdge) => {
      return highlightedPaths.some(path => {
        for (let i = 0; i < path.length - 1; i++) {
          const source = typeof edge.source === 'string' ? edge.source : edge.source.id;
          const target = typeof edge.target === 'string' ? edge.target : edge.target.id;
          if ((path[i] === source && path[i + 1] === target) ||
              (path[i] === target && path[i + 1] === source)) {
            return true;
          }
        }
        return false;
      });
    };

    // Draw edges
    const link = g.append('g')
      .selectAll('line')
      .data(edges)
      .join('line')
      .attr('stroke', d => isEdgeHighlighted(d) ? '#f59e0b' : EDGE_COLORS[d.type])
      .attr('stroke-opacity', d => isEdgeHighlighted(d) ? 1 : 0.6)
      .attr('stroke-width', d => isEdgeHighlighted(d) ? 3 : Math.sqrt(d.weight) * 2)
      .attr('class', d => isEdgeHighlighted(d) ? 'animate-pulse' : '');

    // Draw nodes
    const node = g.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .attr('cursor', 'pointer')
      .call(d3.drag<SVGGElement, GraphNode>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended) as any
      );

    // Node circles
    node.append('circle')
      .attr('r', d => d.id === selectedNodeId ? 12 : 8)
      .attr('fill', d => NODE_COLORS[d.type])
      .attr('stroke', d => d.id === selectedNodeId ? '#fbbf24' : '#fff')
      .attr('stroke-width', d => d.id === selectedNodeId ? 3 : 2);

    // Node labels
    node.append('text')
      .text(d => d.label.length > 20 ? d.label.slice(0, 20) + '...' : d.label)
      .attr('x', 12)
      .attr('y', 4)
      .attr('font-size', '10px')
      .attr('fill', '#374151')
      .attr('class', 'dark:fill-gray-300');

    // Node click handler
    node.on('click', (event, d) => {
      event.stopPropagation();
      onNodeClick?.(d.id);
    });

    // Node double-click to expand
    node.on('dblclick', (event, d) => {
      event.stopPropagation();
      onNodeExpand?.(d.id);
    });

    // Tooltip
    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'graph-tooltip')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background-color', 'rgba(0, 0, 0, 0.8)')
      .style('color', 'white')
      .style('padding', '8px')
      .style('border-radius', '4px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('z-index', '1000');

    node.on('mouseenter', (event, d) => {
      tooltip
        .style('visibility', 'visible')
        .html(`
          <strong>${d.label}</strong><br/>
          Type: ${d.type}<br/>
          ${d.cluster ? `Cluster: ${d.cluster}<br/>` : ''}
          ${Object.keys(d.metadata).length > 0 ? 'Double-click to expand' : ''}
        `);
    });

    node.on('mousemove', (event) => {
      tooltip
        .style('top', (event.pageY - 10) + 'px')
        .style('left', (event.pageX + 10) + 'px');
    });

    node.on('mouseleave', () => {
      tooltip.style('visibility', 'hidden');
    });

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => (d.source as GraphNode).x!)
        .attr('y1', d => (d.source as GraphNode).y!)
        .attr('x2', d => (d.target as GraphNode).x!)
        .attr('y2', d => (d.target as GraphNode).y!);

      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event: any, d: GraphNode) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: GraphNode) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: GraphNode) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    return () => {
      simulation.stop();
      tooltip.remove();
    };
  }, [nodes, edges, dimensions, selectedNodeId, highlightedPaths, onNodeClick, onNodeExpand]);

  const handleZoomIn = () => {
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().scaleBy as any,
      1.3
    );
  };

  const handleZoomOut = () => {
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().scaleBy as any,
      0.7
    );
  };

  const handleResetZoom = () => {
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().transform as any,
      d3.zoomIdentity
    );
  };

  return (
    <div className="relative w-full h-full">
      <svg
        ref={svgRef}
        className="w-full h-full bg-gray-50 dark:bg-gray-900"
      />

      {/* Controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        <button
          onClick={handleZoomIn}
          className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          aria-label="Zoom in"
        >
          <ZoomIn className="w-5 h-5 text-gray-700 dark:text-gray-300" />
        </button>
        <button
          onClick={handleZoomOut}
          className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          aria-label="Zoom out"
        >
          <ZoomOut className="w-5 h-5 text-gray-700 dark:text-gray-300" />
        </button>
        <button
          onClick={handleResetZoom}
          className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          aria-label="Reset zoom"
        >
          <Maximize2 className="w-5 h-5 text-gray-700 dark:text-gray-300" />
        </button>
      </div>

      {/* Mini-map */}
      <div className="absolute bottom-4 right-4 w-32 h-24 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <svg className="w-full h-full">
          <rect width="100%" height="100%" fill="currentColor" className="text-gray-100 dark:text-gray-900" />
          {nodes.map(node => (
            <circle
              key={node.id}
              cx={(node.x || 0) / dimensions.width * 128}
              cy={(node.y || 0) / dimensions.height * 96}
              r="2"
              fill={NODE_COLORS[node.type]}
            />
          ))}
        </svg>
      </div>
    </div>
  );
};
