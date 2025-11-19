"""
Data preparation utilities for ML model training.

This module provides functions to load and prepare training data from test datasets,
including data augmentation and synthetic data generation.
"""

import json
import logging
import random
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_classification_test_data(
    data_path: Optional[str] = None
) -> List[Tuple[str, List[str]]]:
    """
    Load classification test data from JSON dataset.
    
    Args:
        data_path: Path to the classification test JSON file.
                  If None, uses default path.
    
    Returns:
        List of tuples containing (text, [taxonomy_node_ids])
    
    Raises:
        FileNotFoundError: If the data file doesn't exist
        ValueError: If the data format is invalid
    """
    if data_path is None:
        # Default path relative to backend directory
        data_path = "backend/tests/ml_benchmarks/datasets/classification_test.json"
    
    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Classification test data not found at {data_path}")
    
    logger.info(f"Loading classification data from {data_path}")
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {data_path}: {e}")
    
    # Validate data structure
    if 'samples' not in data:
        raise ValueError("Missing 'samples' key in classification data")
    
    samples = data['samples']
    if not isinstance(samples, list):
        raise ValueError("'samples' must be a list")
    
    # Extract text and taxonomy node IDs
    training_data = []
    invalid_count = 0
    
    for idx, sample in enumerate(samples):
        try:
            text = sample.get('text')
            taxonomy_ids = sample.get('taxonomy_node_ids')
            
            if not text:
                logger.warning(f"Sample {idx}: Missing or empty 'text' field")
                invalid_count += 1
                continue
            
            if not taxonomy_ids or not isinstance(taxonomy_ids, list):
                logger.warning(f"Sample {idx}: Missing or invalid 'taxonomy_node_ids' field")
                invalid_count += 1
                continue
            
            training_data.append((text, taxonomy_ids))
            
        except Exception as e:
            logger.warning(f"Sample {idx}: Error processing sample - {e}")
            invalid_count += 1
            continue
    
    logger.info(f"Loaded {len(training_data)} valid samples")
    if invalid_count > 0:
        logger.warning(f"Skipped {invalid_count} invalid samples")
    
    if len(training_data) == 0:
        raise ValueError("No valid samples found in classification data")
    
    return training_data


def load_recommendation_test_data(
    data_path: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, int], Dict[str, int]]:
    """
    Load recommendation test data from JSON dataset.
    
    Args:
        data_path: Path to the recommendation test JSON file.
                  If None, uses default path.
    
    Returns:
        Tuple containing:
        - List of interaction dictionaries
        - User ID to index mapping
        - Item ID to index mapping
    
    Raises:
        FileNotFoundError: If the data file doesn't exist
        ValueError: If the data format is invalid
    """
    if data_path is None:
        # Default path relative to backend directory
        data_path = "backend/tests/ml_benchmarks/datasets/recommendation_test.json"
    
    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Recommendation test data not found at {data_path}")
    
    logger.info(f"Loading recommendation data from {data_path}")
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {data_path}: {e}")
    
    # Validate data structure
    if 'interactions' not in data:
        raise ValueError("Missing 'interactions' key in recommendation data")
    
    interactions = data['interactions']
    if not isinstance(interactions, list):
        raise ValueError("'interactions' must be a list")
    
    # Extract interactions and build ID mappings
    valid_interactions = []
    user_ids = set()
    item_ids = set()
    invalid_count = 0
    
    for idx, interaction in enumerate(interactions):
        try:
            user_id = interaction.get('user_id')
            item_id = interaction.get('resource_id')
            timestamp = interaction.get('timestamp')
            
            if not user_id:
                logger.warning(f"Interaction {idx}: Missing 'user_id' field")
                invalid_count += 1
                continue
            
            if not item_id:
                logger.warning(f"Interaction {idx}: Missing 'resource_id' field")
                invalid_count += 1
                continue
            
            # Add to sets for mapping
            user_ids.add(user_id)
            item_ids.add(item_id)
            
            # Store interaction with all fields
            valid_interactions.append({
                'user_id': user_id,
                'item_id': item_id,
                'timestamp': timestamp,
                'interaction_type': interaction.get('interaction_type', 'view'),
                'strength': interaction.get('strength', 1.0)
            })
            
        except Exception as e:
            logger.warning(f"Interaction {idx}: Error processing interaction - {e}")
            invalid_count += 1
            continue
    
    # Create ID mappings (string to integer index)
    user_id_map = {user_id: idx for idx, user_id in enumerate(sorted(user_ids))}
    item_id_map = {item_id: idx for idx, item_id in enumerate(sorted(item_ids))}
    
    logger.info(f"Loaded {len(valid_interactions)} valid interactions")
    logger.info(f"Found {len(user_id_map)} unique users and {len(item_id_map)} unique items")
    
    if invalid_count > 0:
        logger.warning(f"Skipped {invalid_count} invalid interactions")
    
    if len(valid_interactions) == 0:
        raise ValueError("No valid interactions found in recommendation data")
    
    return valid_interactions, user_id_map, item_id_map


def augment_classification_data(
    data: List[Tuple[str, List[str]]],
    target_size: int = 500,
    multiplier: int = 3
) -> List[Tuple[str, List[str]]]:
    """
    Augment classification data for small datasets.
    
    Creates text variations using simple paraphrasing techniques while
    maintaining label consistency.
    
    Args:
        data: Original training data as list of (text, labels) tuples
        target_size: Minimum desired dataset size
        multiplier: Maximum number of variations per sample
    
    Returns:
        Augmented dataset with original and synthetic samples
    """
    if len(data) >= target_size:
        logger.info(f"Dataset size ({len(data)}) already meets target ({target_size})")
        return data
    
    logger.info(f"Augmenting dataset from {len(data)} to at least {target_size} samples")
    
    augmented_data = list(data)  # Start with original data
    needed = target_size - len(data)
    
    # Simple text variation techniques
    def create_variation(text: str) -> str:
        """Create a simple variation of the text."""
        
        # Add introductory phrases
        intros = [
            "This article discusses: ",
            "An overview of: ",
            "Key concepts include: ",
            "This resource covers: ",
            ""
        ]
        
        # Add concluding phrases
        outros = [
            " - essential knowledge for practitioners.",
            " - important concepts to understand.",
            " - fundamental principles explained.",
            "",
            ""
        ]
        
        intro = random.choice(intros)
        outro = random.choice(outros)
        
        return f"{intro}{text}{outro}"
    
    # Generate variations
    samples_per_original = min(multiplier, (needed // len(data)) + 1)
    
    for text, labels in data:
        for _ in range(samples_per_original):
            if len(augmented_data) >= target_size:
                break
            
            # Create variation
            varied_text = create_variation(text)
            augmented_data.append((varied_text, labels))
        
        if len(augmented_data) >= target_size:
            break
    
    logger.info(f"Augmented dataset to {len(augmented_data)} samples")
    
    # Shuffle to mix original and augmented samples
    random.shuffle(augmented_data)
    
    return augmented_data


def create_synthetic_interactions(
    num_users: int = 50,
    num_items: int = 200,
    num_interactions: int = 1000,
    popularity_bias: float = 0.3
) -> Tuple[List[Dict[str, Any]], Dict[str, int], Dict[str, int]]:
    """
    Generate synthetic user-item interactions for NCF training.
    
    Creates realistic interaction patterns with temporal patterns and
    popularity bias.
    
    Args:
        num_users: Number of unique users
        num_items: Number of unique items
        num_interactions: Total number of interactions to generate
        popularity_bias: Strength of popularity bias (0-1)
    
    Returns:
        Tuple containing:
        - List of interaction dictionaries
        - User ID to index mapping
        - Item ID to index mapping
    """
    logger.info(f"Generating {num_interactions} synthetic interactions")
    logger.info(f"Users: {num_users}, Items: {num_items}")
    
    # Create user and item IDs
    user_ids = [f"user_{i:03d}" for i in range(1, num_users + 1)]
    item_ids = [f"item_{i:03d}" for i in range(1, num_items + 1)]
    
    # Create ID mappings
    user_id_map = {user_id: idx for idx, user_id in enumerate(user_ids)}
    item_id_map = {item_id: idx for idx, item_id in enumerate(item_ids)}
    
    # Generate popularity distribution (power law)
    item_popularity = []
    for i in range(num_items):
        # Power law: more popular items have higher probability
        popularity = (num_items - i) ** (1 + popularity_bias)
        item_popularity.append(popularity)
    
    # Normalize to probabilities
    total = sum(item_popularity)
    item_probs = [p / total for p in item_popularity]
    
    # Interaction types and their strengths
    interaction_types = [
        ('view', 0.25),
        ('bookmark', 0.75),
        ('annotation', 0.60),
        ('share', 0.70),
        ('collection_add', 0.90)
    ]
    
    # Generate interactions
    interactions = []
    start_date = datetime(2025, 1, 1)
    
    # Track user-item pairs to avoid duplicates
    seen_pairs = set()
    
    attempts = 0
    max_attempts = num_interactions * 3
    
    while len(interactions) < num_interactions and attempts < max_attempts:
        attempts += 1
        
        # Select user uniformly
        user_id = random.choice(user_ids)
        
        # Select item with popularity bias
        item_id = random.choices(item_ids, weights=item_probs)[0]
        
        # Skip if we've seen this pair
        pair = (user_id, item_id)
        if pair in seen_pairs:
            continue
        
        seen_pairs.add(pair)
        
        # Select interaction type
        interaction_type, base_strength = random.choice(interaction_types)
        
        # Add some randomness to strength
        strength = base_strength + random.uniform(-0.1, 0.1)
        strength = max(0.2, min(1.0, strength))
        
        # Generate timestamp (spread over 6 months)
        days_offset = random.randint(0, 180)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        
        timestamp = start_date + timedelta(
            days=days_offset,
            hours=hours_offset,
            minutes=minutes_offset
        )
        
        interactions.append({
            'user_id': user_id,
            'item_id': item_id,
            'timestamp': timestamp.isoformat(),
            'interaction_type': interaction_type,
            'strength': round(strength, 2)
        })
    
    if len(interactions) < num_interactions:
        logger.warning(
            f"Could only generate {len(interactions)} unique interactions "
            f"(target was {num_interactions})"
        )
    else:
        logger.info(f"Generated {len(interactions)} synthetic interactions")
    
    # Sort by timestamp
    interactions.sort(key=lambda x: x['timestamp'])
    
    return interactions, user_id_map, item_id_map


def validate_data_format(data: Any, data_type: str) -> bool:
    """
    Validate data format and completeness.
    
    Args:
        data: Data to validate
        data_type: Type of data ('classification' or 'recommendation')
    
    Returns:
        True if data is valid, False otherwise
    """
    try:
        if data_type == 'classification':
            if not isinstance(data, list):
                logger.error("Classification data must be a list")
                return False
            
            if len(data) == 0:
                logger.error("Classification data is empty")
                return False
            
            # Check first few samples
            for idx, item in enumerate(data[:5]):
                if not isinstance(item, tuple) or len(item) != 2:
                    logger.error(f"Sample {idx}: Must be a tuple of (text, labels)")
                    return False
                
                text, labels = item
                if not isinstance(text, str) or not text.strip():
                    logger.error(f"Sample {idx}: Text must be a non-empty string")
                    return False
                
                if not isinstance(labels, list) or len(labels) == 0:
                    logger.error(f"Sample {idx}: Labels must be a non-empty list")
                    return False
            
            logger.info(f"Classification data validation passed ({len(data)} samples)")
            return True
        
        elif data_type == 'recommendation':
            if not isinstance(data, tuple) or len(data) != 3:
                logger.error("Recommendation data must be a tuple of (interactions, user_map, item_map)")
                return False
            
            interactions, user_map, item_map = data
            
            if not isinstance(interactions, list) or len(interactions) == 0:
                logger.error("Interactions must be a non-empty list")
                return False
            
            if not isinstance(user_map, dict) or len(user_map) == 0:
                logger.error("User ID map must be a non-empty dictionary")
                return False
            
            if not isinstance(item_map, dict) or len(item_map) == 0:
                logger.error("Item ID map must be a non-empty dictionary")
                return False
            
            # Check first few interactions
            for idx, interaction in enumerate(interactions[:5]):
                if not isinstance(interaction, dict):
                    logger.error(f"Interaction {idx}: Must be a dictionary")
                    return False
                
                required_fields = ['user_id', 'item_id']
                for field in required_fields:
                    if field not in interaction:
                        logger.error(f"Interaction {idx}: Missing required field '{field}'")
                        return False
            
            logger.info(
                f"Recommendation data validation passed "
                f"({len(interactions)} interactions, {len(user_map)} users, {len(item_map)} items)"
            )
            return True
        
        else:
            logger.error(f"Unknown data type: {data_type}")
            return False
    
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    print("Data Preparation Utilities")
    print("=" * 50)
    
    # Test classification data loading
    try:
        print("\n1. Loading classification data...")
        classification_data = load_classification_test_data()
        print(f"   Loaded {len(classification_data)} samples")
        print(f"   Sample: {classification_data[0][0][:100]}...")
        print(f"   Labels: {classification_data[0][1]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test recommendation data loading
    try:
        print("\n2. Loading recommendation data...")
        interactions, user_map, item_map = load_recommendation_test_data()
        print(f"   Loaded {len(interactions)} interactions")
        print(f"   Users: {len(user_map)}, Items: {len(item_map)}")
        print(f"   Sample interaction: {interactions[0]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test data augmentation
    try:
        print("\n3. Testing data augmentation...")
        small_dataset = classification_data[:10]
        augmented = augment_classification_data(small_dataset, target_size=30)
        print(f"   Augmented from {len(small_dataset)} to {len(augmented)} samples")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test synthetic data generation
    try:
        print("\n4. Generating synthetic interactions...")
        synth_interactions, synth_users, synth_items = create_synthetic_interactions(
            num_users=20,
            num_items=50,
            num_interactions=200
        )
        print(f"   Generated {len(synth_interactions)} interactions")
        print(f"   Users: {len(synth_users)}, Items: {len(synth_items)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("All tests completed!")
