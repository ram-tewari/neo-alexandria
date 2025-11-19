"""
ArXiv Dataset Collector

This module provides functionality to collect academic papers from the arXiv API
with rate limiting, retry logic, and balanced dataset collection across categories.
"""

import arxiv
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArxivCollector:
    """
    Collector for arXiv academic papers with rate limiting and error handling.
    
    This class provides methods to fetch papers from the arXiv API, respecting
    rate limits and implementing retry logic for robust data collection.
    """
    
    def __init__(self, output_dir: str = "data/raw/arxiv"):
        """
        Initialize the ArxivCollector.
        
        Args:
            output_dir: Directory to save collected papers (default: "data/raw/arxiv")
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize arxiv client with rate limiting
        # arXiv API allows 3 requests per second, we use 0.5s delay to be safe
        self.client = arxiv.Client(
            page_size=100,
            delay_seconds=0.5,
            num_retries=3
        )
        
        logger.info(f"ArxivCollector initialized with output directory: {self.output_dir}")
        logger.info("Rate limiting: 0.5s delay between requests, 3 retries on failure")

    def collect_papers_by_category(
        self,
        category: str,
        max_results: int = 1000,
        start_date: Optional[str] = "2020-01-01"
    ) -> List[Dict]:
        """
        Collect papers from a specific arXiv category.
        
        Args:
            category: arXiv category code (e.g., "cs.AI", "cs.LG")
            max_results: Maximum number of papers to collect (default: 1000)
            start_date: Start date for filtering papers in YYYY-MM-DD format (default: "2020-01-01")
            
        Returns:
            List of paper dictionaries with metadata
            
        Raises:
            Exception: If collection fails after retries
        """
        logger.info(f"Starting collection for category: {category}")
        logger.info(f"Target: {max_results} papers, Start date: {start_date}")
        
        papers = []
        
        # Build search query
        query = f"cat:{category}"
        if start_date:
            # arXiv uses submittedDate for filtering
            query += f" AND submittedDate:[{start_date.replace('-', '')} TO *]"
        
        try:
            # Create search with client
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            # Fetch papers with progress logging
            count = 0
            for result in self.client.results(search):
                try:
                    # Extract paper metadata
                    paper = {
                        "arxiv_id": result.entry_id.split("/")[-1],
                        "title": result.title,
                        "abstract": result.summary,
                        "authors": [author.name for author in result.authors],
                        "categories": result.categories,
                        "primary_category": result.primary_category,
                        "published": result.published.isoformat(),
                        "updated": result.updated.isoformat() if result.updated else None,
                        "pdf_url": result.pdf_url,
                        "comment": result.comment,
                        "journal_ref": result.journal_ref
                    }
                    
                    papers.append(paper)
                    count += 1
                    
                    # Progress logging every 100 papers
                    if count % 100 == 0:
                        logger.info(f"Collected {count}/{max_results} papers from {category}")
                        
                        # Save intermediate results to prevent data loss
                        self._save_intermediate_results(category, papers, count)
                        
                except Exception as e:
                    logger.warning(f"Error extracting paper metadata: {e}")
                    continue
            
            logger.info(f"Successfully collected {len(papers)} papers from {category}")
            return papers
            
        except Exception as e:
            logger.error(f"Error collecting papers from {category}: {e}")
            
            # Save partial results before raising
            if papers:
                self._save_intermediate_results(category, papers, len(papers), error=True)
                logger.info(f"Saved {len(papers)} partial results before failure")
            
            raise
    
    def _save_intermediate_results(
        self,
        category: str,
        papers: List[Dict],
        count: int,
        error: bool = False
    ):
        """
        Save intermediate results to prevent data loss.
        
        Args:
            category: Category being collected
            papers: List of papers collected so far
            count: Number of papers collected
            error: Whether this is an error save
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = "_error" if error else "_intermediate"
        filename = f"{category.replace('.', '_')}_{count}{suffix}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "category": category,
                    "count": count,
                    "timestamp": timestamp,
                    "papers": papers
                }, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved intermediate results to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save intermediate results: {e}")

    def collect_balanced_dataset(
        self,
        categories: List[str],
        papers_per_category: int = 1000,
        start_date: Optional[str] = "2020-01-01"
    ) -> Dict[str, List[Dict]]:
        """
        Collect equal number of papers from multiple categories for balanced dataset.
        
        Args:
            categories: List of arXiv category codes
            papers_per_category: Number of papers to collect per category (default: 1000)
            start_date: Start date for filtering papers (default: "2020-01-01")
            
        Returns:
            Dictionary mapping category to list of papers
        """
        logger.info("Starting balanced dataset collection")
        logger.info(f"Categories: {categories}")
        logger.info(f"Papers per category: {papers_per_category}")
        
        dataset = {}
        
        for i, category in enumerate(categories):
            logger.info(f"Processing category {i+1}/{len(categories)}: {category}")
            
            try:
                # Collect papers for this category
                papers = self.collect_papers_by_category(
                    category=category,
                    max_results=papers_per_category,
                    start_date=start_date
                )
                
                dataset[category] = papers
                
                # Save category results to separate JSON file
                category_filename = f"{category.replace('.', '_')}_papers.json"
                category_filepath = self.output_dir / category_filename
                
                with open(category_filepath, 'w', encoding='utf-8') as f:
                    json.dump({
                        "category": category,
                        "num_papers": len(papers),
                        "collected_at": datetime.now().isoformat(),
                        "papers": papers
                    }, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Saved {len(papers)} papers to {category_filepath}")
                
                # Rate limiting between categories (1s delay)
                if i < len(categories) - 1:  # Don't delay after last category
                    logger.debug("Waiting 1s before next category...")
                    time.sleep(1.0)
                    
            except Exception as e:
                logger.error(f"Failed to collect papers for {category}: {e}")
                dataset[category] = []
                continue
        
        # Log summary
        total_papers = sum(len(papers) for papers in dataset.values())
        logger.info("Balanced dataset collection complete")
        logger.info(f"Total papers collected: {total_papers}")
        logger.info(f"Papers per category: {[len(papers) for papers in dataset.values()]}")
        
        return dataset

    def create_classification_dataset(
        self,
        num_papers: int = 10000,
        output_file: str = "arxiv_classification.json",
        start_date: Optional[str] = "2020-01-01"
    ):
        """
        Create complete classification dataset with 10 CS categories.
        
        This method collects papers from 10 computer science subcategories,
        combines them into a single dataset, and saves with metadata.
        
        Args:
            num_papers: Total number of papers to collect (default: 10000)
            output_file: Output filename (default: "arxiv_classification.json")
            start_date: Start date for filtering papers (default: "2020-01-01")
        """
        # Define 10 CS categories
        categories = [
            "cs.AI",  # Artificial Intelligence
            "cs.CL",  # Computation and Language (NLP)
            "cs.CV",  # Computer Vision
            "cs.LG",  # Machine Learning
            "cs.CR",  # Cryptography and Security
            "cs.DB",  # Databases
            "cs.DC",  # Distributed Computing
            "cs.NE",  # Neural and Evolutionary Computing
            "cs.RO",  # Robotics
            "cs.SE"   # Software Engineering
        ]
        
        logger.info("=" * 80)
        logger.info("Creating Classification Dataset")
        logger.info("=" * 80)
        logger.info(f"Target papers: {num_papers}")
        logger.info(f"Categories: {len(categories)}")
        logger.info(f"Papers per category: {num_papers // len(categories)}")
        logger.info(f"Start date: {start_date}")
        logger.info("=" * 80)
        
        # Calculate papers per category
        papers_per_category = num_papers // len(categories)
        
        # Collect balanced dataset
        dataset_by_category = self.collect_balanced_dataset(
            categories=categories,
            papers_per_category=papers_per_category,
            start_date=start_date
        )
        
        # Flatten dataset and combine title + abstract as text
        samples = []
        for category, papers in dataset_by_category.items():
            for paper in papers:
                sample = {
                    "text": f"{paper['title']}. {paper['abstract']}",
                    "label": category,
                    "arxiv_id": paper["arxiv_id"],
                    "title": paper["title"],
                    "authors": paper["authors"],
                    "published": paper["published"]
                }
                samples.append(sample)
        
        # Create complete dataset with metadata
        complete_dataset = {
            "metadata": {
                "num_samples": len(samples),
                "num_categories": len(categories),
                "categories": categories,
                "created_at": datetime.now().isoformat(),
                "source": "arXiv API",
                "start_date": start_date,
                "papers_per_category": papers_per_category
            },
            "samples": samples
        }
        
        # Save complete dataset
        output_path = self.output_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(complete_dataset, f, indent=2, ensure_ascii=False)
        
        # Calculate file size
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        
        # Log dataset statistics
        logger.info("=" * 80)
        logger.info("Dataset Creation Complete!")
        logger.info("=" * 80)
        logger.info(f"Total samples: {len(samples)}")
        logger.info(f"Categories: {len(categories)}")
        logger.info("Samples per category:")
        for category in categories:
            count = sum(1 for s in samples if s["label"] == category)
            logger.info(f"  {category}: {count}")
        logger.info(f"Output file: {output_path}")
        logger.info(f"File size: {file_size_mb:.2f} MB")
        logger.info("=" * 80)
        
        return complete_dataset


# Example usage
if __name__ == "__main__":
    # Create collector
    collector = ArxivCollector(output_dir="backend/data/raw/arxiv")
    
    # Create classification dataset with 10,000 papers
    collector.create_classification_dataset(
        num_papers=10000,
        output_file="arxiv_classification.json",
        start_date="2020-01-01"
    )
