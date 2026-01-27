"""
Retrieval Quality Audit Script (Fixed for Current API)

This script evaluates retrieval quality using annotation ground truth.
It tests FTS, Vector, and Hybrid search methods against synthetic data.

Usage:
    python scripts/audit_retrieval_fixed.py --sample-size 100
"""

import sys
import json
import argparse
import random
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Any
from collections import defaultdict

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text, or_
from sqlalchemy.orm import sessionmaker, Session

# Model imports
from app.database.models import Resource, Annotation


class RetrievalAuditor:
    """
    Auditor for comparing retrieval methods using annotation ground truth.
    
    Ground Truth Logic:
    - Query: Annotation highlighted_text (what user highlighted/noted)
    - Target: Resource the annotation belongs to
    - Success: Target resource appears in top-K results
    """
    
    def __init__(self, db: Session, sample_size: int = 100):
        """
        Initialize auditor.
        
        Args:
            db: Database session
            sample_size: Number of annotations to sample for evaluation
        """
        self.db = db
        self.sample_size = sample_size
        self.results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "sample_size": sample_size,
                "database": str(db.bind.url)
            },
            "methods": {}
        }
    
    def _get_annotation_samples(self) -> List[Tuple[str, str, str]]:
        """
        Fetch random annotation samples as ground truth queries.
        
        Returns:
            List of (annotation_id, annotation_text, target_resource_id) tuples
        """
        print("\n" + "=" * 80)
        print("STEP 1: Fetching Annotation Samples")
        print("=" * 80)
        
        # Count total annotations with non-empty highlighted_text
        total_annotations = (
            self.db.query(Annotation)
            .filter(Annotation.highlighted_text.isnot(None))
            .filter(Annotation.highlighted_text != "")
            .filter(Annotation.resource_id.isnot(None))
            .count()
        )
        
        print(f"Total annotations with text: {total_annotations}")
        
        if total_annotations == 0:
            raise ValueError(
                "No annotations found in database. "
                "Run 'python scripts/seed_audit_data_simple.py' first."
            )
        
        # Adjust sample size if needed
        actual_sample_size = min(self.sample_size, total_annotations)
        if actual_sample_size < self.sample_size:
            print(f"[WARN] Reducing sample size from {self.sample_size} to {actual_sample_size}")
        
        # Fetch all annotations
        all_annotations = (
            self.db.query(Annotation)
            .filter(Annotation.highlighted_text.isnot(None))
            .filter(Annotation.highlighted_text != "")
            .filter(Annotation.resource_id.isnot(None))
            .all()
        )
        
        # Random sample
        sampled = random.sample(all_annotations, actual_sample_size)
        
        samples = [
            (str(ann.id), ann.highlighted_text, str(ann.resource_id))
            for ann in sampled
        ]
        
        avg_length = sum(len(text) for _, text, _ in samples) / len(samples)
        print(f"[OK] Sampled {len(samples)} annotations")
        print(f"  Average text length: {avg_length:.1f} chars")
        
        return samples
    
    def _evaluate_method(
        self,
        method_name: str,
        samples: List[Tuple[str, str, str]],
        search_func: callable
    ) -> Dict[str, Any]:
        """
        Evaluate a search method using annotation samples.
        
        Args:
            method_name: Name of the method being evaluated
            samples: List of (ann_id, query_text, target_resource_id) tuples
            search_func: Function that takes query_text and returns list of resource IDs
        
        Returns:
            Dictionary with evaluation metrics
        """
        print(f"\n{'=' * 80}")
        print(f"EVALUATING: {method_name}")
        print(f"{'=' * 80}")
        
        hits_at_5 = 0
        hits_at_10 = 0
        reciprocal_ranks = []
        latencies = []
        errors = 0
        
        for idx, (ann_id, query_text, target_id) in enumerate(samples, 1):
            if idx % 10 == 0:
                print(f"  Progress: {idx}/{len(samples)}")
            
            try:
                # Execute search and measure latency
                start_time = datetime.now()
                result_ids = search_func(query_text)
                latency_ms = (datetime.now() - start_time).total_seconds() * 1000
                latencies.append(latency_ms)
                
                # Check if target is in results
                if target_id in result_ids[:5]:
                    hits_at_5 += 1
                if target_id in result_ids[:10]:
                    hits_at_10 += 1
                
                # Calculate reciprocal rank
                try:
                    rank = result_ids.index(target_id) + 1
                    reciprocal_ranks.append(1.0 / rank)
                except ValueError:
                    reciprocal_ranks.append(0.0)
                    
            except Exception as e:
                errors += 1
                if errors <= 3:  # Only print first 3 errors
                    print(f"  [WARN] Error on query {idx}: {str(e)}")
        
        # Calculate metrics
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
        recall_at_5 = hits_at_5 / len(samples) if samples else 0.0
        recall_at_10 = hits_at_10 / len(samples) if samples else 0.0
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        
        print(f"\n[OK] {method_name} Evaluation Complete")
        print(f"  MRR: {mrr:.4f}")
        print(f"  Recall@5: {recall_at_5:.4f} ({hits_at_5}/{len(samples)})")
        print(f"  Recall@10: {recall_at_10:.4f} ({hits_at_10}/{len(samples)})")
        print(f"  Avg Latency: {avg_latency:.1f}ms")
        if errors > 0:
            print(f"  [WARN] Errors: {errors}/{len(samples)}")
        
        return {
            "mrr": mrr,
            "recall_at_5": recall_at_5,
            "recall_at_10": recall_at_10,
            "hits_at_5": hits_at_5,
            "hits_at_10": hits_at_10,
            "avg_latency_ms": avg_latency,
            "errors": errors,
            "total_queries": len(samples)
        }
    
    def _search_basic(self, query_text: str) -> List[str]:
        """Execute basic search (FTS-based)."""
        # Direct FTS search implementation to avoid circular imports
        try:
            dialect_name = self.db.bind.dialect.name
            
            if dialect_name == "sqlite":
                # SQLite LIKE search
                results = (
                    self.db.query(Resource)
                    .filter(
                        or_(
                            Resource.title.ilike(f"%{query_text}%"),
                            Resource.description.ilike(f"%{query_text}%"),
                        )
                    )
                    .limit(10)
                    .all()
                )
                return [str(r.id) for r in results]
            
            elif dialect_name == "postgresql":
                # PostgreSQL tsvector search
                sql = text("""
                    SELECT id
                    FROM resources
                    WHERE to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, ''))
                        @@ plainto_tsquery('english', :query)
                    ORDER BY ts_rank(
                        to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, '')),
                        plainto_tsquery('english', :query)
                    ) DESC
                    LIMIT 10
                """)
                result = self.db.execute(sql, {"query": query_text})
                return [str(row[0]) for row in result]
            
            else:
                # Fallback
                results = (
                    self.db.query(Resource)
                    .filter(
                        or_(
                            Resource.title.ilike(f"%{query_text}%"),
                            Resource.description.ilike(f"%{query_text}%"),
                        )
                    )
                    .limit(10)
                    .all()
                )
                return [str(r.id) for r in results]
        
        except Exception as e:
            print(f"  ⚠️  FTS search error: {e}")
            return []
    
    def _search_hybrid(self, query_text: str) -> List[str]:
        """Execute hybrid search (FTS + Dense Vector)."""
        try:
            # Get FTS results
            fts_results = self._execute_fts_search(query_text, limit=100)
            
            # Get dense vector results
            dense_results = self._execute_dense_search(query_text, limit=100)
            
            # Merge with RRF (simple 50/50 weighting)
            from app.modules.search.rrf import ReciprocalRankFusionService
            rrf_service = ReciprocalRankFusionService(k=60)
            merged = rrf_service.fuse([fts_results, dense_results], weights=[0.5, 0.5])
            
            # Return top 10 resource IDs
            return [resource_id for resource_id, _ in merged[:10]]
        
        except Exception as e:
            print(f"  [WARN] Hybrid search error: {e}")
            return []
    
    def _search_three_way(self, query_text: str) -> List[str]:
        """Execute three-way hybrid search (FTS + Dense + Sparse)."""
        try:
            # Get FTS results
            fts_results = self._execute_fts_search(query_text, limit=100)
            
            # Get dense vector results
            dense_results = self._execute_dense_search(query_text, limit=100)
            
            # Get sparse vector results
            sparse_results = self._execute_sparse_search(query_text, limit=100)
            
            # Compute adaptive weights
            weights = self._compute_adaptive_weights(query_text)
            
            # Merge with RRF
            from app.modules.search.rrf import ReciprocalRankFusionService
            rrf_service = ReciprocalRankFusionService(k=60)
            merged = rrf_service.fuse([fts_results, dense_results, sparse_results], weights=weights)
            
            # Return top 10 resource IDs
            return [resource_id for resource_id, _ in merged[:10]]
        
        except Exception as e:
            print(f"  [WARN] Three-way search error: {e}")
            return []
    
    def _execute_fts_search(self, query: str, limit: int = 100) -> List[Tuple[str, float]]:
        """Execute FTS5 full-text search."""
        try:
            dialect_name = self.db.bind.dialect.name
            
            # Split query into individual words for better matching
            query_words = query.lower().split()
            
            if dialect_name == "sqlite":
                # Build OR condition for each word
                conditions = []
                for word in query_words:
                    conditions.append(Resource.title.ilike(f"%{word}%"))
                    conditions.append(Resource.description.ilike(f"%{word}%"))
                
                if not conditions:
                    return []
                
                from sqlalchemy import or_
                results = (
                    self.db.query(Resource)
                    .filter(or_(*conditions))
                    .limit(limit)
                    .all()
                )
                
                # Score by number of matching words
                scored_results = []
                for r in results:
                    score = 0.0
                    text = f"{r.title or ''} {r.description or ''}".lower()
                    for word in query_words:
                        if word in text:
                            score += 1.0
                    scored_results.append((str(r.id), score / len(query_words)))
                
                # Sort by score descending
                scored_results.sort(key=lambda x: x[1], reverse=True)
                return scored_results[:limit]
            
            elif dialect_name == "postgresql":
                sql = text("""
                    SELECT id, ts_rank(
                        to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, '')),
                        plainto_tsquery('english', :query)
                    ) as rank
                    FROM resources
                    WHERE to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, ''))
                        @@ plainto_tsquery('english', :query)
                    ORDER BY rank DESC
                    LIMIT :limit
                """)
                result = self.db.execute(sql, {"query": query, "limit": limit})
                return [(str(row[0]), float(row[1])) for row in result]
            
            else:
                # Fallback - same as SQLite
                conditions = []
                for word in query_words:
                    conditions.append(Resource.title.ilike(f"%{word}%"))
                    conditions.append(Resource.description.ilike(f"%{word}%"))
                
                if not conditions:
                    return []
                
                from sqlalchemy import or_
                results = (
                    self.db.query(Resource)
                    .filter(or_(*conditions))
                    .limit(limit)
                    .all()
                )
                
                scored_results = []
                for r in results:
                    score = 0.0
                    text = f"{r.title or ''} {r.description or ''}".lower()
                    for word in query_words:
                        if word in text:
                            score += 1.0
                    scored_results.append((str(r.id), score / len(query_words)))
                
                scored_results.sort(key=lambda x: x[1], reverse=True)
                return scored_results[:limit]
        
        except Exception:
            return []
    
    def _execute_dense_search(self, query: str, limit: int = 100) -> List[Tuple[str, float]]:
        """Execute dense vector semantic search."""
        try:
            from app.shared.embeddings import EmbeddingService
            
            # Generate query embedding
            embedding_service = EmbeddingService(self.db)
            query_embedding = embedding_service.generate_embedding(query)
            
            if not query_embedding:
                return []
            
            # Fetch all resources with embeddings
            resources = self.db.query(Resource).filter(Resource.embedding.isnot(None)).all()
            
            if not resources:
                return []
            
            # Compute cosine similarity
            query_vec = np.array(query_embedding)
            query_norm = np.linalg.norm(query_vec)
            
            if query_norm == 0:
                return []
            
            similarities = []
            for resource in resources:
                try:
                    resource_embedding = resource.embedding
                    if isinstance(resource_embedding, str):
                        resource_embedding = json.loads(resource_embedding)
                    
                    if not resource_embedding:
                        continue
                    
                    resource_vec = np.array(resource_embedding)
                    resource_norm = np.linalg.norm(resource_vec)
                    
                    if resource_norm == 0:
                        continue
                    
                    # Cosine similarity
                    similarity = np.dot(query_vec, resource_vec) / (query_norm * resource_norm)
                    similarities.append((str(resource.id), float(similarity)))
                
                except Exception:
                    continue
            
            # Sort by similarity descending and return top N
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:limit]
        
        except Exception:
            return []
    
    def _execute_sparse_search(self, query: str, limit: int = 100) -> List[Tuple[str, float]]:
        """Execute sparse vector search using learned keyword importance."""
        try:
            from app.modules.search.sparse_embeddings import SparseEmbeddingService
            
            # Use sparse embedding service
            sparse_service = SparseEmbeddingService(self.db)
            query_sparse = sparse_service.generate_embedding(query)
            
            if not query_sparse:
                return []
            
            # Fetch all resources with sparse embeddings
            resources = (
                self.db.query(Resource)
                .filter(
                    Resource.sparse_embedding.isnot(None),
                    Resource.sparse_embedding != "",
                )
                .all()
            )
            
            if not resources:
                return []
            
            # Compute sparse similarity scores
            scores = []
            for resource in resources:
                try:
                    resource_sparse = json.loads(resource.sparse_embedding)
                    
                    # Compute dot product (sparse vectors are already normalized)
                    score = 0.0
                    for token_id, weight in query_sparse.items():
                        if str(token_id) in resource_sparse:
                            score += weight * resource_sparse[str(token_id)]
                    
                    if score > 0:
                        scores.append((str(resource.id), float(score)))
                
                except Exception:
                    continue
            
            # Sort by score descending and return top N
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[:limit]
        
        except Exception:
            return []
    
    def _compute_adaptive_weights(self, query: str) -> List[float]:
        """Compute query-adaptive weights for RRF fusion."""
        # Start with equal weights
        weights = [1.0, 1.0, 1.0]  # [FTS5, dense, sparse]
        
        word_count = len(query.split())
        
        # Short queries: boost FTS5
        if word_count <= 3:
            weights[0] *= 1.5
        
        # Long queries: boost dense
        if word_count > 10:
            weights[1] *= 1.5
        
        # Technical queries: boost sparse
        if any(c in query for c in ["(", ")", "{", "}", "=", "+", "-", "/", "*", ";", ":"]):
            weights[2] *= 1.5
        
        # Question queries: boost dense
        if query.lower().strip().startswith(("who", "what", "when", "where", "why", "how")):
            weights[1] *= 1.3
        
        # Normalize to sum to 1.0
        total = sum(weights)
        return [w / total for w in weights]
    
    def run_audit(self) -> Dict[str, Any]:
        """
        Run complete retrieval audit.
        
        Returns:
            Dictionary with all evaluation results
        """
        print("\n" + "=" * 80)
        print("RETRIEVAL QUALITY AUDIT")
        print("=" * 80)
        print(f"Sample Size: {self.sample_size}")
        print(f"Database: {self.db.bind.url}")
        
        # Get annotation samples
        samples = self._get_annotation_samples()
        
        # Evaluate each method
        self.results["methods"]["basic_search"] = self._evaluate_method(
            "Basic Search (FTS)",
            samples,
            self._search_basic
        )
        
        self.results["methods"]["hybrid_search"] = self._evaluate_method(
            "Hybrid Search (FTS + Vector)",
            samples,
            self._search_hybrid
        )
        
        self.results["methods"]["three_way_hybrid"] = self._evaluate_method(
            "Three-Way Hybrid (FTS + Dense + Sparse)",
            samples,
            self._search_three_way
        )
        
        # Print comparison
        self._print_comparison()
        
        # Save results
        output_file = "retrieval_audit_results.json"
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n[OK] Results saved to: {output_file}")
        
        # Determine if audit passed
        best_mrr = max(
            m["mrr"] for m in self.results["methods"].values()
        )
        
        if best_mrr < 0.3:
            print("\n[FAIL] AUDIT FAILED: Poor retrieval quality (MRR < 0.3)")
            return self.results
        
        print("\n[PASS] AUDIT PASSED: Retrieval quality acceptable")
        return self.results
    
    def _print_comparison(self):
        """Print comparison table of all methods."""
        print(f"\n{'=' * 80}")
        print("COMPARISON RESULTS")
        print(f"{'=' * 80}\n")
        
        # Table header
        print(f"{'Method':<30} {'MRR':>8} {'Recall@5':>12} {'Recall@10':>12} {'Latency (ms)':>15}")
        print("-" * 80)
        
        # Table rows
        for method_name, metrics in self.results["methods"].items():
            display_name = method_name.replace("_", " ").title()
            print(
                f"{display_name:<30} "
                f"{metrics['mrr']:>8.4f} "
                f"{metrics['recall_at_5']:>12.4f} "
                f"{metrics['recall_at_10']:>12.4f} "
                f"{metrics['avg_latency_ms']:>15.1f}"
            )
        
        print("-" * 80)
        
        # Analysis
        print("\nANALYSIS:")
        best_method = max(
            self.results["methods"].items(),
            key=lambda x: x[1]["mrr"]
        )
        print(f"  Best Method: {best_method[0]} (MRR: {best_method[1]['mrr']:.4f})")
        
        # Latency analysis
        print("\nLATENCY ANALYSIS:")
        for method_name, metrics in self.results["methods"].items():
            latency = metrics["avg_latency_ms"]
            status = "[OK] Excellent" if latency < 100 else "[WARN] Acceptable" if latency < 500 else "[SLOW] Slow"
            print(f"  {method_name}: {latency:.1f}ms - {status}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Audit retrieval quality")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=100,
        help="Number of annotations to sample (default: 100)"
    )
    parser.add_argument(
        "--database",
        type=str,
        default="sqlite:///./backend.db",
        help="Database URL (default: sqlite:///./backend.db)"
    )
    
    args = parser.parse_args()
    
    print(f"Using database: {args.database}")
    
    # Setup database
    engine = create_engine(args.database)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Run audit
        auditor = RetrievalAuditor(db, sample_size=args.sample_size)
        results = auditor.run_audit()
        
        # Exit with appropriate code
        best_mrr = max(m["mrr"] for m in results["methods"].values())
        sys.exit(0 if best_mrr >= 0.3 else 1)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
