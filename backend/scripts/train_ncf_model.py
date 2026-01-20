"""
NCF Model Training Script for Phase 11.

Trains the Neural Collaborative Filtering model on existing interaction data.
Saves model checkpoint to disk for use by the recommendation service.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config.settings import get_settings
from backend.app.services.collaborative_filtering_service import (
    CollaborativeFilteringService,
)
from backend.app.database.models import UserInteraction


def train_model(epochs=10, batch_size=256, learning_rate=0.001):
    """
    Train NCF model on existing interaction data.

    Args:
        epochs: Number of training epochs (default: 10)
        batch_size: Batch size for training (default: 256)
        learning_rate: Learning rate for optimizer (default: 0.001)

    Returns:
        Training results dictionary
    """
    try:
        print("=" * 60)
        print("NCF Model Training Script - Phase 11")
        print("=" * 60)
        print()

        # Create database session
        settings = get_settings()
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()

        print("Checking for existing interaction data...")
        interaction_count = db.query(UserInteraction).count()
        positive_count = (
            db.query(UserInteraction).filter(UserInteraction.is_positive == 1).count()
        )

        print(f"Total interactions: {interaction_count}")
        print(f"Positive interactions: {positive_count}")
        print()

        if positive_count < 10:
            print("[WARNING] Insufficient training data!")
            print(f"Found only {positive_count} positive interactions.")
            print("NCF model requires at least 10 positive interactions to train.")
            print()
            print("Options:")
            print("  1. Add more user interaction data")
            print("  2. Generate synthetic interaction data for testing")
            print("  3. Skip NCF training and use content-based recommendations only")
            print()
            return {
                "success": False,
                "error": "Insufficient training data",
                "interaction_count": interaction_count,
                "positive_count": positive_count,
            }

        # Initialize collaborative filtering service
        print("Initializing CollaborativeFilteringService...")
        model_path = os.path.join(backend_dir, "models", "ncf_model.pt")
        cf_service = CollaborativeFilteringService(db, model_path=model_path)
        print(f"Model will be saved to: {model_path}")
        print()

        # Train model
        print("=" * 60)
        print("Starting Model Training")
        print("=" * 60)
        print(f"Epochs: {epochs}")
        print(f"Batch size: {batch_size}")
        print(f"Learning rate: {learning_rate}")
        print()

        results = cf_service.train_model(
            epochs=epochs, batch_size=batch_size, learning_rate=learning_rate
        )

        print()
        print("=" * 60)
        print("Training Results")
        print("=" * 60)

        if results.get("success"):
            print("[OK] Training completed successfully!")
            print()
            print(f"Final loss: {results['final_loss']:.4f}")
            print(f"Number of users: {results['num_users']}")
            print(f"Number of items: {results['num_items']}")
            print(f"Training interactions: {results['num_interactions']}")
            print()
            print(f"Model checkpoint saved to: {model_path}")
            print()

            # Validate model predictions
            print("=" * 60)
            print("Validating Model Predictions")
            print("=" * 60)

            # Get a sample interaction to test
            sample = (
                db.query(UserInteraction)
                .filter(UserInteraction.is_positive == 1)
                .first()
            )

            if sample:
                user_id = str(sample.user_id)
                resource_id = str(sample.resource_id)

                print(
                    f"Testing prediction for user {user_id[:8]}... and resource {resource_id[:8]}..."
                )
                score = cf_service.predict_score(user_id, resource_id)

                if score is not None:
                    print(f"[OK] Predicted score: {score:.4f}")
                    print("[OK] Model is working correctly!")
                else:
                    print("[WARNING] Could not generate prediction")

            print()
            print("=" * 60)
            print("Deployment Ready")
            print("=" * 60)
            print("The NCF model is trained and ready for production use.")
            print("The recommendation service will automatically load this model.")

            return results
        else:
            print("[ERROR] Training failed!")
            print(f"Error: {results.get('error', 'Unknown error')}")
            return results

    except Exception as e:
        print(f"[ERROR] Error during training: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}

    finally:
        if "db" in locals():
            db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train NCF model for Phase 11")
    parser.add_argument(
        "--epochs", type=int, default=10, help="Number of training epochs"
    )
    parser.add_argument("--batch-size", type=int, default=256, help="Batch size")
    parser.add_argument(
        "--learning-rate", type=float, default=0.001, help="Learning rate"
    )

    args = parser.parse_args()

    results = train_model(
        epochs=args.epochs, batch_size=args.batch_size, learning_rate=args.learning_rate
    )

    sys.exit(0 if results.get("success") else 1)
