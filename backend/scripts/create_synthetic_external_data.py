"""
Create synthetic external dataset for pre-training demonstration.

This script generates a larger synthetic dataset that simulates what you'd get
from external sources like arXiv. It's useful for testing the pre-train + fine-tune
workflow without downloading large external datasets.

For production use, replace this with actual external data using load_external_data.py

Usage:
    python backend/scripts/create_synthetic_external_data.py \
        --output data/processed/synthetic_external.json \
        --num-samples 5000
"""

import argparse
import json
import random
from pathlib import Path
from typing import List, Tuple

# Template texts for each category (simulating arXiv-style abstracts)
CATEGORY_TEMPLATES = {
    "ml-node-1": [
        "This paper presents a novel {method} for {task}. We demonstrate {improvement} on {dataset}. Our approach achieves state-of-the-art results.",
        "We propose {method} to address {problem}. Experiments show {result}. The method is evaluated on {dataset} with {metric}.",
        "A new {method} is introduced for {task}. We compare against {baseline} and show {improvement}. Results indicate {conclusion}.",
        "This work explores {method} in the context of {task}. We achieve {result} on {dataset}. Our findings suggest {conclusion}.",
        "We present {method}, a {approach} for {task}. Evaluation on {dataset} demonstrates {improvement}. The method outperforms {baseline}.",
    ],
    "nlp-node-1": [
        "This paper addresses {task} using {method}. We evaluate on {dataset} and achieve {result}. Our approach handles {challenge}.",
        "We propose {method} for {task} in natural language processing. Experiments on {dataset} show {improvement}. The model captures {feature}.",
        "A novel {method} is presented for {task}. We demonstrate {result} on {dataset}. The approach addresses {problem}.",
        "This work introduces {method} to improve {task}. Results on {dataset} indicate {improvement}. We analyze {aspect}.",
        "We develop {method} for {task} with focus on {feature}. Evaluation shows {result}. The method achieves {metric}.",
    ],
    "cv-node-1": [
        "This paper presents {method} for {task} in computer vision. We evaluate on {dataset} and achieve {result}. The approach handles {challenge}.",
        "We propose {method} to address {problem} in visual recognition. Experiments show {improvement} on {dataset}. Our model captures {feature}.",
        "A new {method} is introduced for {task}. We demonstrate {result} on {dataset} with {metric}. The approach outperforms {baseline}.",
        "This work explores {method} for {task}. Evaluation on {dataset} shows {improvement}. We analyze {aspect} of the model.",
        "We present {method}, a {approach} for {task}. Results on {dataset} demonstrate {result}. The method addresses {problem}.",
    ],
    "db-node-1": [
        "This paper addresses {problem} in database systems using {method}. We evaluate on {dataset} and achieve {result}. The approach improves {metric}.",
        "We propose {method} for {task} in distributed databases. Experiments show {improvement}. The system handles {challenge}.",
        "A novel {method} is presented for {task}. We demonstrate {result} on {dataset}. The approach optimizes {aspect}.",
        "This work introduces {method} to improve {task}. Results indicate {improvement}. We analyze {feature} of the system.",
        "We develop {method} for {task} with focus on {aspect}. Evaluation shows {result}. The system achieves {metric}.",
    ],
    "sec-node-1": [
        "This paper presents {method} for {task} in cybersecurity. We evaluate on {dataset} and achieve {result}. The approach detects {threat}.",
        "We propose {method} to address {problem} in security. Experiments show {improvement}. Our system prevents {attack}.",
        "A new {method} is introduced for {task}. We demonstrate {result} with {metric}. The approach mitigates {vulnerability}.",
        "This work explores {method} for {task}. Evaluation shows {improvement}. We analyze {aspect} of security.",
        "We present {method}, a {approach} for {task}. Results demonstrate {result}. The method protects against {threat}.",
    ],
    "cloud-node-1": [
        "This paper addresses {problem} in cloud computing using {method}. We evaluate on {dataset} and achieve {result}. The approach scales to {scale}.",
        "We propose {method} for {task} in distributed systems. Experiments show {improvement}. The system handles {workload}.",
        "A novel {method} is presented for {task}. We demonstrate {result} on {dataset}. The approach optimizes {resource}.",
        "This work introduces {method} to improve {task}. Results indicate {improvement}. We analyze {aspect} of the system.",
        "We develop {method} for {task} with focus on {feature}. Evaluation shows {result}. The system achieves {metric}.",
    ],
    "qc-node-1": [
        "This paper presents {method} for {task} in quantum computing. We evaluate on {dataset} and achieve {result}. The approach implements {algorithm}.",
        "We propose {method} to address {problem} in quantum systems. Experiments show {improvement}. Our method uses {technique}.",
        "A new {method} is introduced for {task}. We demonstrate {result} with {metric}. The approach leverages {feature}.",
        "This work explores {method} for {task}. Evaluation shows {improvement}. We analyze {aspect} of quantum circuits.",
        "We present {method}, a {approach} for {task}. Results demonstrate {result}. The method achieves {metric}.",
    ],
    "algo-node-1": [
        "This paper addresses {problem} using {method}. We evaluate on {dataset} and achieve {result}. The algorithm has {complexity}.",
        "We propose {method} for {task}. Experiments show {improvement}. Our approach achieves {metric} time complexity.",
        "A novel {method} is presented for {task}. We demonstrate {result} on {dataset}. The algorithm optimizes {aspect}.",
        "This work introduces {method} to solve {problem}. Results indicate {improvement}. We analyze {feature} of the algorithm.",
        "We develop {method} for {task} with focus on {aspect}. Evaluation shows {result}. The algorithm achieves {metric}.",
    ],
    "bc-node-1": [
        "This paper presents {method} for {task} in blockchain systems. We evaluate on {dataset} and achieve {result}. The approach ensures {property}.",
        "We propose {method} to address {problem} in distributed ledgers. Experiments show {improvement}. Our protocol achieves {metric}.",
        "A new {method} is introduced for {task}. We demonstrate {result} with {metric}. The approach provides {guarantee}.",
        "This work explores {method} for {task}. Evaluation shows {improvement}. We analyze {aspect} of consensus.",
        "We present {method}, a {approach} for {task}. Results demonstrate {result}. The protocol ensures {property}.",
    ],
    "web-node-1": [
        "This paper addresses {problem} in web development using {method}. We evaluate on {dataset} and achieve {result}. The approach improves {metric}.",
        "We propose {method} for {task} in web applications. Experiments show {improvement}. Our framework handles {feature}.",
        "A novel {method} is presented for {task}. We demonstrate {result} on {dataset}. The approach optimizes {aspect}.",
        "This work introduces {method} to improve {task}. Results indicate {improvement}. We analyze {feature} of the system.",
        "We develop {method} for {task} with focus on {aspect}. Evaluation shows {result}. The framework achieves {metric}.",
    ],
    "dl-node-1": [
        "This paper presents {method} for {task} using deep learning. We evaluate on {dataset} and achieve {result}. The network architecture uses {layer}.",
        "We propose {method} to address {problem} with neural networks. Experiments show {improvement}. Our model has {parameter} parameters.",
        "A new {method} is introduced for {task}. We demonstrate {result} with {metric}. The architecture includes {component}.",
        "This work explores {method} for {task}. Evaluation shows {improvement}. We analyze {aspect} of the network.",
        "We present {method}, a {approach} for {task}. Results demonstrate {result}. The model achieves {metric}.",
    ],
}

# Vocabulary for filling templates
VOCABULARY = {
    "method": ["algorithm", "technique", "approach", "framework", "model", "system", "architecture"],
    "task": ["classification", "prediction", "optimization", "detection", "recognition", "generation"],
    "problem": ["scalability", "efficiency", "accuracy", "latency", "throughput", "robustness"],
    "improvement": ["significant improvements", "better performance", "enhanced accuracy", "reduced latency"],
    "result": ["promising results", "competitive performance", "state-of-the-art accuracy", "improved metrics"],
    "dataset": ["benchmark datasets", "standard benchmarks", "real-world data", "synthetic datasets"],
    "metric": ["high accuracy", "low error rate", "fast inference", "efficient computation"],
    "baseline": ["previous methods", "existing approaches", "traditional techniques", "baseline models"],
    "conclusion": ["practical applications", "future research directions", "theoretical insights"],
    "challenge": ["complex scenarios", "edge cases", "noisy data", "large-scale problems"],
    "feature": ["important patterns", "key characteristics", "semantic information", "structural properties"],
    "aspect": ["performance characteristics", "computational efficiency", "model behavior", "system properties"],
    "approach": ["data-driven method", "learning-based technique", "optimization framework"],
    "threat": ["malicious attacks", "security vulnerabilities", "unauthorized access"],
    "attack": ["injection attacks", "denial of service", "data breaches"],
    "vulnerability": ["security flaws", "system weaknesses", "potential exploits"],
    "scale": ["thousands of nodes", "millions of requests", "petabytes of data"],
    "workload": ["concurrent requests", "heavy traffic", "diverse queries"],
    "resource": ["CPU utilization", "memory usage", "network bandwidth"],
    "algorithm": ["quantum gates", "entanglement operations", "superposition states"],
    "technique": ["quantum annealing", "variational methods", "error correction"],
    "complexity": ["O(n log n) complexity", "polynomial time", "linear complexity"],
    "property": ["consistency", "fault tolerance", "Byzantine resistance"],
    "guarantee": ["security guarantees", "correctness proofs", "liveness properties"],
    "layer": ["convolutional layers", "attention mechanisms", "residual connections"],
    "parameter": ["millions of", "billions of", "trainable"],
    "component": ["encoder-decoder", "multi-head attention", "skip connections"],
}


def generate_text(template: str) -> str:
    """Generate text by filling template with random vocabulary."""
    text = template
    for key, values in VOCABULARY.items():
        placeholder = "{" + key + "}"
        if placeholder in text:
            text = text.replace(placeholder, random.choice(values))
    return text


def generate_synthetic_data(num_samples: int) -> List[Tuple[str, List[str]]]:
    """
    Generate synthetic external dataset.
    
    Args:
        num_samples: Number of samples to generate
    
    Returns:
        List of (text, [taxonomy_node_ids]) tuples
    """
    data = []
    categories = list(CATEGORY_TEMPLATES.keys())
    
    for i in range(num_samples):
        # Randomly select category (with some bias towards ML/DL/NLP/CV)
        weights = [2 if cat in ["ml-node-1", "dl-node-1", "nlp-node-1", "cv-node-1"] else 1 
                   for cat in categories]
        category = random.choices(categories, weights=weights)[0]
        
        # Select random template
        template = random.choice(CATEGORY_TEMPLATES[category])
        
        # Generate text
        text = generate_text(template)
        
        # Add some variation in length
        if random.random() < 0.3:
            # Add another sentence
            template2 = random.choice(CATEGORY_TEMPLATES[category])
            text += " " + generate_text(template2)
        
        # Occasionally add multi-label (10% chance)
        taxonomy_ids = [category]
        if random.random() < 0.1:
            # Add related category
            related = {
                "ml-node-1": ["dl-node-1", "algo-node-1"],
                "dl-node-1": ["ml-node-1", "cv-node-1", "nlp-node-1"],
                "nlp-node-1": ["ml-node-1", "dl-node-1"],
                "cv-node-1": ["ml-node-1", "dl-node-1"],
                "db-node-1": ["algo-node-1", "cloud-node-1"],
                "cloud-node-1": ["db-node-1", "web-node-1"],
                "algo-node-1": ["ml-node-1"],
            }
            if category in related:
                taxonomy_ids.append(random.choice(related[category]))
        
        data.append((text, taxonomy_ids))
    
    return data


def main():
    parser = argparse.ArgumentParser(
        description='Create synthetic external dataset for pre-training'
    )
    
    parser.add_argument(
        '--output',
        required=True,
        help='Output path for synthetic data'
    )
    
    parser.add_argument(
        '--num-samples',
        type=int,
        default=5000,
        help='Number of samples to generate (default: 5000)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    print(f"Generating {args.num_samples} synthetic samples...")
    data = generate_synthetic_data(args.num_samples)
    
    # Convert to JSON format
    json_data = []
    for text, taxonomy_ids in data:
        json_data.append({
            "text": text,
            "taxonomy_node_ids": taxonomy_ids
        })
    
    # Save to file
    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(json_data)} samples to {output_file}")
    
    # Print statistics
    from collections import Counter
    label_counts = Counter()
    for item in json_data:
        for label in item['taxonomy_node_ids']:
            label_counts[label] += 1
    
    print("\nLabel distribution:")
    for label, count in label_counts.most_common():
        print(f"  {label}: {count} samples")
    
    multi_label = sum(1 for item in json_data if len(item['taxonomy_node_ids']) > 1)
    print(f"\nMulti-label samples: {multi_label} ({multi_label/len(json_data)*100:.1f}%)")


if __name__ == "__main__":
    main()
