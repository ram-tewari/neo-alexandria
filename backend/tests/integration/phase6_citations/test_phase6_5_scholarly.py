"""
Neo Alexandria 2.0 - Phase 6.5 Scholarly Metadata Tests

Test suite for advanced metadata extraction functionality.
"""

import pytest
import json
from sqlalchemy.orm import Session

from backend.app.database import models as db_models
from backend.app.services.metadata_extractor import MetadataExtractor
from backend.app.utils.equation_parser import EquationParser
from backend.app.utils.table_extractor import TableExtractor


class TestMetadataExtraction:
    """Test metadata extraction from scholarly content."""

    def test_extract_doi_from_text(self, db_session: Session):
        """Test DOI extraction from text content."""
        extractor = MetadataExtractor(db_session)
        
        content = "This paper is published at DOI: 10.1234/example.2024.001"
        doi = extractor._extract_doi(content)
        
        assert doi == "10.1234/example.2024.001"

    def test_extract_arxiv_id(self, db_session: Session):
        """Test arXiv ID extraction."""
        extractor = MetadataExtractor(db_session)
        
        content = "Available at arXiv:2024.12345"
        arxiv_id = extractor._extract_arxiv_id(content)
        
        assert arxiv_id == "2024.12345"

    def test_extract_publication_year(self, db_session: Session):
        """Test publication year extraction."""
        extractor = MetadataExtractor(db_session)
        
        content = "Published in 2023 by Example Press"
        year = extractor._extract_publication_year(content)
        
        assert year == 2023

    def test_compute_completeness_score(self, db_session: Session):
        """Test metadata completeness scoring."""
        extractor = MetadataExtractor(db_session)
        
        # Complete metadata
        metadata = {
            'doi': '10.1234/test',
            'authors': json.dumps([{'name': 'John Doe'}]),
            'publication_year': 2023,
            'journal': 'Test Journal',
            'equations': json.dumps([])
        }
        
        score = extractor._compute_completeness(metadata)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should have decent completeness

    def test_compute_confidence_score(self, db_session: Session):
        """Test extraction confidence scoring."""
        extractor = MetadataExtractor(db_session)
        
        metadata = {
            'doi': '10.1234/test',
            'authors': json.dumps([]),
            'publication_year': 2023
        }
        
        confidence = extractor._compute_confidence(metadata)
        assert 0.0 <= confidence <= 1.0


class TestEquationExtraction:
    """Test equation extraction and parsing."""

    def test_extract_inline_math(self):
        """Test inline math extraction."""
        parser = EquationParser()
        
        text = "The formula $E = mc^2$ is famous."
        equations = parser.extract_latex_from_text(text)
        
        assert len(equations) == 1
        assert equations[0]['latex'] == 'E = mc^2'
        assert equations[0]['type'] == 'inline'

    def test_extract_display_math(self):
        """Test display math extraction."""
        parser = EquationParser()
        
        text = "The equation is: $$\\frac{d}{dx}(x^2) = 2x$$"
        equations = parser.extract_latex_from_text(text)
        
        assert len(equations) == 1
        assert '\\frac{d}{dx}(x^2) = 2x' in equations[0]['latex']
        assert equations[0]['type'] == 'display'

    def test_validate_latex_balanced(self):
        """Test LaTeX validation with balanced delimiters."""
        parser = EquationParser()
        
        valid, error = parser.validate_latex("\\frac{a}{b}")
        assert valid is True
        assert error is None

    def test_validate_latex_unbalanced(self):
        """Test LaTeX validation with unbalanced delimiters."""
        parser = EquationParser()
        
        valid, error = parser.validate_latex("\\frac{a}{b")
        assert valid is False
        assert "Unbalanced" in error

    def test_normalize_latex(self):
        """Test LaTeX normalization."""
        parser = EquationParser()
        
        latex = "\\frac  {a}  {b}"
        normalized = parser.normalize_latex(latex)
        
        assert normalized == "\\frac{a} {b}"


class TestTableExtraction:
    """Test table extraction from HTML."""

    def test_extract_simple_html_table(self):
        """Test extraction of simple HTML table."""
        extractor = TableExtractor()
        
        html = """
        <table>
            <thead>
                <tr><th>Name</th><th>Value</th></tr>
            </thead>
            <tbody>
                <tr><td>A</td><td>1</td></tr>
                <tr><td>B</td><td>2</td></tr>
            </tbody>
        </table>
        """
        
        tables = extractor.extract_from_html(html)
        
        assert len(tables) == 1
        assert tables[0]['headers'] == ['Name', 'Value']
        assert len(tables[0]['rows']) == 2
        assert tables[0]['rows'][0] == ['A', '1']

    def test_extract_table_with_caption(self):
        """Test extraction of table with caption."""
        extractor = TableExtractor()
        
        html = """
        <table>
            <caption>Table 1: Test Data</caption>
            <tr><td>A</td><td>1</td></tr>
        </table>
        """
        
        tables = extractor.extract_from_html(html)
        
        assert len(tables) == 1
        assert tables[0]['caption'] == 'Table 1: Test Data'

    def test_validate_table_structure(self):
        """Test table structure validation."""
        extractor = TableExtractor()
        
        # Valid table
        table = {
            'headers': ['A', 'B'],
            'rows': [['1', '2'], ['3', '4']]
        }
        
        confidence = extractor.validate_table_structure(table)
        assert confidence > 0.8

    def test_validate_inconsistent_table(self):
        """Test validation of inconsistent table."""
        extractor = TableExtractor()
        
        # Inconsistent column count
        table = {
            'headers': ['A', 'B'],
            'rows': [['1', '2'], ['3']]  # Missing column
        }
        
        confidence = extractor.validate_table_structure(table)
        assert confidence < 1.0


class TestScholarlyIntegration:
    """Integration tests for scholarly metadata."""

    def test_resource_model_has_scholarly_fields(self, db_session: Session):
        """Test that Resource model has all scholarly fields."""
        resource = db_models.Resource(
            title="Test Paper",
            doi="10.1234/test",
            authors=json.dumps([{"name": "John Doe"}]),
            publication_year=2023,
            equation_count=5,
            table_count=3,
            metadata_completeness_score=0.85
        )
        
        db_session.add(resource)
        db_session.commit()
        db_session.refresh(resource)
        
        assert resource.doi == "10.1234/test"
        assert resource.publication_year == 2023
        assert resource.equation_count == 5
        assert resource.metadata_completeness_score == 0.85

    def test_extract_scholarly_metadata_integration(self, db_session: Session):
        """Test full scholarly metadata extraction pipeline."""
        # Create a test resource
        resource = db_models.Resource(
            title="Test Paper",
            description="This paper discusses DOI: 10.1234/test published in 2023. The equation $E=mc^2$ is central.",
            format="text/html"
        )
        
        db_session.add(resource)
        db_session.commit()
        db_session.refresh(resource)
        
        # Extract metadata
        extractor = MetadataExtractor(db_session)
        metadata = extractor.extract_scholarly_metadata(str(resource.id))
        
        # Verify extraction
        assert 'doi' in metadata or 'publication_year' in metadata
        assert 'metadata_completeness_score' in metadata
        assert 'extraction_confidence' in metadata


# Fixtures

@pytest.fixture
def db_session():
    """Create a test database session."""
    from backend.app.database.base import SessionLocal, Base, engine
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
