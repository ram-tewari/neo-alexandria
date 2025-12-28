#!/usr/bin/env python
"""
Script to fix all backend.app. imports to relative imports.
"""

import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Fix backend.app imports in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Determine the depth (how many ../ needed)
    parts = Path(filepath).relative_to(Path('app')).parts
    depth = len(parts) - 1  # -1 because we don't count the file itself
    
    # Pattern to match: from backend.app.{module} import
    pattern = r'from backend\.app\.([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*) import'
    
    def replace_import(match):
        module_path = match.group(1)
        # Calculate relative path
        if depth == 0:
            # Same directory as app/
            return f'from .{module_path} import'
        else:
            # Need to go up
            dots = '.' * (depth + 1)
            return f'from {dots}{module_path} import'
    
    content = re.sub(pattern, replace_import, content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all Python files in app directory."""
    app_dir = Path('app')
    fixed_count = 0
    
    for py_file in app_dir.rglob('*.py'):
        if fix_imports_in_file(py_file):
            print(f"Fixed: {py_file}")
            fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
