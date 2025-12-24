#!/usr/bin/env python3
"""
Phase 13 to Phase 13.5 Endpoint Coverage Verification

This script verifies that all endpoints and features implemented in Phase 13
(PostgreSQL migration) have been properly covered in the Phase 13.5 vertical
slice refactor.

Phase 13 focused on:
- PostgreSQL database support
- Full-text search enhancements
- Database configuration and migration
- Connection pooling and monitoring

Phase 13.5 focused on:
- Vertical slice architecture (modular refactor)
- Event-driven communication
- Module extraction (Collections, Resources, Search)
- Shared kernel pattern

This verification ensures no endpoints were lost during the refactor.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


class EndpointVerifier:
    """Verifies endpoint coverage between Phase 13 and Phase 13.5"""
    
    def __init__(self):
        self.phase13_endpoints: Set[Tuple[str, str]] = set()  # (method, path)
        self.phase135_endpoints: Set[Tuple[str, str]] = set()
        self.routers_dir = backend_dir / "app" / "routers"
        self.modules_dir = backend_dir / "app" / "modules"
        
    def extract_endpoints_from_file(self, filepath: Path) -> List[Tuple[str, str]]:
        """Extract HTTP endpoints from a Python router file"""
        endpoints = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Pattern to match FastAPI route decorators
            # @router.get("/path")
            # @router.post("/path", ...)
            pattern = r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
            
            matches = re.findall(pattern, content)
            for method, path in matches:
                endpoints.append((method.upper(), path))
                
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            
        return endpoints
    
    def scan_routers_directory(self):
        """Scan the app/routers directory for Phase 13 endpoints"""
        print("\n" + "="*80)
        print("SCANNING PHASE 13 ENDPOINTS (app/routers/)")
        print("="*80)
        
        if not self.routers_dir.exists():
            print(f"❌ Routers directory not found: {self.routers_dir}")
            return
            
        for router_file in self.routers_dir.glob("*.py"):
            if router_file.name.startswith("__"):
                continue
                
            endpoints = self.extract_endpoints_from_file(router_file)
            if endpoints:
                print(f"\n📄 {router_file.name}:")
                for method, path in endpoints:
                    print(f"   {method:6} {path}")
                    self.phase13_endpoints.add((method, path))
                    
        print(f"\n✅ Total Phase 13 endpoints found: {len(self.phase13_endpoints)}")
    
    def scan_modules_directory(self):
        """Scan the app/modules directory for Phase 13.5 endpoints"""
        print("\n" + "="*80)
        print("SCANNING PHASE 13.5 ENDPOINTS (app/modules/)")
        print("="*80)
        
        if not self.modules_dir.exists():
            print(f"❌ Modules directory not found: {self.modules_dir}")
            return
            
        for module_dir in self.modules_dir.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith("__"):
                continue
                
            router_file = module_dir / "router.py"
            if router_file.exists():
                endpoints = self.extract_endpoints_from_file(router_file)
                if endpoints:
                    print(f"\n📦 {module_dir.name} module:")
                    for method, path in endpoints:
                        print(f"   {method:6} {path}")
                        self.phase135_endpoints.add((method, path))
                        
        print(f"\n✅ Total Phase 13.5 module endpoints found: {len(self.phase135_endpoints)}")
    
    def normalize_path(self, path: str, module: str = None) -> str:
        """Normalize endpoint paths for comparison"""
        # Remove module prefix from module paths
        if module == 'collections':
            # /health -> /collections/health
            # /{collection_id} -> /collections/{collection_id}
            if path == '/health':
                return '/collections/health'
            elif path.startswith('/{collection_id}'):
                return path.replace('/{collection_id}', '/collections/{collection_id}', 1)
            elif not path.startswith('/collections'):
                return '/collections' + path
        elif module == 'resources':
            # Already has /resources prefix in most cases
            pass
        elif module == 'search':
            # Already has /search prefix in most cases
            pass
        return path
    
    def compare_coverage(self) -> Dict[str, any]:
        """Compare Phase 13 and Phase 13.5 endpoint coverage"""
        print("\n" + "="*80)
        print("COVERAGE ANALYSIS")
        print("="*80)
        
        # Normalize module endpoints
        normalized_phase135 = set()
        for method, path in self.phase135_endpoints:
            # Determine module from path
            if '/collections' in path or path.startswith('/{collection_id}'):
                normalized_path = self.normalize_path(path, 'collections')
            elif '/resources' in path:
                normalized_path = self.normalize_path(path, 'resources')
            elif '/search' in path or '/admin' in path:
                normalized_path = self.normalize_path(path, 'search')
            else:
                normalized_path = path
            normalized_phase135.add((method, normalized_path))
        
        # Endpoints that should have been migrated to modules
        # (Collections, Resources, Search)
        migrated_prefixes = ['/collections', '/resources', '/search']
        
        phase13_migrated = {
            (m, p) for m, p in self.phase13_endpoints
            if any(p.startswith(prefix) for prefix in migrated_prefixes)
        }
        
        phase13_not_migrated = self.phase13_endpoints - phase13_migrated
        
        # Check coverage
        missing_in_modules = phase13_migrated - normalized_phase135
        new_in_modules = normalized_phase135 - phase13_migrated
        covered = phase13_migrated & normalized_phase135
        
        results = {
            'total_phase13': len(self.phase13_endpoints),
            'total_phase135_modules': len(self.phase135_endpoints),
            'should_be_migrated': len(phase13_migrated),
            'covered': len(covered),
            'missing': len(missing_in_modules),
            'new': len(new_in_modules),
            'not_migrated_yet': len(phase13_not_migrated),
            'missing_endpoints': missing_in_modules,
            'new_endpoints': new_in_modules,
            'not_migrated_endpoints': phase13_not_migrated
        }
        
        return results
    
    def print_results(self, results: Dict):
        """Print verification results"""
        print(f"\n📊 STATISTICS:")
        print(f"   Total Phase 13 endpoints: {results['total_phase13']}")
        print(f"   Total Phase 13.5 module endpoints: {results['total_phase135_modules']}")
        print(f"   Endpoints that should be migrated: {results['should_be_migrated']}")
        print(f"   ✅ Covered in modules: {results['covered']}")
        print(f"   ❌ Missing in modules: {results['missing']}")
        print(f"   ➕ New in modules: {results['new']}")
        print(f"   ⏳ Not yet migrated (other routers): {results['not_migrated_yet']}")
        
        if results['missing']:
            print("\n" + "="*80)
            print("❌ MISSING ENDPOINTS IN PHASE 13.5 MODULES")
            print("="*80)
            print("\nThese endpoints exist in Phase 13 routers but are missing from modules:")
            for method, path in sorted(results['missing_endpoints']):
                print(f"   {method:6} {path}")
                
        if results['new']:
            print("\n" + "="*80)
            print("➕ NEW ENDPOINTS IN PHASE 13.5 MODULES")
            print("="*80)
            print("\nThese endpoints are new in Phase 13.5 modules:")
            for method, path in sorted(results['new_endpoints']):
                print(f"   {method:6} {path}")
                
        if results['not_migrated_yet']:
            print("\n" + "="*80)
            print("⏳ ENDPOINTS NOT YET MIGRATED TO MODULES")
            print("="*80)
            print("\nThese endpoints are still in app/routers/ (not part of Collections/Resources/Search):")
            
            # Group by router
            by_prefix = {}
            for method, path in results['not_migrated_endpoints']:
                prefix = path.split('/')[1] if '/' in path else 'root'
                if prefix not in by_prefix:
                    by_prefix[prefix] = []
                by_prefix[prefix].append((method, path))
                
            for prefix in sorted(by_prefix.keys()):
                print(f"\n   {prefix.upper()} endpoints:")
                for method, path in sorted(by_prefix[prefix]):
                    print(f"      {method:6} {path}")
        
        # Final verdict
        print("\n" + "="*80)
        print("FINAL VERDICT")
        print("="*80)
        
        if results['missing'] == 0:
            print("\n✅ SUCCESS: All Phase 13 endpoints that should be migrated are covered in Phase 13.5 modules!")
            print(f"   - {results['covered']} endpoints successfully migrated")
            print(f"   - {results['not_migrated_yet']} endpoints remain in other routers (as expected)")
            return True
        else:
            print(f"\n❌ FAILURE: {results['missing']} endpoint(s) missing from Phase 13.5 modules!")
            print("   These endpoints need to be added to the appropriate modules.")
            return False
    
    def run(self) -> bool:
        """Run the full verification"""
        print("\n" + "="*80)
        print("PHASE 13 TO PHASE 13.5 ENDPOINT COVERAGE VERIFICATION")
        print("="*80)
        
        self.scan_routers_directory()
        self.scan_modules_directory()
        results = self.compare_coverage()
        success = self.print_results(results)
        
        return success


def main():
    """Main entry point"""
    verifier = EndpointVerifier()
    success = verifier.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
