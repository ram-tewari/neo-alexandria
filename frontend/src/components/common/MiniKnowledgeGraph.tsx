import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import './MiniKnowledgeGraph.css';

interface Node {
  id: number;
  x: number;
  y: number;
  radius: number;
  color: string;
  vx: number;
  vy: number;
}

interface Connection {
  from: number;
  to: number;
}

export const MiniKnowledgeGraph = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      const container = canvas.parentElement;
      if (container) {
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
      }
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Create nodes
    const nodes: Node[] = [];
    const nodeCount = 12;
    // Use hex colors that work with canvas
    const colors = [
      '#8b5cf6', // Purple accent
      '#ec4899', // Pink
      '#3b82f6', // Blue  
      '#06b6d4'  // Cyan
    ];

    for (let i = 0; i < nodeCount; i++) {
      nodes.push({
        id: i,
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 8 + 6,
        color: colors[Math.floor(Math.random() * colors.length)],
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
      });
    }

    // Create connections
    const connections: Connection[] = [];
    for (let i = 0; i < nodeCount; i++) {
      const connectionCount = Math.floor(Math.random() * 3) + 1;
      for (let j = 0; j < connectionCount; j++) {
        const target = Math.floor(Math.random() * nodeCount);
        if (target !== i) {
          connections.push({ from: i, to: target });
        }
      }
    }

    let animationId: number;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Update node positions
      nodes.forEach((node) => {
        node.x += node.vx;
        node.y += node.vy;

        // Bounce off edges
        if (node.x + node.radius > canvas.width || node.x - node.radius < 0) {
          node.vx = -node.vx;
        }
        if (node.y + node.radius > canvas.height || node.y - node.radius < 0) {
          node.vy = -node.vy;
        }

        // Keep within bounds
        node.x = Math.max(node.radius, Math.min(canvas.width - node.radius, node.x));
        node.y = Math.max(node.radius, Math.min(canvas.height - node.radius, node.y));
      });

      // Draw connections
      connections.forEach((conn) => {
        const from = nodes[conn.from];
        const to = nodes[conn.to];
        const distance = Math.sqrt(
          Math.pow(to.x - from.x, 2) + Math.pow(to.y - from.y, 2)
        );

        if (distance < 200) {
          ctx.beginPath();
          ctx.moveTo(from.x, from.y);
          ctx.lineTo(to.x, to.y);
          ctx.strokeStyle = `rgba(168, 85, 247, ${0.15 * (1 - distance / 200)})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      });

      // Draw nodes
      nodes.forEach((node) => {
        // Outer glow
        const gradient = ctx.createRadialGradient(
          node.x,
          node.y,
          0,
          node.x,
          node.y,
          node.radius * 2
        );
        // Convert hex to rgba for gradient
        const r = parseInt(node.color.slice(1, 3), 16);
        const g = parseInt(node.color.slice(3, 5), 16);
        const b = parseInt(node.color.slice(5, 7), 16);
        gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, 0.25)`);
        gradient.addColorStop(1, 'transparent');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius * 2, 0, Math.PI * 2);
        ctx.fill();

        // Node
        ctx.fillStyle = node.color;
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fill();

        // Inner highlight
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.beginPath();
        ctx.arc(node.x - node.radius * 0.3, node.y - node.radius * 0.3, node.radius * 0.4, 0, Math.PI * 2);
        ctx.fill();
      });

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <motion.div
      className="mini-knowledge-graph"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <canvas ref={canvasRef} className="graph-canvas" />
      <div className="graph-overlay">
        <h3>Knowledge Network</h3>
        <p>Interactive visualization of connected resources</p>
      </div>
    </motion.div>
  );
};
