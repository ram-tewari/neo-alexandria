"""
Neo Alexandria 2.0 - Main Application Entry Point

This module serves as the main entry point for the Neo Alexandria 2.0 application.
It imports and exposes the FastAPI application instance created in the app module.

Related files:
- app/__init__.py: FastAPI application factory and configuration
- app/routers/: API endpoint definitions
- app/services/: Business logic services
- app/database/: Database models and configuration
- app/schemas/: Pydantic validation schemas

The application provides a comprehensive knowledge management system with:
- URL ingestion and content processing
- Authority control for subjects, creators, and publishers
- Personal classification system with UDC-inspired codes
- Enhanced quality control with multi-factor scoring
- Full-text search with SQLite FTS5 support
- CRUD operations and curation workflows
"""

from __future__ import annotations

from . import app

__all__ = ["app"]


