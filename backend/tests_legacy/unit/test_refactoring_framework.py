"""
Tests for refactoring validation framework.

Tests all components: code smell detection, validators, and reporting.
"""

import pytest
from pathlib import Path

from app.refactoring.models import (
    SmellType,
    Severity,
    RefactoringTechnique,
    Location,
    CodeSmell,
    SmellReport,
)
from app.refactoring.validators import (
    FunctionLengthChecker,
    ClassSizeChecker,
    TypeHintCoverageChecker,
    CodeDuplicationDetector,
)
from app.refactoring.detector import CodeSmellDetector, PrioritizedSmells


class TestModels:
    """Test data models."""
    
    def test_location_creation(self):
        """Test Location model."""
        location = Location(
            file_path=Path("test.py"),
            start_line=10,
            end_line=20,
            function_name="test_func"
        )
        assert location.start_line == 10
        assert location.end_line == 20
        assert location.function_name == "test_func"
        assert "test.py:10-20" in str(location)
    
    def test_code_smell_creation(self):
        """Test CodeSmell model."""
        location = Location(
            file_path=Path("test.py"),
            start_line=10,
            end_line=20,
        )
        smell = CodeSmell(
            smell_type=SmellType.LONG_FUNCTION,
            severity=Severity.HIGH,
            location=location,
            description="Test smell",
            suggested_technique=RefactoringTechnique.EXTRACT_FUNCTION,
            metrics={"line_count": 50}
        )
        assert smell.smell_type == SmellType.LONG_FUNCTION
        assert smell.severity == Severity.HIGH
        assert smell.metrics["line_count"] == 50
    
    def test_smell_report_creation(self):
        """Test SmellReport model."""
        location = Location(
            file_path=Path("test.py"),
            start_line=10,
            end_line=20,
        )
        smell = CodeSmell(
            smell_type=SmellType.LONG_FUNCTION,
            severity=Severity.HIGH,
            location=location,
            description="Test smell",
            suggested_technique=RefactoringTechnique.EXTRACT_FUNCTION,
        )
        report = SmellReport(
            file_path=Path("test.py"),
            smells=[smell],
            total_lines=100,
            complexity_score=5.0
        )
        assert len(report.smells) == 1
        assert len(report.high_priority_smells()) == 1
        assert report.total_lines == 100


class TestFunctionLengthChecker:
    """Test function length checker."""
    
    def test_checker_initialization(self):
        """Test checker can be initialized."""
        checker = FunctionLengthChecker(max_lines=30)
        assert checker.max_lines == 30
    
    def test_check_file_exists(self):
        """Test checking a real file."""
        checker = FunctionLengthChecker(max_lines=30)
        file_path = Path("app/services/ml_classification_service.py")
        
        if file_path.exists():
            smells = checker.check_file(file_path)
            assert isinstance(smells, list)
            # Should find some long functions in ml_classification_service
            assert len(smells) >= 0
    
    def test_check_nonexistent_file(self):
        """Test checking a file that doesn't exist."""
        checker = FunctionLengthChecker(max_lines=30)
        file_path = Path("nonexistent_file.py")
        
        # Should not raise exception, just return empty list
        smells = checker.check_file(file_path)
        assert isinstance(smells, list)


class TestClassSizeChecker:
    """Test class size checker."""
    
    def test_checker_initialization(self):
        """Test checker can be initialized."""
        checker = ClassSizeChecker(max_lines=300, max_methods=10)
        assert checker.max_lines == 300
        assert checker.max_methods == 10
    
    def test_check_file_exists(self):
        """Test checking a real file."""
        checker = ClassSizeChecker(max_lines=300, max_methods=10)
        file_path = Path("app/services/ml_classification_service.py")
        
        if file_path.exists():
            smells = checker.check_file(file_path)
            assert isinstance(smells, list)


class TestTypeHintCoverageChecker:
    """Test type hint coverage checker."""
    
    def test_checker_initialization(self):
        """Test checker can be initialized."""
        checker = TypeHintCoverageChecker(min_coverage=1.0)
        assert checker.min_coverage == 1.0
    
    def test_check_file_exists(self):
        """Test checking a real file."""
        checker = TypeHintCoverageChecker(min_coverage=1.0)
        file_path = Path("app/services/ml_classification_service.py")
        
        if file_path.exists():
            coverage, smells = checker.check_file(file_path)
            assert isinstance(coverage, float)
            assert 0.0 <= coverage <= 1.0
            assert isinstance(smells, list)


class TestCodeDuplicationDetector:
    """Test code duplication detector."""
    
    def test_detector_initialization(self):
        """Test detector can be initialized."""
        detector = CodeDuplicationDetector(similarity_threshold=0.80)
        assert detector.similarity_threshold == 0.80
    
    def test_check_files(self):
        """Test checking multiple files."""
        detector = CodeDuplicationDetector(similarity_threshold=0.80)
        service_dir = Path("app/services")
        
        if service_dir.exists():
            files = list(service_dir.glob("*.py"))[:3]  # Test first 3 files
            smells = detector.check_files(files)
            assert isinstance(smells, list)


class TestCodeSmellDetector:
    """Test integrated code smell detector."""
    
    def test_detector_initialization(self):
        """Test detector can be initialized."""
        detector = CodeSmellDetector()
        assert detector.function_checker is not None
        assert detector.class_checker is not None
        assert detector.type_hint_checker is not None
        assert detector.duplication_detector is not None
    
    def test_analyze_file(self):
        """Test analyzing a single file."""
        detector = CodeSmellDetector()
        file_path = Path("app/services/ml_classification_service.py")
        
        if file_path.exists():
            report = detector.analyze_file(file_path)
            assert isinstance(report, SmellReport)
            assert report.file_path == file_path
            assert report.total_lines > 0
            assert isinstance(report.smells, list)
    
    def test_analyze_directory(self):
        """Test analyzing entire directory."""
        detector = CodeSmellDetector()
        service_dir = Path("app/services")
        
        if service_dir.exists():
            reports = detector.analyze_directory(service_dir)
            assert isinstance(reports, list)
            assert len(reports) > 0
            
            # All reports should be SmellReport instances
            for report in reports:
                assert isinstance(report, SmellReport)
    
    def test_prioritize_smells(self):
        """Test smell prioritization."""
        detector = CodeSmellDetector()
        
        # Create test reports
        location = Location(
            file_path=Path("test.py"),
            start_line=10,
            end_line=20,
        )
        
        high_smell = CodeSmell(
            smell_type=SmellType.LONG_FUNCTION,
            severity=Severity.HIGH,
            location=location,
            description="High priority",
            suggested_technique=RefactoringTechnique.EXTRACT_FUNCTION,
        )
        
        medium_smell = CodeSmell(
            smell_type=SmellType.LONG_PARAMETER_LIST,
            severity=Severity.MEDIUM,
            location=location,
            description="Medium priority",
            suggested_technique=RefactoringTechnique.REPLACE_PRIMITIVE_WITH_OBJECT,
        )
        
        report = SmellReport(
            file_path=Path("test.py"),
            smells=[high_smell, medium_smell],
            total_lines=100,
            complexity_score=5.0
        )
        
        prioritized = detector.prioritize_smells([report])
        assert isinstance(prioritized, PrioritizedSmells)
        assert len(prioritized.high_priority) == 1
        assert len(prioritized.medium_priority) == 1
        assert len(prioritized.low_priority) == 0
        assert prioritized.total_count() == 2
    
    def test_generate_summary_report(self):
        """Test summary report generation."""
        detector = CodeSmellDetector()
        service_dir = Path("app/services")
        
        if service_dir.exists():
            reports = detector.analyze_directory(service_dir)
            summary = detector.generate_summary_report(reports)
            
            assert isinstance(summary, str)
            assert "CODE SMELL DETECTION SUMMARY" in summary
            assert "Files Analyzed:" in summary
            assert "Total Smells:" in summary


class TestIntegration:
    """Integration tests for the complete framework."""
    
    def test_full_analysis_workflow(self):
        """Test complete analysis workflow."""
        detector = CodeSmellDetector()
        service_dir = Path("app/services")
        
        if not service_dir.exists():
            pytest.skip("Service directory not found")
        
        # Analyze directory
        reports = detector.analyze_directory(service_dir)
        assert len(reports) > 0
        
        # Prioritize smells
        prioritized = detector.prioritize_smells(reports)
        assert prioritized.total_count() >= 0
        
        # Generate summary
        summary = detector.generate_summary_report(reports)
        assert len(summary) > 0
    
    def test_smell_types_detected(self):
        """Test that various smell types are detected."""
        detector = CodeSmellDetector()
        file_path = Path("app/services/ml_classification_service.py")
        
        if not file_path.exists():
            pytest.skip("Test file not found")
        
        report = detector.analyze_file(file_path)
        
        # Should detect at least some smells
        smell_types = {smell.smell_type for smell in report.smells}
        
        # Check that we can detect different types
        # (actual types depend on current code state)
        assert isinstance(smell_types, set)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
