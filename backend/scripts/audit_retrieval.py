"""
Offline Model Evaluation Script - Phase 2 Verification

This script performs a data-driven audit of retrieval quality by comparing
FTS5 (keyword), Vector (dense), and Hybrid (three-way) search methods.

Requirements:
- Must run on Edge Worker environment (torch allowed)
- Uses existing annotations as ground truth queries
- Outputs MRR and Recall@5 metrics for comparison

Usage:
    python backend/scripts/audit_retrieval.py [--sample-size 100] [--output results.json]

Metrics:
- MRR (Mean Reciprocal Rank): Average of 1/rank for first correct result
- Recall@5: Percentage of queries where correct result appears in top 5
- Recall@10: Percentage of queries where correct result appears in top 10

Pass Criteria:
- Hybrid > Vector > FTS5 (if not, ML models are not adding value)
"""

import os
import sys
import json
import time
import random
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from collections import defaultdict

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Database imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Model imports
from app.database.models import Resource, Annotation

# Search service imports
from app.modules.search.service import SearchService
from app.domain.search import SearchQuery


class RetrievalAuditor:
    """
    Auditor for comparing retrieval methods using annotation ground truth.
    
    Ground Truth Logic:
    - Query: Annotation text (what user highlighted/noted)
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
                "timestamp": datetime.utcnow().isoformat(),
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
        
        Raises:
            ValueError: If insufficient annotations exist
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
        
        if total_annotations < 10:
            raise ValueError(
                f"Insufficient annotations for evaluation. Found {total_annotations}, need at least 10."
            )
        
        # Adjust sample size if necessary
        actual_sample_size = min(self.sample_size, total_annotations)
        if actual_sample_size < self.sample_size:
            print(f"⚠️  Reducing sample size from {self.sample_size} to {actual_sample_size}")
        
        # Fetch all eligible annotations
        annotations = (
            self.db.query(Annotation)
            .filter(Annotation.highlighted_text.isnot(None))
            .filter(Annotation.highlighted_text != "")
            .filter(Annotation.resource_id.isnot(None))
            .all()
        )
        
        # Random sample
        sampled = random.sample(annotations, actual_sample_size)
        
        # Extract (id, highlighted_text, resource_id) tuples
        samples = [
            (str(ann.id), ann.highlighted_text, str(ann.resource_id))
            for ann in sampled
        ]
        
        print(f"✓ Sampled {len(samples)} annotations")
        print(f"  Average text length: {sum(len(s[1]) for s in samples) / len(samples):.1f} chars")
        
        return samples
    
    def _warmup_model(self, method_name: str):
        """
        Run a dummy query to load lazy models into memory.
        
        This isolates cold start costs from actual query latency.
        
        Args:
            method_name: Name of the method being warmed up
        """
        print(f"   [Warmup] Initializing {method_name} models...")
        try:
            dummy_query = SearchQuery(text="warmup", filters=SearchFilters(), limit=1)
            # Call the service blindly to trigger lazy loads
            AdvancedSearchService.search_three_way_hybrid(
                db=self.db,
                query=dummy_query,
                enable_reranking=False
            )
        except Exception:
            pass  # Ignore errors, just want to trigger imports
    
    def _evaluate_fts5(self, samples: List[Tuple[str, str, str]]) -> Dict:
        """
        Evaluate FTS5 (keyword) search using production pipeline.
        
        CRITICAL: This uses the actual FTS5 implementation from AdvancedSearchService,
        not raw SQL LIKE queries. This ensures we're testing the real production code.
        
        Args:
            samples: List of (annotation_id, text, target_resource_id) tuples
        
        Returns:
            Dictionary with metrics and per-query results
        """
        print("\n" + "=" * 80)
        print("STEP 2: Evaluating FTS5 (Production Pipeline)")
        print("=" * 80)
        
        reciprocal_ranks = []
        recall_at_5 = 0
        recall_at_10 = 0
        query_results = []
        
        start_time = time.time()
        
        for i, (ann_id, query_text, target_id) in enumerate(samples, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(samples)}")
            
            try:
                # Use the actual FTS5 implementation from AdvancedSearchService
                # This ensures we're testing the real production code, not a mock
                fts_results = AdvancedSearchService._execute_fts_search(
                    db=self.db,
                    query=query_text,
                    limit=10
                )
                
                # Extract resource IDs from results
                result_ids = [rid for rid, score in fts_results]
                
                # Calculate rank
                rank = None
                if target_id in result_ids:
                    rank = result_ids.index(target_id) + 1
                    reciprocal_ranks.append(1.0 / rank)
                    
                    if rank <= 5:
                        recall_at_5 += 1
                    if rank <= 10:
                        recall_at_10 += 1
                else:
                    reciprocal_ranks.append(0.0)
                
                query_results.append({
                    "annotation_id": ann_id,
                    "query": query_text[:100],  # Truncate for readability
                    "target_id": target_id,
                    "rank": rank,
                    "found": rank is not None
                })
                
            except Exception as e:
                print(f"  ⚠️  Error on query {i}: {e}")
                reciprocal_ranks.append(0.0)
                query_results.append({
                    "annotation_id": ann_id,
                    "query": query_text[:100],
                    "target_id": target_id,
                    "rank": None,
                    "found": False,
                    "error": str(e)
                })
        
        elapsed = time.time() - start_time
        
        # Calculate metrics
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
        recall_5 = recall_at_5 / len(samples)
        recall_10 = recall_at_10 / len(samples)
        avg_latency = (elapsed / len(samples)) * 1000  # ms
        
        print(f"\n✓ FTS5 Evaluation Complete")
        print(f"  MRR: {mrr:.4f}")
        print(f"  Recall@5: {recall_5:.4f} ({recall_at_5}/{len(samples)})")
        print(f"  Recall@10: {recall_10:.4f} ({recall_at_10}/{len(samples)})")
        print(f"  Avg Latency: {avg_latency:.1f}ms")
        
        return {
            "mrr": mrr,
            "recall_at_5": recall_5,
            "recall_at_10": recall_10,
            "avg_latency_ms": avg_latency,
            "total_time_s": elapsed,
            "query_results": query_results
        }
    
    def _evaluate_vector(self, samples: List[Tuple[str, str, str]]) -> Dict:
        """
        Evaluate Vector (dense embedding) search using production pipeline.
        
        Args:
            samples: List of (annotation_id, text, target_resource_id) tuples
        
        Returns:
            Dictionary with metrics and per-query results
        """
        print("\n" + "=" * 80)
        print("STEP 3: Evaluating Vector (Dense Embedding) Search")
        print("=" * 80)
        
        # Check if embeddings exist
        resources_with_embeddings = (
            self.db.query(Resource)
            .filter(Resource.embedding.isnot(None))
            .count()
        )
        
        print(f"Resources with embeddings: {resources_with_embeddings}")
        
        if resources_with_embeddings == 0:
            print("⚠️  No embeddings found. Vector search will fail.")
            return {
                "mrr": 0.0,
                "recall_at_5": 0.0,
                "recall_at_10": 0.0,
                "avg_latency_ms": 0.0,
                "total_time_s": 0.0,
                "error": "No embeddings available",
                "query_results": []
            }
        
        # Warmup: Load models into memory before timing
        self._warmup_model("Vector Search")
        
        reciprocal_ranks = []
        recall_at_5 = 0
        recall_at_10 = 0
        query_results = []
        
        start_time = time.time()
        
        for i, (ann_id, query_text, target_id) in enumerate(samples, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(samples)}")
            
            try:
                # Use the actual dense vector search implementation
                dense_results = AdvancedSearchService._execute_dense_search(
                    db=self.db,
                    query=query_text,
                    limit=10
                )
                
                # Extract resource IDs from results
                result_ids = [rid for rid, score in dense_results]
                
                # Calculate rank
                rank = None
                if target_id in result_ids:
                    rank = result_ids.index(target_id) + 1
                    reciprocal_ranks.append(1.0 / rank)
                    
                    if rank <= 5:
                        recall_at_5 += 1
                    if rank <= 10:
                        recall_at_10 += 1
                else:
                    reciprocal_ranks.append(0.0)
                
                query_results.append({
                    "annotation_id": ann_id,
                    "query": query_text[:100],
                    "target_id": target_id,
                    "rank": rank,
                    "found": rank is not None
                })
                
            except Exception as e:
                print(f"  ⚠️  Error on query {i}: {e}")
                reciprocal_ranks.append(0.0)
                query_results.append({
                    "annotation_id": ann_id,
                    "query": query_text[:100],
                    "target_id": target_id,
                    "rank": None,
                    "found": False,
                    "error": str(e)
                })
        
        elapsed = time.time() - start_time
        
        # Calculate metrics
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
        recall_5 = recall_at_5 / len(samples)
        recall_10 = recall_at_10 / len(samples)
        avg_latency = (elapsed / len(samples)) * 1000  # ms
        
        print(f"\n✓ Vector Evaluation Complete")
        print(f"  MRR: {mrr:.4f}")
        print(f"  Recall@5: {recall_5:.4f} ({recall_at_5}/{len(samples)})")
        print(f"  Recall@10: {recall_10:.4f} ({recall_at_10}/{len(samples)})")
        print(f"  Avg Latency: {avg_latency:.1f}ms")
        
        return {
            "mrr": mrr,
            "recall_at_5": recall_5,
            "recall_at_10": recall_10,
            "avg_latency_ms": avg_latency,
            "total_time_s": elapsed,
            "query_results": query_results
        }
    
    def _evaluate_hybrid(self, samples: List[Tuple[str, str, str]]) -> Dict:
        """
        Evaluate Hybrid (three-way: FTS5 + dense + sparse) search.
        
        Args:
            samples: List of (annotation_id, text, target_resource_id) tuples
        
        Returns:
            Dictionary with metrics and per-query results
        """
        print("\n" + "=" * 80)
        print("STEP 4: Evaluating Hybrid (Three-Way) Search")
        print("=" * 80)
        
        # Warmup: Load models into memory before timing
        self._warmup_model("Hybrid Search")
        
        reciprocal_ranks = []
        recall_at_5 = 0
        recall_at_10 = 0
        query_results = []
        
        start_time = time.time()
        
        for i, (ann_id, query_text, target_id) in enumerate(samples, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(samples)}")
            
            try:
                # Perform three-way hybrid search
                search_query = SearchQuery(
                    text=query_text,
                    filters=SearchFilters(),
                    limit=10,
                    offset=0
                )
                
                resources, total, _, _, _ = AdvancedSearchService.search_three_way_hybrid(
                    db=self.db,
                    query=search_query,
                    enable_reranking=False,  # Disable reranking for fair comparison
                    adaptive_weighting=True
                )
                
                result_ids = [str(r.id) for r in resources]
                
                # Calculate rank
                rank = None
                if target_id in result_ids:
                    rank = result_ids.index(target_id) + 1
                    reciprocal_ranks.append(1.0 / rank)
                    
                    if rank <= 5:
                        recall_at_5 += 1
                    if rank <= 10:
                        recall_at_10 += 1
                else:
                    reciprocal_ranks.append(0.0)
                
                query_results.append({
                    "annotation_id": ann_id,
                    "query": query_text[:100],
                    "target_id": target_id,
                    "rank": rank,
                    "found": rank is not None
                })
                
            except Exception as e:
                print(f"  ⚠️  Error on query {i}: {e}")
                reciprocal_ranks.append(0.0)
                query_results.append({
                    "annotation_id": ann_id,
                    "query": query_text[:100],
                    "target_id": target_id,
                    "rank": None,
                    "found": False,
                    "error": str(e)
                })
        
        elapsed = time.time() - start_time
        
        # Calculate metrics
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
        recall_5 = recall_at_5 / len(samples)
        recall_10 = recall_at_10 / len(samples)
        avg_latency = (elapsed / len(samples)) * 1000  # ms
        
        print(f"\n✓ Hybrid Evaluation Complete")
        print(f"  MRR: {mrr:.4f}")
        print(f"  Recall@5: {recall_5:.4f} ({recall_at_5}/{len(samples)})")
        print(f"  Recall@10: {recall_10:.4f} ({recall_at_10}/{len(samples)})")
        print(f"  Avg Latency: {avg_latency:.1f}ms")
        
        return {
            "mrr": mrr,
            "recall_at_5": recall_5,
            "recall_at_10": recall_10,
            "avg_latency_ms": avg_latency,
            "total_time_s": elapsed,
            "query_results": query_results
        }
    
    def run_audit(self) -> Dict:
        """
        Run complete retrieval audit.
        
        Returns:
            Dictionary with all results and comparison
        """
        print("\n" + "=" * 80)
        print("RETRIEVAL QUALITY AUDIT")
        print("=" * 80)
        print(f"Sample Size: {self.sample_size}")
        print(f"Database: {self.db.bind.url}")
        
        # Step 1: Get annotation samples
        samples = self._get_annotation_samples()
        self.results["metadata"]["actual_sample_size"] = len(samples)
        
        # Step 2: Evaluate FTS5
        self.results["methods"]["fts5"] = self._evaluate_fts5(samples)
        
        # Step 3: Evaluate Vector
        self.results["methods"]["vector"] = self._evaluate_vector(samples)
        
        # Step 4: Evaluate Hybrid
        self.results["methods"]["hybrid"] = self._evaluate_hybrid(samples)
        
        # Step 5: Compare and analyze
        self._print_comparison()
        
        return self.results
    
    def _print_comparison(self):
        """Print comparison table and analysis."""
        print("\n" + "=" * 80)
        print("COMPARISON RESULTS")
        print("=" * 80)
        
        methods = ["fts5", "vector", "hybrid"]
        
        # Print table header
        print(f"\n{'Method':<15} {'MRR':>10} {'Recall@5':>12} {'Recall@10':>12} {'Latency (ms)':>15}")
        print("-" * 80)
        
        # Print each method
        for method in methods:
            if method in self.results["methods"]:
                data = self.results["methods"][method]
                if "error" not in data:
                    print(
                        f"{method.upper():<15} "
                        f"{data['mrr']:>10.4f} "
                        f"{data['recall_at_5']:>12.4f} "
                        f"{data['recall_at_10']:>12.4f} "
                        f"{data['avg_latency_ms']:>15.1f}"
                    )
                else:
                    print(f"{method.upper():<15} ERROR: {data['error']}")
        
        print("-" * 80)
        
        # Analysis
        print("\nANALYSIS:")
        
        fts5_mrr = self.results["methods"].get("fts5", {}).get("mrr", 0)
        vector_mrr = self.results["methods"].get("vector", {}).get("mrr", 0)
        hybrid_mrr = self.results["methods"].get("hybrid", {}).get("mrr", 0)
        
        # Check if hybrid is best
        if hybrid_mrr > vector_mrr and hybrid_mrr > fts5_mrr:
            print("✓ PASS: Hybrid search outperforms both FTS5 and Vector")
            improvement = ((hybrid_mrr - fts5_mrr) / fts5_mrr * 100) if fts5_mrr > 0 else 0
            print(f"  Hybrid improves MRR by {improvement:.1f}% over FTS5")
        elif vector_mrr > fts5_mrr:
            print("⚠️  WARNING: Vector search better than FTS5, but Hybrid underperforms")
            print("  Possible issues: RRF fusion weights, sparse embedding quality")
        elif fts5_mrr > vector_mrr and fts5_mrr > hybrid_mrr:
            print("❌ FAIL: FTS5 (keyword) outperforms ML models")
            print("  Recommendation: Delete ML models, use FTS5 only")
            print("  Possible causes:")
            print("    - Embeddings not trained on domain-specific data")
            print("    - Annotation text too short for semantic matching")
            print("    - Model mismatch (embeddings trained on different corpus)")
        else:
            print("⚠️  INCONCLUSIVE: Results too close to determine winner")
        
        # Latency analysis
        print("\nLATENCY ANALYSIS:")
        for method in methods:
            if method in self.results["methods"]:
                data = self.results["methods"][method]
                if "avg_latency_ms" in data:
                    latency = data["avg_latency_ms"]
                    if latency < 100:
                        status = "✓ Excellent"
                    elif latency < 500:
                        status = "✓ Acceptable"
                    elif latency < 2000:
                        status = "⚠️  Slow"
                    else:
                        status = "❌ Unacceptable"
                    print(f"  {method.upper()}: {latency:.1f}ms - {status}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit retrieval quality using annotation ground truth"
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=100,
        help="Number of annotations to sample (default: 100)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="retrieval_audit_results.json",
        help="Output JSON file (default: retrieval_audit_results.json)"
    )
    parser.add_argument(
        "--database",
        type=str,
        default=None,
        help="Database URL (default: from DATABASE_URL env var or sqlite:///./backend.db)"
    )
    
    args = parser.parse_args()
    
    # Determine database URL
    if args.database:
        db_url = args.database
    else:
        db_url = os.getenv("DATABASE_URL", "sqlite:///./backend.db")
    
    print(f"Using database: {db_url}")
    
    # Create database session
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Run audit
        auditor = RetrievalAuditor(db, sample_size=args.sample_size)
        results = auditor.run_audit()
        
        # Save results
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Results saved to: {output_path}")
        
        # Determine exit code based on results
        hybrid_mrr = results["methods"].get("hybrid", {}).get("mrr", 0)
        vector_mrr = results["methods"].get("vector", {}).get("mrr", 0)
        fts5_mrr = results["methods"].get("fts5", {}).get("mrr", 0)
        
        if hybrid_mrr > vector_mrr and hybrid_mrr > fts5_mrr:
            print("\n✓ AUDIT PASSED: ML models add value")
            sys.exit(0)
        else:
            print("\n❌ AUDIT FAILED: ML models do not improve retrieval")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Audit failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
