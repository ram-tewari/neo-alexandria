"""
Search Module Tests - Full-Text Search

Tests for keyword matching, boolean operators, and phrase search using Golden Data.
All test expectations are defined in tests/golden_data/fulltext_search.json.

NO inline expected values - all assertions use Golden Data.

**Validates: Requirements 8.2, 8.3**
"""

import sys
from pathlib import Path
from typing import List, Tuple
import re

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tests.protocol import assert_ranking_against_golden, load_golden_data


# ============================================================================
# Full-Text Search Implementation (Minimal for Testing)
# ============================================================================


class FullTextSearchService:
    """
    Full-text search service with keyword matching and boolean operators.

    Supports:
    - Exact keyword matching
    - Boolean operators (AND, OR, NOT)
    - Phrase search with quotes
    - Wildcard search with asterisk
    """

    @staticmethod
    def parse_query(query: str) -> dict:
        """
        Parse search query into components.

        Args:
            query: Search query string

        Returns:
            Dict with query components
        """
        # Check for phrase search (quoted text)
        phrase_match = re.search(r'"([^"]+)"', query)
        if phrase_match:
            return {"type": "phrase", "phrase": phrase_match.group(1)}

        # Check for boolean operators
        if " AND " in query:
            terms = query.split(" AND ")
            return {"type": "and", "terms": [t.strip() for t in terms]}

        if " OR " in query:
            terms = query.split(" OR ")
            return {"type": "or", "terms": [t.strip() for t in terms]}

        if " NOT " in query:
            parts = query.split(" NOT ")
            return {
                "type": "not",
                "include": parts[0].strip(),
                "exclude": parts[1].strip(),
            }

        # Check for wildcard
        if "*" in query:
            return {"type": "wildcard", "pattern": query.replace("*", ".*")}

        # Simple keyword search
        return {"type": "keyword", "terms": query.lower().split()}

    @staticmethod
    def matches_query(resource: dict, parsed_query: dict) -> bool:
        """
        Check if resource matches the parsed query.

        Args:
            resource: Resource dict with 'title' and 'content'
            parsed_query: Parsed query dict

        Returns:
            True if resource matches query
        """
        text = f"{resource.get('title', '')} {resource.get('content', '')}".lower()

        query_type = parsed_query["type"]

        if query_type == "phrase":
            phrase = parsed_query["phrase"].lower()
            return phrase in text

        elif query_type == "and":
            terms = [t.lower() for t in parsed_query["terms"]]
            # Use word boundary matching to avoid substring matches
            return all(
                re.search(r"\b" + re.escape(term) + r"\b", text) for term in terms
            )

        elif query_type == "or":
            terms = [t.lower() for t in parsed_query["terms"]]
            # Use word boundary matching to avoid substring matches
            return any(
                re.search(r"\b" + re.escape(term) + r"\b", text) for term in terms
            )

        elif query_type == "not":
            include = parsed_query["include"].lower()
            exclude = parsed_query["exclude"].lower()
            return include in text and exclude not in text

        elif query_type == "wildcard":
            pattern = parsed_query["pattern"]
            return bool(re.search(pattern, text, re.IGNORECASE))

        elif query_type == "keyword":
            terms = parsed_query["terms"]
            return any(term in text for term in terms)

        return False

    def search(self, query: str, resources: List[dict]) -> Tuple[List[str], int]:
        """
        Search resources using full-text matching.

        Args:
            query: Search query string
            resources: List of resource dicts

        Returns:
            Tuple of (ranked_ids, match_count)
        """
        if not query or not resources:
            return [], 0

        # Parse query
        parsed_query = self.parse_query(query)

        # Find matching resources
        matches = []
        for resource in resources:
            if self.matches_query(resource, parsed_query):
                matches.append(resource["id"])

        return matches, len(matches)


# ============================================================================
# Test Cases
# ============================================================================


def test_keyword_exact_match():
    """
    Test exact keyword matching in full-text search.

    Uses Golden Data case: keyword_exact_match

    Verifies:
    - Keywords found in title and content
    - Only matching resources returned

    **Validates: Requirements 8.2, 8.3**
    """
    # Load Golden Data
    golden_data = load_golden_data("fulltext_search")
    test_case = golden_data["keyword_exact_match"]

    # Get inputs from Golden Data
    query = test_case["query"]
    resources = test_case["resources"]

    # Execute full-text search
    service = FullTextSearchService()
    ranked_ids, match_count = service.search(query, resources)

    # Assert ranking against Golden Data
    assert_ranking_against_golden(
        "fulltext_search",
        "keyword_exact_match",
        ranked_ids,
        check_order=False,  # Order doesn't matter for keyword search
    )

    # Verify match count
    expected_count = test_case["match_count"]
    assert match_count == expected_count, (
        f"Match count mismatch: expected {expected_count}, got {match_count}"
    )


def test_boolean_and_operator():
    """
    Test boolean AND operator in search query.

    Uses Golden Data case: boolean_and_operator

    Verifies:
    - Both terms must be present
    - Resources with only one term excluded

    **Validates: Requirements 8.2, 8.3**
    """
    # Load Golden Data
    golden_data = load_golden_data("fulltext_search")
    test_case = golden_data["boolean_and_operator"]

    # Get inputs from Golden Data
    query = test_case["query"]
    resources = test_case["resources"]

    # Execute full-text search
    service = FullTextSearchService()
    ranked_ids, match_count = service.search(query, resources)

    # Assert ranking against Golden Data
    assert_ranking_against_golden(
        "fulltext_search", "boolean_and_operator", ranked_ids, check_order=False
    )

    # Verify match count
    expected_count = test_case["match_count"]
    assert match_count == expected_count, (
        f"Match count mismatch: expected {expected_count}, got {match_count}"
    )


def test_boolean_or_operator():
    """
    Test boolean OR operator in search query.

    Uses Golden Data case: boolean_or_operator

    Verifies:
    - Either term can be present
    - Resources with at least one term included

    **Validates: Requirements 8.2, 8.3**
    """
    # Load Golden Data
    golden_data = load_golden_data("fulltext_search")
    test_case = golden_data["boolean_or_operator"]

    # Get inputs from Golden Data
    query = test_case["query"]
    resources = test_case["resources"]

    # Execute full-text search
    service = FullTextSearchService()
    ranked_ids, match_count = service.search(query, resources)

    # Assert ranking against Golden Data
    assert_ranking_against_golden(
        "fulltext_search", "boolean_or_operator", ranked_ids, check_order=False
    )

    # Verify match count
    expected_count = test_case["match_count"]
    assert match_count == expected_count, (
        f"Match count mismatch: expected {expected_count}, got {match_count}"
    )


def test_boolean_not_operator():
    """
    Test boolean NOT operator to exclude terms.

    Uses Golden Data case: boolean_not_operator

    Verifies:
    - Include term must be present
    - Exclude term must not be present

    **Validates: Requirements 8.2, 8.3**
    """
    # Load Golden Data
    golden_data = load_golden_data("fulltext_search")
    test_case = golden_data["boolean_not_operator"]

    # Get inputs from Golden Data
    query = test_case["query"]
    resources = test_case["resources"]

    # Execute full-text search
    service = FullTextSearchService()
    ranked_ids, match_count = service.search(query, resources)

    # Assert ranking against Golden Data
    assert_ranking_against_golden(
        "fulltext_search", "boolean_not_operator", ranked_ids, check_order=False
    )

    # Verify match count
    expected_count = test_case["match_count"]
    assert match_count == expected_count, (
        f"Match count mismatch: expected {expected_count}, got {match_count}"
    )


def test_phrase_search_exact():
    """
    Test exact phrase search with quotes.

    Uses Golden Data case: phrase_search_exact

    Verifies:
    - Exact phrase must appear in order
    - Individual words not sufficient

    **Validates: Requirements 8.2, 8.3**
    """
    # Load Golden Data
    golden_data = load_golden_data("fulltext_search")
    test_case = golden_data["phrase_search_exact"]

    # Get inputs from Golden Data
    query = test_case["query"]
    resources = test_case["resources"]

    # Execute full-text search
    service = FullTextSearchService()
    ranked_ids, match_count = service.search(query, resources)

    # Assert ranking against Golden Data
    assert_ranking_against_golden(
        "fulltext_search", "phrase_search_exact", ranked_ids, check_order=False
    )

    # Verify match count
    expected_count = test_case["match_count"]
    assert match_count == expected_count, (
        f"Match count mismatch: expected {expected_count}, got {match_count}"
    )


def test_wildcard_search():
    """
    Test wildcard search with asterisk.

    Uses Golden Data case: wildcard_search

    Verifies:
    - Wildcard matches multiple variations
    - Prefix matching works correctly

    **Validates: Requirements 8.2, 8.3**
    """
    # Load Golden Data
    golden_data = load_golden_data("fulltext_search")
    test_case = golden_data["wildcard_search"]

    # Get inputs from Golden Data
    query = test_case["query"]
    resources = test_case["resources"]

    # Execute full-text search
    service = FullTextSearchService()
    ranked_ids, match_count = service.search(query, resources)

    # Assert ranking against Golden Data
    assert_ranking_against_golden(
        "fulltext_search", "wildcard_search", ranked_ids, check_order=False
    )

    # Verify match count
    expected_count = test_case["match_count"]
    assert match_count == expected_count, (
        f"Match count mismatch: expected {expected_count}, got {match_count}"
    )


def test_empty_query():
    """
    Test empty search query returns no results.

    Uses Golden Data case: empty_query

    Verifies:
    - Empty query handled gracefully
    - No results returned

    **Validates: Requirements 8.2, 8.3**
    """
    # Load Golden Data
    golden_data = load_golden_data("fulltext_search")
    test_case = golden_data["empty_query"]

    # Get inputs from Golden Data
    query = test_case["query"]
    resources = test_case["resources"]

    # Execute full-text search
    service = FullTextSearchService()
    ranked_ids, match_count = service.search(query, resources)

    # Assert ranking against Golden Data
    assert_ranking_against_golden(
        "fulltext_search", "empty_query", ranked_ids, check_order=False
    )

    # Verify match count
    expected_count = test_case["match_count"]
    assert match_count == expected_count, (
        f"Match count mismatch: expected {expected_count}, got {match_count}"
    )


def test_no_matches():
    """
    Test query with no matching documents.

    Uses Golden Data case: no_matches

    Verifies:
    - No matches returns empty results
    - No errors with non-matching query

    **Validates: Requirements 8.2, 8.3**
    """
    # Load Golden Data
    golden_data = load_golden_data("fulltext_search")
    test_case = golden_data["no_matches"]

    # Get inputs from Golden Data
    query = test_case["query"]
    resources = test_case["resources"]

    # Execute full-text search
    service = FullTextSearchService()
    ranked_ids, match_count = service.search(query, resources)

    # Assert ranking against Golden Data
    assert_ranking_against_golden(
        "fulltext_search", "no_matches", ranked_ids, check_order=False
    )

    # Verify match count
    expected_count = test_case["match_count"]
    assert match_count == expected_count, (
        f"Match count mismatch: expected {expected_count}, got {match_count}"
    )
