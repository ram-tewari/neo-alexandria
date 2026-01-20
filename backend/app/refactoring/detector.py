"""
Code smell detector for refactoring validation.

Orchestrates all validators to provide comprehensive code smell
detection across service modules.
"""

import ast
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

from .models import (
    SmellReport,
    CodeSmell,
    SmellType,
    Severity,
    Location,
    RefactoringTechnique,
)
from .validators import (
    FunctionLengthChecker,
    ClassSizeChecker,
    TypeHintCoverageChecker,
    CodeDuplicationDetector,
)


@dataclass
class PrioritizedSmells:
    """Prioritized list of code smells."""

    high_priority: List[CodeSmell]
    medium_priority: List[CodeSmell]
    low_priority: List[CodeSmell]

    def total_count(self) -> int:
        """Get total smell count."""
        return (
            len(self.high_priority) + len(self.medium_priority) + len(self.low_priority)
        )

    def summary(self) -> str:
        """Generate summary string."""
        return (
            f"Total Smells: {self.total_count()}\n"
            f"  High Priority: {len(self.high_priority)}\n"
            f"  Medium Priority: {len(self.medium_priority)}\n"
            f"  Low Priority: {len(self.low_priority)}"
        )


class CodeSmellDetector:
    """
    Detects code smells using AST analysis and pattern matching.

    Orchestrates multiple validators to provide comprehensive
    code smell detection for refactoring validation.
    """

    def __init__(self):
        """Initialize code smell detector with all validators."""
        self.function_checker = FunctionLengthChecker()
        self.class_checker = ClassSizeChecker()
        self.type_hint_checker = TypeHintCoverageChecker()
        self.duplication_detector = CodeDuplicationDetector()

    def analyze_file(self, file_path: Path) -> SmellReport:
        """
        Analyze a single file for code smells.

        Args:
            file_path: Path to Python file to analyze

        Returns:
            SmellReport with all detected smells
        """
        smells: List[CodeSmell] = []

        # Check function length
        smells.extend(self.function_checker.check_file(file_path))

        # Check class size
        smells.extend(self.class_checker.check_file(file_path))

        # Check type hint coverage
        coverage, type_smells = self.type_hint_checker.check_file(file_path)
        smells.extend(type_smells)

        # Additional smell detection
        smells.extend(self._detect_feature_envy(file_path))
        smells.extend(self._detect_long_parameter_lists(file_path))

        # Calculate metrics
        total_lines = self._count_lines(file_path)
        complexity = self._calculate_complexity(file_path)

        return SmellReport(
            file_path=file_path,
            smells=smells,
            total_lines=total_lines,
            complexity_score=complexity,
        )

    def analyze_directory(self, dir_path: Path) -> List[SmellReport]:
        """
        Analyze all Python files in directory.

        Args:
            dir_path: Path to directory to analyze

        Returns:
            List of SmellReport for each file
        """
        reports = []

        # Find all Python files
        python_files = list(dir_path.rglob("*.py"))

        # Analyze each file
        for file_path in python_files:
            # Skip test files and __pycache__
            if "test_" in file_path.name or "__pycache__" in str(file_path):
                continue

            try:
                report = self.analyze_file(file_path)
                reports.append(report)
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

        # Check for code duplication across files
        duplication_smells = self.duplication_detector.check_files(python_files)

        # Add duplication smells to appropriate reports
        for smell in duplication_smells:
            for report in reports:
                if report.file_path == smell.location.file_path:
                    report.smells.append(smell)
                    break

        return reports

    def prioritize_smells(self, reports: List[SmellReport]) -> PrioritizedSmells:
        """
        Rank smells by severity and frequency.

        Args:
            reports: List of smell reports to prioritize

        Returns:
            PrioritizedSmells with categorized smells
        """
        high_priority = []
        medium_priority = []
        low_priority = []

        for report in reports:
            for smell in report.smells:
                if smell.severity == Severity.HIGH:
                    high_priority.append(smell)
                elif smell.severity == Severity.MEDIUM:
                    medium_priority.append(smell)
                else:
                    low_priority.append(smell)

        # Sort by file and line number for easier navigation
        high_priority.sort(
            key=lambda s: (str(s.location.file_path), s.location.start_line)
        )
        medium_priority.sort(
            key=lambda s: (str(s.location.file_path), s.location.start_line)
        )
        low_priority.sort(
            key=lambda s: (str(s.location.file_path), s.location.start_line)
        )

        return PrioritizedSmells(
            high_priority=high_priority,
            medium_priority=medium_priority,
            low_priority=low_priority,
        )

    def _detect_feature_envy(self, file_path: Path) -> List[CodeSmell]:
        """
        Detect feature envy code smell.

        Feature envy occurs when a function uses more methods from
        another class than from its own class.
        """
        smells = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            ast.parse(source, filename=str(file_path))

            # Simplified detection - full implementation would track
            # method calls and compare internal vs external usage
            # This is a placeholder for the concept

        except Exception as e:
            print(f"Error detecting feature envy in {file_path}: {e}")

        return smells

    def _detect_long_parameter_lists(self, file_path: Path) -> List[CodeSmell]:
        """
        Detect functions with too many parameters.

        Long parameter lists indicate the function may be doing too much
        or that parameters should be grouped into an object.
        """
        smells = []
        max_params = 5

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Count parameters (excluding self/cls)
                    param_count = len(
                        [
                            arg
                            for arg in node.args.args
                            if arg.arg not in ("self", "cls")
                        ]
                    )

                    if param_count > max_params:
                        location = Location(
                            file_path=file_path,
                            start_line=node.lineno,
                            end_line=node.end_lineno or node.lineno,
                            function_name=node.name,
                        )

                        smell = CodeSmell(
                            smell_type=SmellType.LONG_PARAMETER_LIST,
                            severity=Severity.MEDIUM,
                            location=location,
                            description=(
                                f"Function '{node.name}' has {param_count} parameters "
                                f"(max recommended: {max_params})"
                            ),
                            suggested_technique=RefactoringTechnique.REPLACE_PRIMITIVE_WITH_OBJECT,
                            metrics={"parameter_count": param_count},
                        )
                        smells.append(smell)

        except Exception as e:
            print(f"Error detecting long parameter lists in {file_path}: {e}")

        return smells

    def _count_lines(self, file_path: Path) -> int:
        """Count total lines in file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return len(f.readlines())
        except Exception:
            return 0

    def _calculate_complexity(self, file_path: Path) -> float:
        """
        Calculate complexity score for file.

        Uses a simple heuristic based on:
        - Number of functions
        - Number of classes
        - Average function length
        - Nesting depth

        Returns score from 0.0 (simple) to 10.0 (very complex).
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))

            function_count = 0
            class_count = 0
            max_nesting = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function_count += 1
                elif isinstance(node, ast.ClassDef):
                    class_count += 1

            # Simple complexity calculation
            complexity = (
                (function_count * 0.1) + (class_count * 0.5) + (max_nesting * 0.3)
            )

            return min(complexity, 10.0)

        except Exception:
            return 0.0

    def generate_summary_report(self, reports: List[SmellReport]) -> str:
        """
        Generate human-readable summary of all reports.

        Args:
            reports: List of smell reports

        Returns:
            Formatted summary string
        """
        total_files = len(reports)
        total_smells = sum(len(r.smells) for r in reports)
        total_lines = sum(r.total_lines for r in reports)

        prioritized = self.prioritize_smells(reports)

        # Count by smell type
        smell_counts: Dict[SmellType, int] = {}
        for report in reports:
            for smell in report.smells:
                smell_counts[smell.smell_type] = (
                    smell_counts.get(smell.smell_type, 0) + 1
                )

        summary = [
            "=" * 70,
            "CODE SMELL DETECTION SUMMARY",
            "=" * 70,
            f"\nFiles Analyzed: {total_files}",
            f"Total Lines: {total_lines:,}",
            f"Total Smells: {total_smells}",
            f"\n{prioritized.summary()}",
            "\nSmells by Type:",
        ]

        for smell_type, count in sorted(
            smell_counts.items(), key=lambda x: x[1], reverse=True
        ):
            summary.append(f"  {smell_type.value}: {count}")

        summary.append("\n" + "=" * 70)

        return "\n".join(summary)
