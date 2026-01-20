#!/usr/bin/env python3
"""
Resource Migration Script for Advanced RAG Architecture

This script migrates existing resources to the new chunking system by:
1. Querying all resources without chunks
2. Processing resources in batches
3. Calling ChunkingService for each resource
4. Tracking progress and handling errors
5. Supporting resume from last processed resource

Usage:
    python scripts/migrate_existing_resources.py [--batch-size 10] [--strategy semantic] [--resume]

Requirements: 5.9, 5.10
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, select, exists
from sqlalchemy.orm import sessionmaker, Session

from app.database.models import Resource, DocumentChunk
from app.modules.resources.service import ChunkingService
from app.config.settings import get_settings
from app.shared.embeddings import EmbeddingGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Progress tracking file
PROGRESS_FILE = Path("storage/migration_progress.json")


class MigrationProgress:
    """Track migration progress for resume capability."""

    def __init__(self, progress_file: Path = PROGRESS_FILE):
        """
        Initialize progress tracker.

        Args:
            progress_file: Path to progress tracking file
        """
        self.progress_file = progress_file
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> Dict:
        """Load progress from file."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load progress file: {e}")
                return self._default_data()
        return self._default_data()

    def _default_data(self) -> Dict:
        """Return default progress data structure."""
        return {
            "last_processed_id": None,
            "processed_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "failed_resources": [],
            "started_at": None,
            "last_updated_at": None,
        }

    def save(self):
        """Save progress to file."""
        try:
            self.data["last_updated_at"] = datetime.now(timezone.utc).isoformat()
            with open(self.progress_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")

    def start(self):
        """Mark migration as started."""
        if not self.data["started_at"]:
            self.data["started_at"] = datetime.now(timezone.utc).isoformat()
            self.save()

    def update(self, resource_id: str, success: bool, error: Optional[str] = None):
        """
        Update progress after processing a resource.

        Args:
            resource_id: ID of processed resource
            success: Whether processing succeeded
            error: Error message if failed
        """
        self.data["last_processed_id"] = resource_id
        self.data["processed_count"] += 1

        if success:
            self.data["success_count"] += 1
        else:
            self.data["failure_count"] += 1
            self.data["failed_resources"].append(
                {
                    "resource_id": resource_id,
                    "error": error,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        self.save()

    def get_last_processed_id(self) -> Optional[str]:
        """Get ID of last processed resource for resume."""
        return self.data.get("last_processed_id")

    def get_summary(self) -> Dict:
        """Get migration summary."""
        return {
            "processed": self.data["processed_count"],
            "success": self.data["success_count"],
            "failed": self.data["failure_count"],
            "started_at": self.data["started_at"],
            "last_updated_at": self.data["last_updated_at"],
        }


def get_resources_without_chunks(
    db: Session, batch_size: int = 10, last_processed_id: Optional[str] = None
) -> List[Resource]:
    """
    Query resources that don't have chunks.

    Args:
        db: Database session
        batch_size: Number of resources to return
        last_processed_id: ID of last processed resource (for resume)

    Returns:
        List of resources without chunks
    """
    # Build query for resources without chunks
    # Use NOT EXISTS subquery to find resources with no chunks
    subquery = select(DocumentChunk.resource_id).where(
        DocumentChunk.resource_id == Resource.id
    )

    query = (
        select(Resource)
        .where(~exists(subquery))
        .where(Resource.ingestion_status == "completed")
        .order_by(Resource.created_at.asc())
    )

    # If resuming, skip resources up to last processed
    if last_processed_id:
        try:
            import uuid as uuid_module

            last_uuid = uuid_module.UUID(last_processed_id)
            # Get the created_at timestamp of the last processed resource
            last_resource = db.query(Resource).filter(Resource.id == last_uuid).first()
            if last_resource:
                # Only get resources created after the last processed one
                query = query.where(Resource.created_at > last_resource.created_at)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid last_processed_id: {e}")

    # Limit to batch size
    query = query.limit(batch_size)

    # Execute query
    result = db.execute(query)
    resources = result.scalars().all()

    return list(resources)


def load_resource_content(resource: Resource) -> Optional[str]:
    """
    Load resource content from archive.

    Args:
        resource: Resource to load content for

    Returns:
        Content text or None if not available
    """
    try:
        # Content is archived to disk, identifier contains the archive path
        if not resource.identifier:
            logger.warning(f"Resource {resource.id} has no archive path")
            return None

        archive_path = Path(resource.identifier)

        # Look for text file in archive
        text_file = archive_path / "text.txt"
        if text_file.exists():
            with open(text_file, "r", encoding="utf-8") as f:
                return f.read()

        logger.warning(f"No text file found in archive: {archive_path}")
        return None

    except Exception as e:
        logger.error(f"Failed to load content for resource {resource.id}: {e}")
        return None


def chunk_resource(
    db: Session, resource: Resource, chunking_service: ChunkingService
) -> Tuple[bool, Optional[str]]:
    """
    Chunk a single resource.

    Args:
        db: Database session
        resource: Resource to chunk
        chunking_service: ChunkingService instance

    Returns:
        Tuple of (success, error_message)
    """
    try:
        resource_id = str(resource.id)
        logger.info(f"Chunking resource {resource_id}: {resource.title}")

        # Load resource content from archive
        content = load_resource_content(resource)
        if not content or not content.strip():
            logger.warning(f"Resource {resource_id} has no content, skipping")
            return True, None  # Not an error, just skip

        # Prepare chunk metadata (if available)
        chunk_metadata = {}
        # Add basic metadata
        if resource.format:
            chunk_metadata["format"] = resource.format

        # Chunk the resource
        chunks = chunking_service.chunk_resource(
            resource_id=resource_id, content=content, chunk_metadata=chunk_metadata
        )

        logger.info(
            f"Successfully chunked resource {resource_id}: {len(chunks)} chunks created"
        )
        return True, None

    except Exception as e:
        error_msg = f"Failed to chunk resource {resource.id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg


def migrate_resources(
    batch_size: int = 10,
    strategy: str = "semantic",
    chunk_size: int = 500,
    overlap: int = 50,
    resume: bool = False,
):
    """
    Migrate existing resources to chunking system.

    Args:
        batch_size: Number of resources to process per batch
        strategy: Chunking strategy ("semantic" or "fixed")
        chunk_size: Target chunk size
        overlap: Overlap size between chunks
        resume: Whether to resume from last processed resource
    """
    logger.info("=" * 80)
    logger.info("Starting Resource Migration to Advanced RAG Architecture")
    logger.info("=" * 80)
    logger.info("Configuration:")
    logger.info(f"  Batch size: {batch_size}")
    logger.info(f"  Strategy: {strategy}")
    logger.info(f"  Chunk size: {chunk_size}")
    logger.info(f"  Overlap: {overlap}")
    logger.info(f"  Resume: {resume}")
    logger.info("=" * 80)

    # Initialize progress tracker
    progress = MigrationProgress()

    # Check if resuming
    last_processed_id = None
    if resume:
        last_processed_id = progress.get_last_processed_id()
        if last_processed_id:
            logger.info(f"Resuming from last processed resource: {last_processed_id}")
            summary = progress.get_summary()
            logger.info(f"Previous progress: {summary}")
        else:
            logger.info("No previous progress found, starting fresh")
    else:
        # Reset progress if not resuming
        progress.data = progress._default_data()
        progress.save()

    progress.start()

    # Get database settings
    settings = get_settings()
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)

    # Initialize embedding service (shared across all chunks)
    embedding_service = EmbeddingGenerator()

    total_processed = 0
    total_success = 0
    total_failed = 0

    try:
        while True:
            # Create new session for each batch
            db = SessionLocal()

            try:
                # Get next batch of resources
                resources = get_resources_without_chunks(
                    db=db, batch_size=batch_size, last_processed_id=last_processed_id
                )

                if not resources:
                    logger.info("No more resources to process")
                    break

                logger.info(f"\nProcessing batch of {len(resources)} resources...")

                # Initialize chunking service for this batch
                chunking_service = ChunkingService(
                    db=db,
                    strategy=strategy,
                    chunk_size=chunk_size,
                    overlap=overlap,
                    parser_type="text",
                    embedding_service=embedding_service,
                )

                # Process each resource in batch
                for resource in resources:
                    resource_id = str(resource.id)

                    # Chunk resource
                    success, error = chunk_resource(db, resource, chunking_service)

                    # Update progress
                    progress.update(resource_id, success, error)
                    last_processed_id = resource_id

                    # Update counters
                    total_processed += 1
                    if success:
                        total_success += 1
                    else:
                        total_failed += 1

                    # Log progress
                    logger.info(
                        f"Progress: {total_processed} processed, "
                        f"{total_success} success, {total_failed} failed"
                    )

            finally:
                # Always close session
                db.close()

            # Log batch completion
            logger.info("Batch complete. Continuing to next batch...")

    except KeyboardInterrupt:
        logger.info("\nMigration interrupted by user")
        logger.info("Progress has been saved. Use --resume to continue")

    except Exception as e:
        logger.error(f"Migration failed with error: {e}", exc_info=True)

    finally:
        # Print final summary
        logger.info("\n" + "=" * 80)
        logger.info("Migration Summary")
        logger.info("=" * 80)
        summary = progress.get_summary()
        logger.info(f"Total processed: {summary['processed']}")
        logger.info(f"Successful: {summary['success']}")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"Started at: {summary['started_at']}")
        logger.info(f"Last updated: {summary['last_updated_at']}")

        if summary["failed"] > 0:
            logger.info("\nFailed resources:")
            for failure in progress.data["failed_resources"][-10:]:  # Show last 10
                logger.info(f"  - {failure['resource_id']}: {failure['error']}")
            if len(progress.data["failed_resources"]) > 10:
                logger.info(
                    f"  ... and {len(progress.data['failed_resources']) - 10} more"
                )

        logger.info("=" * 80)
        logger.info(f"Progress saved to: {PROGRESS_FILE}")
        logger.info("Use --resume to continue from last processed resource")
        logger.info("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate existing resources to Advanced RAG chunking system"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of resources to process per batch (default: 10)",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["semantic", "fixed"],
        default="semantic",
        help="Chunking strategy (default: semantic)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Target chunk size in tokens/characters (default: 500)",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=50,
        help="Overlap size between chunks (default: 50)",
    )
    parser.add_argument(
        "--resume", action="store_true", help="Resume from last processed resource"
    )

    args = parser.parse_args()

    # Run migration
    migrate_resources(
        batch_size=args.batch_size,
        strategy=args.strategy,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()
