#!/usr/bin/env python3
"""Direct test of resource insertion"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Resource
import uuid
from datetime import datetime, timezone

# Create engine
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

session = SessionLocal()

try:
    resource = Resource(
        title="Test",
        source="https://test.com",
    )
    session.add(resource)
    session.commit()
    print(f"✅ SUCCESS: Created resource {resource.id}")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    session.rollback()
finally:
    session.close()
