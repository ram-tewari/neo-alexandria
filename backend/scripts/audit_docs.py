#!/usr/bin/env python3
"""
Documentation Audit Script

This script audits all API documentation against actual router implementations
to ensure docs match the codebase.

Usage:
    python scripts/audit_docs.py
    python scripts/audit_docs.py --fix  # Auto-update docs
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import argparse


@dataclass
class Endpoint:
    """Represents an API endpoint."""
    method: str
    path: str
    function_name: str
    summary: str
    description: str
    line_number: int


@dataclass
class AuditResult:
    """Audit results for a module."""
    module_name: str
    router_file: Path
    doc_file: Path
    endpoints_in_code: List[Endpoint]
    endpoints_in_docs: Set[str]
    missing_in_docs: List[Endpoint]
    extra_in_docs: Set[str]
    outdated_descriptions: List[Tuple[Endpoint, str]]


class RouterParser:
    """Parse FastAPI router files to extract endpoints."""
    
    def __init__(self, router_file: Path):
        self.router_file = router_file
        self.endpoints: List[Endpoint] = []
    
    def parse(self) -> List[Endpoint]:
        """Parse router file and extract all endpoints."""
        with open(self.router_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"⚠️  Syntax error in {self.router_file}: {e}")
            return []
        
        # Find all @router.method decorators
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                endpoint = self._extract_endpoint(node, content)
                if endpoint:
                    self.endpoints.append(endpoint)
        
        return self.endpoints
    
    def _extract_endpoint(self, node: ast.FunctionDef, content: str) -> Endpoint:
        """Extract endpoint info from function node."""
        # Check for @router decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if (isinstance(decorator.func.value, ast.Name) and 
                        decorator.func.value.id == 'router'):
                        
                        method = decorator.func.attr.upper()
                        path = self._extract_path(decorator)
                        summary, description = self._extract_docs(decorator, node)
                        
                        return Endpoint(
                            method=method,
                            path=path,
                            function_name=node.name,
                            summary=summary,
                            description=description,
                            line_number=node.lineno
                        )
        return None
    
    def _extract_path(self, decorator: ast.Call) -> str:
        """Extract path from decorator arguments."""
        if decorator.args:
            if isinstance(decorator.args[0], ast.Constant):
                return decorator.args[0].value
        return ""
    
    def _extract_docs(self, decorator: ast.Call, node: ast.FunctionDef) -> Tuple[str, str]:
        """Extract summary and description from decorator or docstring."""
        summary = ""
        description = ""
        
        # Check decorator kwargs for summary/description
        for keyword in decorator.keywords:
            if keyword.arg == "summary" and isinstance(keyword.value, ast.Constant):
                summary = keyword.value.value
            elif keyword.arg == "description" and isinstance(keyword.value, ast.Constant):
                description = keyword.value.value
        
        # Fallback to docstring
        if not summary and not description:
            docstring = ast.get_docstring(node)
            if docstring:
                lines = docstring.strip().split('\n')
                summary = lines[0] if lines else ""
                description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
        
        return summary, description


class DocParser:
    """Parse API documentation markdown files."""
    
    def __init__(self, doc_file: Path):
        self.doc_file = doc_file
        self.endpoints: Set[str] = set()
    
    def parse(self) -> Set[str]:
        """Parse doc file and extract documented endpoints."""
        if not self.doc_file.exists():
            return set()
        
        with open(self.doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all endpoint definitions (e.g., "POST /api/resources")
        pattern = r'(GET|POST|PUT|DELETE|PATCH)\s+(/api/[^\s\n]+)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        for method, path in matches:
            self.endpoints.add(f"{method.upper()} {path}")
        
        return self.endpoints


class DocumentationAuditor:
    """Main auditor class."""
    
    def __init__(self, backend_dir: Path):
        self.backend_dir = backend_dir
        self.modules_dir = backend_dir / "app" / "modules"
        self.docs_dir = backend_dir / "docs" / "api"
        self.results: List[AuditResult] = []
    
    def audit_all(self) -> List[AuditResult]:
        """Audit all modules."""
        # Find all module routers
        router_files = list(self.modules_dir.glob("*/router.py"))
        
        for router_file in sorted(router_files):
            module_name = router_file.parent.name
            result = self.audit_module(module_name, router_file)
            if result:
                self.results.append(result)
        
        return self.results
    
    def audit_module(self, module_name: str, router_file: Path) -> AuditResult:
        """Audit a single module."""
        doc_file = self.docs_dir / f"{module_name}.md"
        
        # Parse router
        router_parser = RouterParser(router_file)
        endpoints_in_code = router_parser.parse()
        
        # Parse docs
        doc_parser = DocParser(doc_file)
        endpoints_in_docs = doc_parser.parse()
        
        # Build endpoint signatures from code
        code_signatures = set()
        for ep in endpoints_in_code:
            sig = f"{ep.method} {ep.path}"
            code_signatures.add(sig)
        
        # Find discrepancies
        missing_in_docs = []
        for ep in endpoints_in_code:
            sig = f"{ep.method} {ep.path}"
            if sig not in endpoints_in_docs:
                missing_in_docs.append(ep)
        
        extra_in_docs = endpoints_in_docs - code_signatures
        
        return AuditResult(
            module_name=module_name,
            router_file=router_file,
            doc_file=doc_file,
            endpoints_in_code=endpoints_in_code,
            endpoints_in_docs=endpoints_in_docs,
            missing_in_docs=missing_in_docs,
            extra_in_docs=extra_in_docs,
            outdated_descriptions=[]
        )
    
    def print_report(self):
        """Print audit report."""
        print("=" * 80)
        print("DOCUMENTATION AUDIT REPORT")
        print("=" * 80)
        print()
        
        total_endpoints = 0
        total_missing = 0
        total_extra = 0
        
        for result in self.results:
            total_endpoints += len(result.endpoints_in_code)
            total_missing += len(result.missing_in_docs)
            total_extra += len(result.extra_in_docs)
            
            print(f"📦 Module: {result.module_name}")
            print(f"   Router: {result.router_file.relative_to(self.backend_dir)}")
            print(f"   Docs:   {result.doc_file.relative_to(self.backend_dir)}")
            print(f"   Endpoints in code: {len(result.endpoints_in_code)}")
            print(f"   Endpoints in docs: {len(result.endpoints_in_docs)}")
            
            if result.missing_in_docs:
                print(f"   ❌ Missing in docs: {len(result.missing_in_docs)}")
                for ep in result.missing_in_docs:
                    print(f"      - {ep.method} {ep.path} ({ep.function_name})")
            
            if result.extra_in_docs:
                print(f"   ⚠️  Extra in docs (not in code): {len(result.extra_in_docs)}")
                for sig in result.extra_in_docs:
                    print(f"      - {sig}")
            
            if not result.missing_in_docs and not result.extra_in_docs:
                print(f"   ✅ Docs are in sync!")
            
            print()
        
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total modules audited: {len(self.results)}")
        print(f"Total endpoints: {total_endpoints}")
        print(f"Missing in docs: {total_missing}")
        print(f"Extra in docs: {total_extra}")
        
        if total_missing == 0 and total_extra == 0:
            print("\n✅ All documentation is in sync with code!")
        else:
            print(f"\n⚠️  Documentation needs updates")
        
        print()


def main():
    parser = argparse.ArgumentParser(description="Audit API documentation")
    parser.add_argument("--fix", action="store_true", help="Auto-fix documentation")
    args = parser.parse_args()
    
    # Find backend directory
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    
    # Run audit
    auditor = DocumentationAuditor(backend_dir)
    auditor.audit_all()
    auditor.print_report()
    
    if args.fix:
        print("⚠️  Auto-fix not implemented yet. Please update docs manually.")


if __name__ == "__main__":
    main()
