"""
Verification script for ML dependencies installation.
This script checks that all required ML packages are installed and verifies CUDA availability.
"""

import sys


def verify_ml_dependencies():
    """Verify that all ML dependencies are installed and check CUDA availability."""
    print("=" * 60)
    print("ML Dependencies Verification")
    print("=" * 60)

    # Check transformers
    try:
        import transformers

        print(f"✓ transformers: {transformers.__version__}")
    except ImportError as e:
        print(f"✗ transformers: NOT INSTALLED - {e}")
        return False

    # Check torch
    try:
        import torch

        print(f"✓ torch: {torch.__version__}")
    except ImportError as e:
        print(f"✗ torch: NOT INSTALLED - {e}")
        return False

    # Check scikit-learn
    try:
        import sklearn

        print(f"✓ scikit-learn: {sklearn.__version__}")
    except ImportError as e:
        print(f"✗ scikit-learn: NOT INSTALLED - {e}")
        return False

    print("\n" + "=" * 60)
    print("CUDA Availability Check")
    print("=" * 60)

    # Check CUDA availability
    cuda_available = torch.cuda.is_available()
    print(f"CUDA available: {cuda_available}")

    if cuda_available:
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
        print("\n✓ GPU acceleration is available for ML training and inference")
    else:
        print("CUDA version: N/A")
        print("Number of GPUs: 0")
        print("\n⚠ GPU acceleration is NOT available")
        print("  The system will use CPU for ML operations")
        print("  This is acceptable but will be slower than GPU")
        print("  To enable GPU acceleration:")
        print("    1. Install NVIDIA CUDA Toolkit")
        print("    2. Install PyTorch with CUDA support:")
        print(
            "       pip install torch --index-url https://download.pytorch.org/whl/cu118"
        )

    print("\n" + "=" * 60)
    print("Additional ML Package Checks")
    print("=" * 60)

    # Check additional dependencies
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        print("✓ Hugging Face model classes available")
    except ImportError as e:
        print(f"✗ Hugging Face model classes: {e}")
        return False

    try:
        from sklearn.metrics import f1_score, precision_score, recall_score

        print("✓ scikit-learn metrics available")
    except ImportError as e:
        print(f"✗ scikit-learn metrics: {e}")
        return False

    try:
        from sklearn.model_selection import train_test_split

        print("✓ scikit-learn train_test_split available")
    except ImportError as e:
        print(f"✗ scikit-learn train_test_split: {e}")
        return False

    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    print("✓ All required ML dependencies are installed")
    print("✓ System is ready for ML classification tasks")
    if not cuda_available:
        print("⚠ GPU acceleration not available (CPU will be used)")
    else:
        print("✓ GPU acceleration is available")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = verify_ml_dependencies()
    sys.exit(0 if success else 1)
