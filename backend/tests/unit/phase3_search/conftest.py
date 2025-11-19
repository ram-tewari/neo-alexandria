"""
Shared fixtures for Phase 3 Search unit tests.

This module imports fixtures from the services conftest to avoid duplication.
"""

# Import sample_resources from services conftest
# This ensures consistency across service and unit tests
from backend.tests.services.conftest import sample_resources

__all__ = ['sample_resources']
