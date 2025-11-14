"""Fix import statements in moved test files."""

import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix import statements in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix: from app. -> from backend.app.
    content = re.sub(r'\bfrom app\.', 'from backend.app.', content)
    
    # Fix: import app. -> import backend.app.
    content = re.sub(r'\bimport app\.', 'import backend.app.', content)
    
    # Remove sys.path manipulation that's no longer needed
    # Remove lines like: sys.path.insert(0, ...)
    content = re.sub(r'sys\.path\.insert\(0,.*?\)\n', '', content)
    
    # Remove lines like: backend_path = Path(__file__).parent
    content = re.sub(r'backend_path = Path\(__file__\)\.parent.*?\n', '', content)
    
    # Remove unnecessary path additions
    content = re.sub(r'# Add backend to path\n', '', content)
    content = re.sub(r'# Add backend directory to path\n', '', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix imports in all test files."""
    test_dir = Path('backend/tests')
    
    # Find all Python test files
    test_files = list(test_dir.rglob('test_*.py'))
    
    fixed_count = 0
    for test_file in test_files:
        if fix_imports_in_file(test_file):
            print(f"Fixed: {test_file}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()
