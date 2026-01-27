"""Quick script to check database contents"""
from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///./backend.db')
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM resources'))
    print(f'Resources: {result.scalar()}')
    result = conn.execute(text('SELECT COUNT(*) FROM annotations'))
    print(f'Annotations: {result.scalar()}')
