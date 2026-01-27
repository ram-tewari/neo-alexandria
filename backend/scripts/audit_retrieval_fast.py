"""
Fast Retrieval Audit - Tests only FTS and Hybrid (skips slow three-way)

Usage:
    python scripts/audit_retrieval_fast.py --sample-size 24
"""
import sys
from pathlib import Path

# Import from the fixed audit script
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import everything from the fixed script
from audit_retrieval_fixed import *

# Override the run_audit method to skip three-way
class FastRetrievalAuditor(RetrievalAuditor):
    def run_audit(self) -> Dict[str, Any]:
        """Run fast audit (FTS + Hybrid only, skip three-way)."""
        print("\n" + "=" * 80)
        print("FAST RETRIEVAL QUALITY AUDIT (FTS + Hybrid only)")
        print("=" * 80)
        print(f"Sample Size: {self.sample_size}")
        print(f"Database: {self.db.bind.url}")
        
        # Get annotation samples
        samples = self._get_annotation_samples()
        
        # Evaluate FTS
        self.results["methods"]["basic_search"] = self._evaluate_method(
            "Basic Search (FTS)",
            samples,
            self._search_basic
        )
        
        # Evaluate Hybrid
        self.results["methods"]["hybrid_search"] = self._evaluate_method(
            "Hybrid Search (FTS + Vector)",
            samples,
            self._search_hybrid
        )
        
        # Print comparison
        self._print_comparison()
        
        # Save results
        output_file = "retrieval_audit_results_fast.json"
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fast retrieval audit (FTS + Hybrid only)")
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
        # Run fast audit
        auditor = FastRetrievalAuditor(db, sample_size=args.sample_size)
        results = auditor.run_audit()
        
        # Exit with appropriate code
        best_mrr = max(m["mrr"] for m in results["methods"].values())
        sys.exit(0 if best_mrr >= 0.3 else 1)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
