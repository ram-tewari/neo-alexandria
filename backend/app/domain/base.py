"""
Base domain object classes with validation patterns.

This module provides base classes for all domain objects in Neo Alexandria,
implementing common patterns for validation, serialization, and equality.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, fields
from typing import Any, Dict, Type, TypeVar, Optional
import json


T = TypeVar("T", bound="BaseDomainObject")


class BaseDomainObject(ABC):
    """
    Abstract base class for all domain objects.

    Provides common functionality for validation, serialization,
    and equality comparison. All domain objects should inherit from this.
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert domain object to dictionary representation.

        Returns:
            Dictionary with all object attributes
        """
        if hasattr(self, "__dataclass_fields__"):
            return asdict(self)

        # Fallback for non-dataclass objects
        return {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        }

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create domain object from dictionary.

        Args:
            data: Dictionary with object attributes

        Returns:
            New instance of the domain object

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if hasattr(cls, "__dataclass_fields__"):
            # Filter data to only include fields defined in the dataclass
            field_names = {f.name for f in fields(cls)}
            filtered_data = {k: v for k, v in data.items() if k in field_names}
            return cls(**filtered_data)

        # Fallback for non-dataclass objects
        return cls(**data)

    def to_json(self) -> str:
        """
        Convert domain object to JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """
        Create domain object from JSON string.

        Args:
            json_str: JSON string representation

        Returns:
            New instance of the domain object

        Raises:
            ValueError: If JSON is invalid or fields are missing
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @abstractmethod
    def validate(self) -> None:
        """
        Validate domain object state.

        This method should be called in __post_init__ for dataclasses
        or in __init__ for regular classes.

        Raises:
            ValueError: If validation fails with descriptive message
        """
        pass

    def __eq__(self, other: Any) -> bool:
        """
        Compare domain objects for equality.

        Args:
            other: Object to compare with

        Returns:
            True if objects are equal, False otherwise
        """
        if not isinstance(other, self.__class__):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        """
        String representation of domain object.

        Returns:
            String showing class name and attributes
        """
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.to_dict().items())
        return f"{self.__class__.__name__}({attrs})"


@dataclass
class ValueObject(BaseDomainObject):
    """
    Base class for value objects.

    Value objects are immutable objects that represent a descriptive
    aspect of the domain with no conceptual identity. They are defined
    by their attributes rather than a unique identifier.

    Examples: Money, DateRange, Address, Confidence, Score
    """

    def __post_init__(self):
        """Validate value object after initialization."""
        self.validate()
        # Make immutable by freezing (if using frozen=True in dataclass)

    def validate(self) -> None:
        """
        Default validation - override in subclasses.

        Raises:
            ValueError: If validation fails
        """
        pass


class DomainEntity(BaseDomainObject):
    """
    Base class for domain entities.

    Entities are objects that have a distinct identity that runs through
    time and different representations. They are defined by their identity
    rather than their attributes.

    Examples: User, Resource, Collection, Recommendation
    """

    def __init__(self, entity_id: Optional[str] = None):
        """
        Initialize domain entity.

        Args:
            entity_id: Unique identifier for the entity
        """
        self.entity_id = entity_id

    def validate(self) -> None:
        """
        Default validation - override in subclasses.

        Raises:
            ValueError: If validation fails
        """
        pass

    def __eq__(self, other: Any) -> bool:
        """
        Compare entities by identity.

        Args:
            other: Object to compare with

        Returns:
            True if entities have same ID, False otherwise
        """
        if not isinstance(other, self.__class__):
            return False
        return self.entity_id == other.entity_id

    def __hash__(self) -> int:
        """
        Hash entity by identity.

        Returns:
            Hash of entity ID
        """
        return hash(self.entity_id)


def validate_range(
    value: float, min_value: float, max_value: float, field_name: str
) -> None:
    """
    Validate that a value is within a specified range.

    Args:
        value: Value to validate
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)
        field_name: Name of field being validated (for error message)

    Raises:
        ValueError: If value is outside the range
    """
    if not min_value <= value <= max_value:
        raise ValueError(
            f"{field_name} must be between {min_value} and {max_value}, got {value}"
        )


def validate_positive(value: float, field_name: str) -> None:
    """
    Validate that a value is positive.

    Args:
        value: Value to validate
        field_name: Name of field being validated (for error message)

    Raises:
        ValueError: If value is not positive
    """
    if value <= 0:
        raise ValueError(f"{field_name} must be positive, got {value}")


def validate_non_empty(value: str, field_name: str) -> None:
    """
    Validate that a string is not empty.

    Args:
        value: String to validate
        field_name: Name of field being validated (for error message)

    Raises:
        ValueError: If string is empty or only whitespace
    """
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")


def validate_non_negative(value: float, field_name: str) -> None:
    """
    Validate that a value is non-negative.

    Args:
        value: Value to validate
        field_name: Name of field being validated (for error message)

    Raises:
        ValueError: If value is negative
    """
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative, got {value}")
