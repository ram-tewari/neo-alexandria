"""
Generate a test auth token for API testing
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

def generate_token():
    """Generate a JWT token for testing"""
    try:
        from app.shared.security import create_access_token
        from app.config.settings import get_settings
        
        settings = get_settings()
        
        # Create token for test user
        token_data = {
            "sub": "test@example.com",
            "user_id": "test-user-123",
            "tier": "free"
        }
        
        # Generate token (valid for 30 days for testing)
        token = create_access_token(
            data=token_data,
            expires_delta=timedelta(days=30)
        )
        
        print("="*60)
        print("TEST AUTH TOKEN GENERATED")
        print("="*60)
        print(f"\nToken: {token}")
        print(f"\nValid for: 30 days")
        print(f"User: test@example.com")
        print(f"Tier: free")
        print("\nUse this token in your API requests:")
        print(f'  Authorization: Bearer {token}')
        print("="*60)
        
        return token
        
    except Exception as e:
        print(f"Error generating token: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    token = generate_token()
    if token:
        # Save to file for easy access
        with open("test_token.txt", "w") as f:
            f.write(token)
        print("\nToken saved to: test_token.txt")
        sys.exit(0)
    else:
        sys.exit(1)
