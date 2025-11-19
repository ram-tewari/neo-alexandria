#!/usr/bin/env python3
"""
Analyze test failures and categorize them by type.
"""
import re
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict
from pathlib import Path


@dataclass
class TestFailurePattern:
    """Represents a pattern of test failures."""
    category: str
    failure_type: str
    count: int
    example_test: str
    example_error: str
    fix_approach: str
    priority: str
    effort: str
    affected_files: List[str]


def parse_test_output(file_path: str) -> Dict:
    """Parse pytest output file and extract failure information."""
    # Try different encodings
    for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    else:
        # Fallback: read as binary and decode with errors='ignore'
        with open(file_path, 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')
    
    # Extract summary line
    summary_match = re.search(
        r'= (\d+) failed, (\d+) passed, (\d+) skipped, \d+ warnings, (\d+) errors',
        content
    )
    
    if summary_match:
        failed = int(summary_match.group(1))
        passed = int(summary_match.group(2))
        skipped = int(summary_match.group(3))
        errors = int(summary_match.group(4))
        total = failed + passed + skipped + errors
    else:
        failed = passed = skipped = errors = total = 0
    
    # Extract failed test names
    failed_tests = re.findall(r'FAILED (tests/[^\s]+)', content)
    error_tests = re.findall(r'ERROR (tests/[^\s]+)', content)
    
    return {
        'summary': {
            'total': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'skipped': skipped,
            'pass_rate': (passed / total * 100) if total > 0 else 0
        },
        'failed_tests': failed_tests,
        'error_tests': error_tests,
        'content': content
    }


def categorize_failures(data: Dict) -> List[TestFailurePattern]:
    """Categorize test failures by type and pattern."""
    patterns = []
    
    # Group tests by file/module
    failed_by_file = defaultdict(list)
    for test in data['failed_tests']:
        file_path = test.split('::')[0]
        failed_by_file[file_path].append(test)
    
    error_by_file = defaultdict(list)
    for test in data['error_tests']:
        file_path = test.split('::')[0]
        error_by_file[file_path].append(test)
    
    # Analyze QualityScore-related failures
    quality_score_tests = [
        t for t in data['failed_tests'] 
        if 'quality' in t.lower() or 'phase9' in t.lower()
    ]
    if quality_score_tests:
        patterns.append(TestFailurePattern(
            category='QualityScore Integration',
            failure_type='AssertionError / AttributeError',
            count=len(quality_score_tests),
            example_test=quality_score_tests[0] if quality_score_tests else '',
            example_error='Tests expect dict but receive QualityScore domain object',
            fix_approach='Update tests to handle QualityScore domain objects, use .overall_score() method',
            priority='Critical',
            effort='Medium',
            affected_files=list(set([t.split('::')[0] for t in quality_score_tests]))
        ))
    
    # Analyze Search-related failures
    search_tests = [
        t for t in data['failed_tests'] 
        if 'search' in t.lower() or 'phase3' in t.lower()
    ]
    if search_tests:
        patterns.append(TestFailurePattern(
            category='Search Integration',
            failure_type='AssertionError / TypeError',
            count=len(search_tests),
            example_test=search_tests[0] if search_tests else '',
            example_error='Tests expect dict but receive SearchResult domain object',
            fix_approach='Update tests to handle SearchResult domain objects',
            priority='High',
            effort='Medium',
            affected_files=list(set([t.split('::')[0] for t in search_tests]))
        ))
    
    # Analyze Classification-related failures
    classification_tests = [
        t for t in data['failed_tests'] 
        if 'classification' in t.lower() or 'phase8' in t.lower()
    ]
    if classification_tests:
        patterns.append(TestFailurePattern(
            category='Classification Integration',
            failure_type='AssertionError / TypeError',
            count=len(classification_tests),
            example_test=classification_tests[0] if classification_tests else '',
            example_error='Tests expect dict but receive ClassificationResult domain object',
            fix_approach='Update tests to handle ClassificationResult domain objects',
            priority='High',
            effort='Medium',
            affected_files=list(set([t.split('::')[0] for t in classification_tests]))
        ))
    
    # Analyze Recommendation-related errors
    recommendation_tests = [
        t for t in data['error_tests'] 
        if 'recommendation' in t.lower() or 'phase11' in t.lower()
    ]
    if recommendation_tests:
        patterns.append(TestFailurePattern(
            category='Recommendation Integration',
            failure_type='ImportError / FixtureError',
            count=len(recommendation_tests),
            example_test=recommendation_tests[0] if recommendation_tests else '',
            example_error='Fixture or import errors in recommendation tests',
            fix_approach='Fix fixture dependencies and imports',
            priority='High',
            effort='Small',
            affected_files=list(set([t.split('::')[0] for t in recommendation_tests]))
        ))
    
    # Analyze Graph/Discovery-related errors
    graph_tests = [
        t for t in data['error_tests'] 
        if 'graph' in t.lower() or 'discovery' in t.lower() or 'phase10' in t.lower()
    ]
    if graph_tests:
        patterns.append(TestFailurePattern(
            category='Graph/Discovery Integration',
            failure_type='ImportError / FixtureError',
            count=len(graph_tests),
            example_test=graph_tests[0] if graph_tests else '',
            example_error='Fixture or import errors in graph/discovery tests',
            fix_approach='Fix fixture dependencies and imports',
            priority='High',
            effort='Small',
            affected_files=list(set([t.split('::')[0] for t in graph_tests]))
        ))
    
    # Analyze Database-related failures
    database_tests = [
        t for t in data['failed_tests'] 
        if 'database' in t.lower() or 'schema' in t.lower()
    ]
    if database_tests:
        patterns.append(TestFailurePattern(
            category='Database Schema',
            failure_type='AssertionError',
            count=len(database_tests),
            example_test=database_tests[0] if database_tests else '',
            example_error='Database schema or initialization issues',
            fix_approach='Update database schema tests and initialization helpers',
            priority='Medium',
            effort='Small',
            affected_files=list(set([t.split('::')[0] for t in database_tests]))
        ))
    
    # Analyze Discovery/Hypothesis compatibility failures
    discovery_compat_tests = [
        t for t in data['failed_tests'] 
        if 'discovery_hypothesis_compatibility' in t.lower()
    ]
    if discovery_compat_tests:
        patterns.append(TestFailurePattern(
            category='Discovery Hypothesis Compatibility',
            failure_type='AssertionError',
            count=len(discovery_compat_tests),
            example_test=discovery_compat_tests[0] if discovery_compat_tests else '',
            example_error='Backward compatibility issues with discovery/hypothesis fields',
            fix_approach='Update compatibility layer for new field names',
            priority='Medium',
            effort='Small',
            affected_files=list(set([t.split('::')[0] for t in discovery_compat_tests]))
        ))
    
    # Analyze Training/ML-related failures
    training_tests = [
        t for t in data['failed_tests'] 
        if 'training' in t.lower() or 'hyperparameter' in t.lower()
    ]
    if training_tests:
        patterns.append(TestFailurePattern(
            category='Training/ML',
            failure_type='AssertionError / ImportError',
            count=len(training_tests),
            example_test=training_tests[0] if training_tests else '',
            example_error='Training and hyperparameter search test failures',
            fix_approach='Fix ML model mocking and training test setup',
            priority='Low',
            effort='Medium',
            affected_files=list(set([t.split('::')[0] for t in training_tests]))
        ))
    
    # Analyze Celery task failures
    celery_tests = [
        t for t in data['failed_tests'] 
        if 'celery' in t.lower()
    ]
    if celery_tests:
        patterns.append(TestFailurePattern(
            category='Celery Tasks',
            failure_type='AssertionError',
            count=len(celery_tests),
            example_test=celery_tests[0] if celery_tests else '',
            example_error='Celery task test failures',
            fix_approach='Update Celery task tests for domain objects',
            priority='Medium',
            effort='Small',
            affected_files=list(set([t.split('::')[0] for t in celery_tests]))
        ))
    
    # Analyze API endpoint failures
    api_tests = [
        t for t in data['failed_tests'] 
        if 'test_phase2_curation_api' in t or 'test_phase10_discovery_api' in t
    ]
    if api_tests:
        patterns.append(TestFailurePattern(
            category='API Endpoints',
            failure_type='AssertionError',
            count=len(api_tests),
            example_test=api_tests[0] if api_tests else '',
            example_error='API response serialization issues with domain objects',
            fix_approach='Update API tests to handle domain object serialization',
            priority='Critical',
            effort='Small',
            affected_files=list(set([t.split('::')[0] for t in api_tests]))
        ))
    
    # Analyze Domain validation failures
    domain_tests = [
        t for t in data['failed_tests'] 
        if 'test_domain_search' in t and 'validation' in t
    ]
    if domain_tests:
        patterns.append(TestFailurePattern(
            category='Domain Validation',
            failure_type='ValidationError',
            count=len(domain_tests),
            example_test=domain_tests[0] if domain_tests else '',
            example_error='Domain object validation not raising expected errors',
            fix_approach='Update domain object validation logic',
            priority='Low',
            effort='Small',
            affected_files=list(set([t.split('::')[0] for t in domain_tests]))
        ))
    
    # Analyze Performance test errors
    performance_tests = [
        t for t in data['error_tests'] 
        if 'performance' in t.lower()
    ]
    if performance_tests:
        patterns.append(TestFailurePattern(
            category='Performance Tests',
            failure_type='ImportError / FixtureError',
            count=len(performance_tests),
            example_test=performance_tests[0] if performance_tests else '',
            example_error='Performance test fixture or import errors',
            fix_approach='Fix performance test fixtures and dependencies',
            priority='Low',
            effort='Small',
            affected_files=list(set([t.split('::')[0] for t in performance_tests]))
        ))
    
    # Analyze Integration test errors (remaining)
    integration_errors = [
        t for t in data['error_tests'] 
        if 'integration' in t.lower() and 
        'recommendation' not in t.lower() and 
        'graph' not in t.lower() and
        'discovery' not in t.lower() and
        'performance' not in t.lower()
    ]
    if integration_errors:
        patterns.append(TestFailurePattern(
            category='Integration Tests',
            failure_type='ImportError / FixtureError',
            count=len(integration_errors),
            example_test=integration_errors[0] if integration_errors else '',
            example_error='Integration test fixture or import errors',
            fix_approach='Fix integration test fixtures and dependencies',
            priority='High',
            effort='Medium',
            affected_files=list(set([t.split('::')[0] for t in integration_errors]))
        ))
    
    return patterns


def generate_report(data: Dict, patterns: List[TestFailurePattern]) -> str:
    """Generate a markdown report of test failures."""
    report = []
    report.append("# Test Failure Analysis Report")
    report.append("")
    report.append("## Summary")
    report.append("")
    summary = data['summary']
    report.append(f"- **Total Tests**: {summary['total']}")
    report.append(f"- **Passed**: {summary['passed']} ({summary['pass_rate']:.1f}%)")
    report.append(f"- **Failed**: {summary['failed']}")
    report.append(f"- **Errors**: {summary['errors']}")
    report.append(f"- **Skipped**: {summary['skipped']}")
    report.append("")
    
    report.append("## Failure Pattern Matrix")
    report.append("")
    report.append("| Category | Type | Count | Priority | Effort | Fix Approach |")
    report.append("|----------|------|-------|----------|--------|--------------|")
    
    for pattern in sorted(patterns, key=lambda p: (
        {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}[p.priority],
        -p.count
    )):
        report.append(
            f"| {pattern.category} | {pattern.failure_type} | {pattern.count} | "
            f"{pattern.priority} | {pattern.effort} | {pattern.fix_approach} |"
        )
    
    report.append("")
    report.append("## Detailed Patterns")
    report.append("")
    
    for pattern in sorted(patterns, key=lambda p: (
        {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}[p.priority],
        -p.count
    )):
        report.append(f"### {pattern.category}")
        report.append("")
        report.append(f"- **Failure Type**: {pattern.failure_type}")
        report.append(f"- **Count**: {pattern.count}")
        report.append(f"- **Priority**: {pattern.priority}")
        report.append(f"- **Effort**: {pattern.effort}")
        report.append(f"- **Example Test**: `{pattern.example_test}`")
        report.append(f"- **Example Error**: {pattern.example_error}")
        report.append(f"- **Fix Approach**: {pattern.fix_approach}")
        report.append(f"- **Affected Files**: {len(pattern.affected_files)} files")
        report.append("")
        for file in pattern.affected_files[:5]:  # Show first 5 files
            report.append(f"  - {file}")
        if len(pattern.affected_files) > 5:
            report.append(f"  - ... and {len(pattern.affected_files) - 5} more")
        report.append("")
    
    return "\n".join(report)


def main():
    """Main entry point."""
    test_output_file = Path(__file__).parent.parent / 'test_failures.txt'
    
    if not test_output_file.exists():
        print(f"Error: {test_output_file} not found")
        return
    
    print("Parsing test output...")
    data = parse_test_output(str(test_output_file))
    
    print("Categorizing failures...")
    patterns = categorize_failures(data)
    
    print("Generating report...")
    report = generate_report(data, patterns)
    
    # Save markdown report
    report_file = Path(__file__).parent.parent / 'test_failure_analysis.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report saved to: {report_file}")
    
    # Save JSON data
    json_file = Path(__file__).parent.parent / 'test_failure_analysis.json'
    json_data = {
        'summary': data['summary'],
        'patterns': [asdict(p) for p in patterns],
        'failed_tests': data['failed_tests'],
        'error_tests': data['error_tests']
    }
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    print(f"JSON data saved to: {json_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("TEST FAILURE ANALYSIS SUMMARY")
    print("="*80)
    print(f"Total Tests: {data['summary']['total']}")
    print(f"Pass Rate: {data['summary']['pass_rate']:.1f}%")
    print(f"Failed: {data['summary']['failed']}")
    print(f"Errors: {data['summary']['errors']}")
    print(f"\nIdentified {len(patterns)} failure patterns")
    print("\nTop 5 Patterns by Count:")
    for i, pattern in enumerate(sorted(patterns, key=lambda p: -p.count)[:5], 1):
        print(f"{i}. {pattern.category}: {pattern.count} tests ({pattern.priority} priority)")


if __name__ == '__main__':
    main()
