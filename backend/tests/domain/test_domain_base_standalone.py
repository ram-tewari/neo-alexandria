"""
Standalone tests for base domain object classes.

This module tests the validation, serialization, and equality
functionality of the base domain object classes without importing
the full application.
"""

import sys
from pathlib import Path

# Add backend to path for direct imports
backend_path = Path(__file__).parent.parent.parent  # Go up to backend root
sys.path.insert(0, str(backend_path))

import pytest
from dataclasses import dataclass
from typing import Optional
import json

# Direct import to avoid app initialization
import importlib.util
spec = importlib.util.spec_from_file_location("domain_base", backend_path / "app" / "domain" / "base.py")
domain_base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(domain_base)

BaseDomainObject = domain_base.BaseDomainObject
ValueObject = domain_base.ValueObject
DomainEntity = domain_base.DomainEntity
validate_range = domain_base.validate_range
validate_positive = domain_base.validate_positive
validate_non_empty = domain_base.validate_non_empty
validate_non_negative = domain_base.validate_non_negative


# Test fixtures - concrete implementations for testing


@dataclass
class TestValueObject(ValueObject):
    """Test value object with validation."""
    score: float
    name: str
    
    def validate(self) -> None:
        """Validate test value object."""
        validate_range(self.score, 0.0, 1.0, "score")
        validate_non_empty(self.name, "name")


@dataclass
class TestSimpleValueObject(ValueObject):
    """Simple test value object without custom validation."""
    value: int
    
    def validate(self) -> None:
        """No custom validation."""
        pass


class TestEntity(DomainEntity):
    """Test entity with validation."""
    
    def __init__(self, entity_id: str, name: str, count: int):
        super().__init__(entity_id)
        self.name = name
        self.count = count
        self.validate()
    
    def validate(self) -> None:
        """Validate test entity."""
        validate_non_empty(self.name, "name")
        validate_non_negative(self.count, "count")


# Tests for ValueObject


class TestValueObjectClass:
    """Tests for ValueObject base class."""
    
    def test_value_object_creation(self):
        """Test creating a value object."""
        obj = TestValueObject(score=0.8, name="test")
        assert obj.score == 0.8
        assert obj.name == "test"
    
    def test_value_object_validation_on_init(self):
        """Test validation is called on initialization."""
        with pytest.raises(ValueError, match="score must be between"):
            TestValueObject(score=1.5, name="test")
    
    def test_value_object_to_dict(self):
        """Test converting value object to dictionary."""
        obj = TestValueObject(score=0.8, name="test")
        result = obj.to_dict()
        assert result == {"score": 0.8, "name": "test"}
    
    def test_value_object_from_dict(self):
        """Test creating value object from dictionary."""
        data = {"score": 0.8, "name": "test"}
        obj = TestValueObject.from_dict(data)
        assert obj.score == 0.8
        assert obj.name == "test"
    
    def test_value_object_to_json(self):
        """Test converting value object to JSON."""
        obj = TestValueObject(score=0.8, name="test")
        json_str = obj.to_json()
        data = json.loads(json_str)
        assert data == {"score": 0.8, "name": "test"}
    
    def test_value_object_from_json(self):
        """Test creating value object from JSON."""
        json_str = '{"score": 0.8, "name": "test"}'
        obj = TestValueObject.from_json(json_str)
        assert obj.score == 0.8
        assert obj.name == "test"
    
    def test_value_object_equality(self):
        """Test value object equality comparison."""
        obj1 = TestValueObject(score=0.8, name="test")
        obj2 = TestValueObject(score=0.8, name="test")
        obj3 = TestValueObject(score=0.9, name="test")
        
        assert obj1 == obj2
        assert obj1 != obj3
    
    def test_value_object_repr(self):
        """Test value object string representation."""
        obj = TestValueObject(score=0.8, name="test")
        repr_str = repr(obj)
        assert "TestValueObject" in repr_str
        assert "score=0.8" in repr_str
        assert "name='test'" in repr_str


# Tests for DomainEntity


class TestDomainEntityClass:
    """Tests for DomainEntity base class."""
    
    def test_entity_creation(self):
        """Test creating a domain entity."""
        entity = TestEntity(entity_id="123", name="test", count=5)
        assert entity.entity_id == "123"
        assert entity.name == "test"
        assert entity.count == 5
    
    def test_entity_validation_on_init(self):
        """Test validation is called on initialization."""
        with pytest.raises(ValueError, match="count must be non-negative"):
            TestEntity(entity_id="123", name="test", count=-1)
    
    def test_entity_to_dict(self):
        """Test converting entity to dictionary."""
        entity = TestEntity(entity_id="123", name="test", count=5)
        result = entity.to_dict()
        assert result == {"entity_id": "123", "name": "test", "count": 5}
    
    def test_entity_from_dict(self):
        """Test creating entity from dictionary."""
        data = {"entity_id": "123", "name": "test", "count": 5}
        entity = TestEntity.from_dict(data)
        assert entity.entity_id == "123"
        assert entity.name == "test"
        assert entity.count == 5
    
    def test_entity_equality_by_id(self):
        """Test entities are equal if they have same ID."""
        entity1 = TestEntity(entity_id="123", name="test1", count=5)
        entity2 = TestEntity(entity_id="123", name="test2", count=10)
        entity3 = TestEntity(entity_id="456", name="test1", count=5)
        
        assert entity1 == entity2  # Same ID, different attributes
        assert entity1 != entity3  # Different ID
    
    def test_entity_hash(self):
        """Test entity hashing by ID."""
        entity1 = TestEntity(entity_id="123", name="test", count=5)
        entity2 = TestEntity(entity_id="123", name="test", count=5)
        entity3 = TestEntity(entity_id="456", name="test", count=5)
        
        assert hash(entity1) == hash(entity2)
        assert hash(entity1) != hash(entity3)
    
    def test_entity_in_set(self):
        """Test entities can be used in sets."""
        entity1 = TestEntity(entity_id="123", name="test", count=5)
        entity2 = TestEntity(entity_id="123", name="different", count=10)
        entity3 = TestEntity(entity_id="456", name="test", count=5)
        
        entity_set = {entity1, entity2, entity3}
        assert len(entity_set) == 2  # entity1 and entity2 are same


# Tests for validation functions


class TestValidationFunctions:
    """Tests for validation helper functions."""
    
    def test_validate_range_valid(self):
        """Test validate_range with valid value."""
        validate_range(0.5, 0.0, 1.0, "test_field")  # Should not raise
    
    def test_validate_range_at_boundaries(self):
        """Test validate_range at min and max boundaries."""
        validate_range(0.0, 0.0, 1.0, "test_field")  # Min boundary
        validate_range(1.0, 0.0, 1.0, "test_field")  # Max boundary
    
    def test_validate_range_below_min(self):
        """Test validate_range with value below minimum."""
        with pytest.raises(ValueError, match="test_field must be between 0.0 and 1.0"):
            validate_range(-0.1, 0.0, 1.0, "test_field")
    
    def test_validate_range_above_max(self):
        """Test validate_range with value above maximum."""
        with pytest.raises(ValueError, match="test_field must be between 0.0 and 1.0"):
            validate_range(1.1, 0.0, 1.0, "test_field")
    
    def test_validate_positive_valid(self):
        """Test validate_positive with valid value."""
        validate_positive(1.0, "test_field")  # Should not raise
        validate_positive(0.1, "test_field")  # Should not raise
    
    def test_validate_positive_zero(self):
        """Test validate_positive with zero."""
        with pytest.raises(ValueError, match="test_field must be positive"):
            validate_positive(0.0, "test_field")
    
    def test_validate_positive_negative(self):
        """Test validate_positive with negative value."""
        with pytest.raises(ValueError, match="test_field must be positive"):
            validate_positive(-1.0, "test_field")
    
    def test_validate_non_empty_valid(self):
        """Test validate_non_empty with valid string."""
        validate_non_empty("test", "test_field")  # Should not raise
    
    def test_validate_non_empty_empty_string(self):
        """Test validate_non_empty with empty string."""
        with pytest.raises(ValueError, match="test_field cannot be empty"):
            validate_non_empty("", "test_field")
    
    def test_validate_non_empty_whitespace(self):
        """Test validate_non_empty with whitespace only."""
        with pytest.raises(ValueError, match="test_field cannot be empty"):
            validate_non_empty("   ", "test_field")
    
    def test_validate_non_negative_valid(self):
        """Test validate_non_negative with valid value."""
        validate_non_negative(0.0, "test_field")  # Zero is valid
        validate_non_negative(1.0, "test_field")  # Positive is valid
    
    def test_validate_non_negative_negative(self):
        """Test validate_non_negative with negative value."""
        with pytest.raises(ValueError, match="test_field must be non-negative"):
            validate_non_negative(-1.0, "test_field")


# Integration tests


class TestDomainObjectIntegration:
    """Integration tests for domain objects."""
    
    def test_round_trip_serialization_value_object(self):
        """Test complete serialization round trip for value object."""
        original = TestValueObject(score=0.8, name="test")
        json_str = original.to_json()
        restored = TestValueObject.from_json(json_str)
        assert original == restored
    
    def test_round_trip_serialization_entity(self):
        """Test complete serialization round trip for entity."""
        original = TestEntity(entity_id="123", name="test", count=5)
        dict_data = original.to_dict()
        restored = TestEntity.from_dict(dict_data)
        assert original == restored
    
    def test_from_dict_filters_extra_fields(self):
        """Test from_dict ignores extra fields not in dataclass."""
        data = {"score": 0.8, "name": "test", "extra_field": "ignored"}
        obj = TestValueObject.from_dict(data)
        assert obj.score == 0.8
        assert obj.name == "test"
        assert not hasattr(obj, "extra_field")
    
    def test_validation_in_from_dict(self):
        """Test validation is triggered when creating from dict."""
        data = {"score": 1.5, "name": "test"}
        with pytest.raises(ValueError, match="score must be between"):
            TestValueObject.from_dict(data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
