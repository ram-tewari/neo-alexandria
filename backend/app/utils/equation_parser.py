"""
Neo Alexandria 2.0 - Equation Parser Utility

Specialized utility for extracting and parsing LaTeX equations from documents.
"""

import re
from typing import List, Dict, Optional, Tuple


class EquationParser:
    """Utility for extracting and parsing LaTeX equations."""

    def extract_latex_from_text(self, text: str) -> List[Dict]:
        """
        Extract LaTeX equations from text containing inline/display math.

        Patterns to match:
        - Inline math: $...$
        - Display math: $$...$$
        - LaTeX environments: \\begin{equation}...\\end{equation}

        Returns: List of dicts with latex, type (inline/display), position
        """
        equations = []
        position = 0

        # Pattern 1: Display math $$...$$
        display_pattern = r"\$\$(.+?)\$\$"
        for match in re.finditer(display_pattern, text, re.DOTALL):
            equations.append(
                {
                    "latex": match.group(1).strip(),
                    "type": "display",
                    "position": position,
                    "start": match.start(),
                    "end": match.end(),
                }
            )
            position += 1

        # Pattern 2: Inline math $...$  (but not $$)
        inline_pattern = r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)"
        for match in re.finditer(inline_pattern, text):
            equations.append(
                {
                    "latex": match.group(1).strip(),
                    "type": "inline",
                    "position": position,
                    "start": match.start(),
                    "end": match.end(),
                }
            )
            position += 1

        # Pattern 3: LaTeX equation environment
        equation_pattern = r"\\begin\{equation\}(.+?)\\end\{equation\}"
        for match in re.finditer(equation_pattern, text, re.DOTALL):
            equations.append(
                {
                    "latex": match.group(1).strip(),
                    "type": "equation",
                    "position": position,
                    "start": match.start(),
                    "end": match.end(),
                }
            )
            position += 1

        # Pattern 4: LaTeX align environment
        align_pattern = r"\\begin\{align\*?\}(.+?)\\end\{align\*?\}"
        for match in re.finditer(align_pattern, text, re.DOTALL):
            equations.append(
                {
                    "latex": match.group(1).strip(),
                    "type": "align",
                    "position": position,
                    "start": match.start(),
                    "end": match.end(),
                }
            )
            position += 1

        # Sort by position in text
        equations.sort(key=lambda x: x["start"])

        # Reassign positions after sorting
        for i, eq in enumerate(equations):
            eq["position"] = i
            del eq["start"]
            del eq["end"]

        return equations

    def validate_latex(self, latex_str: str) -> Tuple[bool, Optional[str]]:
        """
        Validate LaTeX syntax.

        Algorithm:
        1. Check balanced delimiters: {}, [], ()
        2. Check valid LaTeX commands (starts with \\)
        3. Try parsing with sympy (if available)

        Returns: (is_valid, error_or_none)
        """
        # Check balanced braces
        if not self._check_balanced_delimiters(latex_str):
            return False, "Unbalanced delimiters"

        # Check for basic LaTeX command validity
        if "\\" in latex_str:
            # Commands should be followed by letters or special chars
            invalid_commands = re.findall(r"\\[^a-zA-Z{}\[\](),\s]", latex_str)
            if invalid_commands:
                return False, f"Invalid LaTeX commands: {invalid_commands}"

        # Try sympy parsing (optional, graceful fallback)
        try:
            from sympy.parsing.latex import parse_latex

            parse_latex(latex_str)
            return True, None
        except ImportError:
            # sympy not available, basic checks passed
            return True, None
        except Exception as e:
            return False, f"Parse error: {str(e)}"

    def _check_balanced_delimiters(self, text: str) -> bool:
        """Check if delimiters are balanced."""
        stack = []
        pairs = {"(": ")", "[": "]", "{": "}"}

        for char in text:
            if char in pairs:
                stack.append(char)
            elif char in pairs.values():
                if not stack:
                    return False
                if pairs[stack[-1]] != char:
                    return False
                stack.pop()

        return len(stack) == 0

    def normalize_latex(self, latex_str: str) -> str:
        """
        Normalize LaTeX formatting for consistency.

        Transformations:
        - Remove extra whitespace
        - Standardize command formatting
        """
        # Remove leading/trailing whitespace
        latex_str = latex_str.strip()

        # Normalize multiple spaces to single space
        latex_str = re.sub(r"\s+", " ", latex_str)

        # Standardize spacing around commands
        latex_str = re.sub(r"\\\s+", "\\", latex_str)

        # Remove spaces before braces in commands
        latex_str = re.sub(r"(\\\w+)\s+\{", r"\1{", latex_str)

        return latex_str

    def latex_to_mathml(self, latex_str: str) -> str:
        """
        Convert LaTeX to MathML for web rendering.

        Note: Requires latex2mathml library (optional dependency)
        Returns: MathML string or empty string if conversion fails
        """
        try:
            from latex2mathml.converter import convert

            return convert(latex_str)
        except ImportError:
            return ""
        except Exception:
            return ""
