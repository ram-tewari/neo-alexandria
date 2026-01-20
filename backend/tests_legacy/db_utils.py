"""
Database utility functions for optimized test data creation.

This module provides helper functions for efficient database operations
in tests, including batch inserts, bulk deletes, and minimal data creation.
"""

from typing import List, Dict, Any, Type, TypeVar
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.app.database.models import Resource, AuthoritySubject, TaxonomyNode
from backend.app.domain.quality import QualityScore


T = TypeVar("T")


def batch_insert(db: Session, objects: List[Any]) -> List[Any]:
    """
    Batch insert multiple objects into the database.

    This is much faster than individual inserts as it uses a single
    database transaction and minimizes round trips.

    Args:
        db: Database session
        objects: List of SQLAlchemy model instances to insert

    Returns:
        List of inserted objects with IDs populated

    Example:
        resources = [Resource(title=f"Resource {i}") for i in range(10)]
        inserted = batch_insert(db, resources)
    """
    if not objects:
        return []

    db.add_all(objects)
    db.commit()

    # Refresh all objects to get IDs
    for obj in objects:
        db.refresh(obj)

    return objects


def bulk_delete(db: Session, model: Type[T], ids: List[Any]) -> int:
    """
    Bulk delete objects by ID.

    This is much faster than individual deletes as it uses a single
    DELETE query with an IN clause.

    Args:
        db: Database session
        model: SQLAlchemy model class
        ids: List of IDs to delete

    Returns:
        Number of rows deleted

    Example:
        deleted_count = bulk_delete(db, Resource, resource_ids)
    """
    if not ids:
        return 0

    try:
        count = (
            db.query(model).filter(model.id.in_(ids)).delete(synchronize_session=False)
        )
        db.commit()
        return count
    except Exception:
        db.rollback()
        raise


def create_minimal_resource(
    title: str = "Test Resource", quality_score: float = 0.8, **kwargs
) -> Resource:
    """
    Create a Resource with minimal required fields.

    This creates a resource with only the essential fields populated,
    which is faster than creating resources with all fields.

    Args:
        title: Resource title
        quality_score: Overall quality score (0.0-1.0)
        **kwargs: Additional fields to set on the resource

    Returns:
        Resource instance (not yet persisted to database)

    Example:
        resource = create_minimal_resource(
            title="My Resource",
            quality_score=0.9,
            language="en"
        )
        db.add(resource)
        db.commit()
    """
    # Set defaults for required fields
    defaults = {
        "description": "Test description",
        "type": "article",
        "language": "en",
        "quality_score": quality_score,
        "quality_overall": quality_score,
        "quality_accuracy": min(1.0, quality_score + 0.02),
        "quality_completeness": min(1.0, quality_score - 0.01),
        "quality_consistency": min(1.0, quality_score + 0.01),
        "quality_timeliness": min(1.0, quality_score - 0.02),
        "quality_relevance": min(1.0, quality_score + 0.03),
    }

    # Override defaults with provided kwargs
    defaults.update(kwargs)

    return Resource(title=title, **defaults)


def create_minimal_resources_batch(
    count: int = 10,
    base_quality: float = 0.7,
    quality_increment: float = 0.05,
    **common_kwargs,
) -> List[Resource]:
    """
    Create multiple resources with minimal fields in batch.

    This is optimized for creating test data quickly by using
    minimal fields and preparing all objects in memory before
    database insertion.

    Args:
        count: Number of resources to create
        base_quality: Starting quality score
        quality_increment: Amount to increment quality for each resource
        **common_kwargs: Common fields to set on all resources

    Returns:
        List of Resource instances (not yet persisted to database)

    Example:
        resources = create_minimal_resources_batch(
            count=5,
            base_quality=0.8,
            language="en"
        )
        batch_insert(db, resources)
    """
    resources = []
    for i in range(count):
        quality = min(1.0, base_quality + i * quality_increment)
        resource = create_minimal_resource(
            title=f"Test Resource {i}", quality_score=quality, **common_kwargs
        )
        resources.append(resource)

    return resources


def create_resource_with_quality_score(
    title: str, quality_score: QualityScore, **kwargs
) -> Resource:
    """
    Create a Resource from a QualityScore domain object.

    This helper converts a QualityScore domain object into the
    individual quality dimension fields required by the Resource model.

    Args:
        title: Resource title
        quality_score: QualityScore domain object
        **kwargs: Additional fields to set on the resource

    Returns:
        Resource instance (not yet persisted to database)

    Example:
        quality = QualityScore(0.9, 0.85, 0.88, 0.92, 0.9)
        resource = create_resource_with_quality_score(
            "My Resource",
            quality,
            language="en"
        )
        db.add(resource)
        db.commit()
    """
    defaults = {
        "description": "Test description",
        "type": "article",
        "language": "en",
        "quality_score": quality_score.overall_score(),
        "quality_overall": quality_score.overall_score(),
        "quality_accuracy": quality_score.accuracy,
        "quality_completeness": quality_score.completeness,
        "quality_consistency": quality_score.consistency,
        "quality_timeliness": quality_score.timeliness,
        "quality_relevance": quality_score.relevance,
        "quality_last_computed": datetime.now(timezone.utc),
        "quality_computation_version": "v2.0",
    }

    defaults.update(kwargs)

    return Resource(title=title, **defaults)


def create_minimal_authority_subject(
    canonical_form: str, usage_count: int = 1, **kwargs
) -> AuthoritySubject:
    """
    Create an AuthoritySubject with minimal required fields.

    Args:
        canonical_form: Canonical form of the subject
        usage_count: Usage count
        **kwargs: Additional fields to set

    Returns:
        AuthoritySubject instance (not yet persisted to database)

    Example:
        subject = create_minimal_authority_subject(
            "Machine Learning",
            usage_count=100
        )
        db.add(subject)
        db.commit()
    """
    defaults = {
        "variants": [canonical_form.lower()],
        "usage_count": usage_count,
    }

    defaults.update(kwargs)

    return AuthoritySubject(canonical_form=canonical_form, **defaults)


def create_minimal_taxonomy_node(code: str, label: str, **kwargs) -> TaxonomyNode:
    """
    Create a TaxonomyNode with minimal required fields.

    Args:
        code: Taxonomy code (e.g., "004")
        label: Node label
        **kwargs: Additional fields to set

    Returns:
        TaxonomyNode instance (not yet persisted to database)

    Example:
        node = create_minimal_taxonomy_node(
            "004",
            "Computer Science"
        )
        db.add(node)
        db.commit()
    """
    defaults = {
        "level": len(code.split(".")),
        "parent_code": None,
    }

    defaults.update(kwargs)

    return TaxonomyNode(code=code, label=label, **defaults)


def cleanup_test_data(db: Session, *model_id_pairs):
    """
    Clean up test data with bulk deletes.

    This helper performs bulk deletes for multiple model types
    in a single transaction, which is much faster than individual
    deletes.

    Args:
        db: Database session
        *model_id_pairs: Tuples of (Model, [ids]) to delete

    Example:
        cleanup_test_data(
            db,
            (Resource, resource_ids),
            (AuthoritySubject, subject_ids),
            (TaxonomyNode, node_ids)
        )
    """
    try:
        for model, ids in model_id_pairs:
            if ids:
                db.query(model).filter(model.id.in_(ids)).delete(
                    synchronize_session=False
                )
        db.commit()
    except Exception:
        db.rollback()
        raise


# ============================================================================
# Database Migration and Setup Utilities
# ============================================================================


def run_migrations(engine, alembic_ini_path: str = None):
    """
    Run Alembic migrations to create database schema.

    This function executes all Alembic migrations up to the latest version,
    ensuring the test database schema matches the production schema exactly.

    Args:
        engine: SQLAlchemy engine
        alembic_ini_path: Path to alembic.ini file (optional, auto-detected if None)

    Example:
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///:memory:")
        run_migrations(engine)
    """
    from alembic import command
    from alembic.config import Config
    from pathlib import Path

    # Auto-detect alembic.ini path if not provided
    if alembic_ini_path is None:
        backend_dir = Path(__file__).parent.parent
        alembic_ini_path = backend_dir / "alembic.ini"

    if not Path(alembic_ini_path).exists():
        raise FileNotFoundError(f"Alembic config not found at {alembic_ini_path}")

    # Configure Alembic
    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url))

    # Run migrations using the existing connection
    with engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")


def verify_tables_exist(engine, required_tables: List[str] = None) -> Dict[str, bool]:
    """
    Verify that required database tables exist.

    This function checks if all required tables have been created by migrations.
    Useful for debugging migration issues in tests.

    Args:
        engine: SQLAlchemy engine
        required_tables: List of table names to check (optional, checks all core tables if None)

    Returns:
        Dictionary mapping table names to existence status (True/False)

    Example:
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///:memory:")
        run_migrations(engine)
        status = verify_tables_exist(engine)
        assert all(status.values()), f"Missing tables: {[k for k, v in status.items() if not v]}"
    """
    import sqlalchemy as sa

    # Default list of core tables
    if required_tables is None:
        required_tables = [
            "resources",
            "users",
            "collections",
            "collection_resources",
            "taxonomy_nodes",
            "resource_taxonomy",
            "user_profiles",
            "user_interactions",
            "annotations",
            "citations",
            "authority_subjects",
            "authority_creators",
            "authority_publishers",
            "classification_codes",
        ]

    inspector = sa.inspect(engine)
    existing_tables = inspector.get_table_names()

    return {table: table in existing_tables for table in required_tables}


def get_migration_version(engine) -> str:
    """
    Get the current Alembic migration version of the database.

    Args:
        engine: SQLAlchemy engine

    Returns:
        Current migration version (revision ID) or None if no migrations applied

    Example:
        version = get_migration_version(engine)
        print(f"Database is at migration version: {version}")
    """
    from alembic.migration import MigrationContext

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_rev = context.get_current_revision()
        return current_rev


def reset_database(engine):
    """
    Reset the database by dropping all tables and re-running migrations.

    WARNING: This will delete all data in the database!
    Only use this in test environments.

    Args:
        engine: SQLAlchemy engine

    Example:
        reset_database(engine)
        # Database is now empty with fresh schema
    """
    from backend.app.database.base import Base

    # Drop all tables
    Base.metadata.drop_all(engine)

    # Re-run migrations
    run_migrations(engine)


def create_test_database_with_migrations(db_url: str = "sqlite:///:memory:"):
    """
    Create a complete test database with migrations applied.

    This is a convenience function that creates an engine, runs migrations,
    and returns both the engine and a session factory.

    Args:
        db_url: Database URL (defaults to in-memory SQLite)

    Returns:
        Tuple of (engine, SessionLocal factory)

    Example:
        engine, SessionLocal = create_test_database_with_migrations()
        db = SessionLocal()
        # Use db for testing
        db.close()
        engine.dispose()
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Create engine
    engine = create_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    )

    # Run migrations
    run_migrations(engine)

    # Create session factory
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
    )

    return engine, SessionLocal


def verify_resource_model_fields(engine) -> Dict[str, List[str]]:
    """
    Verify that the Resource model has the correct Dublin Core field names.

    This function checks that the resources table has the correct field names
    (source, type, identifier) rather than legacy names (url, resource_type, resource_id).

    Args:
        engine: SQLAlchemy engine

    Returns:
        Dictionary with 'correct_fields' and 'missing_fields' lists

    Example:
        result = verify_resource_model_fields(engine)
        assert not result['missing_fields'], f"Missing fields: {result['missing_fields']}"
    """
    import sqlalchemy as sa

    inspector = sa.inspect(engine)

    if "resources" not in inspector.get_table_names():
        return {
            "correct_fields": [],
            "missing_fields": ["resources table does not exist"],
        }

    columns = [col["name"] for col in inspector.get_columns("resources")]

    # Check for correct Dublin Core field names
    required_fields = ["source", "type", "identifier"]
    legacy_fields = ["url", "resource_type", "resource_id"]

    correct_fields = [field for field in required_fields if field in columns]
    missing_fields = [field for field in required_fields if field not in columns]

    # Check if legacy fields are present (they shouldn't be)
    legacy_present = [field for field in legacy_fields if field in columns]

    if legacy_present:
        missing_fields.append(f"Legacy fields present: {legacy_present}")

    return {
        "correct_fields": correct_fields,
        "missing_fields": missing_fields,
        "all_columns": columns,
    }
