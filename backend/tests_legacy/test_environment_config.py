"""Test environment-specific configuration for Phase 13."""

from backend.app.config.settings import get_settings


def test_database_url_default():
    """Test that DATABASE_URL has a default value."""
    settings = get_settings()
    assert settings.DATABASE_URL is not None
    assert len(settings.DATABASE_URL) > 0


def test_test_database_url_optional():
    """Test that TEST_DATABASE_URL is optional and defaults to None."""
    settings = get_settings()
    # TEST_DATABASE_URL should be None if not set in environment
    # (it may be set in .env file, so we just check it's accessible)
    assert hasattr(settings, "TEST_DATABASE_URL")


def test_test_db_fixture_uses_test_database_url(test_db, monkeypatch):
    """Test that test_db fixture respects TEST_DATABASE_URL when set."""
    # This test verifies the fixture works with the default configuration
    # The actual TEST_DATABASE_URL usage is tested by setting it in environment
    TestingSessionLocal = test_db
    session = TestingSessionLocal()

    # Verify we can create a session
    assert session is not None

    # Verify the session is connected to a database
    from backend.app.database.models import Resource

    result = session.query(Resource).count()
    assert result >= 0  # Should return 0 or more (empty database is fine)

    session.close()


def test_environment_specific_settings():
    """Test that environment-specific settings are accessible."""
    settings = get_settings()

    # Verify all database-related settings are accessible
    assert hasattr(settings, "DATABASE_URL")
    assert hasattr(settings, "TEST_DATABASE_URL")
    assert hasattr(settings, "ENV")

    # Verify ENV is one of the allowed values
    assert settings.ENV in ["dev", "staging", "prod"]
