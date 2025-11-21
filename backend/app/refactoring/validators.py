"""
Validators for code quality checks.

Implements specific validators for function length, class size,
type hint coverage, and code duplication detection.
"""

import ast
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass

from .models import CodeSmell, SmellType, Severity, Location, RefactoringTechnique
from .constants import (
    MAX_FUNCTION_LINES,
    MAX_CLASS_LINES,
    DUPLICATION_SIMILARITY_THRESHOLD,
    MIN_TYPE_HINT_COVERAGE,
)


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    start_line: int
    end_line: int
    line_count: int
    class_name: Optional[str] = None
    has_type_hints: bool = False
    parameter_count: int = 0


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    start_line: int
    end_line: int
    line_count: int
    method_count: int
    public_method_count: int


class FunctionLengthChecker:
    """
    Checks for functions exceeding maximum line count.
    
    Identifies LONG_FUNCTION code smell by analyzing function
    definitions and counting non-comment, non-whitespace lines.
    """
    
    def __init__(self, max_lines: int = MAX_FUNCTION_LINES):
        """
        Initialize function length checker.
        
        Args:
            max_lines: Maximum allowed lines per function
        """
        self.max_lines = max_lines
    
    def check_file(self, file_path: Path) -> List[CodeSmell]:
        """
        Check all functions in a file for length violations.
        
        Args:
            file_path: Path to Python file to check
            
        Returns:
            List of CodeSmell instances for long functions
        """
        smells = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            functions = self._extract_functions(tree, source)
            
            for func in functions:
                if func.line_count > self.max_lines:
                    smell = self._create_smell(file_path, func)
                    smells.append(smell)
        
        except Exception as e:
            # Log error but don't fail - continue with other files
            print(f"Error checking {file_path}: {e}")
        
        return smells
    
    def _extract_functions(
        self, 
        tree: ast.AST, 
        source: str
    ) -> List[FunctionInfo]:
        """Extract all function definitions from AST."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = self._analyze_function(node, source)
                functions.append(func_info)
        
        return functions
    
    def _analyze_function(
        self, 
        node: ast.FunctionDef, 
        source: str
    ) -> FunctionInfo:
        """Analyze a function node and extract information."""
        # Count actual code lines (exclude comments and blank lines)
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        source_lines = source.split('\n')
        code_lines = 0
        
        for i in range(start_line - 1, min(end_line, len(source_lines))):
            line = source_lines[i].strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                code_lines += 1
        
        # Determine if function is in a class
        class_name = None
        # Note: This is simplified - full implementation would track class context
        
        return FunctionInfo(
            name=node.name,
            start_line=start_line,
            end_line=end_line,
            line_count=code_lines,
            class_name=class_name,
        )
    
    def _create_smell(
        self, 
        file_path: Path, 
        func: FunctionInfo
    ) -> CodeSmell:
        """Create CodeSmell for long function."""
        location = Location(
            file_path=file_path,
            start_line=func.start_line,
            end_line=func.end_line,
            function_name=func.name,
            class_name=func.class_name,
        )
        
        severity = Severity.HIGH if func.line_count > self.max_lines * 2 else Severity.MEDIUM
        
        return CodeSmell(
            smell_type=SmellType.LONG_FUNCTION,
            severity=severity,
            location=location,
            description=f"Function '{func.name}' has {func.line_count} lines (max: {self.max_lines})",
            suggested_technique=RefactoringTechnique.EXTRACT_FUNCTION,
            metrics={"line_count": func.line_count, "max_lines": self.max_lines},
        )


class ClassSizeChecker:
    """
    Checks for classes exceeding maximum line count or method count.
    
    Identifies LARGE_CLASS code smell by analyzing class definitions.
    """
    
    def __init__(
        self, 
        max_lines: int = MAX_CLASS_LINES,
        max_methods: int = 10
    ):
        """
        Initialize class size checker.
        
        Args:
            max_lines: Maximum allowed lines per class
            max_methods: Maximum allowed public methods per class
        """
        self.max_lines = max_lines
        self.max_methods = max_methods
    
    def check_file(self, file_path: Path) -> List[CodeSmell]:
        """
        Check all classes in a file for size violations.
        
        Args:
            file_path: Path to Python file to check
            
        Returns:
            List of CodeSmell instances for large classes
        """
        smells = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            classes = self._extract_classes(tree, source)
            
            for cls in classes:
                if cls.line_count > self.max_lines or cls.public_method_count > self.max_methods:
                    smell = self._create_smell(file_path, cls)
                    smells.append(smell)
        
        except Exception as e:
            print(f"Error checking {file_path}: {e}")
        
        return smells
    
    def _extract_classes(
        self, 
        tree: ast.AST, 
        source: str
    ) -> List[ClassInfo]:
        """Extract all class definitions from AST."""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self._analyze_class(node, source)
                classes.append(class_info)
        
        return classes
    
    def _analyze_class(
        self, 
        node: ast.ClassDef, 
        source: str
    ) -> ClassInfo:
        """Analyze a class node and extract information."""
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        # Count code lines
        source_lines = source.split('\n')
        code_lines = 0
        
        for i in range(start_line - 1, min(end_line, len(source_lines))):
            line = source_lines[i].strip()
            if line and not line.startswith('#'):
                code_lines += 1
        
        # Count methods
        method_count = 0
        public_method_count = 0
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_count += 1
                if not item.name.startswith('_'):
                    public_method_count += 1
        
        return ClassInfo(
            name=node.name,
            start_line=start_line,
            end_line=end_line,
            line_count=code_lines,
            method_count=method_count,
            public_method_count=public_method_count,
        )
    
    def _create_smell(
        self, 
        file_path: Path, 
        cls: ClassInfo
    ) -> CodeSmell:
        """Create CodeSmell for large class."""
        location = Location(
            file_path=file_path,
            start_line=cls.start_line,
            end_line=cls.end_line,
            class_name=cls.name,
        )
        
        reasons = []
        if cls.line_count > self.max_lines:
            reasons.append(f"{cls.line_count} lines (max: {self.max_lines})")
        if cls.public_method_count > self.max_methods:
            reasons.append(f"{cls.public_method_count} public methods (max: {self.max_methods})")
        
        severity = Severity.HIGH if cls.line_count > self.max_lines * 1.5 else Severity.MEDIUM
        
        return CodeSmell(
            smell_type=SmellType.LARGE_CLASS,
            severity=severity,
            location=location,
            description=f"Class '{cls.name}' is too large: {', '.join(reasons)}",
            suggested_technique=RefactoringTechnique.EXTRACT_CLASS,
            metrics={
                "line_count": cls.line_count,
                "method_count": cls.method_count,
                "public_method_count": cls.public_method_count,
            },
        )


class TypeHintCoverageChecker:
    """
    Checks for missing type hints on public methods.
    
    Verifies 100% type hint coverage on all public methods
    as required by Phase 12 standards.
    """
    
    def __init__(self, min_coverage: float = MIN_TYPE_HINT_COVERAGE):
        """
        Initialize type hint coverage checker.
        
        Args:
            min_coverage: Minimum required coverage (0.0-1.0)
        """
        self.min_coverage = min_coverage
    
    def check_file(self, file_path: Path) -> Tuple[float, List[CodeSmell]]:
        """
        Check type hint coverage in a file.
        
        Args:
            file_path: Path to Python file to check
            
        Returns:
            Tuple of (coverage_percentage, list of smells)
        """
        smells = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            total_public = 0
            typed_public = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip private methods
                    if node.name.startswith('_') and not node.name.startswith('__'):
                        continue
                    
                    total_public += 1
                    
                    if self._has_complete_type_hints(node):
                        typed_public += 1
                    else:
                        smell = self._create_smell(file_path, node)
                        smells.append(smell)
            
            coverage = typed_public / total_public if total_public > 0 else 1.0
            
            return coverage, smells
        
        except Exception as e:
            print(f"Error checking {file_path}: {e}")
            return 0.0, []
    
    def _has_complete_type_hints(self, node: ast.FunctionDef) -> bool:
        """Check if function has complete type hints."""
        # Check return type
        if node.returns is None and node.name != '__init__':
            return False
        
        # Check parameter types (skip self/cls)
        for arg in node.args.args:
            if arg.arg in ('self', 'cls'):
                continue
            if arg.annotation is None:
                return False
        
        return True
    
    def _create_smell(
        self, 
        file_path: Path, 
        node: ast.FunctionDef
    ) -> CodeSmell:
        """Create CodeSmell for missing type hints."""
        location = Location(
            file_path=file_path,
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            function_name=node.name,
        )
        
        missing = []
        if node.returns is None and node.name != '__init__':
            missing.append("return type")
        
        for arg in node.args.args:
            if arg.arg not in ('self', 'cls') and arg.annotation is None:
                missing.append(f"parameter '{arg.arg}'")
        
        return CodeSmell(
            smell_type=SmellType.PRIMITIVE_OBSESSION,  # Using this as proxy
            severity=Severity.MEDIUM,
            location=location,
            description=f"Function '{node.name}' missing type hints: {', '.join(missing)}",
            suggested_technique=RefactoringTechnique.REPLACE_PRIMITIVE_WITH_OBJECT,
            metrics={"missing_hints": missing},
        )


class CodeDuplicationDetector:
    """
    Detects duplicated code blocks across files.
    
    Uses AST similarity matching to identify code duplication
    above the configured threshold.
    """
    
    def __init__(self, similarity_threshold: float = DUPLICATION_SIMILARITY_THRESHOLD):
        """
        Initialize code duplication detector.
        
        Args:
            similarity_threshold: Minimum similarity to flag as duplicate (0.0-1.0)
        """
        self.similarity_threshold = similarity_threshold
    
    def check_files(self, file_paths: List[Path]) -> List[CodeSmell]:
        """
        Check for code duplication across multiple files.
        
        Args:
            file_paths: List of Python files to check
            
        Returns:
            List of CodeSmell instances for duplicated code
        """
        smells = []
        
        # Extract all function bodies
        function_bodies: Dict[Path, List[Tuple[ast.FunctionDef, str]]] = {}
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                tree = ast.parse(source, filename=str(file_path))
                bodies = self._extract_function_bodies(tree, source)
                function_bodies[file_path] = bodies
            
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # Compare all pairs of functions
        checked_pairs: Set[Tuple[str, str]] = set()
        
        for file1, bodies1 in function_bodies.items():
            for func1, body1 in bodies1:
                for file2, bodies2 in function_bodies.items():
                    for func2, body2 in bodies2:
                        # Skip same function
                        if file1 == file2 and func1.name == func2.name:
                            continue
                        
                        # Skip already checked pairs
                        pair_key = tuple(sorted([
                            f"{file1}:{func1.name}",
                            f"{file2}:{func2.name}"
                        ]))
                        
                        if pair_key in checked_pairs:
                            continue
                        
                        checked_pairs.add(pair_key)
                        
                        # Check similarity
                        similarity = self._calculate_similarity(body1, body2)
                        
                        if similarity >= self.similarity_threshold:
                            smell = self._create_smell(
                                file1, func1, file2, func2, similarity
                            )
                            smells.append(smell)
        
        return smells
    
    def _extract_function_bodies(
        self, 
        tree: ast.AST, 
        source: str
    ) -> List[Tuple[ast.FunctionDef, str]]:
        """Extract function definitions and their body text."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Get function body as text
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                
                source_lines = source.split('\n')
                body_lines = source_lines[start_line - 1:end_line]
                body_text = '\n'.join(body_lines)
                
                functions.append((node, body_text))
        
        return functions
    
    def _calculate_similarity(self, body1: str, body2: str) -> float:
        """
        Calculate similarity between two code bodies.
        
        Uses simple line-based comparison. More sophisticated
        implementations could use AST structural comparison.
        """
        lines1 = set(line.strip() for line in body1.split('\n') if line.strip())
        lines2 = set(line.strip() for line in body2.split('\n') if line.strip())
        
        if not lines1 or not lines2:
            return 0.0
        
        intersection = len(lines1 & lines2)
        union = len(lines1 | lines2)
        
        return intersection / union if union > 0 else 0.0
    
    def _create_smell(
        self,
        file1: Path,
        func1: ast.FunctionDef,
        file2: Path,
        func2: ast.FunctionDef,
        similarity: float
    ) -> CodeSmell:
        """Create CodeSmell for duplicated code."""
        location = Location(
            file_path=file1,
            start_line=func1.lineno,
            end_line=func1.end_lineno or func1.lineno,
            function_name=func1.name,
        )
        
        severity = Severity.HIGH if similarity > 0.95 else Severity.MEDIUM
        
        return CodeSmell(
            smell_type=SmellType.DUPLICATED_CODE,
            severity=severity,
            location=location,
            description=(
                f"Function '{func1.name}' in {file1.name} is {similarity*100:.1f}% "
                f"similar to '{func2.name}' in {file2.name}"
            ),
            suggested_technique=RefactoringTechnique.EXTRACT_FUNCTION,
            metrics={
                "similarity": similarity,
                "duplicate_file": str(file2),
                "duplicate_function": func2.name,
            },
        )
