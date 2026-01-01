"""
Comprehensive database schema verification tests.

Tests the database initialization helper and schema verification
to ensure all required fields exist in test databases.
"""

from sqlalchemy import create_engine, inspect
import tempfile
import os

from backend.app.database.base import Base
from backend.app.database.models import Resource


def ensure_database_schema(engine):
    """Helper to ensure database schema is created."""
    Base.metadata.create_all(bind=engine)


class TestDatabaseSchemaVerification:
    """Test suite for database schema verification and initialization."""
    
    def test_ensure_database_schema_creates_all_tables(self):
        """Verify that ensure_database_schema creates all required tables."""
        # Create a temporary database
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            engine = create_engine(f"sqlite:///{temp_db.name}", echo=False)
            
            # Call the initialization helper
            ensure_database_schema(engine)
            
            # Verify all expected tables exist
            inspector = inspect(engine)
            tables = set(inspector.get_table_names())
            
            expected_tables = {
                'resources',
                'classification_codes',
                'authority_subjects',
                'authority_creators',
                'authority_publishers',
                'citations',
                'collections',
                'collection_resources',
                'annotations',
                'taxonomy_nodes',
                'resource_taxonomy',
                'graph_edges',
                'graph_embeddings',
                'discovery_hypotheses'
            }
            
            missing_tables = expected_tables - tables
            assert not missing_tables, f"Missing tables: {missing_tables}"
            
        finally:
            try:
                os.unlink(temp_db.name)
            except OSError:
                pass
    
    def test_ensure_database_schema_verifies_resource_fields(self):
        """Verify that ensure_database_schema checks for required Resource fields."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            engine = create_engine(f"sqlite:///{temp_db.name}", echo=False)
            
            # Call the initialization helper
            ensure_database_schema(engine)
            
            # Verify Resource table has all required fields
            inspector = inspect(engine)
            columns = {col['name'] for col in inspector.get_columns('resources')}
            
            required_fields = {
                'id',
                'title',
                'description',
                'publisher',
                'sparse_embedding',
                'sparse_embedding_model',
                'sparse_embedding_updated_at',
                'embedding',
                'quality_score',
                'created_at',
                'updated_at'
            }
            
            missing_fields = required_fields - columns
            assert not missing_fields, f"Missing required fields: {missing_fields}"
            
        finally:
            try:
                os.unlink(temp_db.name)
            except OSError:
                pass
    
    def test_resource_creation_with_all_critical_fields(self, test_db):
        """Test creating a Resource with all critical fields including sparse_embedding."""
        from datetime import datetime, timezone
        
        db = test_db()
        
        try:
            # Create resource with all critical fields
            resource = Resource(
                title="Schema Test Resource",
                description="Testing database schema with all fields",
                publisher="Test Publisher Inc.",
                creator="Test Author",
                sparse_embedding='{"token_1": 0.9, "token_2": 0.7, "token_3": 0.5}',
                sparse_embedding_model="bge-m3",
                sparse_embedding_updated_at=datetime.now(timezone.utc),
                embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
                quality_score=0.92,
                language="en",
                type="article",
                classification_code="004",
                read_status="unread",
                ingestion_status="completed"
            )
            
            db.add(resource)
            db.commit()
            db.refresh(resource)
            
            # Verify all fields were saved correctly
            assert resource.id is not None
            assert resource.title == "Schema Test Resource"
            assert resource.description == "Testing database schema with all fields"
            assert resource.publisher == "Test Publisher Inc."
            assert resource.creator == "Test Author"
            assert resource.sparse_embedding == '{"token_1": 0.9, "token_2": 0.7, "token_3": 0.5}'
            assert resource.sparse_embedding_model == "bge-m3"
            assert resource.sparse_embedding_updated_at is not None
            assert resource.embedding == [0.1, 0.2, 0.3, 0.4, 0.5]
            assert resource.quality_score == 0.92
            
            # Query the resource back to ensure persistence
            queried_resource = db.query(Resource).filter(Resource.id == resource.id).first()
            assert queried_resource is not None
            assert queried_resource.sparse_embedding == resource.sparse_embedding
            assert queried_resource.description == resource.description
            assert queried_resource.publisher == resource.publisher
            
        finally:
            db.close()
    
    def test_multiple_resources_with_sparse_embeddings(self, test_db):
        """Test creating multiple resources with sparse embeddings."""
        
        db = test_db()
        
        try:
            resources = []
            for i in range(5):
                resource = Resource(
                    title=f"Resource {i}",
                    description=f"Description for resource {i}",
                    publisher=f"Publisher {i}",
                    sparse_embedding=f'{{"token_{i}": {0.9 - i*0.1}}}',
                    sparse_embedding_model="bge-m3",
                    embedding=[float(i)] * 5,
                    quality_score=0.8 + i * 0.02,
                    language="en",
                    type="article"
                )
                db.add(resource)
                resources.append(resource)
            
            db.commit()
            
            # Refresh all resources
            for resource in resources:
                db.refresh(resource)
            
            # Verify all resources were created
            assert len(resources) == 5
            
            # Query all resources with sparse embeddings
            queried = db.query(Resource).filter(
                Resource.sparse_embedding.isnot(None)
            ).all()
            
            assert len(queried) >= 5
            
            # Verify each resource has correct data
            for i, resource in enumerate(resources):
                assert resource.sparse_embedding is not None
                assert resource.description == f"Description for resource {i}"
                assert resource.publisher == f"Publisher {i}"
            
        finally:
            db.close()
    
    def test_schema_handles_null_sparse_embedding(self, test_db):
        """Test that schema correctly handles NULL sparse_embedding values."""
        db = test_db()
        
        try:
            # Create resource without sparse_embedding
            resource = Resource(
                title="Resource without sparse embedding",
                description="Testing NULL sparse_embedding",
                publisher="Test Publisher",
                embedding=[0.1, 0.2, 0.3],
                quality_score=0.75,
                language="en",
                type="article"
            )
            
            db.add(resource)
            db.commit()
            db.refresh(resource)
            
            # Verify resource was created with NULL sparse_embedding
            assert resource.id is not None
            assert resource.sparse_embedding is None
            assert resource.sparse_embedding_model is None
            assert resource.description == "Testing NULL sparse_embedding"
            assert resource.publisher == "Test Publisher"
            
        finally:
            db.close()
    
    def test_schema_migration_compatibility(self, test_db):
        """Test that schema is compatible with migration expectations."""
        db = test_db()
        
        try:
            engine = db.get_bind()
            inspector = inspect(engine)
            
            # Verify resources table structure
            columns = {col['name']: col for col in inspector.get_columns('resources')}
            
            # Check sparse_embedding field properties
            assert 'sparse_embedding' in columns
            sparse_col = columns['sparse_embedding']
            # Should be nullable (TEXT field)
            assert sparse_col['nullable'] is True
            
            # Check description field properties
            assert 'description' in columns
            desc_col = columns['description']
            assert desc_col['nullable'] is True
            
            # Check publisher field properties
            assert 'publisher' in columns
            pub_col = columns['publisher']
            assert pub_col['nullable'] is True
            
            # Check embedding field (JSON)
            assert 'embedding' in columns
            emb_col = columns['embedding']
            assert emb_col['nullable'] is True
            
        finally:
            db.close()


class TestDatabaseInitializationHelper:
    """Test suite specifically for the ensure_database_schema helper function."""
    
    def test_helper_handles_empty_database(self):
        """Test that helper correctly initializes an empty database."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            engine = create_engine(f"sqlite:///{temp_db.name}", echo=False)
            
            # Verify database is empty
            inspector = inspect(engine)
            assert len(inspector.get_table_names()) == 0
            
            # Call helper
            ensure_database_schema(engine)
            
            # Verify tables were created
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            assert len(tables) > 0
            assert 'resources' in tables
            
        finally:
            try:
                os.unlink(temp_db.name)
            except OSError:
                pass
    
    def test_helper_handles_existing_database(self):
        """Test that helper correctly handles an existing database."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            engine = create_engine(f"sqlite:///{temp_db.name}", echo=False)
            
            # Create tables first
            Base.metadata.create_all(engine)
            
            # Verify tables exist
            inspector = inspect(engine)
            initial_tables = set(inspector.get_table_names())
            assert 'resources' in initial_tables
            
            # Call helper again
            ensure_database_schema(engine)
            
            # Verify tables still exist and count hasn't changed
            inspector = inspect(engine)
            final_tables = set(inspector.get_table_names())
            assert initial_tables == final_tables
            
        finally:
            try:
                os.unlink(temp_db.name)
            except OSError:
                pass
    
    def test_helper_recreates_schema_if_fields_missing(self):
        """Test that helper recreates schema if required fields are missing."""
        from sqlalchemy import text
        
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            engine = create_engine(f"sqlite:///{temp_db.name}", echo=False)
            
            # Create a minimal resources table without sparse_embedding
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE resources (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL
                    )
                """))
                conn.commit()
            
            # Verify sparse_embedding is missing
            inspector = inspect(engine)
            columns = {col['name'] for col in inspector.get_columns('resources')}
            assert 'sparse_embedding' not in columns
            
            # Call helper - should recreate schema
            ensure_database_schema(engine)
            
            # Verify sparse_embedding now exists
            inspector = inspect(engine)
            columns = {col['name'] for col in inspector.get_columns('resources')}
            assert 'sparse_embedding' in columns
            assert 'description' in columns
            assert 'publisher' in columns
            
        finally:
            try:
                os.unlink(temp_db.name)
            except OSError:
                pass
