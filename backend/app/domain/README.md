# Domain Objects Foundation

This directory contains the domain objects foundation for Neo Alexandria's Phase 12 refactoring initiative.

## Overview

The domain objects foundation provides base classes and validation utilities for creating rich domain objects that replace primitive obsession throughout the codebase.

## Base Classes

### `BaseDomainObject`
Abstract base class for all domain objects providing:
- Serialization methods (`to_dict()`, `from_dict()`, `to_json()`, `from_json()`)
- Equality comparison
- String representation
- Abstract `validate()` method

### `ValueObject`
Base class for immutable value objects (dataclass-based):
- Represents descriptive aspects of the domain
- Defined by attributes rather than identity
- Automatic validation on initialization via `__post_init__`
- Examples: Money, Score, Confidence, DateRange

### `DomainEntity`
Base class for domain entities with identity:
- Objects with distinct identity that runs through time
- Equality based on entity ID
- Hashable for use in sets and dictionaries
- Examples: User, Resource, Collection

## Validation Utilities

The module provides common validation functions:

- `validate_range(value, min_value, max_value, field_name)` - Validate numeric range
- `validate_positive(value, field_name)` - Validate positive numbers
- `validate_non_negative(value, field_name)` - Validate non-negative numbers
- `validate_non_empty(value, field_name)` - Validate non-empty strings

## Usage Examples

### Creating a Value Object

```python
from dataclasses import dataclass
from backend.app.domain import ValueObject, validate_range

@dataclass
class Confidence(ValueObject):
    """Confidence score value object."""
    score: float
    
    def validate(self) -> None:
        validate_range(self.score, 0.0, 1.0, "score")
    
    def is_high(self) -> bool:
        return self.score >= 0.8

# Usage
confidence = Confidence(score=0.95)
print(confidence.is_high())  # True
print(confidence.to_dict())  # {"score": 0.95}
```

### Creating a Domain Entity

```python
from backend.app.domain import DomainEntity, validate_non_empty

class User(DomainEntity):
    """User entity with identity."""
    
    def __init__(self, user_id: str, username: str, email: str):
        super().__init__(user_id)
        self.username = username
        self.email = email
        self.validate()
    
    def validate(self) -> None:
        validate_non_empty(self.username, "username")
        validate_non_empty(self.email, "email")

# Usage
user = User(user_id="123", username="alice", email="alice@example.com")
print(user.entity_id)  # "123"
```

## Domain Object Modules

The following domain object modules are available:

- `classification.py` - Classification domain objects (Task 2)
- `search.py` - Search domain objects (Task 3)
- `quality.py` - Quality assessment domain objects (Task 4)
- `recommendation.py` - Recommendation domain objects (Task 5)

## Testing

Comprehensive tests are available in `backend/tests/test_domain_base_standalone.py`:
- 31 test cases covering all base functionality
- Value object creation and validation
- Entity identity and hashing
- Serialization round-trips
- Validation functions

Run tests with:
```bash
python backend/tests/test_domain_base_standalone.py
```

## Design Principles

1. **Validation on Construction** - All domain objects validate on creation
2. **Immutability** - Value objects are immutable (use frozen dataclasses)
3. **Rich Behavior** - Domain objects encapsulate business logic
4. **Type Safety** - Full type hints on all methods
5. **Serialization** - Easy conversion to/from dictionaries and JSON

## Requirements Satisfied

This implementation satisfies the following requirements from the Phase 12 specification:

- **Requirement 3.1**: Create Value Objects with validation logic
- **Requirement 3.2**: Implement type hints for all attributes
- **Requirement 11.1**: Create Domain Objects using dataclasses
- **Requirement 11.2**: Add validation in __post_init__
- **Requirement 11.3**: Add methods for common operations
- **Requirement 11.4**: Implement serialization methods (to_dict, from_dict)
- **Requirement 11.5**: Add type hints for all attributes

## Next Steps

The foundation is now in place for implementing specific domain objects:
1. Classification domain objects (ClassificationPrediction, ClassificationResult)
2. Search domain objects (SearchQuery, SearchResult)
3. Quality domain objects (QualityScore with five dimensions)
4. Recommendation domain objects (Recommendation, RecommendationScore)
