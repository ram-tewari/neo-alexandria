"""
Unit tests for DatasetPreprocessor class.
"""

import json
import pytest
import tempfile
from pathlib import Path
from backend.scripts.dataset_acquisition.dataset_preprocessor import DatasetPreprocessor


class TestDatasetPreprocessor:
    """Test suite for DatasetPreprocessor."""
    
    @pytest.fixture
    def preprocessor(self):
        """Create a DatasetPreprocessor instance."""
        return DatasetPreprocessor()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample dataset for testing."""
        return {
            "metadata": {
                "source": "test",
                "num_samples": 10
            },
            "samples": [
                {
                    "arxiv_id": "2301.00001",
                    "title": "Machine Learning Paper",
                    "text": "This is a test abstract about machine learning with http://example.com and $x^2$ math.",
                    "label": "cs.AI"
                },
                {
                    "arxiv_id": "2301.00002",
                    "title": "Deep Learning Study",
                    "text": "This paper discusses deep learning methods using \\textbf{neural networks} and various techniques.",
                    "label": "cs.LG"
                },
                {
                    "arxiv_id": "2301.00001",  # Duplicate ID
                    "title": "Machine Learning Paper",
                    "text": "This is a duplicate paper.",
                    "label": "cs.AI"
                },
                {
                    "arxiv_id": "2301.00003",
                    "title": "Machine Learning Paper",  # Duplicate title
                    "text": "Different content but same title.",
                    "label": "cs.AI"
                },
                {
                    "arxiv_id": "2301.00004",
                    "title": "Short Paper",
                    "text": "Too short.",  # Too short (< 50 words)
                    "label": "cs.CV"
                },
                {
                    "arxiv_id": "2301.00005",
                    "title": "Empty Text Paper",
                    "text": "",  # Empty text
                    "label": "cs.NE"
                },
                {
                    "arxiv_id": "2301.00006",
                    "title": "No Label Paper",
                    "text": "This paper has enough words to pass the minimum word count requirement for quality filtering.",
                    "label": ""  # Missing label
                },
                {
                    "arxiv_id": "2301.00007",
                    "title": "Non-English Paper",
                    "text": "这是一篇中文论文，包含足够的字符来通过最小字数要求，但应该被语言检测过滤掉。",
                    "label": "cs.CL"
                },
                {
                    "arxiv_id": "2301.00008",
                    "title": "Valid Computer Vision Paper",
                    "text": "This is a valid paper about computer vision with sufficient length and proper formatting for testing purposes.",
                    "label": "cs.CV"
                },
                {
                    "arxiv_id": "2301.00009",
                    "title": "Valid Robotics Paper",
                    "text": "This paper explores robotics applications and autonomous systems with detailed analysis and experimental results.",
                    "label": "cs.RO"
                }
            ]
        }
    
    def test_clean_text_removes_urls(self, preprocessor):
        """Test that clean_text removes URLs."""
        text = "Check out http://example.com and https://test.org for more info."
        cleaned = preprocessor.clean_text(text)
        assert "http://example.com" not in cleaned
        assert "https://test.org" not in cleaned
    
    def test_clean_text_removes_latex(self, preprocessor):
        """Test that clean_text removes LaTeX commands."""
        text = "This uses \\textbf{bold text} and \\cite{reference} commands."
        cleaned = preprocessor.clean_text(text)
        assert "\\textbf" not in cleaned
        assert "\\cite" not in cleaned
    
    def test_clean_text_removes_inline_math(self, preprocessor):
        """Test that clean_text removes inline math."""
        text = "The equation $x^2 + y^2 = z^2$ is famous."
        cleaned = preprocessor.clean_text(text)
        assert "$x^2 + y^2 = z^2$" not in cleaned
    
    def test_clean_text_normalizes_whitespace(self, preprocessor):
        """Test that clean_text normalizes whitespace."""
        text = "This  has   multiple    spaces."
        cleaned = preprocessor.clean_text(text)
        assert "  " not in cleaned
        assert cleaned == "This has multiple spaces."
    
    def test_clean_text_removes_multiple_punctuation(self, preprocessor):
        """Test that clean_text removes multiple punctuation."""
        text = "Wait... really??? Yes!!!"
        cleaned = preprocessor.clean_text(text)
        assert "..." not in cleaned
        assert "???" not in cleaned
        assert "!!!" not in cleaned
    
    def test_compute_text_hash(self, preprocessor):
        """Test that compute_text_hash generates consistent hashes."""
        text1 = "Machine Learning Paper"
        text2 = "Machine Learning Paper"
        text3 = "Different Paper"
        
        hash1 = preprocessor.compute_text_hash(text1)
        hash2 = preprocessor.compute_text_hash(text2)
        hash3 = preprocessor.compute_text_hash(text3)
        
        assert hash1 == hash2  # Same text should have same hash
        assert hash1 != hash3  # Different text should have different hash
        assert len(hash1) == 32  # MD5 hash is 32 characters
    
    def test_deduplicate_samples_removes_duplicate_ids(self, preprocessor):
        """Test that deduplicate_samples removes duplicates by arXiv ID."""
        samples = [
            {"arxiv_id": "2301.00001", "title": "Paper 1", "text": "Text 1", "label": "cs.AI"},
            {"arxiv_id": "2301.00001", "title": "Paper 1 Duplicate", "text": "Text 2", "label": "cs.AI"},
            {"arxiv_id": "2301.00002", "title": "Paper 2", "text": "Text 3", "label": "cs.LG"}
        ]
        
        unique = preprocessor.deduplicate_samples(samples)
        
        assert len(unique) == 2
        assert unique[0]["arxiv_id"] == "2301.00001"
        assert unique[1]["arxiv_id"] == "2301.00002"
    
    def test_deduplicate_samples_removes_duplicate_titles(self, preprocessor):
        """Test that deduplicate_samples removes duplicates by title hash."""
        samples = [
            {"arxiv_id": "2301.00001", "title": "Machine Learning", "text": "Text 1", "label": "cs.AI"},
            {"arxiv_id": "2301.00002", "title": "Machine Learning", "text": "Text 2", "label": "cs.AI"},
            {"arxiv_id": "2301.00003", "title": "Deep Learning", "text": "Text 3", "label": "cs.LG"}
        ]
        
        unique = preprocessor.deduplicate_samples(samples)
        
        assert len(unique) == 2
        assert unique[0]["title"] == "Machine Learning"
        assert unique[1]["title"] == "Deep Learning"
    
    def test_filter_by_quality_removes_short_text(self, preprocessor):
        """Test that filter_by_quality removes short text."""
        samples = [
            {"text": "Short", "label": "cs.AI"},
            {"text": " ".join(["word"] * 60), "label": "cs.LG"}  # 60 words
        ]
        
        filtered = preprocessor.filter_by_quality(samples, min_words=50)
        
        assert len(filtered) == 1
        assert len(filtered[0]["text"].split()) >= 50
    
    def test_filter_by_quality_removes_empty_text(self, preprocessor):
        """Test that filter_by_quality removes empty text."""
        samples = [
            {"text": "", "label": "cs.AI"},
            {"text": "   ", "label": "cs.LG"},
            {"text": " ".join(["word"] * 60), "label": "cs.CV"}
        ]
        
        filtered = preprocessor.filter_by_quality(samples, min_words=50)
        
        assert len(filtered) == 1
    
    def test_filter_by_quality_removes_missing_label(self, preprocessor):
        """Test that filter_by_quality removes samples with missing labels."""
        samples = [
            {"text": " ".join(["word"] * 60), "label": ""},
            {"text": " ".join(["word"] * 60), "label": "cs.AI"}
        ]
        
        filtered = preprocessor.filter_by_quality(samples, min_words=50)
        
        assert len(filtered) == 1
        assert filtered[0]["label"] == "cs.AI"
    
    def test_filter_by_quality_removes_non_english(self, preprocessor):
        """Test that filter_by_quality removes non-English text."""
        samples = [
            {"text": "这是一篇中文论文" * 20, "label": "cs.AI"},  # Chinese text
            {"text": " ".join(["english"] * 60), "label": "cs.LG"}
        ]
        
        filtered = preprocessor.filter_by_quality(samples, min_words=50)
        
        # Should keep only English text
        assert len(filtered) == 1
        assert "english" in filtered[0]["text"]
    
    def test_preprocess_dataset_complete_pipeline(self, preprocessor, sample_data):
        """Test complete preprocessing pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_file = Path(tmpdir) / "output.json"
            
            # Save sample data
            with open(input_file, 'w') as f:
                json.dump(sample_data, f)
            
            # Run preprocessing
            stats = preprocessor.preprocess_dataset(
                input_file=str(input_file),
                output_file=str(output_file),
                min_words=50
            )
            
            # Check stats
            assert stats["original_count"] == 10
            assert stats["duplicates_removed"] > 0
            assert stats["quality_filtered"] > 0
            assert stats["after_quality_filter"] < stats["original_count"]
            
            # Load and verify output
            with open(output_file, 'r') as f:
                output_data = json.load(f)
            
            assert "metadata" in output_data
            assert "samples" in output_data
            assert "preprocessing_steps" in output_data["metadata"]
            assert len(output_data["samples"]) == stats["after_quality_filter"]
    
    def test_create_train_val_test_split_ratios(self, preprocessor):
        """Test that train/val/test split maintains correct ratios."""
        # Create test dataset with enough samples
        samples = []
        for i in range(100):
            samples.append({
                "arxiv_id": f"2301.{i:05d}",
                "title": f"Paper {i}",
                "text": " ".join(["word"] * 60),
                "label": f"cs.{['AI', 'LG', 'CV', 'NE', 'RO'][i % 5]}"
            })
        
        test_data = {
            "metadata": {"source": "test"},
            "samples": samples
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_dir = Path(tmpdir) / "splits"
            
            # Save test data
            with open(input_file, 'w') as f:
                json.dump(test_data, f)
            
            # Create splits
            train, val, test = preprocessor.create_train_val_test_split(
                input_file=str(input_file),
                output_dir=str(output_dir),
                train_ratio=0.8,
                val_ratio=0.1,
                test_ratio=0.1,
                random_seed=42
            )
            
            # Check ratios (allow small rounding differences)
            total = len(train) + len(val) + len(test)
            assert total == 100
            assert abs(len(train) / total - 0.8) < 0.05
            assert abs(len(val) / total - 0.1) < 0.05
            assert abs(len(test) / total - 0.1) < 0.05
    
    def test_create_train_val_test_split_no_overlap(self, preprocessor):
        """Test that train/val/test splits have no overlap."""
        samples = []
        for i in range(100):
            samples.append({
                "arxiv_id": f"2301.{i:05d}",
                "title": f"Paper {i}",
                "text": " ".join(["word"] * 60),
                "label": f"cs.{['AI', 'LG'][i % 2]}"
            })
        
        test_data = {
            "metadata": {"source": "test"},
            "samples": samples
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_dir = Path(tmpdir) / "splits"
            
            with open(input_file, 'w') as f:
                json.dump(test_data, f)
            
            train, val, test = preprocessor.create_train_val_test_split(
                input_file=str(input_file),
                output_dir=str(output_dir),
                random_seed=42
            )
            
            # Check no overlap
            train_ids = {s["arxiv_id"] for s in train}
            val_ids = {s["arxiv_id"] for s in val}
            test_ids = {s["arxiv_id"] for s in test}
            
            assert len(train_ids & val_ids) == 0
            assert len(train_ids & test_ids) == 0
            assert len(val_ids & test_ids) == 0
    
    def test_create_train_val_test_split_reproducibility(self, preprocessor):
        """Test that splits are reproducible with fixed random seed."""
        samples = []
        for i in range(100):
            samples.append({
                "arxiv_id": f"2301.{i:05d}",
                "title": f"Paper {i}",
                "text": " ".join(["word"] * 60),
                "label": f"cs.{['AI', 'LG'][i % 2]}"
            })
        
        test_data = {
            "metadata": {"source": "test"},
            "samples": samples
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            
            with open(input_file, 'w') as f:
                json.dump(test_data, f)
            
            # Create splits twice with same seed
            output_dir1 = Path(tmpdir) / "splits1"
            train1, val1, test1 = preprocessor.create_train_val_test_split(
                input_file=str(input_file),
                output_dir=str(output_dir1),
                random_seed=42
            )
            
            output_dir2 = Path(tmpdir) / "splits2"
            train2, val2, test2 = preprocessor.create_train_val_test_split(
                input_file=str(input_file),
                output_dir=str(output_dir2),
                random_seed=42
            )
            
            # Check reproducibility
            train_ids1 = {s["arxiv_id"] for s in train1}
            train_ids2 = {s["arxiv_id"] for s in train2}
            assert train_ids1 == train_ids2
            
            val_ids1 = {s["arxiv_id"] for s in val1}
            val_ids2 = {s["arxiv_id"] for s in val2}
            assert val_ids1 == val_ids2
            
            test_ids1 = {s["arxiv_id"] for s in test1}
            test_ids2 = {s["arxiv_id"] for s in test2}
            assert test_ids1 == test_ids2
    
    def test_create_train_val_test_split_maintains_class_balance(self, preprocessor):
        """Test that stratified splitting maintains class balance."""
        # Create imbalanced dataset
        samples = []
        for i in range(80):
            samples.append({
                "arxiv_id": f"2301.{i:05d}",
                "title": f"Paper {i}",
                "text": " ".join(["word"] * 60),
                "label": "cs.AI"  # 80% cs.AI
            })
        for i in range(80, 100):
            samples.append({
                "arxiv_id": f"2301.{i:05d}",
                "title": f"Paper {i}",
                "text": " ".join(["word"] * 60),
                "label": "cs.LG"  # 20% cs.LG
            })
        
        test_data = {
            "metadata": {"source": "test"},
            "samples": samples
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_dir = Path(tmpdir) / "splits"
            
            with open(input_file, 'w') as f:
                json.dump(test_data, f)
            
            train, val, test = preprocessor.create_train_val_test_split(
                input_file=str(input_file),
                output_dir=str(output_dir),
                random_seed=42
            )
            
            # Check class balance in each split
            for split, split_name in [(train, "train"), (val, "val"), (test, "test")]:
                ai_count = sum(1 for s in split if s["label"] == "cs.AI")
                sum(1 for s in split if s["label"] == "cs.LG")
                ai_ratio = ai_count / len(split)
                
                # Should be approximately 80% cs.AI in each split
                assert abs(ai_ratio - 0.8) < 0.15, f"{split_name} split has imbalanced classes"
