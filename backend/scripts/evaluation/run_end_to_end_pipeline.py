"""
End-to-end pipeline validation script.

This script runs the complete ML training pipeline from data collection to deployment:
1. Collect 10,000 arXiv papers
2. Preprocess dataset
3. Create train/val/test splits
4. Train classification model
5. Evaluate on test set
6. Create model version
7. Deploy to staging
8. Run validation tests

Requirements: 1.7, 2.9, 3.5, 4.11, 4.12
"""

import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from scripts.dataset_acquisition.arxiv_collector import ArxivCollector
    from scripts.dataset_acquisition.dataset_preprocessor import DatasetPreprocessor
    from scripts.training.train_classification import ClassificationTrainer
    from scripts.deployment.model_versioning import ModelVersioning
    from scripts.deployment.validate import validate_deployment
except ImportError as e:
    logger.warning(f"Some imports failed: {e}")
    logger.warning("This is expected if running verification only")


class EndToEndPipeline:
    """Orchestrates the complete ML training pipeline."""
    
    def __init__(self, output_dir: str = "data/e2e_validation"):
        """
        Initialize the end-to-end pipeline.
        
        Args:
            output_dir: Directory for pipeline outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "pipeline_start": datetime.now().isoformat(),
            "steps": {},
            "timings": {},
            "metrics": {}
        }
        
        logger.info(f"Initialized end-to-end pipeline with output dir: {output_dir}")
    
    def run_step(self, step_name: str, step_func, *args, **kwargs) -> Any:
        """
        Run a pipeline step with timing and error handling.
        
        Args:
            step_name: Name of the step
            step_func: Function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result from the step function
        """
        logger.info(f"Starting step: {step_name}")
        start_time = time.time()
        
        try:
            result = step_func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            self.results["steps"][step_name] = "SUCCESS"
            self.results["timings"][step_name] = elapsed
            
            logger.info(f"Completed step: {step_name} in {elapsed:.2f}s")
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.results["steps"][step_name] = f"FAILED: {str(e)}"
            self.results["timings"][step_name] = elapsed
            
            logger.error(f"Failed step: {step_name} after {elapsed:.2f}s - {str(e)}")
            raise
    
    def step1_collect_data(self, num_papers: int = 10000) -> Path:
        """
        Step 1: Collect arXiv papers.
        
        Args:
            num_papers: Number of papers to collect
            
        Returns:
            Path to collected dataset
        """
        def collect():
            collector = ArxivCollector(output_dir=str(self.output_dir / "raw"))
            output_file = self.output_dir / "raw" / "arxiv_classification.json"
            
            logger.info(f"Collecting {num_papers} arXiv papers...")
            collector.create_classification_dataset(
                num_papers=num_papers,
                output_file=str(output_file)
            )
            
            # Load and verify
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            self.results["metrics"]["collected_papers"] = len(data.get("samples", []))
            self.results["metrics"]["categories"] = data.get("metadata", {}).get("num_categories", 0)
            
            logger.info(f"Collected {self.results['metrics']['collected_papers']} papers")
            return output_file
        
        return self.run_step("1_collect_data", collect)
    
    def step2_preprocess_data(self, input_file: Path) -> Path:
        """
        Step 2: Preprocess dataset.
        
        Args:
            input_file: Path to raw dataset
            
        Returns:
            Path to preprocessed dataset
        """
        def preprocess():
            preprocessor = DatasetPreprocessor()
            output_file = self.output_dir / "processed" / "arxiv_classification_clean.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info("Preprocessing dataset...")
            result = preprocessor.preprocess_dataset(
                input_file=str(input_file),
                output_file=str(output_file),
                min_words=50
            )
            
            self.results["metrics"]["preprocessed_samples"] = result.get("num_samples", 0)
            self.results["metrics"]["removed_samples"] = result.get("removed_samples", 0)
            
            logger.info(f"Preprocessed {self.results['metrics']['preprocessed_samples']} samples")
            return output_file
        
        return self.run_step("2_preprocess_data", preprocess)
    
    def step3_create_splits(self, input_file: Path) -> Path:
        """
        Step 3: Create train/val/test splits.
        
        Args:
            input_file: Path to preprocessed dataset
            
        Returns:
            Path to splits directory
        """
        def create_splits():
            preprocessor = DatasetPreprocessor()
            splits_dir = self.output_dir / "splits"
            splits_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("Creating train/val/test splits...")
            train, val, test = preprocessor.create_train_val_test_split(
                input_file=str(input_file),
                output_dir=str(splits_dir),
                train_ratio=0.8,
                val_ratio=0.1,
                test_ratio=0.1,
                random_seed=42
            )
            
            self.results["metrics"]["train_samples"] = len(train)
            self.results["metrics"]["val_samples"] = len(val)
            self.results["metrics"]["test_samples"] = len(test)
            
            logger.info(f"Created splits: train={len(train)}, val={len(val)}, test={len(test)}")
            return splits_dir
        
        return self.run_step("3_create_splits", create_splits)
    
    def step4_train_model(self, splits_dir: Path) -> Path:
        """
        Step 4: Train classification model.
        
        Args:
            splits_dir: Path to splits directory
            
        Returns:
            Path to trained model
        """
        def train():
            model_dir = self.output_dir / "model"
            model_dir.mkdir(parents=True, exist_ok=True)
            
            trainer = ClassificationTrainer(
                model_name="distilbert-base-uncased",
                output_dir=str(model_dir)
            )
            
            logger.info("Loading datasets...")
            trainer.load_datasets(str(splits_dir))
            
            logger.info("Training model...")
            train_result = trainer.train(
                train_samples=trainer.train_samples,
                val_samples=trainer.val_samples,
                epochs=3,
                batch_size=16,
                learning_rate=2e-5
            )
            
            self.results["metrics"]["train_accuracy"] = train_result.get("train_accuracy", 0)
            self.results["metrics"]["val_accuracy"] = train_result.get("val_accuracy", 0)
            
            logger.info(f"Training complete: val_accuracy={self.results['metrics']['val_accuracy']:.4f}")
            return model_dir
        
        return self.run_step("4_train_model", train)
    
    def step5_evaluate_model(self, model_dir: Path, splits_dir: Path) -> Dict[str, Any]:
        """
        Step 5: Evaluate on test set.
        
        Args:
            model_dir: Path to trained model
            splits_dir: Path to splits directory
            
        Returns:
            Evaluation metrics
        """
        def evaluate():
            trainer = ClassificationTrainer(
                model_name="distilbert-base-uncased",
                output_dir=str(model_dir)
            )
            
            # Load test data
            test_file = splits_dir / "test.json"
            with open(test_file, 'r') as f:
                test_data = json.load(f)
            test_samples = test_data.get("samples", [])
            
            logger.info("Evaluating on test set...")
            eval_result = trainer.evaluate(test_samples)
            
            self.results["metrics"]["test_accuracy"] = eval_result.get("accuracy", 0)
            self.results["metrics"]["test_f1"] = eval_result.get("macro_f1", 0)
            
            logger.info(f"Evaluation complete: test_accuracy={self.results['metrics']['test_accuracy']:.4f}")
            return eval_result
        
        return self.run_step("5_evaluate_model", evaluate)
    
    def step6_create_version(self, model_dir: Path) -> str:
        """
        Step 6: Create model version.
        
        Args:
            model_dir: Path to trained model
            
        Returns:
            Version string
        """
        def create_version():
            versioning = ModelVersioning(base_dir="models/classification")
            
            version = "v1.0.0-e2e-test"
            metadata = {
                "created_at": datetime.now().isoformat(),
                "model_name": "distilbert-base-uncased",
                "dataset": {
                    "source": "arXiv",
                    "num_samples": self.results["metrics"].get("preprocessed_samples", 0),
                    "num_categories": self.results["metrics"].get("categories", 0)
                },
                "metrics": {
                    "train_accuracy": self.results["metrics"].get("train_accuracy", 0),
                    "val_accuracy": self.results["metrics"].get("val_accuracy", 0),
                    "test_accuracy": self.results["metrics"].get("test_accuracy", 0),
                    "f1_score": self.results["metrics"].get("test_f1", 0)
                },
                "training_time": self.results["timings"].get("4_train_model", 0)
            }
            
            logger.info(f"Creating model version: {version}")
            versioning.create_version(
                model_path=str(model_dir),
                version=version,
                metadata=metadata
            )
            
            self.results["metrics"]["model_version"] = version
            logger.info(f"Created model version: {version}")
            return version
        
        return self.run_step("6_create_version", create_version)
    
    def step7_validate_deployment(self, version: str) -> Dict[str, Any]:
        """
        Step 7: Validate deployment readiness.
        
        Args:
            version: Model version string
            
        Returns:
            Validation results
        """
        def validate():
            logger.info(f"Validating deployment for version: {version}")
            
            model_path = Path("models/classification") / f"arxiv_{version}"
            validation_result = validate_deployment(str(model_path))
            
            self.results["metrics"]["model_size_mb"] = validation_result.get("model_size_mb", 0)
            self.results["metrics"]["load_time_s"] = validation_result.get("load_time_s", 0)
            self.results["metrics"]["inference_latency_ms"] = validation_result.get("inference_latency_ms", 0)
            
            logger.info(f"Validation complete: model_size={self.results['metrics']['model_size_mb']:.2f}MB")
            return validation_result
        
        return self.run_step("7_validate_deployment", validate)
    
    def save_results(self):
        """Save pipeline results to JSON file."""
        self.results["pipeline_end"] = datetime.now().isoformat()
        
        # Calculate total time
        total_time = sum(self.results["timings"].values())
        self.results["total_time_seconds"] = total_time
        self.results["total_time_hours"] = total_time / 3600
        
        # Save results
        results_file = self.output_dir / "pipeline_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Results saved to: {results_file}")
        logger.info(f"Total pipeline time: {total_time / 3600:.2f} hours")
    
    def run_full_pipeline(self, num_papers: int = 10000):
        """
        Run the complete end-to-end pipeline.
        
        Args:
            num_papers: Number of papers to collect
        """
        try:
            logger.info("=" * 80)
            logger.info("Starting End-to-End ML Training Pipeline")
            logger.info("=" * 80)
            
            # Step 1: Collect data
            raw_data = self.step1_collect_data(num_papers)
            
            # Step 2: Preprocess
            clean_data = self.step2_preprocess_data(raw_data)
            
            # Step 3: Create splits
            splits_dir = self.step3_create_splits(clean_data)
            
            # Step 4: Train model
            model_dir = self.step4_train_model(splits_dir)
            
            # Step 5: Evaluate
            self.step5_evaluate_model(model_dir, splits_dir)
            
            # Step 6: Create version
            version = self.step6_create_version(model_dir)
            
            # Step 7: Validate deployment
            self.step7_validate_deployment(version)
            
            # Save results
            self.save_results()
            
            logger.info("=" * 80)
            logger.info("End-to-End Pipeline Completed Successfully!")
            logger.info("=" * 80)
            
            # Print summary
            self.print_summary()
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            self.save_results()
            raise
    
    def print_summary(self):
        """Print a summary of pipeline results."""
        print("\n" + "=" * 80)
        print("PIPELINE SUMMARY")
        print("=" * 80)
        
        print("\nData Collection:")
        print(f"  - Papers collected: {self.results['metrics'].get('collected_papers', 0)}")
        print(f"  - Categories: {self.results['metrics'].get('categories', 0)}")
        print(f"  - Time: {self.results['timings'].get('1_collect_data', 0):.2f}s")
        
        print("\nPreprocessing:")
        print(f"  - Samples after cleaning: {self.results['metrics'].get('preprocessed_samples', 0)}")
        print(f"  - Samples removed: {self.results['metrics'].get('removed_samples', 0)}")
        print(f"  - Time: {self.results['timings'].get('2_preprocess_data', 0):.2f}s")
        
        print("\nData Splits:")
        print(f"  - Train: {self.results['metrics'].get('train_samples', 0)}")
        print(f"  - Validation: {self.results['metrics'].get('val_samples', 0)}")
        print(f"  - Test: {self.results['metrics'].get('test_samples', 0)}")
        print(f"  - Time: {self.results['timings'].get('3_create_splits', 0):.2f}s")
        
        print("\nTraining:")
        print(f"  - Train accuracy: {self.results['metrics'].get('train_accuracy', 0):.4f}")
        print(f"  - Val accuracy: {self.results['metrics'].get('val_accuracy', 0):.4f}")
        print(f"  - Time: {self.results['timings'].get('4_train_model', 0) / 3600:.2f} hours")
        
        print("\nEvaluation:")
        print(f"  - Test accuracy: {self.results['metrics'].get('test_accuracy', 0):.4f}")
        print(f"  - Test F1: {self.results['metrics'].get('test_f1', 0):.4f}")
        print(f"  - Time: {self.results['timings'].get('5_evaluate_model', 0):.2f}s")
        
        print("\nModel:")
        print(f"  - Version: {self.results['metrics'].get('model_version', 'N/A')}")
        print(f"  - Size: {self.results['metrics'].get('model_size_mb', 0):.2f} MB")
        print(f"  - Load time: {self.results['metrics'].get('load_time_s', 0):.2f}s")
        print(f"  - Inference latency: {self.results['metrics'].get('inference_latency_ms', 0):.2f}ms")
        
        print("\nTotal Pipeline Time:")
        print(f"  - {self.results.get('total_time_hours', 0):.2f} hours")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run end-to-end ML training pipeline")
    parser.add_argument(
        "--num-papers",
        type=int,
        default=10000,
        help="Number of papers to collect (default: 10000)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/e2e_validation",
        help="Output directory for pipeline results"
    )
    
    args = parser.parse_args()
    
    # Run pipeline
    pipeline = EndToEndPipeline(output_dir=args.output_dir)
    pipeline.run_full_pipeline(num_papers=args.num_papers)


if __name__ == "__main__":
    main()
