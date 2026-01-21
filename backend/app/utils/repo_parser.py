"""
Repository Parser for Phase 19 - Hybrid Edge-Cloud Orchestration.

This module provides functionality to clone Git repositories, parse source files,
extract import statements, and build dependency graphs for neural graph learning.
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Dict
import torch
from git import Repo
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript


class DependencyGraph:
    """Container for dependency graph data."""
    
    def __init__(self, edge_index: torch.Tensor, file_paths: List[str]):
        """
        Initialize a dependency graph.
        
        Args:
            edge_index: Edge list tensor of shape [2, num_edges]
            file_paths: List of file paths corresponding to node indices
        """
        self.edge_index = edge_index
        self.file_paths = file_paths
        self.num_nodes = len(file_paths)


class RepositoryParser:
    """Parse code repositories and build dependency graphs."""
    
    def __init__(self):
        """Initialize the repository parser with Tree-sitter parsers."""
        # Initialize Tree-sitter parsers for supported languages
        self._parsers = self._initialize_parsers()
        self._supported_extensions = {'.py', '.js', '.ts'}
    
    def _initialize_parsers(self) -> Dict[str, Parser]:
        """
        Initialize Tree-sitter parsers for each supported language.
        
        Returns:
            Dictionary mapping file extensions to Parser instances
        """
        parsers = {}
        
        # Python parser
        py_parser = Parser(Language(tspython.language()))
        parsers['.py'] = py_parser
        
        # JavaScript/TypeScript parser (same parser for both)
        js_parser = Parser(Language(tsjavascript.language()))
        parsers['.js'] = js_parser
        parsers['.ts'] = js_parser
        
        return parsers
    
    def clone_repository(self, repo_url: str) -> str:
        """
        Clone a Git repository to an isolated temporary directory.
        
        Uses tempfile.mkdtemp() with unique prefixes to ensure different
        jobs use different temp directories, preventing conflicts and
        security issues (Requirement 11.5).
        
        Args:
            repo_url: Repository URL (e.g., github.com/user/repo or https://github.com/user/repo)
            
        Returns:
            Path to cloned repository
            
        Raises:
            Exception: If cloning fails
        """
        # Ensure URL has protocol
        if not repo_url.startswith(('http://', 'https://', 'git@')):
            repo_url = f"https://{repo_url}"
        
        # Create temp directory with unique prefix (includes timestamp and PID)
        # This ensures concurrent clones use different directories
        import time
        timestamp = int(time.time() * 1000)  # Millisecond precision
        pid = os.getpid()
        prefix = f"neo_repo_{timestamp}_{pid}_"
        
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        
        try:
            print(f"📥 Cloning {repo_url}...")
            Repo.clone_from(repo_url, temp_dir, depth=1)  # Shallow clone for efficiency
            print(f"✅ Cloned to {temp_dir}")
            return temp_dir
        except Exception as e:
            # Clean up on failure
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"Failed to clone repository: {e}")
    
    def _find_source_files(self, repo_path: str) -> List[str]:
        """
        Find all source files in repository.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            List of absolute paths to source files
        """
        source_files = []
        
        # Directories to skip
        skip_dirs = {'.git', 'node_modules', '__pycache__', 'venv', '.venv', 
                     'dist', 'build', '.pytest_cache', '.hypothesis'}
        
        for ext in self._supported_extensions:
            for file_path in Path(repo_path).rglob(f"*{ext}"):
                # Skip files in excluded directories
                if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    continue
                source_files.append(str(file_path))
        
        print(f"📁 Found {len(source_files)} source files")
        return source_files
    
    def cleanup(self, repo_path: str):
        """
        Clean up temporary repository directory.
        
        Args:
            repo_path: Path to repository to remove
        """
        try:
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path, ignore_errors=True)
                print(f"🧹 Cleaned up {repo_path}")
        except Exception as e:
            print(f"⚠️  Cleanup failed: {e}")
    
    def _extract_imports(self, file_path: str) -> List[str]:
        """
        Extract import statements from a source file.
        
        Args:
            file_path: Path to source file
            
        Returns:
            List of imported module/file paths
        """
        ext = Path(file_path).suffix
        parser = self._parsers.get(ext)
        
        if not parser:
            return []
        
        try:
            with open(file_path, 'rb') as f:
                code = f.read()
            
            tree = parser.parse(code)
            imports = []
            
            # Language-specific import extraction
            if ext == '.py':
                imports = self._extract_python_imports(tree.root_node, code)
            elif ext in ['.js', '.ts']:
                imports = self._extract_javascript_imports(tree.root_node, code)
            
            return imports
            
        except Exception as e:
            # Log error but continue with remaining files
            print(f"⚠️  Failed to parse {file_path}: {e}")
            return []
    
    def _extract_python_imports(self, node, code: bytes) -> List[str]:
        """
        Extract Python import statements.
        
        Args:
            node: Tree-sitter root node
            code: Source code as bytes
            
        Returns:
            List of imported module names
        """
        imports = []
        
        def traverse(node):
            if node.type == 'import_statement':
                # import module
                for child in node.children:
                    if child.type == 'dotted_name':
                        import_name = code[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                        imports.append(import_name)
            elif node.type == 'import_from_statement':
                # from module import ...
                for child in node.children:
                    if child.type == 'dotted_name':
                        import_name = code[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                        imports.append(import_name)
            
            # Recursively traverse children
            for child in node.children:
                traverse(child)
        
        traverse(node)
        return imports
    
    def _extract_javascript_imports(self, node, code: bytes) -> List[str]:
        """
        Extract JavaScript/TypeScript import statements.
        
        Args:
            node: Tree-sitter root node
            code: Source code as bytes
            
        Returns:
            List of imported module/file paths
        """
        imports = []
        
        def traverse(node):
            if node.type == 'import_statement':
                # import ... from 'module'
                for child in node.children:
                    if child.type == 'string':
                        # Remove quotes
                        import_path = code[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                        import_path = import_path.strip('"\'')
                        imports.append(import_path)
            
            # Recursively traverse children
            for child in node.children:
                traverse(child)
        
        traverse(node)
        return imports

    def build_dependency_graph(self, repo_path: str) -> DependencyGraph:
        """
        Build dependency graph from repository.
        
        Args:
            repo_path: Path to cloned repository
            
        Returns:
            DependencyGraph with edge_index and file_paths
        """
        # Find all source files
        file_paths = self._find_source_files(repo_path)
        
        if not file_paths:
            # Empty repository - return empty graph with self-loop
            print("⚠️  No source files found")
            edge_index = torch.tensor([[0], [0]], dtype=torch.long)
            return DependencyGraph(edge_index=edge_index, file_paths=["<empty>"])
        
        # Create file index mapping
        file_to_idx = {path: idx for idx, path in enumerate(file_paths)}
        
        # Extract imports and build edges
        edges = []
        for file_path in file_paths:
            imports = self._extract_imports(file_path)
            
            # Resolve imports to file paths
            for import_path in imports:
                resolved = self._resolve_import(import_path, file_path, repo_path)
                if resolved and resolved in file_to_idx:
                    # Add edge: file -> imported_file
                    edges.append([file_to_idx[file_path], file_to_idx[resolved]])
        
        # Convert to PyTorch tensor
        if edges:
            edge_index = torch.tensor(edges, dtype=torch.long).t()
        else:
            # Empty graph - create self-loops for all nodes
            edge_index = torch.tensor([[i, i] for i in range(len(file_paths))], dtype=torch.long).t()
        
        print(f"📊 Built graph: {len(file_paths)} nodes, {edge_index.shape[1]} edges")
        
        return DependencyGraph(edge_index=edge_index, file_paths=file_paths)
    
    def _resolve_import(self, import_path: str, current_file: str, repo_path: str) -> Optional[str]:
        """
        Resolve import path to actual file path.
        
        Args:
            import_path: Import statement path (e.g., './utils' or 'app.models')
            current_file: Path to file containing the import
            repo_path: Root path of repository
            
        Returns:
            Resolved absolute file path or None if not found
        """
        # Handle relative imports (JavaScript/TypeScript style)
        if import_path.startswith('.'):
            current_dir = Path(current_file).parent
            resolved = (current_dir / import_path).resolve()
            
            # Try with common extensions
            for ext in ['.py', '.js', '.ts', '/index.js', '/index.ts']:
                candidate = Path(str(resolved) + ext)
                if candidate.exists() and str(candidate) != current_file:
                    return str(candidate)
        
        # Handle absolute imports (Python style)
        # Convert module path to file path (e.g., 'app.models' -> 'app/models.py')
        if '.' in import_path and not import_path.startswith('.'):
            # Try to resolve as Python module
            module_parts = import_path.split('.')
            
            # Try different combinations
            for i in range(len(module_parts), 0, -1):
                module_path = Path(repo_path) / '/'.join(module_parts[:i])
                
                # Try as file
                for ext in ['.py']:
                    candidate = Path(str(module_path) + ext)
                    if candidate.exists() and str(candidate) != current_file:
                        return str(candidate)
                
                # Try as package
                candidate = module_path / '__init__.py'
                if candidate.exists() and str(candidate) != current_file:
                    return str(candidate)
        
        # Could not resolve
        return None
