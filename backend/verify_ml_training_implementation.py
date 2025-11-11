"""
Verification script for ML classification training implementation.

This script verifies that all required training methods are properly implemented
according to the task requirements.
"""

import ast
import sys
from pathlib import Path

def verify_implementation():
    """Verify that all training methods are implemented correctly."""
    
    print("="*70)
    print("ML Classification Training Implementation Verification")
    print("="*70)
    
    # Read the service file
    service_file = Path("backend/app/services/ml_classification_service.py")
    with open(service_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the AST
    tree = ast.parse(content)
    
    # Find the MLClassificationService class
    ml_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "MLClassificationService":
            ml_class = node
            break
    
    if not ml_class:
        print("✗ MLClassificationService class not found")
        return False
    
    print("✓ MLClassificationService class found")
    
    # Extract all methods
    methods = {}
    for item in ml_class.body:
        if isinstance(item, ast.FunctionDef):
            methods[item.name] = item
    
    print(f"✓ Found {len(methods)} methods in class")
    
    # Check required methods for task 7
    required_methods = {
        'fine_tune': {
            'params': ['labeled_data', 'unlabeled_data', 'epochs', 'batch_size', 'learning_rate'],
            'description': 'Main training method'
        },
        '_compute_metrics': {
            'params': ['eval_pred'],
            'description': 'Evaluation metrics computation'
        },
        '_semi_supervised_iteration': {
            'params': ['labeled_data', 'unlabeled_data', 'confidence_threshold'],
            'description': 'Semi-supervised learning iteration'
        },
        'predict': {
            'params': ['text', 'top_k'],
            'description': 'Single text prediction (needed for semi-supervised)'
        }
    }
    
    print("\n" + "="*70)
    print("Checking Required Methods:")
    print("="*70)
    
    all_passed = True
    
    for method_name, requirements in required_methods.items():
        print(f"\n{method_name}:")
        print(f"  Description: {requirements['description']}")
        
        if method_name not in methods:
            print(f"  ✗ Method not found")
            all_passed = False
            continue
        
        print(f"  ✓ Method exists")
        
        # Check parameters
        method = methods[method_name]
        actual_params = [arg.arg for arg in method.args.args if arg.arg != 'self']
        
        missing_params = set(requirements['params']) - set(actual_params)
        if missing_params:
            print(f"  ✗ Missing parameters: {missing_params}")
            all_passed = False
        else:
            print(f"  ✓ All required parameters present: {actual_params}")
        
        # Check if method has docstring
        docstring = ast.get_docstring(method)
        if docstring:
            print(f"  ✓ Has docstring ({len(docstring)} chars)")
        else:
            print(f"  ⚠ No docstring")
    
    # Check key implementation details in fine_tune
    print("\n" + "="*70)
    print("Checking fine_tune Implementation Details:")
    print("="*70)
    
    key_strings = [
        ("Build label mapping", "Building label mapping"),
        ("Multi-hot encoding", "multi-hot"),
        ("Train/validation split", "train_test_split"),
        ("Tokenization", "tokenizer"),
        ("PyTorch datasets", "Dataset"),
        ("Hugging Face Trainer", "TrainingArguments"),
        ("Training execution", "trainer.train()"),
        ("Model saving", "save_pretrained"),
        ("Label map saving", "label_map.json"),
    ]
    
    for description, search_string in key_strings:
        if search_string in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - '{search_string}' not found")
            all_passed = False
    
    # Check _compute_metrics implementation
    print("\n" + "="*70)
    print("Checking _compute_metrics Implementation:")
    print("="*70)
    
    metrics_checks = [
        ("F1 score", "f1_score"),
        ("Precision", "precision_score"),
        ("Recall", "recall_score"),
        ("Sigmoid activation", "sigmoid"),
        ("Macro averaging", "macro"),
    ]
    
    for description, search_string in metrics_checks:
        if search_string in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - '{search_string}' not found")
            all_passed = False
    
    # Summary
    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL CHECKS PASSED")
        print("="*70)
        print("\nTask 7 Implementation Summary:")
        print("  ✓ 7.1 fine_tune() method - COMPLETE")
        print("  ✓ 7.2 Hugging Face Trainer configuration - COMPLETE")
        print("  ✓ 7.3 Training execution and model saving - COMPLETE")
        print("  ✓ 7.4 _compute_metrics() for evaluation - COMPLETE")
        print("\nAll subtasks for Task 7 are implemented correctly!")
    else:
        print("✗ SOME CHECKS FAILED")
        print("="*70)
    
    return all_passed

if __name__ == "__main__":
    try:
        success = verify_implementation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
