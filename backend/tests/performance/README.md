# Phase 19 Performance Tests

## Overview

This directory contains performance and stress tests for Phase 19 - Hybrid Edge-Cloud Orchestration.

## Test Files

### 1. `test_phase19_benchmarks.py`
Performance benchmarks measuring:
- API dispatch latency (< 100ms)
- Embedding generation time (< 5 min for 100 files)
- GPU utilization (> 70%)
- Throughput (> 10 repos/hour)

### 2. `test_phase19_stress.py`
Stress tests for extreme conditions:
- Large repository (10,000 files)
- 100 concurrent API requests
- Queue overflow (1000 repositories)
- Limited GPU memory scenarios

### 3. `test_phase19_performance.py`
Comprehensive performance tests combining benchmarks and stress tests.

## Quick Start

### Validate Tests (No Dependencies)
```bash
python tests/performance/validate_tests.py
```

### Run All Performance Tests
```bash
pytest tests/performance/ -v
```

### Run Specific Test File
```bash
pytest tests/performance/test_phase19_benchmarks.py -v
pytest tests/performance/test_phase19_stress.py -v
pytest tests/performance/test_phase19_performance.py -v
```

### Run by Marker
```bash
# Benchmark tests only
pytest tests/performance/ -v -m benchmark

# Stress tests only
pytest tests/performance/ -v -m stress

# Skip slow tests
pytest tests/performance/ -v -m "not slow"

# GPU tests only (requires CUDA)
pytest tests/performance/ -v -k "gpu"
```

## Test Markers

- `@pytest.mark.performance` - All performance tests
- `@pytest.mark.benchmark` - Benchmark tests
- `@pytest.mark.stress` - Stress tests
- `@pytest.mark.slow` - Tests taking > 30 seconds

## Requirements

### Core Dependencies
```bash
pip install pytest torch fastapi upstash-redis
```

### GPU Tests
- CUDA-enabled GPU
- nvidia-smi (for utilization monitoring)

## Performance Targets

| Metric | Target | Test |
|--------|--------|------|
| API Latency (P95) | < 100ms | `test_ingest_endpoint_latency` |
| Embedding Generation | < 5 min (100 files) | `test_embedding_generation_100_files` |
| GPU Utilization | > 70% | `test_gpu_utilization_during_training` |
| Throughput | > 10 repos/hour | `test_repository_processing_throughput` |
| Large Repository | 10,000 files | `test_large_repository_processing` |

## Example Output

```
=== API Dispatch Latency Benchmark ===
Requests: 100
Average: 45.23ms
P50: 42.10ms
P95: 78.45ms
P99: 95.32ms
Max: 102.15ms
Target: < 100ms
✓ PASS
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'upstash_redis'"
Install dependencies:
```bash
pip install -r requirements-edge.txt
```

### "CUDA not available"
GPU tests will be skipped automatically. Run with CPU:
```bash
pytest tests/performance/ -v -m "not gpu"
```

### "Out of memory"
Large repository tests may cause OOM on limited hardware. This is expected and tests will skip gracefully.

## CI/CD Integration

Add to `.github/workflows/phase19-performance.yml`:
```yaml
- name: Run performance tests
  run: |
    cd backend
    pytest tests/performance/ -v -m "not slow"
```

## Documentation

See `PHASE19_PERFORMANCE_TESTING_SUMMARY.md` for detailed documentation.
