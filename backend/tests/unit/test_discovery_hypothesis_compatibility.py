"""
Unit tests for DiscoveryHypothesis backward compatibility.
"""
import uuid
import pytest
from backend.app.database.models import DiscoveryHypothesis


class TestDiscoveryHypothesisCompatibility:
    """Test backward compatibility of DiscoveryHypothesis model."""
    
    def test_new_field_names(self):
        """Test creating hypothesis with new field names."""
        resource_a_id = uuid.uuid4()
        resource_b_id = uuid.uuid4()
        resource_c_id = uuid.uuid4()
        
        hypothesis = DiscoveryHypothesis(
            concept_a="Concept A",
            concept_b="Concept B",
            resource_a_id=resource_a_id,
            resource_b_id=resource_b_id,
            resource_c_id=resource_c_id,
            supporting_resources="[]",
            confidence_score=0.8,
            hypothesis_type="test"
        )
        
        assert hypothesis.resource_a_id == resource_a_id
        assert hypothesis.resource_b_id == resource_b_id
        assert hypothesis.resource_c_id == resource_c_id
    
    def test_backward_compatibility_properties(self):
        """Test that old property names work via aliases."""
        resource_a_id = uuid.uuid4()
        resource_b_id = uuid.uuid4()
        resource_c_id = uuid.uuid4()
        
        hypothesis = DiscoveryHypothesis(
            concept_a="Concept A",
            concept_b="Concept B",
            resource_a_id=resource_a_id,
            resource_b_id=resource_b_id,
            resource_c_id=resource_c_id,
            supporting_resources="[]",
            confidence_score=0.8,
            hypothesis_type="test"
        )
        
        # Test that old property names return the same values
        assert hypothesis.a_resource_id == resource_a_id
        assert hypothesis.b_resource_id == resource_b_id
        assert hypothesis.c_resource_id == resource_c_id
    
    def test_backward_compatibility_setters(self):
        """Test that old property names can be used to set values."""
        resource_a_id = uuid.uuid4()
        resource_c_id = uuid.uuid4()
        
        hypothesis = DiscoveryHypothesis(
            concept_a="Concept A",
            concept_b="Concept B",
            supporting_resources="[]",
            confidence_score=0.8,
            hypothesis_type="test"
        )
        
        # Set using old property names
        hypothesis.a_resource_id = resource_a_id
        hypothesis.c_resource_id = resource_c_id
        
        # Verify they set the actual fields
        assert hypothesis.resource_a_id == resource_a_id
        assert hypothesis.resource_c_id == resource_c_id
        
        # Verify reading via old names still works
        assert hypothesis.a_resource_id == resource_a_id
        assert hypothesis.c_resource_id == resource_c_id
    
    def test_query_with_new_field_names(self, test_db):
        """Test that queries work with new field names and results can be accessed via old properties."""
        db = test_db()
        
        resource_a_id = uuid.uuid4()
        resource_c_id = uuid.uuid4()
        
        # Create hypothesis using new field names
        hypothesis = DiscoveryHypothesis(
            concept_a="Concept A",
            concept_b="Concept C",
            resource_a_id=resource_a_id,
            resource_c_id=resource_c_id,
            supporting_resources="[]",
            confidence_score=0.8,
            hypothesis_type="test"
        )
        db.add(hypothesis)
        db.commit()
        db.refresh(hypothesis)
        
        # Query using new field names (the actual database columns)
        result = db.query(DiscoveryHypothesis).filter(
            DiscoveryHypothesis.resource_a_id == resource_a_id,
            DiscoveryHypothesis.resource_c_id == resource_c_id
        ).first()
        
        assert result is not None
        assert result.id == hypothesis.id
        
        # Access via old property names (backward compatibility for reading)
        assert result.a_resource_id == resource_a_id
        assert result.c_resource_id == resource_c_id
        
        # Access via new field names
        assert result.resource_a_id == resource_a_id
        assert result.resource_c_id == resource_c_id
        
        # Cleanup
        db.delete(hypothesis)
        db.commit()
        db.close()
