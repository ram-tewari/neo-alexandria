"""
Load and preprocess external datasets for model training.

This script supports loading various external datasets and mapping their
categories to Neo Alexandria's taxonomy for improved model training.

Supported datasets:
- arXiv: Academic papers with categories
- AG News: News articles with topics
- Wikipedia: Articles with categories
- MovieLens: User-item ratings for recommendations

Usage:
    # Load arXiv dataset
    python backend/scripts/load_external_data.py \
        --dataset arxiv \
        --data-path data/external/arxiv/arxiv-metadata-oai-snapshot.json \
        --mapping-file backend/data/category_mappings/arxiv_mapping.json \
        --output data/processed/arxiv_training.json \
        --max-samples 50000

    # Load AG News dataset
    python backend/scripts/load_external_data.py \
        --dataset ag_news \
        --mapping-file backend/data/category_mappings/ag_news_mapping.json \
        --output data/processed/ag_news_training.json

    # Load MovieLens dataset
    python backend/scripts/load_external_data.py \
        --dataset movielens \
        --data-path data/external/movielens/ml-25m \
        --output data/processed/movielens_training.json \
        --min-rating 4.0
"""

import argparse
import json
import logging
from pathlib import Path
from typing import List, Tuple, Dict
from collections import Counter

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_category_mapping(mapping_file: str) -> Dict[str, List[str]]:
    """
    Load category mapping from JSON file.

    Args:
        mapping_file: Path to mapping JSON file

    Returns:
        Dictionary mapping external categories to taxonomy node IDs
    """
    logger.info(f"Loading category mapping from {mapping_file}")

    with open(mapping_file, "r") as f:
        data = json.load(f)

    mappings = data.get("mappings", {})
    logger.info(f"Loaded {len(mappings)} category mappings")

    return mappings


def load_arxiv_dataset(
    data_path: str, mapping_file: str, max_samples: int = 50000
) -> List[Tuple[str, List[str]]]:
    """
    Load arXiv dataset with category mapping.

    The arXiv dataset contains academic papers with titles, abstracts, and
    categories (e.g., cs.AI, cs.LG, physics.*, etc.). This function maps
    arXiv categories to Neo Alexandria taxonomy nodes.

    Args:
        data_path: Path to arxiv-metadata-oai-snapshot.json
        mapping_file: Path to category mapping JSON
        max_samples: Maximum samples to load (for memory efficiency)

    Returns:
        List of (text, [taxonomy_node_ids]) tuples
    """
    logger.info(f"Loading arXiv dataset from {data_path}")
    logger.info(f"Maximum samples: {max_samples}")

    category_mapping = load_category_mapping(mapping_file)
    data = []
    skipped = 0
    category_counts = Counter()

    with open(data_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if len(data) >= max_samples:
                break

            if i % 10000 == 0 and i > 0:
                logger.info(f"Processed {i} papers, collected {len(data)} samples...")

            try:
                paper = json.loads(line)

                # Extract text (title + abstract)
                title = paper.get("title", "").strip()
                abstract = paper.get("abstract", "").strip()

                # Clean up text (remove newlines, extra spaces)
                title = " ".join(title.split())
                abstract = " ".join(abstract.split())

                text = f"{title}. {abstract}"

                # Skip if text is too short
                if len(text) < 50:
                    skipped += 1
                    continue

                # Map categories to taxonomy nodes
                categories = paper.get("categories", "").split()
                taxonomy_ids = set()

                for cat in categories:
                    # Try exact match first
                    if cat in category_mapping:
                        mapped = category_mapping[cat]
                        if isinstance(mapped, list):
                            taxonomy_ids.update(mapped)
                        else:
                            taxonomy_ids.add(mapped)
                        category_counts[cat] += 1
                    else:
                        # Try prefix match (e.g., cs.AI -> cs)
                        prefix = cat.split(".")[0]
                        if prefix in category_mapping:
                            mapped = category_mapping[prefix]
                            if isinstance(mapped, list):
                                taxonomy_ids.update(mapped)
                            else:
                                taxonomy_ids.add(mapped)
                            category_counts[prefix] += 1

                # Only include if we have valid taxonomy mappings
                if text and taxonomy_ids:
                    data.append((text, list(taxonomy_ids)))
                else:
                    skipped += 1

            except Exception as e:
                logger.warning(f"Error processing line {i}: {e}")
                skipped += 1
                continue

    logger.info(f"Loaded {len(data)} samples from arXiv")
    logger.info(f"Skipped {skipped} samples (no mapping or too short)")

    # Log category distribution
    logger.info("Top 10 categories:")
    for cat, count in category_counts.most_common(10):
        logger.info(f"  {cat}: {count} samples")

    return data


def load_ag_news_dataset(
    mapping_file: str, max_samples: int = None
) -> List[Tuple[str, List[str]]]:
    """
    Load AG News dataset from Hugging Face.

    AG News contains 120K news articles in 4 categories:
    - World (0)
    - Sports (1)
    - Business (2)
    - Sci/Tech (3)

    Args:
        mapping_file: Path to category mapping JSON
        max_samples: Maximum samples to load (None = all)

    Returns:
        List of (text, [taxonomy_node_ids]) tuples
    """
    try:
        from datasets import load_dataset
    except ImportError:
        logger.error(
            "datasets library not installed. Install with: pip install datasets"
        )
        raise

    logger.info("Loading AG News dataset from Hugging Face")

    category_mapping = load_category_mapping(mapping_file)

    # AG News category labels
    ag_categories = {0: "world", 1: "sports", 2: "business", 3: "sci-tech"}

    # Load dataset
    dataset = load_dataset("ag_news")

    data = []
    skipped = 0

    for split in ["train", "test"]:
        logger.info(f"Processing {split} split...")

        for item in dataset[split]:
            if max_samples and len(data) >= max_samples:
                break

            text = item["text"].strip()
            ag_cat = ag_categories[item["label"]]

            # Map to taxonomy
            if ag_cat in category_mapping:
                mapped = category_mapping[ag_cat]
                taxonomy_ids = mapped if isinstance(mapped, list) else [mapped]
                data.append((text, taxonomy_ids))
            else:
                skipped += 1

    logger.info(f"Loaded {len(data)} samples from AG News")
    logger.info(f"Skipped {skipped} samples (no mapping)")

    return data


def load_movielens_dataset(
    data_path: str, min_rating: float = 4.0, max_samples: int = None
) -> List[Tuple[str, str, float, int]]:
    """
    Load MovieLens dataset for recommendation training.

    Args:
        data_path: Path to MovieLens directory (e.g., ml-25m)
        min_rating: Minimum rating to consider as positive interaction
        max_samples: Maximum samples to load (None = all)

    Returns:
        List of (user_id, item_id, rating, timestamp) tuples
    """
    try:
        import pandas as pd
    except ImportError:
        logger.error("pandas library not installed. Install with: pip install pandas")
        raise

    logger.info(f"Loading MovieLens dataset from {data_path}")
    logger.info(f"Minimum rating threshold: {min_rating}")

    ratings_file = Path(data_path) / "ratings.csv"

    if not ratings_file.exists():
        raise FileNotFoundError(f"Ratings file not found: {ratings_file}")

    # Load ratings
    logger.info("Reading ratings.csv...")
    ratings = pd.read_csv(ratings_file)

    logger.info(f"Total ratings: {len(ratings)}")

    # Filter for positive interactions
    positive_ratings = ratings[ratings["rating"] >= min_rating]
    logger.info(f"Positive ratings (>= {min_rating}): {len(positive_ratings)}")

    # Limit samples if specified
    if max_samples:
        positive_ratings = positive_ratings.head(max_samples)
        logger.info(f"Limited to {max_samples} samples")

    # Convert to list of tuples
    interactions = []
    for _, row in positive_ratings.iterrows():
        interactions.append(
            (
                str(row["userId"]),
                str(row["movieId"]),
                float(row["rating"]),
                int(row["timestamp"]),
            )
        )

    logger.info(f"Loaded {len(interactions)} interactions")

    # Log statistics
    unique_users = len(set(u for u, _, _, _ in interactions))
    unique_items = len(set(i for _, i, _, _ in interactions))
    logger.info(f"Unique users: {unique_users}")
    logger.info(f"Unique items: {unique_items}")

    return interactions


def save_classification_data(data: List[Tuple[str, List[str]]], output_path: str):
    """
    Save classification data in training format.

    Args:
        data: List of (text, [taxonomy_node_ids]) tuples
        output_path: Output file path
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert to JSON format
    json_data = []
    for text, taxonomy_ids in data:
        json_data.append({"text": text, "taxonomy_node_ids": taxonomy_ids})

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(json_data)} samples to {output_file}")

    # Log statistics
    total_labels = sum(len(item["taxonomy_node_ids"]) for item in json_data)
    avg_labels = total_labels / len(json_data) if json_data else 0
    logger.info(f"Average labels per sample: {avg_labels:.2f}")

    # Count label distribution
    label_counts = Counter()
    for item in json_data:
        for label in item["taxonomy_node_ids"]:
            label_counts[label] += 1

    logger.info("Label distribution:")
    for label, count in label_counts.most_common():
        logger.info(f"  {label}: {count} samples")


def save_recommendation_data(data: List[Tuple[str, str, float, int]], output_path: str):
    """
    Save recommendation data in training format.

    Args:
        data: List of (user_id, item_id, rating, timestamp) tuples
        output_path: Output file path
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert to JSON format
    json_data = []
    for user_id, item_id, rating, timestamp in data:
        json_data.append(
            {
                "user_id": user_id,
                "item_id": item_id,
                "rating": rating,
                "timestamp": timestamp,
            }
        )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    logger.info(f"Saved {len(json_data)} interactions to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Load external datasets for training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load arXiv dataset
  python backend/scripts/load_external_data.py \\
    --dataset arxiv \\
    --data-path data/external/arxiv/arxiv-metadata-oai-snapshot.json \\
    --mapping-file backend/data/category_mappings/arxiv_mapping.json \\
    --output data/processed/arxiv_training.json \\
    --max-samples 50000

  # Load AG News dataset
  python backend/scripts/load_external_data.py \\
    --dataset ag_news \\
    --mapping-file backend/data/category_mappings/ag_news_mapping.json \\
    --output data/processed/ag_news_training.json

  # Load MovieLens dataset
  python backend/scripts/load_external_data.py \\
    --dataset movielens \\
    --data-path data/external/movielens/ml-25m \\
    --output data/processed/movielens_training.json \\
    --min-rating 4.0
        """,
    )

    parser.add_argument(
        "--dataset",
        required=True,
        choices=["arxiv", "ag_news", "movielens"],
        help="Dataset to load",
    )

    parser.add_argument(
        "--data-path", help="Path to raw dataset (required for arxiv, movielens)"
    )

    parser.add_argument(
        "--mapping-file",
        help="Path to category mapping JSON (required for classification datasets)",
    )

    parser.add_argument(
        "--output", required=True, help="Output path for processed data"
    )

    parser.add_argument(
        "--max-samples", type=int, help="Maximum samples to load (default: all)"
    )

    parser.add_argument(
        "--min-rating",
        type=float,
        default=4.0,
        help="Minimum rating for MovieLens (default: 4.0)",
    )

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("External Dataset Loader")
    logger.info("=" * 70)
    logger.info(f"Dataset: {args.dataset}")
    logger.info(f"Output: {args.output}")
    logger.info("")

    try:
        if args.dataset == "arxiv":
            if not args.data_path:
                parser.error("--data-path is required for arxiv dataset")
            if not args.mapping_file:
                parser.error("--mapping-file is required for arxiv dataset")

            data = load_arxiv_dataset(
                args.data_path, args.mapping_file, args.max_samples or 50000
            )
            save_classification_data(data, args.output)

        elif args.dataset == "ag_news":
            if not args.mapping_file:
                parser.error("--mapping-file is required for ag_news dataset")

            data = load_ag_news_dataset(args.mapping_file, args.max_samples)
            save_classification_data(data, args.output)

        elif args.dataset == "movielens":
            if not args.data_path:
                parser.error("--data-path is required for movielens dataset")

            data = load_movielens_dataset(
                args.data_path, args.min_rating, args.max_samples
            )
            save_recommendation_data(data, args.output)

        logger.info("")
        logger.info("=" * 70)
        logger.info("Dataset loading complete!")
        logger.info("=" * 70)
        logger.info(f"Output saved to: {args.output}")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Verify the output file")
        logger.info(
            "  2. Train model with: python backend/scripts/train_classification.py --data-path "
            + args.output
        )

    except Exception as e:
        logger.error(f"Error loading dataset: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
