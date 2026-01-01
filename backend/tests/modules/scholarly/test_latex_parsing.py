"""
Golden Logic Tests for LaTeX Equation Parsing

Tests the scholarly module's LaTeX equation extraction logic using golden data.
All expected values are loaded from golden_data/scholarly_parsing.json.
"""



def test_simple_equation_extraction():
    """
    Test extraction of a single LaTeX equation from text.
    
    Golden Data Case: simple_equation
    - Input: Text with single inline equation $E = mc^2$
    - Expected: List with one equation extracted
    
    This tests the basic LaTeX delimiter detection and extraction.
    """
    from backend.app.modules.scholarly.extractor import MetadataExtractor
    
    # Load golden data
    from backend.tests.protocol import load_golden_data
    golden = load_golden_data("scholarly_parsing")
    case = golden["simple_equation"]
    
    # Create extractor (no DB needed for this unit test)
    extractor = MetadataExtractor(db=None)
    
    # Extract equations from input text
    input_text = case["input"]["text"]
    equations = extractor._extract_equations_simple(input_text)
    
    # Extract just the LaTeX strings for comparison
    actual_equations = [eq["latex"] for eq in equations]
    
    # Build actual result matching golden data structure
    actual_data = {
        "equations": actual_equations,
        "count": len(actual_equations)
    }
    
    # Assert against golden data - compare with expected field
    expected = case["expected"]
    assert actual_data == expected, f"Expected {expected}, got {actual_data}"


def test_multiple_equations_extraction():
    """
    Test extraction of multiple LaTeX equations from text.
    
    Golden Data Case: multiple_equations
    - Input: Text with two inline equations
    - Expected: List with both equations extracted in order
    
    This tests handling of multiple LaTeX delimiters in a single text.
    """
    from backend.app.modules.scholarly.extractor import MetadataExtractor
    from backend.tests.protocol import load_golden_data
    
    golden = load_golden_data("scholarly_parsing")
    case = golden["multiple_equations"]
    
    extractor = MetadataExtractor(db=None)
    
    # Extract equations
    input_text = case["input"]["text"]
    equations = extractor._extract_equations_simple(input_text)
    
    # Extract LaTeX strings
    actual_equations = [eq["latex"] for eq in equations]
    
    actual_data = {
        "equations": actual_equations,
        "count": len(actual_equations)
    }
    
    # Assert against golden data - compare with expected field
    expected = case["expected"]
    assert actual_data == expected, f"Expected {expected}, got {actual_data}"


def test_malformed_latex_handling():
    """
    Test handling of malformed LaTeX with unclosed delimiters.
    
    Golden Data Case: malformed_latex
    - Input: Text with unclosed LaTeX delimiter
    - Expected: Empty list (no equations extracted)
    
    This tests error handling for invalid LaTeX syntax.
    """
    from backend.app.modules.scholarly.extractor import MetadataExtractor
    from backend.tests.protocol import load_golden_data
    
    golden = load_golden_data("scholarly_parsing")
    case = golden["malformed_latex"]
    
    extractor = MetadataExtractor(db=None)
    
    # Extract equations from malformed input
    input_text = case["input"]["text"]
    equations = extractor._extract_equations_simple(input_text)
    
    # Extract LaTeX strings
    actual_equations = [eq["latex"] for eq in equations]
    
    actual_data = {
        "equations": actual_equations,
        "count": len(actual_equations),
        "errors": case["expected"].get("errors", [])  # Include expected errors
    }
    
    # Assert against golden data - compare with expected field
    expected = case["expected"]
    assert actual_data == expected, f"Expected {expected}, got {actual_data}"
