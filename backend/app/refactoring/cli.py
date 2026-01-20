"""
Command-line interface for refactoring validation framework.

Provides commands to run code smell detection, generate reports,
and validate refactoring progress.
"""

import json
from pathlib import Path
from typing import Optional
import argparse

from .detector import CodeSmellDetector
from .models import SmellReport
from .constants import SERVICE_DIR


def analyze_service(service_name: Optional[str] = None) -> None:
    """
    Analyze a specific service or all services.

    Args:
        service_name: Name of service file (e.g., 'ml_classification_service.py')
                     If None, analyzes all services
    """
    detector = CodeSmellDetector()
    service_path = Path(SERVICE_DIR)

    if not service_path.exists():
        print(f"Error: Service directory not found: {service_path}")
        return

    if service_name:
        # Analyze single service
        file_path = service_path / service_name
        if not file_path.exists():
            print(f"Error: Service file not found: {file_path}")
            return

        print(f"Analyzing {service_name}...")
        report = detector.analyze_file(file_path)
        print_report(report)
    else:
        # Analyze all services
        print(f"Analyzing all services in {service_path}...")
        reports = detector.analyze_directory(service_path)

        # Print summary
        summary = detector.generate_summary_report(reports)
        print(summary)

        # Print detailed reports for files with smells
        print("\nDetailed Reports:")
        print("=" * 70)
        for report in reports:
            if report.smells:
                print(f"\n{report.summary()}")
                for smell in report.smells:
                    print(f"  {smell}")


def print_report(report: SmellReport) -> None:
    """Print a single smell report."""
    print("\n" + "=" * 70)
    print(report.summary())

    if report.smells:
        print("\nCode Smells:")
        for smell in report.smells:
            print(f"\n{smell}")
    else:
        print("\n✓ No code smells detected!")

    print("=" * 70)


def check_file(file_path: str) -> None:
    """
    Check a specific file for code smells.

    Args:
        file_path: Path to Python file to check
    """
    detector = CodeSmellDetector()
    path = Path(file_path)

    if not path.exists():
        print(f"Error: File not found: {file_path}")
        return

    print(f"Analyzing {file_path}...")
    report = detector.analyze_file(path)
    print_report(report)


def generate_json_report(output_file: str) -> None:
    """
    Generate JSON report of all code smells.

    Args:
        output_file: Path to output JSON file
    """
    detector = CodeSmellDetector()
    service_path = Path(SERVICE_DIR)

    if not service_path.exists():
        print(f"Error: Service directory not found: {service_path}")
        return

    print("Analyzing all services...")
    reports = detector.analyze_directory(service_path)

    # Convert to JSON-serializable format
    data = {
        "total_files": len(reports),
        "total_smells": sum(len(r.smells) for r in reports),
        "reports": [
            {
                "file": str(r.file_path),
                "total_lines": r.total_lines,
                "complexity_score": r.complexity_score,
                "smell_count": len(r.smells),
                "smells": [
                    {
                        "type": s.smell_type.value,
                        "severity": s.severity.value,
                        "location": str(s.location),
                        "description": s.description,
                        "suggested_technique": s.suggested_technique.value,
                        "metrics": s.metrics,
                    }
                    for s in r.smells
                ],
            }
            for r in reports
        ],
    }

    # Write to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nReport written to: {output_file}")
    print(f"Total files analyzed: {data['total_files']}")
    print(f"Total smells detected: {data['total_smells']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Refactoring Validation Framework - Code Smell Detection"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze services for code smells"
    )
    analyze_parser.add_argument(
        "--service",
        type=str,
        help="Specific service file to analyze (e.g., ml_classification_service.py)",
    )

    # Check command
    check_parser = subparsers.add_parser("check", help="Check a specific file")
    check_parser.add_argument("file", type=str, help="Path to Python file to check")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate JSON report")
    report_parser.add_argument(
        "--output",
        type=str,
        default="refactoring_report.json",
        help="Output file path (default: refactoring_report.json)",
    )

    args = parser.parse_args()

    if args.command == "analyze":
        analyze_service(args.service)
    elif args.command == "check":
        check_file(args.file)
    elif args.command == "report":
        generate_json_report(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
