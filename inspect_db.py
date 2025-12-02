import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, inspect
from backend.app.config.settings import get_settings

try:
    settings = get_settings()
    print(f"Database URL: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    if 'resources' in inspector.get_table_names():
        print("Table 'resources' exists.")
        columns = inspector.get_columns('resources')
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
    else:
        print("Table 'resources' does NOT exist.")
        
except Exception as e:
    print(f"Error: {e}")
