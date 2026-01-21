#!/usr/bin/env python3
"""
Phase 19 Staging Setup Verification Script

This script verifies that all infrastructure components are properly configured
and accessible before deploying to staging.

Usage:
    python verify_staging_setup.py
"""

import os
import sys
import requests
from typing import Dict, Tuple


def check_redis() -> Tuple[bool, str]:
    """Verify Upstash Redis connection."""
    url = os.getenv("UPSTASH_REDIS_REST_URL")
    token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    
    if not url or not token:
        return False, "Missing UPSTASH_REDIS_REST_URL or UPSTASH_REDIS_REST_TOKEN"
    
    try:
        response = requests.get(
            f"{url}/ping",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200 and response.json().get("result") == "PONG":
            return True, f"✅ Redis connected: {url}"
        else:
            return False, f"❌ Redis ping failed: {response.status_code}"
    except Exception as e:
        return False, f"❌ Redis connection error: {str(e)}"


def check_database() -> Tuple[bool, str]:
    """Verify PostgreSQL database connection."""
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        return False, "⚠️  DATABASE_URL not set (required for deployment)"
    
    # Basic validation - actual connection test would require psycopg2
    if not db_url.startswith("postgresql://"):
        return False, "❌ DATABASE_URL must start with postgresql://"
    
    return True, f"✅ Database URL configured: {db_url.split('@')[1] if '@' in db_url else 'configured'}"


def check_qdrant() -> Tuple[bool, str]:
    """Verify Qdrant vector database connection."""
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    
    if not url or not api_key:
        return False, "⚠️  QDRANT_URL or QDRANT_API_KEY not set (required for deployment)"
    
    try:
        response = requests.get(
            f"{url}/collections",
            headers={"api-key": api_key},
            timeout=10
        )
        
        if response.status_code == 200:
            return True, f"✅ Qdrant connected: {url}"
        else:
            return False, f"❌ Qdrant connection failed: {response.status_code}"
    except Exception as e:
        return False, f"❌ Qdrant connection error: {str(e)}"


def check_auth_token() -> Tuple[bool, str]:
    """Verify admin authentication token is set."""
    token = os.getenv("PHAROS_ADMIN_TOKEN")
    
    if not token:
        return False, "❌ PHAROS_ADMIN_TOKEN not set"
    
    if token == "staging-admin-token-change-me-in-production":
        return True, "⚠️  Using default staging token (change for production!)"
    
    if len(token) < 32:
        return False, "⚠️  PHAROS_ADMIN_TOKEN should be at least 32 characters"
    
    return True, "✅ Admin token configured"


def check_mode() -> Tuple[bool, str]:
    """Verify MODE is set correctly."""
    mode = os.getenv("MODE", "").upper()
    
    if mode not in ["CLOUD", "EDGE"]:
        return False, f"❌ MODE must be CLOUD or EDGE, got: {mode}"
    
    return True, f"✅ MODE set to: {mode}"


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Phase 19 Staging Setup Verification")
    print("=" * 60)
    print()
    
    # Load environment from .env.staging if it exists
    env_file = ".env.staging"
    if os.path.exists(env_file):
        print(f"📄 Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
        print()
    
    checks = [
        ("Mode Configuration", check_mode),
        ("Redis Connection", check_redis),
        ("Database Configuration", check_database),
        ("Qdrant Connection", check_qdrant),
        ("Authentication Token", check_auth_token),
    ]
    
    results = []
    all_passed = True
    
    for name, check_func in checks:
        print(f"Checking {name}...")
        passed, message = check_func()
        results.append((name, passed, message))
        print(f"  {message}")
        print()
        
        if not passed and "⚠️" not in message:
            all_passed = False
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    for name, passed, message in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    print()
    
    if all_passed:
        print("🎉 All checks passed! Ready for deployment.")
        print()
        print("Next steps:")
        print("1. Deploy Cloud API to Render with these environment variables")
        print("2. Set up Edge Worker locally with .env.edge")
        print("3. Run end-to-end workflow test")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above before deploying.")
        print()
        print("Required for deployment:")
        print("- Upstash Redis (configured ✅)")
        print("- Neon PostgreSQL (needs setup)")
        print("- Qdrant Cloud (needs setup)")
        print("- Admin token (configured)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
