"""
Neo Alexandria 2.0 - Table Extractor Utility

Multi-strategy table extraction from PDFs and HTML with structure preservation.
"""

import logging
from typing import List, Dict

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class TableExtractor:
    """Multi-strategy table extraction from PDFs and HTML."""

    def extract_from_pdf(self, file_path: str, method: str = "auto") -> List[Dict]:
        """
        Extract tables from PDF using best available method.
        
        Args:
            file_path: Path to PDF file
            method: "camelot", "tabula", or "auto" (try both, pick best)
        
        Returns: List of table dicts with headers, rows, caption, position
        """
        tables = []
        
        if method in ["auto", "camelot"]:
            tables_camelot = self._extract_with_camelot(file_path)
            if tables_camelot:
                tables.extend(tables_camelot)
        
        if method in ["auto", "tabula"] and not tables:
            tables_tabula = self._extract_with_tabula(file_path)
            if tables_tabula:
                tables.extend(tables_tabula)
        
        return tables

    def _extract_with_camelot(self, file_path: str) -> List[Dict]:
        """Extract tables using camelot-py."""
        try:
            import camelot
            
            tables = []
            # Try lattice mode first (for bordered tables)
            try:
                camelot_tables = camelot.read_pdf(file_path, flavor='lattice')
                for i, table in enumerate(camelot_tables):
                    df = table.df
                    tables.append({
                        'position': i,
                        'headers': df.iloc[0].tolist() if len(df) > 0 else [],
                        'rows': df.iloc[1:].values.tolist() if len(df) > 1 else [],
                        'format': 'lattice',
                        'confidence': table.accuracy / 100.0 if hasattr(table, 'accuracy') else 0.8
                    })
            except Exception:
                # Try stream mode (for borderless tables)
                camelot_tables = camelot.read_pdf(file_path, flavor='stream')
                for i, table in enumerate(camelot_tables):
                    df = table.df
                    tables.append({
                        'position': i,
                        'headers': df.iloc[0].tolist() if len(df) > 0 else [],
                        'rows': df.iloc[1:].values.tolist() if len(df) > 1 else [],
                        'format': 'stream',
                        'confidence': 0.7
                    })
            
            return tables
        except ImportError:
            logger.warning("camelot-py not available")
            return []
        except Exception as e:
            logger.error(f"Camelot extraction failed: {e}")
            return []

    def _extract_with_tabula(self, file_path: str) -> List[Dict]:
        """Extract tables using tabula-py."""
        try:
            import tabula
            
            tables = []
            dfs = tabula.read_pdf(file_path, pages='all', multiple_tables=True)
            
            for i, df in enumerate(dfs):
                if df.empty:
                    continue
                
                tables.append({
                    'position': i,
                    'headers': df.columns.tolist(),
                    'rows': df.values.tolist(),
                    'format': 'tabula',
                    'confidence': 0.75
                })
            
            return tables
        except ImportError:
            logger.warning("tabula-py not available")
            return []
        except Exception as e:
            logger.error(f"Tabula extraction failed: {e}")
            return []

    def extract_from_html(self, html: str) -> List[Dict]:
        """
        Extract tables from HTML.
        
        Algorithm:
        1. Parse HTML with BeautifulSoup
        2. Find all <table> elements
        3. Extract headers and rows
        
        Returns: List of table dicts
        """
        tables = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            html_tables = soup.find_all('table')
            
            for i, table in enumerate(html_tables):
                # Extract caption
                caption = None
                caption_tag = table.find('caption')
                if caption_tag:
                    caption = caption_tag.get_text(strip=True)
                
                # Extract headers
                headers = []
                thead = table.find('thead')
                if thead:
                    header_row = thead.find('tr')
                    if header_row:
                        headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                
                # Extract rows
                rows = []
                tbody = table.find('tbody') or table
                for row in tbody.find_all('tr'):
                    cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                    if cells and cells != headers:  # Skip header row if it appears in tbody
                        rows.append(cells)
                
                if rows:  # Only add if we have data
                    tables.append({
                        'position': i,
                        'caption': caption,
                        'headers': headers,
                        'rows': rows,
                        'format': 'html',
                        'confidence': 0.9
                    })
            
            return tables
        except Exception as e:
            logger.error(f"HTML table extraction failed: {e}")
            return []

    def validate_table_structure(self, table: Dict) -> float:
        """
        Compute confidence score for extracted table.
        
        Checks:
        - All rows have same column count
        - Headers are non-empty
        - At least 2 rows of data
        - No all-empty columns
        
        Returns: Confidence score 0.0-1.0
        """
        score = 1.0
        
        rows = table.get('rows', [])
        headers = table.get('headers', [])
        
        # Check minimum data
        if len(rows) < 2:
            score *= 0.7
        
        # Check consistent column count
        if rows:
            col_counts = [len(row) for row in rows]
            if len(set(col_counts)) > 1:
                score *= 0.8
            
            # Check against headers
            if headers and col_counts:
                if len(headers) != col_counts[0]:
                    score *= 0.9
        
        # Check for empty headers
        if headers:
            empty_headers = sum(1 for h in headers if not str(h).strip())
            if empty_headers > 0:
                score *= (1 - empty_headers / len(headers) * 0.3)
        
        # Check for all-empty columns
        if rows and rows[0]:
            num_cols = len(rows[0])
            for col_idx in range(num_cols):
                col_values = [row[col_idx] if col_idx < len(row) else '' for row in rows]
                if all(not str(v).strip() for v in col_values):
                    score *= 0.9
        
        return max(score, 0.0)
