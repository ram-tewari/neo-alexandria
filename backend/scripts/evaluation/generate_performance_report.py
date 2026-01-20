"""
Performance report generator.

This script generates a comprehensive performance report documenting:
- Dataset statistics
- Training results
- Inference performance
- Comparison with baseline
- Lessons learned and recommendations

Requirements: 12.5, 14.1, 14.2, 14.3
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PerformanceReportGenerator:
    """Generates comprehensive performance reports."""

    def __init__(
        self,
        pipeline_results_file: str,
        validation_results_file: str,
        benchmark_results_file: str,
    ):
        """
        Initialize report generator.

        Args:
            pipeline_results_file: Path to pipeline results JSON
            validation_results_file: Path to validation results JSON
            benchmark_results_file: Path to benchmark results JSON
        """
        self.pipeline_results = self._load_json(pipeline_results_file)
        self.validation_results = self._load_json(validation_results_file)
        self.benchmark_results = self._load_json(benchmark_results_file)

        logger.info("Loaded all result files")

    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load JSON file."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return {}

        with open(path, "r") as f:
            return json.load(f)

    def generate_markdown_report(self) -> str:
        """
        Generate markdown performance report.

        Returns:
            Markdown report content
        """
        report = []

        # Header
        report.append("# Production ML Training Results")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append(
            "This document presents the results of the end-to-end production ML training pipeline validation."
        )
        report.append("")

        # Executive Summary
        report.append("## Executive Summary")
        report.append("")

        all_passed = self.validation_results.get("all_passed", False)
        if all_passed:
            report.append("✅ **All performance requirements met**")
        else:
            report.append("⚠️ **Some performance requirements not met**")
        report.append("")

        # Key metrics
        metrics = self.pipeline_results.get("metrics", {})
        report.append("### Key Metrics")
        report.append("")
        report.append(f"- **Test Accuracy:** {metrics.get('test_accuracy', 0):.2%}")
        report.append(f"- **Test F1 Score:** {metrics.get('test_f1', 0):.2%}")
        report.append(f"- **Model Size:** {metrics.get('model_size_mb', 0):.2f} MB")
        report.append(
            f"- **Training Time:** {self.pipeline_results.get('total_time_hours', 0):.2f} hours"
        )
        report.append(
            f"- **Inference Latency (p95):** {metrics.get('inference_latency_ms', 0):.2f} ms"
        )
        report.append("")

        # Dataset Statistics
        report.append("## Dataset Statistics")
        report.append("")
        report.append("### Collection")
        report.append("")
        report.append(
            f"- **Total Papers Collected:** {metrics.get('collected_papers', 0):,}"
        )
        report.append(f"- **Categories:** {metrics.get('categories', 0)}")
        report.append(
            f"- **Collection Time:** {self.pipeline_results.get('timings', {}).get('1_collect_data', 0):.2f} seconds"
        )
        report.append("")

        report.append("### Preprocessing")
        report.append("")
        report.append(
            f"- **Samples After Cleaning:** {metrics.get('preprocessed_samples', 0):,}"
        )
        report.append(f"- **Samples Removed:** {metrics.get('removed_samples', 0):,}")
        report.append(
            f"- **Removal Rate:** {(metrics.get('removed_samples', 0) / max(metrics.get('collected_papers', 1), 1) * 100):.2f}%"
        )
        report.append(
            f"- **Preprocessing Time:** {self.pipeline_results.get('timings', {}).get('2_preprocess_data', 0):.2f} seconds"
        )
        report.append("")

        report.append("### Data Splits")
        report.append("")
        report.append("| Split | Samples | Percentage |")
        report.append("|-------|---------|------------|")

        train_samples = metrics.get("train_samples", 0)
        val_samples = metrics.get("val_samples", 0)
        test_samples = metrics.get("test_samples", 0)
        total_samples = train_samples + val_samples + test_samples

        if total_samples > 0:
            report.append(
                f"| Train | {train_samples:,} | {train_samples / total_samples * 100:.1f}% |"
            )
            report.append(
                f"| Validation | {val_samples:,} | {val_samples / total_samples * 100:.1f}% |"
            )
            report.append(
                f"| Test | {test_samples:,} | {test_samples / total_samples * 100:.1f}% |"
            )
            report.append(f"| **Total** | **{total_samples:,}** | **100%** |")
        report.append("")

        # Training Results
        report.append("## Training Results")
        report.append("")

        report.append("### Model Configuration")
        report.append("")
        report.append("- **Base Model:** DistilBERT-base-uncased")
        report.append("- **Task:** Multi-class classification (10 categories)")
        report.append("- **Training Epochs:** 3")
        report.append("- **Batch Size:** 16")
        report.append("- **Learning Rate:** 2e-5")
        report.append("")

        report.append("### Training Metrics")
        report.append("")
        report.append("| Metric | Value |")
        report.append("|--------|-------|")
        report.append(f"| Train Accuracy | {metrics.get('train_accuracy', 0):.2%} |")
        report.append(f"| Validation Accuracy | {metrics.get('val_accuracy', 0):.2%} |")
        report.append(f"| Test Accuracy | {metrics.get('test_accuracy', 0):.2%} |")
        report.append(f"| Test F1 Score | {metrics.get('test_f1', 0):.2%} |")
        report.append(
            f"| Training Time | {self.pipeline_results.get('timings', {}).get('4_train_model', 0) / 3600:.2f} hours |"
        )
        report.append("")

        # Inference Performance
        report.append("## Inference Performance")
        report.append("")

        latency = self.benchmark_results.get("performance", {}).get("latency", {})
        if latency:
            report.append("### Latency Statistics")
            report.append("")
            report.append("| Percentile | Latency (ms) |")
            report.append("|------------|--------------|")
            report.append(f"| Mean | {latency.get('mean', 0):.2f} |")
            report.append(f"| Median (p50) | {latency.get('p50', 0):.2f} |")
            report.append(f"| p95 | {latency.get('p95', 0):.2f} |")
            report.append(f"| p99 | {latency.get('p99', 0):.2f} |")
            report.append(f"| Min | {latency.get('min', 0):.2f} |")
            report.append(f"| Max | {latency.get('max', 0):.2f} |")
            report.append("")

        throughput = self.benchmark_results.get("performance", {}).get("throughput", {})
        if throughput:
            report.append("### Throughput")
            report.append("")
            report.append(
                f"- **Predictions per Second:** {throughput.get('predictions_per_second', 0):.2f}"
            )
            report.append(
                f"- **Total Predictions:** {throughput.get('total_predictions', 0):,}"
            )
            report.append(
                f"- **Duration:** {throughput.get('duration_seconds', 0):.2f} seconds"
            )
            report.append("")

        memory = self.benchmark_results.get("performance", {}).get("memory", {})
        if memory:
            report.append("### Memory Usage")
            report.append("")
            report.append(
                f"- **Model Load Overhead:** {memory.get('model_load_overhead_mb', 0):.2f} MB"
            )
            report.append(
                f"- **After Predictions:** {memory.get('after_predictions_mb', 0):.2f} MB"
            )
            report.append(
                f"- **Prediction Overhead:** {memory.get('prediction_overhead_mb', 0):.2f} MB"
            )
            report.append("")

        # Performance Validation
        report.append("## Performance Validation")
        report.append("")

        report.append("### Requirements Validation")
        report.append("")

        passed = self.validation_results.get("passed", [])
        failed = self.validation_results.get("failed", [])

        if passed:
            report.append("#### ✅ Passed")
            report.append("")
            for item in passed:
                report.append(f"- {item}")
            report.append("")

        if failed:
            report.append("#### ❌ Failed")
            report.append("")
            for item in failed:
                report.append(f"- {item}")
            report.append("")

        # Comparison with Baseline
        comparison = self.benchmark_results.get("comparison", {})
        if comparison:
            report.append("## Comparison with Baseline")
            report.append("")

            latency_comp = comparison.get("latency", {})
            if latency_comp:
                improvement = latency_comp.get("improvement_percent", 0)
                report.append("### Latency")
                report.append("")
                report.append(
                    f"- **Current (p95):** {latency_comp.get('current_p95', 0):.2f} ms"
                )
                report.append(
                    f"- **Baseline (p95):** {latency_comp.get('baseline_p95', 0):.2f} ms"
                )

                if improvement > 0:
                    report.append(f"- **Improvement:** ✅ {improvement:.2f}% faster")
                else:
                    report.append(f"- **Change:** ⚠️ {abs(improvement):.2f}% slower")
                report.append("")

        # Lessons Learned
        report.append("## Lessons Learned")
        report.append("")
        report.append("### What Worked Well")
        report.append("")
        report.append(
            "1. **Data Collection:** The arXiv API provided reliable access to high-quality academic papers"
        )
        report.append(
            "2. **Preprocessing:** Text cleaning and deduplication significantly improved data quality"
        )
        report.append(
            "3. **Model Selection:** DistilBERT provided a good balance of accuracy and efficiency"
        )
        report.append(
            "4. **Training Pipeline:** Automated pipeline reduced manual intervention and errors"
        )
        report.append("")

        report.append("### Challenges")
        report.append("")
        report.append(
            "1. **API Rate Limits:** Required careful rate limiting and retry logic"
        )
        report.append(
            "2. **Data Quality:** Some papers had incomplete abstracts or metadata"
        )
        report.append(
            "3. **Training Time:** Full training on large datasets requires significant compute resources"
        )
        report.append(
            "4. **Memory Management:** Large batch sizes can cause OOM errors on limited hardware"
        )
        report.append("")

        # Recommendations
        report.append("## Recommendations")
        report.append("")

        report.append("### For Production Deployment")
        report.append("")
        report.append(
            "1. **Model Serving:** Use model versioning and A/B testing for safe deployments"
        )
        report.append(
            "2. **Monitoring:** Implement comprehensive monitoring for latency, accuracy, and errors"
        )
        report.append(
            "3. **Retraining:** Set up automated retraining pipeline to keep model current"
        )
        report.append(
            "4. **Scaling:** Consider model quantization or distillation for edge deployment"
        )
        report.append("")

        report.append("### For Future Improvements")
        report.append("")
        report.append(
            "1. **Data Augmentation:** Explore techniques to increase training data diversity"
        )
        report.append(
            "2. **Hyperparameter Tuning:** Use Optuna for systematic hyperparameter optimization"
        )
        report.append(
            "3. **Model Architecture:** Experiment with newer transformer models (RoBERTa, ALBERT)"
        )
        report.append(
            "4. **Multi-task Learning:** Train on multiple related tasks simultaneously"
        )
        report.append("")

        # Conclusion
        report.append("## Conclusion")
        report.append("")

        if all_passed:
            report.append(
                "The production ML training pipeline successfully met all performance requirements. "
            )
            report.append(
                "The trained model achieves high accuracy while maintaining low latency and reasonable "
            )
            report.append(
                "resource usage. The pipeline is ready for production deployment with automated retraining."
            )
        else:
            report.append(
                "The production ML training pipeline completed successfully, though some performance "
            )
            report.append(
                "requirements were not fully met. Review the validation results above and consider "
            )
            report.append(
                "adjustments to training configuration or infrastructure before production deployment."
            )
        report.append("")

        # Appendix
        report.append("## Appendix")
        report.append("")

        report.append("### Pipeline Steps and Timings")
        report.append("")
        report.append("| Step | Status | Time |")
        report.append("|------|--------|------|")

        steps = self.pipeline_results.get("steps", {})
        timings = self.pipeline_results.get("timings", {})

        for step_name in sorted(steps.keys()):
            status = steps[step_name]
            timing = timings.get(step_name, 0)

            if timing > 3600:
                time_str = f"{timing / 3600:.2f} hours"
            elif timing > 60:
                time_str = f"{timing / 60:.2f} minutes"
            else:
                time_str = f"{timing:.2f} seconds"

            status_icon = "✅" if status == "SUCCESS" else "❌"
            report.append(f"| {step_name} | {status_icon} {status} | {time_str} |")

        report.append("")
        report.append(
            f"**Total Pipeline Time:** {self.pipeline_results.get('total_time_hours', 0):.2f} hours"
        )
        report.append("")

        return "\n".join(report)

    def save_report(self, output_file: str):
        """
        Save report to file.

        Args:
            output_file: Path to output file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report_content = self.generate_markdown_report()

        with open(output_path, "w") as f:
            f.write(report_content)

        logger.info(f"Performance report saved to: {output_file}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate performance report")
    parser.add_argument(
        "--pipeline-results",
        type=str,
        default="data/e2e_validation/pipeline_results.json",
        help="Path to pipeline results JSON",
    )
    parser.add_argument(
        "--validation-results",
        type=str,
        default="data/e2e_validation/validation_report.json",
        help="Path to validation results JSON",
    )
    parser.add_argument(
        "--benchmark-results",
        type=str,
        default="data/benchmarks/benchmark_results.json",
        help="Path to benchmark results JSON",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="backend/docs/PRODUCTION_ML_TRAINING_RESULTS.md",
        help="Path to output report file",
    )

    args = parser.parse_args()

    # Generate report
    generator = PerformanceReportGenerator(
        pipeline_results_file=args.pipeline_results,
        validation_results_file=args.validation_results,
        benchmark_results_file=args.benchmark_results,
    )

    generator.save_report(args.output_file)

    print("\n" + "=" * 80)
    print("Performance report generated successfully!")
    print(f"Report saved to: {args.output_file}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
