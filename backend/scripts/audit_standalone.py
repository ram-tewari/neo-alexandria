"""
Standalone Retrieval Audit - No Circular Imports
Tests FTS5 vs Hybrid Search with MRR metric
"""
import sys
import time
import random
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, or_, text
from sqlalchemy.orm import sessionmaker

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.models import Resource, Annotation

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    print("ERROR: Missing dependencies")
    print("Run: pip install sentence-transformers numpy")
    sys.exit(1)

DB_URL = "sqlite:///./backend.db"
RESULTS_DIR = backend_dir / "ml_results" / "retrieval_audits"


def calculate_mrr(result_ids, target_id):
    """Calculate Mean Reciprocal Rank"""
    try:
        rank = result_ids.index(target_id) + 1
        return 1.0 / rank
    except ValueError:
        return 0.0


def fts5_search(session, query_text, limit=10):
    """FTS5 search using ILIKE (SQLite fallback)"""
    results = (
        session.query(Resource)
        .filter(
            or_(
                Resource.title.ilike(f"%{query_text}%"),
                Resource.description.ilike(f"%{query_text}%")
            )
        )
        .limit(limit)
        .all()
    )
    return [str(r.id) for r in results]


def vector_search(session, model, query_text, limit=10):
    """Dense vector search"""
    # Generate query embedding
    query_vec = model.encode(query_text).tolist()
    
    # Get all resources with embeddings
    resources = session.query(Resource).filter(Resource.embedding.isnot(None)).all()
    
    if not resources:
        return []
    
    # Calculate cosine similarity
    scores = []
    for res in resources:
        try:
            res_vec = json.loads(res.embedding)
            # Cosine similarity
            dot = sum(a * b for a, b in zip(query_vec, res_vec))
            norm_q = sum(a * a for a in query_vec) ** 0.5
            norm_r = sum(b * b for b in res_vec) ** 0.5
            sim = dot / (norm_q * norm_r) if (norm_q * norm_r) > 0 else 0
            scores.append((str(res.id), sim))
        except:
            continue
    
    # Sort by similarity
    scores.sort(key=lambda x: x[1], reverse=True)
    return [rid for rid, _ in scores[:limit]]


def hybrid_search(session, model, query_text, limit=10, alpha=0.5):
    """Hybrid search combining FTS5 and vector"""
    # Get FTS5 results
    fts_ids = fts5_search(session, query_text, limit=50)
    
    # Get vector results
    vec_ids = vector_search(session, model, query_text, limit=50)
    
    # RRF fusion
    k = 60
    scores = {}
    
    for rank, rid in enumerate(fts_ids, 1):
        scores[rid] = scores.get(rid, 0) + (1 - alpha) / (k + rank)
    
    for rank, rid in enumerate(vec_ids, 1):
        scores[rid] = scores.get(rid, 0) + alpha / (k + rank)
    
    # Sort by score
    sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [rid for rid, _ in sorted_ids[:limit]]


def run_audit(sample_size=20):
    print("="*80)
    print("STANDALONE RETRIEVAL AUDIT")
    print("="*80)
    
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 1. Fetch samples
    annotations = session.query(Annotation).filter(
        Annotation.resource_id.isnot(None),
        Annotation.user_id.isnot(None)  # Ensure valid user_id
    ).all()
    if not annotations:
        print("❌ No annotations found. Run seeder first.")
        return
    
    samples = random.sample(annotations, min(len(annotations), sample_size))
    print(f"✓ Selected {len(samples)} ground truth samples\n")
    
    # 2. Load model (warmup)
    print("[Warmup] Loading embedding model...")
    start_warmup = time.time()
    model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)
    # Warmup encode
    _ = model.encode("warmup")
    warmup_time = time.time() - start_warmup
    print(f"✓ Warmup complete in {warmup_time:.2f}s\n")
    
    # 3. Evaluation
    results = {
        "fts5": {"mrr": [], "latency": []},
        "vector": {"mrr": [], "latency": []},
        "hybrid": {"mrr": [], "latency": []}
    }
    
    print(f"Evaluating {len(samples)} queries...")
    print(f"{'Query':<30} | {'FTS5':<8} | {'Vector':<8} | {'Hybrid':<8} | {'Lat(ms)':<8}")
    print("-" * 80)
    
    for ann in samples:
        query_text = ann.highlighted_text
        target_id = str(ann.resource_id)
        
        # FTS5
        t0 = time.time()
        fts_ids = fts5_search(session, query_text, limit=10)
        t_fts = (time.time() - t0) * 1000
        fts_mrr = calculate_mrr(fts_ids, target_id)
        results["fts5"]["mrr"].append(fts_mrr)
        results["fts5"]["latency"].append(t_fts)
        
        # Vector
        t0 = time.time()
        vec_ids = vector_search(session, model, query_text, limit=10)
        t_vec = (time.time() - t0) * 1000
        vec_mrr = calculate_mrr(vec_ids, target_id)
        results["vector"]["mrr"].append(vec_mrr)
        results["vector"]["latency"].append(t_vec)
        
        # Hybrid
        t0 = time.time()
        hyb_ids = hybrid_search(session, model, query_text, limit=10, alpha=0.5)
        t_hyb = (time.time() - t0) * 1000
        hyb_mrr = calculate_mrr(hyb_ids, target_id)
        results["hybrid"]["mrr"].append(hyb_mrr)
        results["hybrid"]["latency"].append(t_hyb)
        
        print(f"{query_text[:30]:<30} | {fts_mrr:<8.3f} | {vec_mrr:<8.3f} | {hyb_mrr:<8.3f} | {t_hyb:<8.0f}")
    
    # 4. Final stats
    print("\n" + "="*80)
    print("FINAL METRICS")
    print("="*80)
    
    for method in ["fts5", "vector", "hybrid"]:
        mrr = sum(results[method]["mrr"]) / len(samples)
        lat = sum(results[method]["latency"]) / len(samples)
        print(f"\n{method.upper()}:")
        print(f"  MRR:     {mrr:.4f}")
        print(f"  Latency: {lat:.1f}ms")
    
    print("\n" + "-"*80)
    
    # Analysis
    fts_mrr = sum(results["fts5"]["mrr"]) / len(samples)
    vec_mrr = sum(results["vector"]["mrr"]) / len(samples)
    hyb_mrr = sum(results["hybrid"]["mrr"]) / len(samples)
    hyb_lat = sum(results["hybrid"]["latency"]) / len(samples)
    
    if hyb_mrr > fts_mrr and hyb_mrr > vec_mrr:
        improvement = ((hyb_mrr - fts_mrr) / fts_mrr * 100) if fts_mrr > 0 else 0
        print(f"✅ PASS: Hybrid improves MRR by {improvement:.1f}% over FTS5")
    elif vec_mrr > fts_mrr:
        print(f"⚠️  Vector beats FTS5, but Hybrid underperforms")
    elif fts_mrr > hyb_mrr:
        degradation = ((fts_mrr - hyb_mrr) / fts_mrr * 100) if fts_mrr > 0 else 0
        print(f"❌ FAIL: Hybrid is {degradation:.1f}% worse than FTS5")
        print("   Recommendation: Use FTS5 only")
    else:
        print("⚠️  INCONCLUSIVE: Results too close")
    
    if hyb_lat > 1000:
        print(f"\n❌ CRITICAL: Hybrid latency > 1s ({hyb_lat:.0f}ms)")
    elif hyb_lat > 500:
        print(f"\n⚠️  WARNING: Hybrid latency is high ({hyb_lat:.0f}ms)")
    else:
        print(f"\n✅ Latency acceptable ({hyb_lat:.0f}ms)")
    
    # 5. Save results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = RESULTS_DIR / f"audit_{timestamp}.json"
    
    # Ensure directory exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    audit_results = {
        "timestamp": timestamp,
        "sample_size": len(samples),
        "warmup_time_seconds": warmup_time,
        "metrics": {
            "fts5": {
                "mrr": fts_mrr,
                "avg_latency_ms": sum(results["fts5"]["latency"]) / len(samples)
            },
            "vector": {
                "mrr": vec_mrr,
                "avg_latency_ms": sum(results["vector"]["latency"]) / len(samples)
            },
            "hybrid": {
                "mrr": hyb_mrr,
                "avg_latency_ms": hyb_lat
            }
        },
        "per_query_results": [
            {
                "query": samples[i].highlighted_text,
                "target_id": str(samples[i].resource_id),
                "fts5_mrr": results["fts5"]["mrr"][i],
                "vector_mrr": results["vector"]["mrr"][i],
                "hybrid_mrr": results["hybrid"]["mrr"][i],
                "hybrid_latency_ms": results["hybrid"]["latency"][i]
            }
            for i in range(len(samples))
        ]
    }
    
    with open(results_file, 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    print(f"\n📊 Results saved to: {results_file.relative_to(backend_dir)}")


if __name__ == "__main__":
    run_audit()
