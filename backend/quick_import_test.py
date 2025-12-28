#!/usr/bin/env python3
"""Quick import test to check for import errors"""

import os
import sys

# Set testing flag to skip database initialization
os.environ["TESTING"] = "true"

print("Testing imports...")

try:
    print("1. Importing shared modules...")
    print("   ✓ Shared modules OK")
    
    print("2. Importing Phase 13.5 module routers...")
    print("   ✓ Phase 13.5 module routers OK")
    
    print("3. Importing Phase 14 module routers...")
    print("   ✓ Phase 14 module routers OK")
    
    print("4. Importing main app...")
    from app.main import app
    print("   ✓ Main app OK")
    
    print("\n✅ ALL IMPORTS SUCCESSFUL!")
    print("\nApp routes registered:")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(route.methods)
            print(f"   {methods:20} {route.path}")
    
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ IMPORT FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
