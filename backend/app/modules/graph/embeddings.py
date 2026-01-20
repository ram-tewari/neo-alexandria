"""
Graph Embeddings Service for Phase 16.7 - Task 11

Implements Node2Vec and DeepWalk embeddings for citation graph analysis.
Provides embedding generation, storage, retrieval, and similarity search.

Note: Uses custom implementation compatible with Python 3.13 instead of node2vec package.
"""

import logging
import time
import random
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID

logger = logging.getLogger(__name__)


class GraphEmbeddingsService:
    """Service for computing and managing graph embeddings."""

    def __init__(self, db: Session):
        self.db = db
        self.embeddings_cache: Dict[str, List[float]] = {}
        self._graph_cache = None

    def _build_networkx_graph(self):
        """Build NetworkX graph from citation data."""
        try:
            import networkx as nx
        except ImportError:
            raise ImportError(
                "NetworkX is required for graph embeddings. Install with: pip install networkx"
            )

        from app.database.models import Citation, Resource

        G = nx.DiGraph()

        # Query all citations
        citations = self.db.query(Citation).all()

        # Add edges from citations
        for citation in citations:
            if citation.source_resource_id and citation.target_resource_id:
                G.add_edge(
                    str(citation.source_resource_id), str(citation.target_resource_id)
                )

        # Add isolated nodes (resources without citations)
        resources = self.db.query(Resource).all()
        for resource in resources:
            node_id = str(resource.id)
            if node_id not in G:
                G.add_node(node_id)

        logger.info(
            f"Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges"
        )
        return G

    def _generate_random_walks(
        self, G, num_walks: int, walk_length: int, p: float = 1.0, q: float = 1.0
    ) -> List[List[str]]:
        """
        Generate random walks using Node2Vec biased random walk strategy.

        Args:
            G: NetworkX graph
            num_walks: Number of walks per node
            walk_length: Length of each walk
            p: Return parameter (likelihood of returning to previous node)
            q: In-out parameter (likelihood of exploring outward)

        Returns:
            List of walks, where each walk is a list of node IDs
        """
        walks = []
        nodes = list(G.nodes())

        for _ in range(num_walks):
            random.shuffle(nodes)
            for node in nodes:
                walk = self._node2vec_walk(G, node, walk_length, p, q)
                if len(walk) > 1:  # Only include walks with at least 2 nodes
                    walks.append(walk)

        logger.info(f"Generated {len(walks)} random walks")
        return walks

    def _node2vec_walk(
        self, G, start_node: str, walk_length: int, p: float, q: float
    ) -> List[str]:
        """
        Perform a single biased random walk from start_node.

        Args:
            G: NetworkX graph
            start_node: Starting node
            walk_length: Maximum walk length
            p: Return parameter
            q: In-out parameter

        Returns:
            List of node IDs in the walk
        """
        walk = [start_node]

        while len(walk) < walk_length:
            cur = walk[-1]
            neighbors = list(G.neighbors(cur))

            if len(neighbors) == 0:
                break

            if len(walk) == 1:
                # First step: uniform random
                walk.append(random.choice(neighbors))
            else:
                # Biased random walk based on p and q
                prev = walk[-2]
                next_node = self._biased_choice(G, cur, prev, neighbors, p, q)
                walk.append(next_node)

        return walk

    def _biased_choice(
        self, G, cur: str, prev: str, neighbors: List[str], p: float, q: float
    ) -> str:
        """
        Choose next node based on Node2Vec bias.

        Args:
            G: NetworkX graph
            cur: Current node
            prev: Previous node
            neighbors: List of neighbor nodes
            p: Return parameter
            q: In-out parameter

        Returns:
            Selected next node
        """
        # Calculate unnormalized probabilities
        probs = []
        for neighbor in neighbors:
            if neighbor == prev:
                # Return to previous node
                probs.append(1.0 / p)
            elif G.has_edge(prev, neighbor):
                # Common neighbor (distance 1 from prev)
                probs.append(1.0)
            else:
                # Explore outward (distance 2 from prev)
                probs.append(1.0 / q)

        # Normalize probabilities
        total = sum(probs)
        probs = [prob / total for prob in probs]

        # Choose based on probabilities
        return random.choices(neighbors, weights=probs)[0]

    def compute_node2vec_embeddings(
        self,
        dimensions: int = 128,
        walk_length: int = 80,
        num_walks: int = 10,
        p: float = 1.0,
        q: float = 1.0,
        window: int = 10,
        min_count: int = 1,
        workers: int = 4,
    ) -> Dict[str, Any]:
        """
        Compute Node2Vec embeddings for the citation graph.

        Uses custom implementation with gensim Word2Vec for Python 3.13 compatibility.

        Args:
            dimensions: Embedding dimensionality (default: 128)
            walk_length: Length of random walks (default: 80)
            num_walks: Number of walks per node (default: 10)
            p: Return parameter (default: 1.0)
            q: In-out parameter (default: 1.0)
            window: Context window size (default: 10)
            min_count: Minimum word count (default: 1)
            workers: Number of worker threads (default: 4)

        Returns:
            Dict with status, embeddings_computed, dimensions, and execution_time
        """
        start_time = time.time()

        try:
            from gensim.models import Word2Vec
        except ImportError:
            raise ImportError(
                "gensim is required for graph embeddings. Install with: pip install gensim"
            )

        # Build NetworkX graph
        G = self._build_networkx_graph()

        if G.number_of_nodes() == 0:
            logger.warning("Graph has no nodes, cannot compute embeddings")
            return {
                "status": "error",
                "message": "Graph has no nodes",
                "embeddings_computed": 0,
                "dimensions": dimensions,
                "execution_time": 0.0,
            }

        # Generate random walks
        logger.info(f"Generating random walks with p={p}, q={q}")
        walks = self._generate_random_walks(G, num_walks, walk_length, p, q)

        if len(walks) == 0:
            logger.warning("No walks generated, cannot compute embeddings")
            return {
                "status": "error",
                "message": "No walks generated",
                "embeddings_computed": 0,
                "dimensions": dimensions,
                "execution_time": 0.0,
            }

        # Train Word2Vec model
        logger.info(f"Training Word2Vec model with dimensions={dimensions}")
        model = Word2Vec(
            sentences=walks,
            vector_size=dimensions,
            window=window,
            min_count=min_count,
            workers=workers,
            sg=1,  # Skip-gram
            hs=0,  # Negative sampling
            negative=5,
            epochs=5,
        )

        # Extract embeddings
        embeddings = {}
        for node in G.nodes():
            try:
                embeddings[node] = model.wv[node].tolist()
            except KeyError:
                # Node not in vocabulary (isolated node with no walks)
                logger.warning(f"Node {node} not in vocabulary, using zero vector")
                embeddings[node] = [0.0] * dimensions

        # Cache embeddings
        self.embeddings_cache.update(embeddings)

        # Store in database
        self._store_embeddings(embeddings, algorithm="node2vec")

        execution_time = time.time() - start_time
        logger.info(
            f"Node2Vec embeddings computed in {execution_time:.2f}s for {len(embeddings)} nodes"
        )

        return {
            "status": "success",
            "embeddings_computed": len(embeddings),
            "dimensions": dimensions,
            "execution_time": execution_time,
            "algorithm": "node2vec",
            "parameters": {
                "p": p,
                "q": q,
                "walk_length": walk_length,
                "num_walks": num_walks,
            },
        }

    def compute_deepwalk_embeddings(
        self,
        dimensions: int = 128,
        walk_length: int = 80,
        num_walks: int = 10,
        window: int = 10,
        min_count: int = 1,
        workers: int = 4,
    ) -> Dict[str, Any]:
        """
        Compute DeepWalk embeddings (Node2Vec with p=1, q=1).

        Args:
            dimensions: Embedding dimensionality (default: 128)
            walk_length: Length of random walks (default: 80)
            num_walks: Number of walks per node (default: 10)
            window: Context window size (default: 10)
            min_count: Minimum word count (default: 1)
            workers: Number of worker threads (default: 4)

        Returns:
            Dict with status, embeddings_computed, dimensions, and execution_time
        """
        logger.info("Computing DeepWalk embeddings (Node2Vec with p=1, q=1)")
        result = self.compute_node2vec_embeddings(
            dimensions=dimensions,
            walk_length=walk_length,
            num_walks=num_walks,
            p=1.0,
            q=1.0,
            window=window,
            min_count=min_count,
            workers=workers,
        )
        result["algorithm"] = "deepwalk"
        return result

    def _store_embeddings(
        self, embeddings: Dict[str, List[float]], algorithm: str = "node2vec"
    ) -> None:
        """
        Store embeddings in database.

        Args:
            embeddings: Dictionary mapping node IDs to embedding vectors
            algorithm: Algorithm used to generate embeddings
        """
        from app.database.models import Resource

        for node_id, embedding in embeddings.items():
            try:
                # Convert string UUID to UUID object
                resource_id = UUID(node_id)

                # Update resource with graph embedding
                resource = (
                    self.db.query(Resource).filter(Resource.id == resource_id).first()
                )
                if resource:
                    # Store as JSON in a graph_embedding field (if it exists)
                    # For now, we'll store in cache only
                    # In production, you might want to add a graph_embedding column to Resource
                    pass

            except (ValueError, AttributeError) as e:
                logger.warning(f"Could not store embedding for node {node_id}: {e}")
                continue

        logger.info(f"Stored {len(embeddings)} embeddings in cache")

    def get_embedding(self, resource_id: UUID) -> Optional[List[float]]:
        """
        Get embedding for a resource.

        Args:
            resource_id: UUID of the resource

        Returns:
            Embedding vector or None if not found
        """
        node_id = str(resource_id)

        # Check cache first
        if node_id in self.embeddings_cache:
            return self.embeddings_cache[node_id]

        # Could query from database here if embeddings are persisted
        logger.debug(f"Embedding not found for resource {resource_id}")
        return None

    def find_similar_nodes(
        self, resource_id: UUID, limit: int = 10, min_similarity: float = 0.0
    ) -> List[Tuple[str, float]]:
        """
        Find similar nodes using embedding similarity.

        Args:
            resource_id: UUID of the source resource
            limit: Maximum number of similar nodes to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of (node_id, similarity_score) tuples, sorted by similarity descending
        """
        target_embedding = self.get_embedding(resource_id)

        if target_embedding is None:
            logger.warning(f"No embedding found for resource {resource_id}")
            return []

        similarities = []
        node_id = str(resource_id)

        # Compute cosine similarity with all other nodes
        for other_id, other_embedding in self.embeddings_cache.items():
            if other_id != node_id:
                similarity = self._cosine_similarity(target_embedding, other_embedding)
                if similarity >= min_similarity:
                    similarities.append((other_id, similarity))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:limit]

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Compute cosine similarity between two vectors.

        Args:
            vec_a: First vector
            vec_b: Second vector

        Returns:
            Cosine similarity in range [-1, 1]
        """
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0

        try:
            import numpy as np

            a = np.array(vec_a, dtype=np.float32)
            b = np.array(vec_b, dtype=np.float32)

            # Check for zero vectors
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)

            if norm_a == 0.0 or norm_b == 0.0:
                return 0.0

            # Compute cosine similarity
            dot_product = np.dot(a, b)
            similarity = dot_product / (norm_a * norm_b)

            # Ensure result is in valid range
            return float(np.clip(similarity, -1.0, 1.0))

        except ImportError:
            # Fallback to manual computation
            dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
            norm_a = sum(a * a for a in vec_a) ** 0.5
            norm_b = sum(b * b for b in vec_b) ** 0.5

            if norm_a == 0.0 or norm_b == 0.0:
                return 0.0

            similarity = dot_product / (norm_a * norm_b)
            return max(-1.0, min(1.0, similarity))

    def update_embeddings_incremental(
        self,
        affected_node_ids: List[str],
        dimensions: int = 128,
        algorithm: str = "node2vec",
    ) -> Dict[str, Any]:
        """
        Update embeddings incrementally for affected nodes.

        This is a simplified implementation that recomputes all embeddings.
        A more sophisticated approach would only recompute affected subgraphs.

        Args:
            affected_node_ids: List of node IDs that were affected by graph changes
            dimensions: Embedding dimensionality
            algorithm: Algorithm to use ("node2vec" or "deepwalk")

        Returns:
            Dict with status and update information
        """
        logger.info(f"Incremental update requested for {len(affected_node_ids)} nodes")
        logger.info("Recomputing all embeddings (full recomputation)")

        # For now, recompute all embeddings
        # In production, you might want to implement true incremental updates
        if algorithm == "deepwalk":
            result = self.compute_deepwalk_embeddings(dimensions=dimensions)
        else:
            result = self.compute_node2vec_embeddings(dimensions=dimensions)

        result["update_type"] = "full_recomputation"
        result["affected_nodes"] = len(affected_node_ids)

        return result

    def clear_cache(self) -> None:
        """Clear the embeddings cache."""
        self.embeddings_cache.clear()
        logger.info("Embeddings cache cleared")
