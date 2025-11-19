"""
Dataset preprocessing module for cleaning, deduplicating, and validating ML training data.
"""

import json
import logging
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
from sklearn.model_selection import train_test_split

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetPreprocessor:
    """
    Preprocessor for cleaning and preparing datasets for ML training.
    
    Handles text cleaning, deduplication, quality filtering, and train/val/test splitting.
    """
    
    def __init__(self):
        """Initialize the dataset preprocessor."""
        self.stats = {
            "original_count": 0,
            "after_cleaning": 0,
            "after_deduplication": 0,
            "after_quality_filter": 0,
            "duplicates_removed": 0,
            "quality_filtered": 0
        }
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing URLs, LaTeX commands, and normalizing whitespace.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        
        # Remove LaTeX commands (e.g., \textbf{...}, \cite{...})
        text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
        
        # Remove inline math (e.g., $x^2$)
        text = re.sub(r'\$[^$]*\$', '', text)
        
        # Remove display math (e.g., $$...$$)
        text = re.sub(r'\$\$[^$]*\$\$', '', text)
        
        # Normalize whitespace (multiple spaces to single space)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove multiple punctuation (e.g., ... -> .)
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\!{2,}', '!', text)
        text = re.sub(r'\?{2,}', '?', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def compute_text_hash(self, text: str) -> str:
        """
        Compute MD5 hash of text for deduplication.
        
        Args:
            text: Text to hash
            
        Returns:
            MD5 hash as hexadecimal string
        """
        # Normalize text before hashing (lowercase, strip whitespace)
        normalized = text.lower().strip()
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def deduplicate_samples(self, samples: List[Dict]) -> List[Dict]:
        """
        Remove duplicate samples by arXiv ID and title hash.
        
        Args:
            samples: List of sample dictionaries
            
        Returns:
            List of unique samples
        """
        seen_ids = set()
        seen_hashes = set()
        unique_samples = []
        duplicates_by_id = 0
        duplicates_by_hash = 0
        
        for sample in samples:
            arxiv_id = sample.get('arxiv_id', '')
            title = sample.get('title', '')
            
            # Check for duplicate arXiv ID
            if arxiv_id and arxiv_id in seen_ids:
                duplicates_by_id += 1
                continue
            
            # Check for duplicate title hash (near-duplicates)
            title_hash = self.compute_text_hash(title)
            if title_hash in seen_hashes:
                duplicates_by_hash += 1
                continue
            
            # Add to unique samples
            unique_samples.append(sample)
            if arxiv_id:
                seen_ids.add(arxiv_id)
            seen_hashes.add(title_hash)
        
        total_duplicates = duplicates_by_id + duplicates_by_hash
        logger.info(f"Removed {total_duplicates} duplicates ({duplicates_by_id} by ID, {duplicates_by_hash} by title hash)")
        self.stats["duplicates_removed"] = total_duplicates
        
        return unique_samples
    
    def filter_by_quality(self, samples: List[Dict], min_words: int = 50) -> List[Dict]:
        """
        Filter samples by quality criteria.
        
        Args:
            samples: List of sample dictionaries
            min_words: Minimum word count for text (default: 50)
            
        Returns:
            List of quality-filtered samples
        """
        filtered_samples = []
        removed_counts = {
            "empty_text": 0,
            "too_short": 0,
            "non_english": 0,
            "missing_label": 0
        }
        
        for sample in samples:
            text = sample.get('text', '')
            label = sample.get('label', '')
            
            # Check for non-empty text
            if not text or not text.strip():
                removed_counts["empty_text"] += 1
                continue
            
            # Check for valid label
            if not label:
                removed_counts["missing_label"] += 1
                continue
            
            # Check text length (word count)
            word_count = len(text.split())
            if word_count < min_words:
                removed_counts["too_short"] += 1
                continue
            
            # Check for English language (character-based detection)
            # Count ASCII alphabetic characters vs total characters
            alpha_chars = sum(1 for c in text if c.isalpha())
            ascii_chars = sum(1 for c in text if ord(c) < 128 and c.isalpha())
            
            if alpha_chars > 0:
                ascii_ratio = ascii_chars / alpha_chars
                # If less than 80% ASCII characters, likely not English
                if ascii_ratio < 0.8:
                    removed_counts["non_english"] += 1
                    continue
            
            # Sample passed all quality checks
            filtered_samples.append(sample)
        
        total_removed = sum(removed_counts.values())
        logger.info(f"Quality filtering removed {total_removed} samples:")
        for reason, count in removed_counts.items():
            if count > 0:
                logger.info(f"  - {reason}: {count}")
        
        self.stats["quality_filtered"] = total_removed
        
        return filtered_samples
    
    def preprocess_dataset(
        self,
        input_file: str,
        output_file: str,
        min_words: int = 50
    ) -> Dict:
        """
        Complete preprocessing pipeline: load, clean, deduplicate, filter, save.
        
        Args:
            input_file: Path to raw dataset JSON file
            output_file: Path to save preprocessed dataset
            min_words: Minimum word count for quality filtering
            
        Returns:
            Dictionary with preprocessing statistics
        """
        logger.info(f"Loading raw dataset from {input_file}")
        
        # Load raw dataset
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        samples = data.get('samples', [])
        metadata = data.get('metadata', {})
        
        self.stats["original_count"] = len(samples)
        logger.info(f"Loaded {len(samples)} samples")
        
        # Apply text cleaning to all samples
        logger.info("Applying text cleaning...")
        for sample in samples:
            if 'text' in sample:
                sample['text'] = self.clean_text(sample['text'])
            if 'title' in sample:
                sample['title'] = self.clean_text(sample['title'])
            if 'abstract' in sample:
                sample['abstract'] = self.clean_text(sample['abstract'])
        
        self.stats["after_cleaning"] = len(samples)
        
        # Apply deduplication
        logger.info("Applying deduplication...")
        samples = self.deduplicate_samples(samples)
        self.stats["after_deduplication"] = len(samples)
        
        # Apply quality filtering
        logger.info("Applying quality filtering...")
        samples = self.filter_by_quality(samples, min_words=min_words)
        self.stats["after_quality_filter"] = len(samples)
        
        # Prepare output data
        output_data = {
            "metadata": {
                **metadata,
                "preprocessing_steps": [
                    "text_cleaning",
                    "deduplication",
                    "quality_filtering"
                ],
                "preprocessing_params": {
                    "min_words": min_words
                },
                "sample_count": len(samples),
                "original_count": self.stats["original_count"],
                "duplicates_removed": self.stats["duplicates_removed"],
                "quality_filtered": self.stats["quality_filtered"]
            },
            "samples": samples
        }
        
        # Save preprocessed dataset
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved preprocessed dataset to {output_file}")
        logger.info("Preprocessing statistics:")
        logger.info(f"  - Original samples: {self.stats['original_count']}")
        logger.info(f"  - After cleaning: {self.stats['after_cleaning']}")
        logger.info(f"  - After deduplication: {self.stats['after_deduplication']}")
        logger.info(f"  - After quality filter: {self.stats['after_quality_filter']}")
        logger.info(f"  - Final samples: {len(samples)}")
        
        return self.stats
    
    def create_train_val_test_split(
        self,
        input_file: str,
        output_dir: str,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        random_seed: int = 42
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Create stratified train/val/test splits with fixed random seed.
        
        Args:
            input_file: Path to preprocessed dataset JSON file
            output_dir: Directory to save split files
            train_ratio: Proportion for training set (default: 0.8)
            val_ratio: Proportion for validation set (default: 0.1)
            test_ratio: Proportion for test set (default: 0.1)
            random_seed: Random seed for reproducibility (default: 42)
            
        Returns:
            Tuple of (train_samples, val_samples, test_samples)
        """
        # Validate ratios
        total_ratio = train_ratio + val_ratio + test_ratio
        if abs(total_ratio - 1.0) > 0.001:
            raise ValueError(f"Ratios must sum to 1.0, got {total_ratio}")
        
        logger.info(f"Loading preprocessed dataset from {input_file}")
        
        # Load preprocessed dataset
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        samples = data.get('samples', [])
        metadata = data.get('metadata', {})
        
        logger.info(f"Loaded {len(samples)} samples")
        
        # Extract labels for stratification
        labels = [sample['label'] for sample in samples]
        
        # First split: separate test set
        train_val_samples, test_samples, train_val_labels, test_labels = train_test_split(
            samples,
            labels,
            test_size=test_ratio,
            random_state=random_seed,
            stratify=labels
        )
        
        # Second split: separate train and validation
        # Adjust val_ratio relative to remaining data
        val_ratio_adjusted = val_ratio / (train_ratio + val_ratio)
        
        train_samples, val_samples, train_labels, val_labels = train_test_split(
            train_val_samples,
            train_val_labels,
            test_size=val_ratio_adjusted,
            random_state=random_seed,
            stratify=train_val_labels
        )
        
        # Log split sizes
        logger.info("Split sizes:")
        logger.info(f"  - Train: {len(train_samples)} ({len(train_samples)/len(samples)*100:.1f}%)")
        logger.info(f"  - Validation: {len(val_samples)} ({len(val_samples)/len(samples)*100:.1f}%)")
        logger.info(f"  - Test: {len(test_samples)} ({len(test_samples)/len(samples)*100:.1f}%)")
        
        # Verify no overlap between splits
        train_ids = {s.get('arxiv_id', id(s)) for s in train_samples}
        val_ids = {s.get('arxiv_id', id(s)) for s in val_samples}
        test_ids = {s.get('arxiv_id', id(s)) for s in test_samples}
        
        overlap_train_val = train_ids & val_ids
        overlap_train_test = train_ids & test_ids
        overlap_val_test = val_ids & test_ids
        
        if overlap_train_val or overlap_train_test or overlap_val_test:
            logger.warning("WARNING: Overlap detected between splits!")
        else:
            logger.info("Verified: No overlap between splits")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save each split with metadata
        splits = {
            'train': train_samples,
            'val': val_samples,
            'test': test_samples
        }
        
        for split_name, split_samples in splits.items():
            split_file = output_path / f"{split_name}.json"
            
            split_data = {
                "metadata": {
                    **metadata,
                    "split_name": split_name,
                    "sample_count": len(split_samples),
                    "random_seed": random_seed,
                    "split_ratios": {
                        "train": train_ratio,
                        "val": val_ratio,
                        "test": test_ratio
                    }
                },
                "samples": split_samples
            }
            
            with open(split_file, 'w', encoding='utf-8') as f:
                json.dump(split_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {split_name} split to {split_file}")
        
        return train_samples, val_samples, test_samples


if __name__ == "__main__":
    # Example usage
    preprocessor = DatasetPreprocessor()
    
    # Preprocess dataset
    stats = preprocessor.preprocess_dataset(
        input_file="data/raw/arxiv/arxiv_classification.json",
        output_file="data/processed/arxiv_classification_clean.json",
        min_words=50
    )
    
    # Create train/val/test splits
    train, val, test = preprocessor.create_train_val_test_split(
        input_file="data/processed/arxiv_classification_clean.json",
        output_dir="data/splits/arxiv_classification",
        random_seed=42
    )
    
    print("\nPreprocessing complete!")
    print(f"Train: {len(train)} samples")
    print(f"Val: {len(val)} samples")
    print(f"Test: {len(test)} samples")
