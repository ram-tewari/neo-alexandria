# Refactoring Validation Framework

Automated code smell detection and validation framework for Phase 12 refactoring.

## Overview

This framework provides comprehensive code quality analysis tools to support systematic refactoring following Martin Fowler's methodology. It detects code smells, validates refactoring progress, and generates detailed reports.

## Components

### 1. Code Smell Detector (`detector.py`)

Main orchestrator that coordinates all validators and provides comprehensive analysis.

**Features:**
- Analyzes individual files or entire directories
- Detects multiple code smell types
- Prioritizes smells by severity
- Generates summary reports

**Usage:**
```python
from app.refactoring.detector import CodeSmellDetector

detector = CodeSmellDetector()

# Analyze single file
report = detector.analyze_file(Path("app/services/my_service.py"))
print(report.summary())

# Analyze directory
reports = detector.analyze_directory(Path("app/services"))
summary = detector.generate_summary_report(reports)
print(summary)

# Prioritize smells
prioritized = detector.prioritize_smells(reports)
print(f"High priority: {len(prioritized.high_priority)}")
```

### 2. Validators (`validators.py`)

Specialized validators for specific code quality checks.

#### FunctionLengthChecker

Detects functions exceeding maximum line count (default: 30 lines).

```python
from app.refactoring.validators import FunctionLengthChecker

checker = FunctionLengthChecker(max_lines=30)
smells = checker.check_file(file_path)
```

#### ClassSizeChecker

Detects classes exceeding maximum size (default: 300 lines or 10 public methods).

```python
from app.refactoring.validators import ClassSizeChecker

checker = ClassSizeChecker(max_lines=300, max_methods=10)
smells = checker.check_file(file_path)
```

#### TypeHintCoverageChecker

Verifies type hint coverage on public methods (target: 100%).

```python
from app.refactoring.validators import TypeHintCoverageChecker

checker = TypeHintCoverageChecker(min_coverage=1.0)
coverage, smells = checker.check_file(file_path)
print(f"Coverage: {coverage*100:.1f}%")
```

#### CodeDuplicationDetector

Detects duplicated code across multiple files (threshold: 80% similarity).

```python
from app.refactoring.validators import CodeDuplicationDetector

detector = CodeDuplicationDetector(similarity_threshold=0.80)
smells = detector.check_files([file1, file2, file3])
```

### 3. Data Models (`models.py`)

Type-safe data structures for representing code smells and reports.

**Key Models:**
- `SmellType`: Enum of code smell types (Fowler's taxonomy)
- `Severity`: HIGH, MEDIUM, LOW priority levels
- `RefactoringTechnique`: Suggested refactoring techniques
- `Location`: Code location with file, line numbers, function/class names
- `CodeSmell`: Individual smell instance with all metadata
- `SmellReport`: Complete report for a file
- `PrioritizedSmells`: Categorized smells by severity

### 4. Constants (`constants.py`)

Configuration values and thresholds.

**Key Constants:**
- `MAX_FUNCTION_LINES = 30`
- `MAX_CLASS_LINES = 300`
- `MAX_PUBLIC_METHODS = 10`
- `DUPLICATION_SIMILARITY_THRESHOLD = 0.80`
- `MIN_TYPE_HINT_COVERAGE = 1.0`
- `MIN_TEST_COVERAGE = 0.85`

### 5. CLI (`cli.py`)

Command-line interface for running analyses.

**Commands:**

```bash
# Analyze all services
python -m app.refactoring.cli analyze

# Analyze specific service
python -m app.refactoring.cli analyze --service ml_classification_service.py

# Check specific file
python -m app.refactoring.cli check app/services/my_service.py

# Generate JSON report
python -m app.refactoring.cli report --output refactoring_report.json
```

## Code Smells Detected

The framework detects the following code smells from Fowler's taxonomy:

1. **DUPLICATED_CODE**: Identical or highly similar code in multiple locations
2. **LONG_FUNCTION**: Functions exceeding 30 lines
3. **LARGE_CLASS**: Classes exceeding 300 lines or 10 public methods
4. **LONG_PARAMETER_LIST**: Functions with more than 5 parameters
5. **PRIMITIVE_OBSESSION**: Missing type hints (proxy for primitive usage)
6. **FEATURE_ENVY**: Functions using more external methods than internal (placeholder)

## Severity Levels

- **HIGH**: Must fix - blocks production readiness
- **MEDIUM**: Should fix - technical debt
- **LOW**: Nice to fix - minor improvement

## Suggested Refactoring Techniques

For each smell, the framework suggests appropriate Fowler refactoring techniques:

- `EXTRACT_FUNCTION`: Break down long functions
- `EXTRACT_CLASS`: Split large classes
- `REPLACE_PRIMITIVE_WITH_OBJECT`: Create domain objects
- `COMBINE_FUNCTIONS_INTO_CLASS`: Group related functions
- `SEPARATE_QUERY_FROM_MODIFIER`: Split side effects from queries
- `ENCAPSULATE_COLLECTION`: Hide collection internals
- `SPLIT_PHASE`: Separate parsing from processing
- `REPLACE_CONDITIONAL_WITH_POLYMORPHISM`: Use strategy pattern

## Example Workflow

```python
from pathlib import Path
from app.refactoring.detector import CodeSmellDetector

# Initialize detector
detector = CodeSmellDetector()

# Analyze service directory
service_dir = Path("app/services")
reports = detector.analyze_directory(service_dir)

# Prioritize smells
prioritized = detector.prioritize_smells(reports)

# Focus on high priority smells
for smell in prioritized.high_priority:
    print(f"\n{smell}")
    print(f"Suggested: {smell.suggested_technique.value}")

# Generate summary
summary = detector.generate_summary_report(reports)
print(summary)
```

## Integration with Testing

The framework is designed to work with the existing test suite:

```bash
# Run framework tests
python -m pytest tests/test_refactoring_framework.py -v

# Run with coverage
python -m pytest tests/test_refactoring_framework.py --cov=app.refactoring
```

## Output Examples

### Console Output

```
======================================================================
CODE SMELL DETECTION SUMMARY
======================================================================

Files Analyzed: 32
Total Lines: 15,234
Total Smells: 127

Total Smells: 127
  High Priority: 23
  Medium Priority: 78
  Low Priority: 26

Smells by Type:
  long_function: 45
  long_parameter_list: 32
  large_class: 18
  duplicated_code: 15
  primitive_obsession: 17

======================================================================
```

### JSON Report

```json
{
  "total_files": 32,
  "total_smells": 127,
  "reports": [
    {
      "file": "app/services/ml_classification_service.py",
      "total_lines": 686,
      "complexity_score": 7.5,
      "smell_count": 12,
      "smells": [
        {
          "type": "long_function",
          "severity": "high",
          "location": "ml_classification_service.py:150-210 (predict)",
          "description": "Function 'predict' has 60 lines (max: 30)",
          "suggested_technique": "extract_function",
          "metrics": {
            "line_count": 60,
            "max_lines": 30
          }
        }
      ]
    }
  ]
}
```

## Requirements Satisfied

This framework satisfies the following Phase 12 requirements:

- **1.1-1.5**: Automated code smell detection (all types)
- **8.2**: Function length checking (<30 lines)
- **8.3**: Class size checking (<300 lines)
- **8.4**: Type hint coverage checking (100% on public methods)
- **9.2-9.5**: Validation and testing support

## Future Enhancements

Potential improvements for future iterations:

1. **Cyclomatic Complexity**: Add McCabe complexity calculation
2. **Cognitive Complexity**: Implement cognitive complexity metrics
3. **Feature Envy Detection**: Complete implementation with call graph analysis
4. **Data Clumps**: Detect parameter groups that should be objects
5. **Repeated Switches**: Identify conditional logic patterns
6. **AST-based Duplication**: More sophisticated structural comparison
7. **Auto-fix Suggestions**: Generate refactoring code snippets
8. **IDE Integration**: VS Code extension for real-time analysis
9. **Git Integration**: Track smell trends over commits
10. **Performance Profiling**: Identify performance bottlenecks

## Architecture

```
app/refactoring/
├── __init__.py          # Package exports
├── models.py            # Data models and enums
├── constants.py         # Configuration constants
├── validators.py        # Individual validators
├── detector.py          # Main orchestrator
├── cli.py              # Command-line interface
└── README.md           # This file

tests/
└── test_refactoring_framework.py  # Comprehensive tests
```

## Contributing

When adding new validators or smell types:

1. Add the smell type to `SmellType` enum in `models.py`
2. Create validator class in `validators.py`
3. Integrate into `CodeSmellDetector` in `detector.py`
4. Add tests to `test_refactoring_framework.py`
5. Update this README with usage examples

## References

- Martin Fowler, "Refactoring: Improving the Design of Existing Code" (2nd Edition)
- INCOSE Requirements Quality Rules
- EARS (Easy Approach to Requirements Syntax)
- Phase 12 Design Document: `.kiro/specs/phase12-fowler-refactoring/design.md`
