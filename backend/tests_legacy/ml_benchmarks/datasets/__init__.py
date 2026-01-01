"""
Test datasets for ML benchmarking.

This module provides utilities for loading and validating test datasets
used in ML benchmarking. All datasets are stored as JSON files with
standardized metadata and schema validation.
"""

import json
from pathlib import Path
from typing import Dict, Any


def load_dataset(dataset_name: str) -> Dict[str, Any]:
    """
    Load a test dataset from JSON file.
    
    Args:
        dataset_name: Name of the dataset file (without .json extension)
        
    Returns:
        Dictionary containing dataset metadata and samples
        
    Raises:
        FileNotFoundError: If dataset file doesn't exist
        ValueError: If dataset has invalid format
    """
    dataset_path = Path(__file__).parent / f"{dataset_name}.json"
    
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Validate required fields
    if "metadata" not in data:
        raise ValueError(f"Dataset {dataset_name} missing 'metadata' field")
    
    if "samples" not in data and "queries" not in data and "interactions" not in data:
        raise ValueError(f"Dataset {dataset_name} missing data field (samples/queries/interactions)")
    
    return data


def validate_classification_dataset(data: Dict[str, Any]) -> None:
    """
    Validate classification test dataset schema.
    
    Args:
        data: Dataset dictionary to validate
        
    Raises:
        ValueError: If dataset has invalid format or missing fields
    """
    required_fields = ["metadata", "samples", "class_distribution"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(data["samples"], list) or len(data["samples"]) == 0:
        raise ValueError("Dataset must contain at least one sample")
    
    for i, sample in enumerate(data["samples"]):
        required_sample_fields = ["text", "true_labels", "taxonomy_node_ids"]
        for field in required_sample_fields:
            if field not in sample:
                raise ValueError(f"Sample {i} missing required field: {field}")


def validate_recommendation_dataset(data: Dict[str, Any]) -> None:
    """
    Validate recommendation test dataset schema.
    
    Args:
        data: Dataset dictionary to validate
        
    Raises:
        ValueError: If dataset has invalid format or missing fields
    """
    required_fields = ["metadata", "interactions", "held_out_test"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(data["interactions"], list) or len(data["interactions"]) == 0:
        raise ValueError("Dataset must contain at least one interaction")
    
    for i, interaction in enumerate(data["interactions"]):
        required_fields = ["user_id", "resource_id", "interaction_type", "strength"]
        for field in required_fields:
            if field not in interaction:
                raise ValueError(f"Interaction {i} missing required field: {field}")


def validate_search_dataset(data: Dict[str, Any]) -> None:
    """
    Validate search relevance test dataset schema.
    
    Args:
        data: Dataset dictionary to validate
        
    Raises:
        ValueError: If dataset has invalid format or missing fields
    """
    required_fields = ["metadata", "queries"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(data["queries"], list) or len(data["queries"]) == 0:
        raise ValueError("Dataset must contain at least one query")
    
    for i, query in enumerate(data["queries"]):
        required_fields = ["query_id", "query_text", "relevance_judgments"]
        for field in required_fields:
            if field not in query:
                raise ValueError(f"Query {i} missing required field: {field}")


def validate_summarization_dataset(data: Dict[str, Any]) -> None:
    """
    Validate summarization test dataset schema.
    
    Args:
        data: Dataset dictionary to validate
        
    Raises:
        ValueError: If dataset has invalid format or missing fields
    """
    required_fields = ["metadata", "samples"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(data["samples"], list) or len(data["samples"]) == 0:
        raise ValueError("Dataset must contain at least one sample")
    
    for i, sample in enumerate(data["samples"]):
        required_fields = ["original_text", "reference_summary"]
        for field in required_fields:
            if field not in sample:
                raise ValueError(f"Sample {i} missing required field: {field}")
