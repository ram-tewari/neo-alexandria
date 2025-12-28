"""
Neo Alexandria 2.0 - Scholarly Module Models

This module does not define separate database models.
Scholarly metadata is stored directly on the Resource model.

The following fields on the Resource model are used:
- authors: JSON array of author objects
- affiliations: JSON array of affiliations
- doi, pmid, arxiv_id, isbn: Academic identifiers
- journal, conference, volume, issue, pages: Publication details
- publication_year: Year of publication
- funding_sources: JSON array of funding sources
- acknowledgments: Acknowledgments text
- equation_count, table_count, figure_count: Content counts
- reference_count: Number of references
- equations: JSON array of equation objects
- tables: JSON array of table objects
- metadata_completeness_score: Completeness score (0-1)
- extraction_confidence: Confidence score (0-1)
- requires_manual_review: Boolean flag
- is_ocr_processed: Boolean flag
- ocr_confidence: OCR confidence score
- ocr_corrections_applied: Number of OCR corrections
"""

# No models defined - uses Resource model from shared.base_model
