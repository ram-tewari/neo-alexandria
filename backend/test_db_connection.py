"""
Test database connection
"""
import os
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment or use default
database_url = os.getenv("DATABASE_URL", "postgresql://postgres:devpassword@localhost:5432/neo_alexandria_dev")

print(f"Testing connection to: {database_url}")

try:
    engine = create_engine(database_url, echo=False)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ Connection successful!")
        print(f"PostgreSQL version: {version}")
        
        # Test if we can query resources table
        result = conn.execute(text("SELECT COUNT(*) FROM resources"))
        count = result.fetchone()[0]
        print(f"✅ Resources table accessible, count: {count}")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()
