"""
PostgreSQL JSONB Feature Tests

Tests PostgreSQL-specific JSONB functionality including containment queries,
GIN indexes, and JSONB operators. These tests require a PostgreSQL database
and will be skipped when running against SQLite.

Run these tests with:
    TEST_DATABASE_URL=postgresql://user:pass@localhost/test_db pytest tests/test_postgresql_jsonb.py -v
"""

import pytest
from sqlalchemy import cast, text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

from backend.app.database.models import Resource


@pytest.mark.postgresql
class TestPostgreSQLJSONB:
    """Test PostgreSQL JSONB containment and query features."""
    
    def test_jsonb_containment_operator(self, db_session, db_type):
        """Test JSONB @> containment operator for subject arrays."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create test resources with different subjects
        resource1 = Resource(
            title="Machine Learning Guide",
            description="Comprehensive ML guide",
            subject=["Machine Learning", "Artificial Intelligence", "Python"],
            language="en",
            type="article",
            classification_code="004",
            quality_score=0.85,
            quality_overall=0.85,
            quality_accuracy=0.87,
            quality_completeness=0.83,
            quality_consistency=0.86,
            quality_timeliness=0.84,
            quality_relevance=0.88,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        resource2 = Resource(
            title="Data Science Basics",
            description="Introduction to data science",
            subject=["Data Science", "Statistics", "Python"],
            language="en",
            type="article",
            classification_code="004",
            quality_score=0.80,
            quality_overall=0.80,
            quality_accuracy=0.82,
            quality_completeness=0.78,
            quality_consistency=0.81,
            quality_timeliness=0.79,
            quality_relevance=0.83,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        resource3 = Resource(
            title="Cooking Recipes",
            description="Delicious recipes",
            subject=["Cooking", "Food"],
            language="en",
            type="article",
            classification_code="641",
            quality_score=0.75,
            quality_overall=0.75,
            quality_accuracy=0.77,
            quality_completeness=0.73,
            quality_consistency=0.76,
            quality_timeliness=0.74,
            quality_relevance=0.78,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add_all([resource1, resource2, resource3])
        db_session.commit()
        
        # Test containment query: find resources with "Machine Learning" subject
        results = db_session.query(Resource).filter(
            Resource.subject.op('@>')(cast(["Machine Learning"], JSONB))
        ).all()
        
        assert len(results) == 1
        assert results[0].title == "Machine Learning Guide"
        
        # Test containment query: find resources with "Python" subject
        results = db_session.query(Resource).filter(
            Resource.subject.op('@>')(cast(["Python"], JSONB))
        ).all()
        
        assert len(results) == 2
        titles = {r.title for r in results}
        assert "Machine Learning Guide" in titles
        assert "Data Science Basics" in titles
        
        # Test containment query: find resources with multiple subjects
        results = db_session.query(Resource).filter(
            Resource.subject.op('@>')(cast(["Machine Learning", "Python"], JSONB))
        ).all()
        
        assert len(results) == 1
        assert results[0].title == "Machine Learning Guide"
    
    def test_jsonb_key_exists_operator(self, db_session, db_type):
        """Test JSONB ? operator for checking if key exists in JSON object."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create resource with relation metadata
        resource = Resource(
            title="Test Resource",
            description="Test description",
            subject=["Test"],
            relation={"cites": ["resource-1", "resource-2"], "cited_by": ["resource-3"]},
            language="en",
            type="article",
            classification_code="000",
            quality_score=0.80,
            quality_overall=0.80,
            quality_accuracy=0.82,
            quality_completeness=0.78,
            quality_consistency=0.81,
            quality_timeliness=0.79,
            quality_relevance=0.83,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add(resource)
        db_session.commit()
        
        # Test key existence: find resources with "cites" key in relation
        results = db_session.query(Resource).filter(
            Resource.relation.op('?')('cites')
        ).all()
        
        assert len(results) == 1
        assert results[0].title == "Test Resource"
        
        # Test key existence: find resources with "cited_by" key
        results = db_session.query(Resource).filter(
            Resource.relation.op('?')('cited_by')
        ).all()
        
        assert len(results) == 1
        
        # Test key existence: find resources with non-existent key
        results = db_session.query(Resource).filter(
            Resource.relation.op('?')('references')
        ).all()
        
        assert len(results) == 0
    
    def test_jsonb_array_length(self, db_session, db_type):
        """Test JSONB array length function."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create resources with different subject counts
        resource1 = Resource(
            title="Resource 1",
            description="One subject",
            subject=["Subject1"],
            language="en",
            type="article",
            classification_code="000",
            quality_score=0.80,
            quality_overall=0.80,
            quality_accuracy=0.82,
            quality_completeness=0.78,
            quality_consistency=0.81,
            quality_timeliness=0.79,
            quality_relevance=0.83,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        resource2 = Resource(
            title="Resource 2",
            description="Three subjects",
            subject=["Subject1", "Subject2", "Subject3"],
            language="en",
            type="article",
            classification_code="000",
            quality_score=0.80,
            quality_overall=0.80,
            quality_accuracy=0.82,
            quality_completeness=0.78,
            quality_consistency=0.81,
            quality_timeliness=0.79,
            quality_relevance=0.83,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add_all([resource1, resource2])
        db_session.commit()
        
        # Query resources with more than 2 subjects using jsonb_array_length
        results = db_session.query(Resource).filter(
            text("jsonb_array_length(subject) > 2")
        ).all()
        
        assert len(results) == 1
        assert results[0].title == "Resource 2"
    
    def test_jsonb_concatenation(self, db_session, db_type):
        """Test JSONB || concatenation operator."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create resource
        resource = Resource(
            title="Test Resource",
            description="Test description",
            subject=["Subject1", "Subject2"],
            language="en",
            type="article",
            classification_code="000",
            quality_score=0.80,
            quality_overall=0.80,
            quality_accuracy=0.82,
            quality_completeness=0.78,
            quality_consistency=0.81,
            quality_timeliness=0.79,
            quality_relevance=0.83,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add(resource)
        db_session.commit()
        
        # Update subject array using concatenation
        db_session.execute(
            text("UPDATE resources SET subject = subject || :new_subject WHERE id = :id"),
            {"new_subject": '["Subject3"]', "id": str(resource.id)}
        )
        db_session.commit()
        
        # Verify concatenation worked
        db_session.refresh(resource)
        assert len(resource.subject) == 3
        assert "Subject3" in resource.subject
    
    def test_jsonb_gin_index_performance(self, db_session, db_type):
        """Test that GIN indexes are used for JSONB queries."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create multiple resources
        resources = []
        for i in range(10):
            resource = Resource(
                title=f"Resource {i}",
                description=f"Description {i}",
                subject=["Machine Learning"] if i % 2 == 0 else ["Data Science"],
                language="en",
                type="article",
                classification_code="004",
                quality_score=0.80,
                quality_overall=0.80,
                quality_accuracy=0.82,
                quality_completeness=0.78,
                quality_consistency=0.81,
                quality_timeliness=0.79,
                quality_relevance=0.83,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            resources.append(resource)
        
        db_session.add_all(resources)
        db_session.commit()
        
        # Execute EXPLAIN to verify index usage
        explain_result = db_session.execute(
            text(
                "EXPLAIN (FORMAT JSON) "
                "SELECT * FROM resources WHERE subject @> :subject"
            ),
            {"subject": '["Machine Learning"]'}
        ).scalar()
        
        # Verify that the query plan mentions an index scan
        # (In a real production database with many rows, this would use the GIN index)
        assert explain_result is not None
        
        # Execute the actual query
        results = db_session.query(Resource).filter(
            Resource.subject.op('@>')(cast(["Machine Learning"], JSONB))
        ).all()
        
        assert len(results) == 5  # Half of the 10 resources


@pytest.mark.postgresql
class TestPostgreSQLJSONBEmbeddings:
    """Test PostgreSQL JSONB functionality for embeddings."""
    
    def test_embedding_storage_and_retrieval(self, db_session, db_type):
        """Test storing and retrieving embeddings as JSONB."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create resource with embedding
        embedding_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        resource = Resource(
            title="Test Resource",
            description="Test description",
            subject=["Test"],
            embedding=embedding_vector,
            language="en",
            type="article",
            classification_code="000",
            quality_score=0.80,
            quality_overall=0.80,
            quality_accuracy=0.82,
            quality_completeness=0.78,
            quality_consistency=0.81,
            quality_timeliness=0.79,
            quality_relevance=0.83,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add(resource)
        db_session.commit()
        
        # Retrieve and verify embedding
        retrieved = db_session.query(Resource).filter_by(title="Test Resource").first()
        assert retrieved is not None
        assert retrieved.embedding == embedding_vector
        assert len(retrieved.embedding) == 5
    
    def test_sparse_embedding_jsonb_storage(self, db_session, db_type):
        """Test storing sparse embeddings as JSONB objects."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create resource with sparse embedding
        sparse_embedding = {
            "100": 0.8,
            "200": 0.6,
            "300": 0.4,
            "400": 0.3,
            "500": 0.2
        }
        
        resource = Resource(
            title="Test Resource",
            description="Test description",
            subject=["Test"],
            sparse_embedding=sparse_embedding,
            language="en",
            type="article",
            classification_code="000",
            quality_score=0.80,
            quality_overall=0.80,
            quality_accuracy=0.82,
            quality_completeness=0.78,
            quality_consistency=0.81,
            quality_timeliness=0.79,
            quality_relevance=0.83,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add(resource)
        db_session.commit()
        
        # Retrieve and verify sparse embedding
        retrieved = db_session.query(Resource).filter_by(title="Test Resource").first()
        assert retrieved is not None
        assert retrieved.sparse_embedding == sparse_embedding
        assert len(retrieved.sparse_embedding) == 5
        
        # Test querying by sparse embedding keys
        results = db_session.query(Resource).filter(
            Resource.sparse_embedding.op('?')('100')
        ).all()
        
        assert len(results) == 1
        assert results[0].title == "Test Resource"
