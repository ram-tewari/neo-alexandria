"""
Hyperparameter search module using Optuna for automated model tuning.

This module provides the HyperparameterSearch class for automated hyperparameter
optimization using Optuna's TPE sampler and pruning strategies.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler

from train_classification import ClassificationTrainer


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HyperparameterSearch:
    """
    Automated hyperparameter search using Optuna.

    This class implements hyperparameter optimization for classification models
    using Optuna's Tree-structured Parzen Estimator (TPE) sampler and median
    pruning for early stopping of unpromising trials.

    Attributes:
        data_dir (Path): Directory containing train/val datasets
        output_dir (Path): Directory for saving search results
        train_samples (List[Dict]): Training samples
        val_samples (List[Dict]): Validation samples
    """

    def __init__(
        self, data_dir: str, output_dir: str = "models/classification/hp_search"
    ):
        """
        Initialize HyperparameterSearch with data and output directories.

        Args:
            data_dir: Directory containing train.json and val.json files
            output_dir: Directory for saving search results and best hyperparameters
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)

        # Create output directory for search results
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("HyperparameterSearch initialized")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Output directory: {self.output_dir}")

        # Load train/val datasets from data_dir
        logger.info("Loading datasets...")
        train_file = self.data_dir / "train.json"
        val_file = self.data_dir / "val.json"

        if not train_file.exists():
            raise FileNotFoundError(f"Training file not found: {train_file}")
        if not val_file.exists():
            raise FileNotFoundError(f"Validation file not found: {val_file}")

        # Load JSON files
        with open(train_file, "r", encoding="utf-8") as f:
            train_data = json.load(f)
        with open(val_file, "r", encoding="utf-8") as f:
            val_data = json.load(f)

        # Extract samples (handle both direct list and dict with 'samples' key)
        self.train_samples = (
            train_data
            if isinstance(train_data, list)
            else train_data.get("samples", [])
        )
        self.val_samples = (
            val_data if isinstance(val_data, list) else val_data.get("samples", [])
        )

        logger.info(f"Loaded {len(self.train_samples)} training samples")
        logger.info(f"Loaded {len(self.val_samples)} validation samples")

        # Set up logging for search progress
        logger.info("Ready to start hyperparameter search")

    def objective(self, trial: optuna.Trial) -> float:
        """
        Objective function for Optuna optimization.

        This function defines the hyperparameter search space and trains a model
        with the sampled hyperparameters. It returns the validation accuracy as
        the objective value to maximize.

        Args:
            trial: Optuna trial object for sampling hyperparameters

        Returns:
            Validation accuracy (float) to be maximized
        """
        # Define search space for hyperparameters

        # Learning rate: log-uniform distribution between 1e-5 and 5e-5
        learning_rate = trial.suggest_float("learning_rate", 1e-5, 5e-5, log=True)

        # Batch size: categorical choice from [8, 16, 32]
        batch_size = trial.suggest_categorical("batch_size", [8, 16, 32])

        # Warmup steps: categorical choice from [100, 500, 1000]
        warmup_steps = trial.suggest_categorical("warmup_steps", [100, 500, 1000])

        logger.info(f"\nTrial {trial.number}:")
        logger.info(f"  learning_rate: {learning_rate:.2e}")
        logger.info(f"  batch_size: {batch_size}")
        logger.info(f"  warmup_steps: {warmup_steps}")

        # Create trial-specific output directory
        trial_output_dir = self.output_dir / f"trial_{trial.number}"

        # Initialize ClassificationTrainer with trial hyperparameters
        trainer = ClassificationTrainer(
            model_name="distilbert-base-uncased", output_dir=str(trial_output_dir)
        )

        # Load datasets and build label mapping
        trainer.load_datasets(str(self.data_dir))

        try:
            # Train model for 3 epochs with sampled hyperparameters
            train_metrics = trainer.train(
                train_samples=self.train_samples,
                val_samples=self.val_samples,
                epochs=3,
                batch_size=batch_size,
                learning_rate=learning_rate,
                warmup_steps=warmup_steps,
            )

            # Extract validation accuracy as objective value
            val_accuracy = train_metrics["eval_accuracy"]

            logger.info(f"Trial {trial.number} completed:")
            logger.info(f"  Validation accuracy: {val_accuracy:.4f}")

            # Return validation accuracy to maximize
            return val_accuracy

        except Exception as e:
            logger.error(f"Trial {trial.number} failed: {e}")
            # Return a low value for failed trials
            return 0.0

    def search(
        self, n_trials: int = 20, timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run hyperparameter search with Optuna and return best parameters.

        This method creates an Optuna study with TPE sampler and MedianPruner,
        runs the optimization, logs trial results, and saves the best hyperparameters.

        Args:
            n_trials: Number of trials to run (default: 20)
            timeout: Maximum time in seconds for the search (default: None, no timeout)

        Returns:
            Dictionary containing:
                - best_params: Best hyperparameters found
                - best_value: Best validation accuracy achieved
                - n_trials: Number of trials completed
                - study: Optuna study object for further analysis
        """
        logger.info("=" * 60)
        logger.info("Starting Hyperparameter Search")
        logger.info("=" * 60)
        logger.info(f"Number of trials: {n_trials}")
        if timeout:
            logger.info(f"Timeout: {timeout} seconds ({timeout / 3600:.1f} hours)")
        logger.info("Optimization direction: maximize (validation accuracy)")
        logger.info("=" * 60)

        # Create Optuna study with TPE sampler
        sampler = TPESampler(seed=42)

        # Add MedianPruner for early stopping of unpromising trials
        pruner = MedianPruner(
            n_startup_trials=5,  # Don't prune first 5 trials
            n_warmup_steps=10,  # Wait 10 steps before pruning
            interval_steps=1,  # Check every step
        )

        # Set optimization direction to maximize (validation accuracy)
        study = optuna.create_study(
            study_name="arxiv_classification_hp_search",
            direction="maximize",
            sampler=sampler,
            pruner=pruner,
        )

        logger.info("Optuna study created with TPE sampler and MedianPruner")

        # Run study.optimize() with objective function
        logger.info("\nStarting optimization...")
        study.optimize(
            self.objective, n_trials=n_trials, timeout=timeout, show_progress_bar=True
        )

        logger.info("\n" + "=" * 60)
        logger.info("Hyperparameter Search Complete!")
        logger.info("=" * 60)

        # Get best trial
        best_trial = study.best_trial

        # Log trial results (hyperparameters and metrics)
        logger.info(f"\nBest trial: {best_trial.number}")
        logger.info(f"Best validation accuracy: {best_trial.value:.4f}")
        logger.info("\nBest hyperparameters:")
        for param_name, param_value in best_trial.params.items():
            if param_name == "learning_rate":
                logger.info(f"  {param_name}: {param_value:.2e}")
            else:
                logger.info(f"  {param_name}: {param_value}")

        # Log all trials summary
        logger.info(f"\nTotal trials completed: {len(study.trials)}")
        logger.info(
            f"Pruned trials: {len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED])}"
        )
        logger.info(
            f"Failed trials: {len([t for t in study.trials if t.state == optuna.trial.TrialState.FAIL])}"
        )
        logger.info(
            f"Completed trials: {len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE])}"
        )

        # Prepare best hyperparameters dictionary
        best_params = best_trial.params
        best_value = best_trial.value

        # Save best hyperparameters to JSON file
        results = {
            "best_params": best_params,
            "best_value": float(best_value),
            "n_trials": len(study.trials),
            "study_name": study.study_name,
            "optimization_direction": "maximize",
            "metric": "validation_accuracy",
        }

        results_file = self.output_dir / "best_hyperparameters.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        logger.info(f"\nBest hyperparameters saved to {results_file}")

        # Save study statistics
        study_stats = {
            "total_trials": len(study.trials),
            "completed_trials": len(
                [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
            ),
            "pruned_trials": len(
                [t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED]
            ),
            "failed_trials": len(
                [t for t in study.trials if t.state == optuna.trial.TrialState.FAIL]
            ),
            "best_trial_number": best_trial.number,
            "best_value": float(best_value),
            "trials": [
                {
                    "number": t.number,
                    "value": float(t.value) if t.value is not None else None,
                    "params": t.params,
                    "state": str(t.state),
                }
                for t in study.trials
            ],
        }

        stats_file = self.output_dir / "study_statistics.json"
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(study_stats, f, indent=2)

        logger.info(f"Study statistics saved to {stats_file}")
        logger.info("=" * 60)

        # Return best hyperparameters and best value
        return {
            "best_params": best_params,
            "best_value": best_value,
            "n_trials": len(study.trials),
            "study": study,
        }

    def visualize_results(self, study: optuna.Study) -> None:
        """
        Generate visualization plots of hyperparameter search results.

        This method creates several plots to visualize the optimization process:
        - Optimization history plot (trial values over time)
        - Parameter importance plot (which parameters matter most)
        - Parallel coordinate plot (relationship between parameters and objective)

        Args:
            study: Optuna study object containing trial results
        """
        logger.info("\nGenerating visualization plots...")

        try:
            import optuna.visualization as vis
            import plotly.io as pio

            # Generate optimization history plot
            logger.info("Creating optimization history plot...")
            fig_history = vis.plot_optimization_history(study)
            history_file = self.output_dir / "optimization_history.html"
            pio.write_html(fig_history, str(history_file))
            logger.info(f"  Saved to {history_file}")

            # Generate parameter importance plot
            logger.info("Creating parameter importance plot...")
            try:
                fig_importance = vis.plot_param_importances(study)
                importance_file = self.output_dir / "parameter_importance.html"
                pio.write_html(fig_importance, str(importance_file))
                logger.info(f"  Saved to {importance_file}")
            except Exception as e:
                logger.warning(f"  Could not create parameter importance plot: {e}")

            # Generate parallel coordinate plot
            logger.info("Creating parallel coordinate plot...")
            fig_parallel = vis.plot_parallel_coordinate(study)
            parallel_file = self.output_dir / "parallel_coordinate.html"
            pio.write_html(fig_parallel, str(parallel_file))
            logger.info(f"  Saved to {parallel_file}")

            logger.info("Visualization plots generated successfully!")

        except ImportError as e:
            logger.warning(f"Could not generate plots: {e}")
            logger.warning("Install plotly for visualization: pip install plotly")
        except Exception as e:
            logger.error(f"Error generating plots: {e}")


def main():
    """
    Main function for command-line usage.

    Example usage:
        python hyperparameter_search.py --data-dir backend/data/splits/arxiv_classification --n-trials 20
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Hyperparameter search for arXiv classification"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="backend/data/splits/arxiv_classification",
        help="Directory containing train/val splits",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="backend/models/classification/hp_search",
        help="Output directory for search results",
    )
    parser.add_argument(
        "--n-trials", type=int, default=20, help="Number of trials to run"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Maximum time in seconds for the search",
    )

    args = parser.parse_args()

    # Initialize hyperparameter search
    hp_search = HyperparameterSearch(data_dir=args.data_dir, output_dir=args.output_dir)

    # Run search
    results = hp_search.search(n_trials=args.n_trials, timeout=args.timeout)

    # Visualize results
    hp_search.visualize_results(results["study"])

    logger.info("\n" + "=" * 60)
    logger.info("Hyperparameter Search Complete!")
    logger.info("=" * 60)
    logger.info(f"Best validation accuracy: {results['best_value']:.4f}")
    logger.info("\nBest hyperparameters:")
    for param_name, param_value in results["best_params"].items():
        if param_name == "learning_rate":
            logger.info(f"  {param_name}: {param_value:.2e}")
        else:
            logger.info(f"  {param_name}: {param_value}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
