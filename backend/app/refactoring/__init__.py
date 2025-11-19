"""
Refactoring validation framework for Phase 12.

This module provides automated code smell detection, validation,
and quality metrics for the systematic refactoring process.
"""

from .models import (
    SmellType,
    Severity,
    RefactoringTechnique,
    Location,
    CodeSmell,
    SmellReport,
    RefactoringResult,
    TestResults,
)
from .detector import CodeSmellDetector
from .validators import (
    FunctionLengthChecker,
    ClassSizeChecker,
    TypeHintCoverageChecker,
    CodeDuplicationDetector,
)

__all__ = [
    # Models
    "SmellType",
    "Severity",
    "RefactoringTechnique",
    "Location",
    "CodeSmell",
    "SmellReport",
    "RefactoringResult",
    "TestResults",
    # Detector
    "CodeSmellDetector",
    # Validators
    "FunctionLengthChecker",
    "ClassSizeChecker",
    "TypeHintCoverageChecker",
    "CodeDuplicationDetector",
]
