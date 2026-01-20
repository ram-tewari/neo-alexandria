#!/usr/bin/env python3
"""
Verification script for Tree-Sitter installation and language grammars.

This script tests that:
1. Tree-Sitter is properly installed
2. All required language grammars are available (Python, JS, TS, Rust, Go, Java)
3. Tree-Sitter can successfully parse sample code in each language
"""

import sys
from typing import Dict, Tuple

try:
    from tree_sitter import Language, Parser
    import tree_sitter_python
    import tree_sitter_javascript
    import tree_sitter_typescript
    import tree_sitter_rust
    import tree_sitter_go
    import tree_sitter_java
except ImportError as e:
    print(f"❌ Failed to import Tree-Sitter dependencies: {e}")
    print(
        "Please install dependencies: pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript tree-sitter-rust tree-sitter-go tree-sitter-java"
    )
    sys.exit(1)


# Sample code snippets for each language
SAMPLE_CODE: Dict[str, Tuple[str, bytes]] = {
    "Python": (
        "tree_sitter_python",
        b"""
def hello_world(name: str) -> str:
    \"\"\"Greet someone by name.\"\"\"
    return f"Hello, {name}!"

class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b
""",
    ),
    "JavaScript": (
        "tree_sitter_javascript",
        b"""
function helloWorld(name) {
    return `Hello, ${name}!`;
}

class Calculator {
    add(a, b) {
        return a + b;
    }
}
""",
    ),
    "TypeScript": (
        "tree_sitter_typescript.typescript",
        b"""
function helloWorld(name: string): string {
    return `Hello, ${name}!`;
}

class Calculator {
    add(a: number, b: number): number {
        return a + b;
    }
}
""",
    ),
    "Rust": (
        "tree_sitter_rust",
        b"""
fn hello_world(name: &str) -> String {
    format!("Hello, {}!", name)
}

struct Calculator;

impl Calculator {
    fn add(&self, a: i32, b: i32) -> i32 {
        a + b
    }
}
""",
    ),
    "Go": (
        "tree_sitter_go",
        b"""
package main

func helloWorld(name string) string {
    return "Hello, " + name + "!"
}

type Calculator struct{}

func (c Calculator) Add(a, b int) int {
    return a + b
}
""",
    ),
    "Java": (
        "tree_sitter_java",
        b"""
public class HelloWorld {
    public static String helloWorld(String name) {
        return "Hello, " + name + "!";
    }
    
    public static class Calculator {
        public int add(int a, int b) {
            return a + b;
        }
    }
}
""",
    ),
}


def get_language(language_module: str) -> Language:
    """Get the Language object for a given module path."""
    if language_module == "tree_sitter_python":
        return Language(tree_sitter_python.language())
    elif language_module == "tree_sitter_javascript":
        return Language(tree_sitter_javascript.language())
    elif language_module == "tree_sitter_typescript.typescript":
        return Language(tree_sitter_typescript.language_typescript())
    elif language_module == "tree_sitter_rust":
        return Language(tree_sitter_rust.language())
    elif language_module == "tree_sitter_go":
        return Language(tree_sitter_go.language())
    elif language_module == "tree_sitter_java":
        return Language(tree_sitter_java.language())
    else:
        raise ValueError(f"Unknown language module: {language_module}")


def test_language_parsing(
    language_name: str, language_module: str, code: bytes
) -> bool:
    """Test parsing code in a specific language."""
    try:
        # Get the language
        language = get_language(language_module)

        # Create parser
        parser = Parser(language)

        # Parse the code
        tree = parser.parse(code)
        root_node = tree.root_node

        # Check for parse errors
        if root_node.has_error:
            print(f"  ❌ {language_name}: Parse errors detected")
            print(f"     Root node: {root_node.sexp()[:200]}...")
            return False

        # Verify we got a valid AST
        if root_node.child_count == 0:
            print(f"  ❌ {language_name}: Empty AST (no children)")
            return False

        # Count nodes to verify parsing depth
        node_count = count_nodes(root_node)

        print(f"  ✅ {language_name}: Successfully parsed ({node_count} nodes)")
        return True

    except Exception as e:
        print(f"  ❌ {language_name}: Exception during parsing: {e}")
        return False


def count_nodes(node) -> int:
    """Recursively count all nodes in the AST."""
    count = 1
    for child in node.children:
        count += count_nodes(child)
    return count


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Tree-Sitter Installation Verification")
    print("=" * 60)
    print()

    # Test 1: Check Tree-Sitter version
    print("1. Checking Tree-Sitter installation...")
    try:
        # Tree-sitter doesn't expose __version__, just verify it imports
        print("  ✅ Tree-Sitter imported successfully")
    except Exception as e:
        print(f"  ❌ Failed to import Tree-Sitter: {e}")
        sys.exit(1)

    print()

    # Test 2: Check all language grammars
    print("2. Checking language grammar availability...")
    all_available = True

    languages = [
        ("Python", tree_sitter_python),
        ("JavaScript", tree_sitter_javascript),
        ("TypeScript", tree_sitter_typescript),
        ("Rust", tree_sitter_rust),
        ("Go", tree_sitter_go),
        ("Java", tree_sitter_java),
    ]

    for lang_name, lang_module in languages:
        try:
            # Try to get the language
            if lang_name == "TypeScript":
                Language(lang_module.language_typescript())
            else:
                Language(lang_module.language())
            print(f"  ✅ {lang_name}: Grammar available")
        except Exception as e:
            print(f"  ❌ {lang_name}: Grammar not available - {e}")
            all_available = False

    if not all_available:
        print("\n❌ Some language grammars are missing!")
        sys.exit(1)

    print()

    # Test 3: Parse sample code in each language
    print("3. Testing code parsing for each language...")
    all_passed = True

    for language_name, (language_module, code) in SAMPLE_CODE.items():
        if not test_language_parsing(language_name, language_module, code):
            all_passed = False

    print()

    # Final summary
    print("=" * 60)
    if all_passed:
        print("✅ All verification tests passed!")
        print("Tree-Sitter is properly installed and all language grammars work.")
        print()
        print("Supported languages:")
        for lang_name in SAMPLE_CODE.keys():
            print(f"  • {lang_name}")
        sys.exit(0)
    else:
        print("❌ Some verification tests failed!")
        print(
            "Please check the errors above and ensure all dependencies are installed."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
