"""
Create a test user and generate an access token for API testing.
Run with: python create_test_user.py
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.shared.database import init_database, SessionLocal
from app.database import models as db_models
from app.shared.security import get_password_hash, create_access_token
from datetime import timedelta

def create_test_user():
    """Create a test user and return an access token."""
    # Initialize database
    init_database()
    
    # Import after init
    from app.shared.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Check if test user exists
        test_email = "test@example.com"
        user = db.query(db_models.User).filter(db_models.User.email == test_email).first()
        
        if not user:
            # Create test user
            user = db_models.User(
                email=test_email,
                username="testuser",
                hashed_password=get_password_hash("testpassword123"),
                is_active=True,
                tier="premium"  # Give premium tier for testing
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✓ Created test user: {test_email}")
        else:
            print(f"✓ Test user already exists: {test_email}")
        
        # Generate access token with all required fields
        access_token = create_access_token(
            data={
                "sub": user.email,
                "user_id": str(user.id),        # Required by security.py (UUID as string)
                "username": user.username,      # Required by security.py
                "tier": user.tier,              # Include tier for rate limiting
                "scopes": []                    # Empty scopes for now
            },
            expires_delta=timedelta(days=7)  # 7 day token for testing
        )
        
        print(f"\n{'='*60}")
        print(f"Access Token (valid for 7 days):")
        print(f"{'='*60}")
        print(access_token)
        print(f"{'='*60}")
        print(f"\nUse this token in your requests:")
        print(f'Authorization: Bearer {access_token}')
        print(f"\nOr set in localStorage:")
        print(f"localStorage.setItem('access_token', '{access_token}');")
        
        return access_token
        
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
