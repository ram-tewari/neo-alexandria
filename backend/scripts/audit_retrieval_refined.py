"""
Refined Retrieval Audit Script
Fixes: 1) Proper FTS5 baseline, 2) Warmup for latency, 3) MRR calculation
"""
import sys
import time
import random
from pathlib import Path
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.models import Resource, Annotation
from app.services.search_service import AdvancedSearchService
from app.domain.search import SearchQuery, SearchFilters

DB_URL = "sqlite:///./backend.db"


def calculate_mrr(result_ids, target_id):
    """Calculate Mean Reciprocal Rank for a single query."""
    try:
        rank = result_ids.index(target_id) + 1
        return 1.0 / rank
    except ValueError:
        return 0.0


def run_audit(sample_size=20):
    print("="*80)
    print("REFINED RETRIEVAL AUDIT")
    print("="*80)
    
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 1. Fetch Samples
    annotations = session.query(Annotation).filter(Annotation.resource_id.isnot(None)).all()
    if not annotations:
        print("❌ No annotations found. Run seed script first.")
        return
    
    samples = random.sample(annotations, min(len(annotations), sample_size))
    print(f"✓ Selected {len(samples)} ground truth samples.")
    
    # 2. Warmup (Crucial for Latency Check)
    print("\n[Warmup] Initializing Models... (This absorbs the cold start cost)")
    start_warmup = time.time()
    try:
        # Trigger model load
        dummy = SearchQuery(text="warmup", filters=SearchFilters(), limit=1)
        AdvancedSearchService.search_three_way_hybrid(session, dummy, enable_reranking=False)
    except Exception as e:
        print(f"⚠️ Warmup Warning: {e}")
    print(f"✓ Warmup Complete in {time.time() - start_warmup:.2f}s")
    
    # 3. Evaluation Loop
    results = {
        "fts5": {"mrr": [], "latency": []},
        "hybrid": {"mrr": [], "latency": []}
    }
    
    print(f"\nEvaluating {len(samples)} queries...")
    print(f"{'Query':<30} | {'FTS5 MRR':<10} | {'Hybrid MRR':<12} | {'Lat(ms)':<10}")
    print("-" * 75)
    
    for ann in samples:
        query_text = ann.text  # Title acts as query
        target_id = str(ann.resource_id)
        
        # --- Method A: FTS5 (Production Implementation) ---
        t0 = time.time()
        try:
            # Use the actual FTS5 implementation from AdvancedSearchService
            # This uses ILIKE for SQLite, tsvector for PostgreSQL
            fts_results = AdvancedSearchService._execute_fts_search(
                db=session,
                query=query_text,
                limit=10
            )
            fts_ids = [rid for rid, score in fts_results]
        except Exception as e:
            print(f"  ⚠️ FTS5 error: {e}")
            fts_ids = []
        t_fts = (time.time() - t0) * 1000
        
        fts_mrr = calculate_mrr(fts_ids, target_id)
        results["fts5"]["mrr"].append(fts_mrr)
        results["fts5"]["latency"].append(t_fts)
        
        # --- Method B: Hybrid (The System) ---
        t0 = time.time()
        sq = SearchQuery(text=query_text, filters=SearchFilters(), limit=10)
        try:
            hybrid_res_obj, _, _, _, _ = AdvancedSearchService.search_three_way_hybrid(
                db=session,
                query=sq,
                enable_reranking=False
            )
            hybrid_ids = [str(r.id) for r in hybrid_res_obj]
        except Exception as e:
            print(f"  ⚠️ Hybrid error: {e}")
            hybrid_ids = []
        t_hybrid = (time.time() - t0) * 1000
        
        hybrid_mrr = calculate_mrr(hybrid_ids, target_id)
        results["hybrid"]["mrr"].append(hybrid_mrr)
        results["hybrid"]["latency"].append(t_hybrid)
        
        print(f"{query_text[:30]:<30} | {fts_mrr:<10.3f} | {hybrid_mrr:<12.3f} | {t_hybrid:.0f}")
    
    # 4. Final Stats
    print("\n" + "="*80)
    print("FINAL METRICS")
    print("="*80)
    
    fts_mrr = sum(results['fts5']['mrr']) / len(samples)
    hybrid_mrr = sum(results['hybrid']['mrr']) / len(samples)
    fts_lat = sum(results['fts5']['latency']) / len(samples)
    hybrid_lat = sum(results['hybrid']['latency']) / len(samples)
    
    print(f"\nFTS5 (Baseline):")
    print(f"  MRR:     {fts_mrr:.4f}")
    print(f"  Latency: {fts_lat:.1f}ms")
    
    print(f"\nHybrid (ML):")
    print(f"  MRR:     {hybrid_mrr:.4f}")
    print(f"  Latency: {hybrid_lat:.1f}ms")
    
    print("\n" + "-"*80)
    
    # Analysis
    if hybrid_mrr > fts_mrr:
        improvement = ((hybrid_mrr - fts_mrr) / fts_mrr * 100) if fts_mrr > 0 else 0
        print(f"✅ PASS: Hybrid improves MRR by {improvement:.1f}% over FTS5")
    elif fts_mrr > hybrid_mrr:
        degradation = ((fts_mrr - hybrid_mrr) / fts_mrr * 100) if fts_mrr > 0 else 0
        print(f"❌ FAIL: Hybrid is {degradation:.1f}% worse than FTS5")
        print("   Recommendation: Use FTS5 only, ML models not adding value")
    else:
        print("⚠️  INCONCLUSIVE: FTS5 and Hybrid perform equally")
    
    if hybrid_lat > 1000:
        print(f"\n❌ CRITICAL: Hybrid latency > 1s ({hybrid_lat:.0f}ms)")
        print("   Suspect: BGE-M3 Sparse Encoding on CPU")
        print("   Action: Profile with cProfile or switch to lighter model")
    elif hybrid_lat > 500:
        print(f"\n⚠️  WARNING: Hybrid latency is high ({hybrid_lat:.0f}ms)")
    else:
        print(f"\n✅ Latency acceptable ({hybrid_lat:.0f}ms)")


if __name__ == "__main__":
    run_audit()
