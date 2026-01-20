#!/usr/bin/env python3
"""
Neo Alexandria - Scheduled Tasks Runner

Command-line interface for running scheduled quality monitoring tasks.
Can be invoked manually or via cron/scheduler.

Usage:
    # Run all scheduled tasks
    python scripts/run_scheduled_tasks.py all

    # Run outlier detection only
    python scripts/run_scheduled_tasks.py outlier-detection

    # Run degradation monitoring only
    python scripts/run_scheduled_tasks.py degradation-monitoring

    # Run with custom parameters
    python scripts/run_scheduled_tasks.py outlier-detection --batch-size 500
    python scripts/run_scheduled_tasks.py degradation-monitoring --time-window 60

Cron Examples:
    # Daily outlier detection at 2 AM
    0 2 * * * cd /path/to/backend && python scripts/run_scheduled_tasks.py outlier-detection

    # Weekly degradation monitoring on Sundays at 3 AM
    0 3 * * 0 cd /path/to/backend && python scripts/run_scheduled_tasks.py degradation-monitoring
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to enable backend imports
backend_dir = Path(__file__).parent
parent_dir = backend_dir.parent
sys.path.insert(0, str(parent_dir))

from backend.app.services.scheduled_tasks import (
    run_outlier_detection,
    run_degradation_monitoring,
    run_all_scheduled_tasks,
)


def main():
    parser = argparse.ArgumentParser(
        description="Run Neo Alexandria scheduled quality monitoring tasks"
    )

    parser.add_argument(
        "task",
        choices=["all", "outlier-detection", "degradation-monitoring"],
        help="Task to run",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        help="Batch size for outlier detection (default: 1000)",
    )

    parser.add_argument(
        "--time-window",
        type=int,
        help="Time window in days for degradation monitoring (default: 30)",
    )

    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    # Run the requested task
    if args.task == "all":
        results = run_all_scheduled_tasks()
    elif args.task == "outlier-detection":
        results = run_outlier_detection(batch_size=args.batch_size)
    elif args.task == "degradation-monitoring":
        results = run_degradation_monitoring(time_window_days=args.time_window)
    else:
        print(f"Unknown task: {args.task}", file=sys.stderr)
        sys.exit(1)

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if args.task == "all":
            print("=== Scheduled Tasks Execution Results ===")
            for task_name, task_result in results.items():
                print(f"\n{task_name.upper()}:")
                if task_result.get("success"):
                    print("  ✓ Success")
                    if "outlier_count" in task_result:
                        print(f"  Outliers detected: {task_result['outlier_count']}")
                    if "degraded_count" in task_result:
                        print(f"  Degraded resources: {task_result['degraded_count']}")
                    print(f"  Duration: {task_result.get('duration_seconds', 0):.2f}s")
                else:
                    print(f"  ✗ Failed: {task_result.get('error')}")
        else:
            if results.get("success"):
                print("✓ Task completed successfully")
                if "outlier_count" in results:
                    print(f"  Outliers detected: {results['outlier_count']}")
                if "degraded_count" in results:
                    print(f"  Degraded resources: {results['degraded_count']}")
                print(f"  Duration: {results.get('duration_seconds', 0):.2f}s")
                sys.exit(0)
            else:
                print(f"✗ Task failed: {results.get('error')}", file=sys.stderr)
                sys.exit(1)


if __name__ == "__main__":
    main()
