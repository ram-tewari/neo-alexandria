"""
Data models for refactoring validation framework.

Defines enums, dataclasses, and value objects used throughout
the refactoring process.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime


class SmellType(Enum):
    """Types of code smells (Fowler's taxonomy)."""
    DUPLICATED_CODE = "duplicated_code"
    LONG_FUNCTION = "long_function"
    LARGE_CLASS = "large_class"
    GLOBAL_DATA = "global_data"
    FEATURE_ENVY = "feature_envy"
    DATA_CLUMPS = "data_clumps"
    PRIMITIVE_OBSESSION = "primitive_obsession"
    REPEATED_SWITCHES = "repeated_switches"
    DATA_CLASS = "data_class"
    LONG_PARAMETER_LIST = "long_parameter_list"


class Severity(Enum):
    """Severity levels for code smells."""
    HIGH = "high"      # Must fix (blocks production)
    MEDIUM = "medium"  # Should fix (technical debt)
    LOW = "low"        # Nice to fix (minor improvement)


class RefactoringTechnique(Enum):
    """Fowler refactoring techniques."""
    EXTRACT_FUNCTION = "extract_function"
    EXTRACT_CLASS = "extract_class"
    REPLACE_PRIMITIVE_WITH_OBJECT = "replace_primitive_with_object"
    COMBINE_FUNCTIONS_INTO_CLASS = "combine_functions_into_class"
    SEPARATE_QUERY_FROM_MODIFIER = "separate_query_from_modifier"
    ENCAPSULATE_COLLECTION = "encapsulate_collection"
    SPLIT_PHASE = "split_phase"
    REPLACE_CONDITIONAL_WITH_POLYMORPHISM = "replace_conditional_with_polymorphism"
    MOVE_FUNCTION = "move_function"
    INLINE_FUNCTION = "inline_function"


@dataclass
class Location:
    """Code location information."""
    file_path: Path
    start_line: int
    end_line: int
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    
    def __str__(self) -> str:
        """Human-readable location string."""
        location = f"{self.file_path}:{self.start_line}-{self.end_line}"
        if self.class_name and self.function_name:
            location += f" ({self.class_name}.{self.function_name})"
        elif self.function_name:
            location += f" ({self.function_name})"
        elif self.class_name:
            location += f" ({self.class_name})"
        return location


@dataclass
class CodeSmell:
    """Individual code smell instance."""
    smell_type: SmellType
    severity: Severity
    location: Location
    description: str
    suggested_technique: RefactoringTechnique
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Human-readable smell description."""
        return (
            f"[{self.severity.value.upper()}] {self.smell_type.value} at {self.location}\n"
            f"  {self.description}\n"
            f"  Suggested: {self.suggested_technique.value}"
        )


@dataclass
class SmellReport:
    """Report of code smells found in a file."""
    file_path: Path
    smells: List[CodeSmell]
    total_lines: int
    complexity_score: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def high_priority_smells(self) -> List[CodeSmell]:
        """Get high severity smells."""
        return [s for s in self.smells if s.severity == Severity.HIGH]
    
    def smells_by_type(self, smell_type: SmellType) -> List[CodeSmell]:
        """Filter smells by type."""
        return [s for s in self.smells if s.smell_type == smell_type]
    
    def summary(self) -> str:
        """Generate human-readable summary."""
        high = len(self.high_priority_smells())
        medium = len([s for s in self.smells if s.severity == Severity.MEDIUM])
        low = len([s for s in self.smells if s.severity == Severity.LOW])
        
        return (
            f"File: {self.file_path}\n"
            f"Total Lines: {self.total_lines}\n"
            f"Complexity Score: {self.complexity_score:.2f}\n"
            f"Smells: {len(self.smells)} total (High: {high}, Medium: {medium}, Low: {low})"
        )


@dataclass
class RefactoringResult:
    """Result of applying refactoring."""
    success: bool
    original_code: str
    refactored_code: str
    technique_applied: RefactoringTechnique
    changes_made: List[str]
    test_results: Optional['TestResults'] = None
    
    def summary(self) -> str:
        """Generate human-readable summary."""
        status = "SUCCESS" if self.success else "FAILED"
        return (
            f"{status}: Applied {self.technique_applied.value}, "
            f"{len(self.changes_made)} changes"
        )


@dataclass
class TestResults:
    """Results from running test suite."""
    total_tests: int
    passed: int
    failed: int
    errors: List[str]
    coverage_percentage: float
    execution_time_seconds: float = 0.0
    
    def all_passed(self) -> bool:
        """Check if all tests passed."""
        return self.failed == 0 and self.passed == self.total_tests
    
    def coverage_acceptable(self, threshold: float = 0.85) -> bool:
        """Check if coverage meets threshold."""
        return self.coverage_percentage >= threshold
    
    def summary(self) -> str:
        """Generate human-readable summary."""
        return (
            f"Tests: {self.passed}/{self.total_tests} passed, {self.failed} failed\n"
            f"Coverage: {self.coverage_percentage:.1f}%\n"
            f"Time: {self.execution_time_seconds:.2f}s"
        )


@dataclass
class ServiceRefactoringStatus:
    """Track refactoring status for a service module."""
    service_name: str
    file_path: Path
    status: str  # "not_started", "in_progress", "completed"
    smells_detected: int
    smells_fixed: int
    techniques_applied: List[RefactoringTechnique]
    test_coverage_before: float
    test_coverage_after: float
    lines_before: int
    lines_after: int
    functions_before: int
    functions_after: int
    
    def improvement_percentage(self) -> float:
        """Calculate improvement in code quality."""
        if self.smells_detected == 0:
            return 0.0
        return (self.smells_fixed / self.smells_detected) * 100
