#!/usr/bin/env python3
"""Test if auth module can be imported."""

import sys
import os

# Set MODE to CLOUD to simulate cloud environment
os.environ["MODE"] = "CLOUD"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

print("Testing auth module import...")
print(f"MODE: {os.environ.get('MODE')}")
print()

try:
    print("1. Importing shared.oauth2...")
    from app.shared.oauth2 import GoogleOAuth2Provider, GitHubOAuth2Provider
    print("   ✓ oauth2 imported successfully")
except Exception as e:
    print(f"   ✗ Failed to import oauth2: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("2. Importing auth.service...")
    from app.modules.auth.service import authenticate_user
    print("   ✓ auth.service imported successfully")
except Exception as e:
    print(f"   ✗ Failed to import auth.service: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("3. Importing auth.router...")
    from app.modules.auth.router import router
    print("   ✓ auth.router imported successfully")
    print(f"   Router prefix: {router.prefix}")
    print(f"   Router tags: {router.tags}")
except Exception as e:
    print(f"   ✗ Failed to import auth.router: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("4. Importing auth module...")
    from app.modules.auth import router as auth_router
    print("   ✓ auth module imported successfully")
    print(f"   Router: {auth_router}")
except Exception as e:
    print(f"   ✗ Failed to import auth module: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("✓ All auth module imports successful!")
print()
print("Auth module should work in cloud deployment.")
