"""
Basic test to verify fixtures work correctly.
"""



def test_db_engine_fixture(db_engine):
    """Verify db_engine fixture creates an engine."""
    assert db_engine is not None
    assert str(db_engine.url) == "sqlite:///:memory:"


def test_db_session_fixture(db_session):
    """Verify db_session fixture creates a session."""
    assert db_session is not None
    assert db_session.is_active


def test_client_fixture(client):
    """Verify client fixture creates a TestClient."""
    assert client is not None


def test_mock_event_bus_fixture(mock_event_bus):
    """Verify mock_event_bus fixture creates a mock."""
    assert mock_event_bus is not None
    # Verify it's a MagicMock
    from unittest.mock import MagicMock
    assert isinstance(mock_event_bus, MagicMock)


def test_clean_event_bus_fixture(clean_event_bus):
    """Verify clean_event_bus fixture provides event bus."""
    assert clean_event_bus is not None
    # Verify metrics are reset
    metrics = clean_event_bus.get_metrics()
    assert metrics["events_emitted"] == 0


def test_create_test_resource_fixture(create_test_resource, db_session):
    """Verify create_test_resource factory fixture works."""
    # Create a resource
    resource = create_test_resource(title="Test Resource")
    
    assert resource is not None
    assert resource.title == "Test Resource"
    assert resource.id is not None
