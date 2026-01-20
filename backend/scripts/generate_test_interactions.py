"""
Generate synthetic test interaction data for Phase 11 NCF model training.

This script creates test users and interactions for demonstration purposes.
"""

import sys
import uuid
from datetime import datetime, timedelta
import random
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config.settings import get_settings
from backend.app.database.models import User, UserInteraction, Resource


def generate_test_data(num_users=10, interactions_per_user=20):
    """
    Generate synthetic test data for NCF training.

    Args:
        num_users: Number of test users to create
        interactions_per_user: Average interactions per user

    Returns:
        Dictionary with generation results
    """
    try:
        print("=" * 60)
        print("Test Data Generation Script - Phase 11")
        print("=" * 60)
        print()

        # Create database session
        settings = get_settings()
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()

        # Check for existing resources
        print("Checking for existing resources...")
        resources = db.query(Resource).limit(100).all()

        if len(resources) < 10:
            print(f"[WARNING] Only {len(resources)} resources found in database.")
            print("Need at least 10 resources to generate meaningful interactions.")
            print("Please ingest some resources first.")
            return {"success": False, "error": "Insufficient resources"}

        print(f"Found {len(resources)} resources")
        print()

        # Generate test users
        print(f"Generating {num_users} test users...")
        users_created = []

        for i in range(num_users):
            user_id = str(uuid.uuid4())
            username = f"test_user_{i + 1}"
            email = f"test_user_{i + 1}@example.com"

            # Check if user already exists
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                print(f"  User {username} already exists, skipping...")
                users_created.append(existing)
                continue

            user = User(
                id=user_id, email=email, username=username, created_at=datetime.utcnow()
            )
            db.add(user)
            users_created.append(user)
            print(f"  Created user: {username}")

        db.commit()
        print(f"[OK] Created {len(users_created)} users")
        print()

        # Generate interactions
        print(f"Generating interactions (avg {interactions_per_user} per user)...")
        interactions_created = 0

        interaction_types = ["view", "annotation", "collection_add", "export"]

        for user in users_created:
            # Random number of interactions per user
            num_interactions = random.randint(
                interactions_per_user - 5, interactions_per_user + 5
            )

            # Select random resources for this user
            user_resources = random.sample(
                resources, min(num_interactions, len(resources))
            )

            for resource in user_resources:
                # Random interaction type
                interaction_type = random.choice(interaction_types)

                # Compute interaction strength based on type
                if interaction_type == "view":
                    dwell_time = random.randint(10, 300)  # 10-300 seconds
                    scroll_depth = random.uniform(0.3, 1.0)
                    interaction_strength = (
                        0.1 + min(0.3, dwell_time / 1000) + 0.1 * scroll_depth
                    )
                elif interaction_type == "annotation":
                    dwell_time = random.randint(60, 600)
                    scroll_depth = random.uniform(0.7, 1.0)
                    interaction_strength = 0.7
                elif interaction_type == "collection_add":
                    dwell_time = random.randint(30, 180)
                    scroll_depth = random.uniform(0.5, 1.0)
                    interaction_strength = 0.8
                else:  # export
                    dwell_time = random.randint(20, 120)
                    scroll_depth = random.uniform(0.6, 1.0)
                    interaction_strength = 0.9

                # Determine if positive
                is_positive = 1 if interaction_strength > 0.4 else 0

                # Random timestamp in the past 30 days
                days_ago = random.randint(0, 30)
                interaction_time = datetime.utcnow() - timedelta(days=days_ago)

                interaction = UserInteraction(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    resource_id=resource.id,
                    interaction_type=interaction_type,
                    interaction_strength=interaction_strength,
                    dwell_time=dwell_time,
                    scroll_depth=scroll_depth,
                    annotation_count=1 if interaction_type == "annotation" else 0,
                    return_visits=0,
                    session_id=str(uuid.uuid4()),
                    interaction_timestamp=interaction_time,
                    is_positive=is_positive,
                    confidence=random.uniform(0.7, 1.0),
                    created_at=interaction_time,
                    updated_at=interaction_time,
                )

                db.add(interaction)
                interactions_created += 1

            print(f"  User {user.username}: {len(user_resources)} interactions")

        db.commit()
        print()
        print(f"[OK] Created {interactions_created} interactions")
        print()

        # Summary
        positive_count = (
            db.query(UserInteraction).filter(UserInteraction.is_positive == 1).count()
        )

        print("=" * 60)
        print("Generation Complete")
        print("=" * 60)
        print(f"Users created: {len(users_created)}")
        print(f"Total interactions: {interactions_created}")
        print(f"Positive interactions: {positive_count}")
        print()
        print("You can now train the NCF model with:")
        print("  python scripts/train_ncf_model.py")

        return {
            "success": True,
            "users_created": len(users_created),
            "interactions_created": interactions_created,
            "positive_interactions": positive_count,
        }

    except Exception as e:
        print(f"[ERROR] Error generating test data: {str(e)}")
        import traceback

        traceback.print_exc()
        if "db" in locals():
            db.rollback()
        return {"success": False, "error": str(e)}

    finally:
        if "db" in locals():
            db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate test interaction data")
    parser.add_argument("--users", type=int, default=10, help="Number of test users")
    parser.add_argument(
        "--interactions", type=int, default=20, help="Avg interactions per user"
    )

    args = parser.parse_args()

    results = generate_test_data(
        num_users=args.users, interactions_per_user=args.interactions
    )

    sys.exit(0 if results.get("success") else 1)
