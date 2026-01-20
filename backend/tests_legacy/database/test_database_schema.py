"""Test database schema verification."""

from sqlalchemy import inspect


def test_database_schema_has_required_fields(test_db):
    """Verify that the test database has all required Resource fields."""
    # Get a session from the test_db fixture
    db = test_db()

    try:
        # Get the engine from the session
        engine = db.get_bind()

        # Inspect the database schema
        inspector = inspect(engine)

        # Verify resources table exists
        tables = inspector.get_table_names()
        assert "resources" in tables, "Resources table should exist"

        # Get all columns in resources table
        columns = {col["name"] for col in inspector.get_columns("resources")}

        # Verify critical fields exist
        required_fields = {
            "sparse_embedding",
            "description",
            "publisher",
            "title",
            "id",
            "quality_score",
            "embedding",
        }

        missing_fields = required_fields - columns
        assert not missing_fields, f"Missing required fields: {missing_fields}"

        print("✓ All required fields present in resources table")
        print(f"✓ Total columns in resources table: {len(columns)}")

    finally:
        db.close()


def test_can_create_resource_with_all_fields(test_db):
    """Verify that we can create a Resource with all critical fields."""
    from backend.app.database.models import Resource
    from datetime import datetime, timezone

    db = test_db()

    try:
        # Create a resource with all critical fields
        resource = Resource(
            title="Test Resource",
            description="Test description",
            publisher="Test Publisher",
            sparse_embedding='{"1": 0.5, "2": 0.3}',
            embedding=[0.1, 0.2, 0.3],
            quality_score=0.85,
            language="en",
            type="article",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        db.add(resource)
        db.commit()
        db.refresh(resource)

        # Verify the resource was created
        assert resource.id is not None
        assert resource.title == "Test Resource"
        assert resource.description == "Test description"
        assert resource.publisher == "Test Publisher"
        assert resource.sparse_embedding == '{"1": 0.5, "2": 0.3}'
        assert resource.embedding == [0.1, 0.2, 0.3]
        assert resource.quality_score == 0.85

        print(f"✓ Successfully created resource with ID: {resource.id}")
        print("✓ All critical fields populated correctly")

    finally:
        db.close()


def test_database_initialization_helper(test_db):
    """Verify that the database initialization helper works correctly."""
    from backend.tests.conftest import ensure_database_schema

    db = test_db()

    try:
        engine = db.get_bind()

        # Call the helper function (should not raise any errors)
        ensure_database_schema(engine)

        # Verify tables still exist after calling helper
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        assert "resources" in tables
        assert "collections" in tables
        assert "annotations" in tables

        print("✓ Database initialization helper executed successfully")
        print(f"✓ Total tables in database: {len(tables)}")

    finally:
        db.close()
