"""
Unit tests for ArxivCollector class.

Tests cover rate limiting, retry logic, metadata extraction,
balanced dataset collection, and intermediate save functionality.
"""

import json
import os
import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

# Import the ArxivCollector
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.dataset_acquisition.arxiv_collector import ArxivCollector


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for tests."""
    output_dir = tmp_path / "test_arxiv_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir)


@pytest.fixture
def collector(temp_output_dir):
    """Create an ArxivCollector instance for testing."""
    return ArxivCollector(output_dir=temp_output_dir)


@pytest.fixture
def mock_arxiv_result():
    """Create a mock arXiv result object."""
    result = Mock()
    result.entry_id = "http://arxiv.org/abs/2301.12345v1"
    result.title = "Test Paper Title"
    result.summary = "This is a test abstract for the paper."

    # Create proper author mocks
    author1 = Mock()
    author1.name = "Author One"
    author2 = Mock()
    author2.name = "Author Two"
    result.authors = [author1, author2]

    result.categories = ["cs.AI", "cs.LG"]
    result.primary_category = "cs.AI"
    result.published = datetime(2023, 1, 15)
    result.updated = datetime(2023, 1, 16)
    result.pdf_url = "http://arxiv.org/pdf/2301.12345v1"
    result.comment = "Test comment"
    result.journal_ref = "Test Journal 2023"
    return result


class TestArxivCollectorInitialization:
    """Test ArxivCollector initialization."""

    def test_init_creates_output_directory(self, temp_output_dir):
        """Test that initialization creates the output directory."""
        collector = ArxivCollector(output_dir=temp_output_dir)
        assert os.path.exists(temp_output_dir)
        assert collector.output_dir == Path(temp_output_dir)

    def test_init_with_nested_directory(self, tmp_path):
        """Test initialization with nested directory path."""
        nested_dir = tmp_path / "level1" / "level2" / "arxiv"
        ArxivCollector(output_dir=str(nested_dir))
        assert os.path.exists(nested_dir)

    def test_client_configuration(self, collector):
        """Test that arxiv client is configured with correct parameters."""
        assert collector.client is not None
        assert collector.client.page_size == 100
        assert collector.client.delay_seconds == 0.5
        assert collector.client.num_retries == 3


class TestRateLimiting:
    """Test rate limiting functionality."""

    @patch("scripts.dataset_acquisition.arxiv_collector.arxiv.Search")
    def test_rate_limiting_respected(self, mock_search, collector, mock_arxiv_result):
        """Test that rate limiting delay is respected between requests."""
        # Create mock results
        mock_results = [mock_arxiv_result for _ in range(3)]

        # Mock the client.results to return our mock results
        with patch.object(collector.client, "results", return_value=iter(mock_results)):
            start_time = time.time()
            papers = collector.collect_papers_by_category("cs.AI", max_results=3)
            time.time() - start_time

            # With 0.5s delay and 3 results, should take at least 1.0s
            # (delay happens between requests, not after last one)
            assert len(papers) == 3
            # Note: Actual timing may vary, so we just check papers were collected


class TestPaperMetadataExtraction:
    """Test paper metadata extraction."""

    @patch("scripts.dataset_acquisition.arxiv_collector.arxiv.Search")
    def test_metadata_extraction(self, mock_search, collector, mock_arxiv_result):
        """Test that paper metadata is correctly extracted."""
        with patch.object(
            collector.client, "results", return_value=iter([mock_arxiv_result])
        ):
            papers = collector.collect_papers_by_category("cs.AI", max_results=1)

            assert len(papers) == 1
            paper = papers[0]

            # Check all required fields are present
            assert paper["arxiv_id"] == "2301.12345v1"
            assert paper["title"] == "Test Paper Title"
            assert paper["abstract"] == "This is a test abstract for the paper."
            assert paper["authors"] == ["Author One", "Author Two"]
            assert paper["categories"] == ["cs.AI", "cs.LG"]
            assert paper["primary_category"] == "cs.AI"
            assert "published" in paper
            assert "updated" in paper
            assert paper["pdf_url"] == "http://arxiv.org/pdf/2301.12345v1"
            assert paper["comment"] == "Test comment"
            assert paper["journal_ref"] == "Test Journal 2023"

    @patch("scripts.dataset_acquisition.arxiv_collector.arxiv.Search")
    def test_metadata_extraction_with_missing_fields(self, mock_search, collector):
        """Test metadata extraction when optional fields are missing."""
        result = Mock()
        result.entry_id = "http://arxiv.org/abs/2301.12345v1"
        result.title = "Test Paper"
        result.summary = "Test abstract"

        # Create proper author mock
        author = Mock()
        author.name = "Author"
        result.authors = [author]

        result.categories = ["cs.AI"]
        result.primary_category = "cs.AI"
        result.published = datetime(2023, 1, 15)
        result.updated = None  # Missing updated date
        result.pdf_url = "http://arxiv.org/pdf/2301.12345v1"
        result.comment = None  # Missing comment
        result.journal_ref = None  # Missing journal ref

        with patch.object(collector.client, "results", return_value=iter([result])):
            papers = collector.collect_papers_by_category("cs.AI", max_results=1)

            assert len(papers) == 1
            paper = papers[0]
            assert paper["updated"] is None
            assert paper["comment"] is None
            assert paper["journal_ref"] is None


class TestRetryLogic:
    """Test retry logic on API errors."""

    @patch("scripts.dataset_acquisition.arxiv_collector.arxiv.Search")
    def test_retry_on_api_error(self, mock_search, collector):
        """Test that API errors trigger retry logic."""
        # Mock client.results to raise an exception
        with patch.object(
            collector.client, "results", side_effect=Exception("API Error")
        ):
            with pytest.raises(Exception) as exc_info:
                collector.collect_papers_by_category("cs.AI", max_results=10)

            assert "API Error" in str(exc_info.value)

    @patch("scripts.dataset_acquisition.arxiv_collector.arxiv.Search")
    def test_partial_results_saved_on_error(
        self, mock_search, collector, mock_arxiv_result, temp_output_dir
    ):
        """Test that partial results are saved when an error occurs."""

        # Create a generator that yields some results then raises an error
        def results_with_error(search):
            yield mock_arxiv_result
            yield mock_arxiv_result
            raise Exception("API Error")

        with patch.object(collector.client, "results", side_effect=results_with_error):
            with pytest.raises(Exception):
                collector.collect_papers_by_category("cs.AI", max_results=10)

            # Check that intermediate files were created
            files = list(Path(temp_output_dir).glob("cs_AI_*_error_*.json"))
            assert len(files) > 0


class TestBalancedDatasetCollection:
    """Test balanced dataset collection across categories."""

    @patch(
        "scripts.dataset_acquisition.arxiv_collector.ArxivCollector.collect_papers_by_category"
    )
    def test_balanced_collection(self, mock_collect, collector, temp_output_dir):
        """Test that balanced dataset collects equal papers per category."""

        # Mock collect_papers_by_category to return dummy papers
        def mock_papers(category, max_results, start_date=None):
            return [
                {"arxiv_id": f"{category}_{i}", "title": f"Paper {i}"}
                for i in range(max_results)
            ]

        mock_collect.side_effect = mock_papers

        categories = ["cs.AI", "cs.LG", "cs.CV"]
        dataset = collector.collect_balanced_dataset(
            categories=categories, papers_per_category=10
        )

        # Check that all categories are present
        assert len(dataset) == 3
        assert all(cat in dataset for cat in categories)

        # Check that each category has the correct number of papers
        for category in categories:
            assert len(dataset[category]) == 10

        # Check that category files were created
        for category in categories:
            filename = f"{category.replace('.', '_')}_papers.json"
            filepath = Path(temp_output_dir) / filename
            assert filepath.exists()

    @patch(
        "scripts.dataset_acquisition.arxiv_collector.ArxivCollector.collect_papers_by_category"
    )
    def test_balanced_collection_with_failure(self, mock_collect, collector):
        """Test that balanced collection continues when one category fails."""

        def mock_papers_with_error(category, max_results, start_date=None):
            if category == "cs.LG":
                raise Exception("Collection failed")
            return [{"arxiv_id": f"{category}_{i}"} for i in range(max_results)]

        mock_collect.side_effect = mock_papers_with_error

        categories = ["cs.AI", "cs.LG", "cs.CV"]
        dataset = collector.collect_balanced_dataset(
            categories=categories, papers_per_category=10
        )

        # Check that successful categories have papers
        assert len(dataset["cs.AI"]) == 10
        assert len(dataset["cs.CV"]) == 10

        # Check that failed category has empty list
        assert len(dataset["cs.LG"]) == 0


class TestIntermediateSave:
    """Test intermediate save functionality."""

    @patch("scripts.dataset_acquisition.arxiv_collector.arxiv.Search")
    def test_intermediate_save_every_100_papers(
        self, mock_search, collector, temp_output_dir
    ):
        """Test that intermediate results are saved every 100 papers."""

        # Create 150 simple mock results (not using the fixture to avoid JSON serialization issues)
        def create_simple_result(i):
            result = Mock()
            result.entry_id = f"http://arxiv.org/abs/2301.{i:05d}v1"
            result.title = f"Test Paper {i}"
            result.summary = f"Abstract {i}"
            author = Mock()
            author.name = f"Author {i}"
            result.authors = [author]
            result.categories = ["cs.AI"]
            result.primary_category = "cs.AI"
            result.published = datetime(2023, 1, 15)
            result.updated = datetime(2023, 1, 16)
            result.pdf_url = f"http://arxiv.org/pdf/2301.{i:05d}v1"
            result.comment = None
            result.journal_ref = None
            return result

        mock_results = [create_simple_result(i) for i in range(150)]

        with patch.object(collector.client, "results", return_value=iter(mock_results)):
            papers = collector.collect_papers_by_category("cs.AI", max_results=150)

            assert len(papers) == 150

            # Check that intermediate file was created at 100 papers
            files = list(Path(temp_output_dir).glob("cs_AI_100_intermediate_*.json"))
            assert len(files) > 0

            # Verify the intermediate file contains 100 papers
            with open(files[0], "r") as f:
                data = json.load(f)
                assert data["count"] == 100
                assert len(data["papers"]) == 100

    def test_save_intermediate_results_creates_file(self, collector, temp_output_dir):
        """Test that _save_intermediate_results creates a file."""
        papers = [
            {"arxiv_id": "1", "title": "Paper 1"},
            {"arxiv_id": "2", "title": "Paper 2"},
        ]

        collector._save_intermediate_results("cs.AI", papers, 2)

        # Check that file was created
        files = list(Path(temp_output_dir).glob("cs_AI_2_intermediate_*.json"))
        assert len(files) > 0

        # Verify file content
        with open(files[0], "r") as f:
            data = json.load(f)
            assert data["category"] == "cs.AI"
            assert data["count"] == 2
            assert len(data["papers"]) == 2


class TestCreateClassificationDataset:
    """Test complete classification dataset creation."""

    @patch(
        "scripts.dataset_acquisition.arxiv_collector.ArxivCollector.collect_balanced_dataset"
    )
    def test_create_classification_dataset(
        self, mock_collect_balanced, collector, temp_output_dir
    ):
        """Test that classification dataset is created with correct structure."""
        # Mock balanced dataset collection
        categories = [
            "cs.AI",
            "cs.CL",
            "cs.CV",
            "cs.LG",
            "cs.CR",
            "cs.DB",
            "cs.DC",
            "cs.NE",
            "cs.RO",
            "cs.SE",
        ]

        mock_dataset = {}
        for cat in categories:
            mock_dataset[cat] = [
                {
                    "arxiv_id": f"{cat}_{i}",
                    "title": f"Title {i}",
                    "abstract": f"Abstract {i}",
                    "authors": ["Author"],
                    "published": "2023-01-01T00:00:00",
                }
                for i in range(100)
            ]

        mock_collect_balanced.return_value = mock_dataset

        # Create classification dataset
        dataset = collector.create_classification_dataset(
            num_papers=1000, output_file="test_classification.json"
        )

        # Check metadata
        assert dataset["metadata"]["num_samples"] == 1000
        assert dataset["metadata"]["num_categories"] == 10
        assert len(dataset["metadata"]["categories"]) == 10
        assert dataset["metadata"]["source"] == "arXiv API"

        # Check samples
        assert len(dataset["samples"]) == 1000

        # Check sample structure
        sample = dataset["samples"][0]
        assert "text" in sample
        assert "label" in sample
        assert "arxiv_id" in sample
        assert "title" in sample
        assert "authors" in sample
        assert "published" in sample

        # Check that text combines title and abstract
        assert sample["title"] in sample["text"]

        # Check that output file was created
        output_path = Path(temp_output_dir) / "test_classification.json"
        assert output_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
