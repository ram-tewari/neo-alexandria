# ML Model Benchmark Report - v2.0

**Date:** 2025-11-16  
**Model Version:** v2.0  
**Baseline Version:** v1.0

## Executive Summary

This report presents the benchmark results for the ML classification model version v2.0. The benchmarks include inference latency, throughput, memory usage, and integration tests.

## Test Results

### Integration Tests
- **Status:** No tests collected (pytest found 0 tests matching "classification")
- **Note:** The pytest benchmark filter `-k classification` did not match any tests in the current test suite. The existing ML classification tests may use different naming conventions.

## Performance Metrics

### Inference Latency
Measured across 1,000 predictions:

| Metric | Value (ms) | Status |
|--------|------------|--------|
| **Mean** | 52.84 | ✓ |
| **Median (p50)** | 40.01 | ✓ Good |
| **p95** | 105.23 | ⚠ Acceptable |
| **p99** | 234.00 | ⚠ High variance |
| **Min** | 21.31 | ✓ |
| **Max** | 1,875.08 | ⚠ Outlier detected |
| **Std Dev** | 73.43 | - |

**Analysis:**
- The median latency of 40ms is excellent for CPU inference
- p95 latency of 105ms is acceptable but could be improved
- High p99 (234ms) and max (1,875ms) indicate occasional slow predictions
- Standard deviation of 73ms suggests moderate variability

**Recommendations:**
- Investigate outliers causing max latency of 1.8 seconds
- Consider implementing request batching to improve consistency
- Monitor for memory pressure or GC pauses causing spikes

### Throughput
Measured over 30 seconds:

| Metric | Value |
|--------|-------|
| **Predictions/second** | 17.99 |
| **Total predictions** | 540 |
| **Duration** | 30.02 seconds |

**Analysis:**
- Throughput of ~18 predictions/second on CPU is reasonable
- Consistent with the median latency of 40ms per prediction
- Could be significantly improved with GPU acceleration or batching

### Memory Usage

| Metric | Value (MB) |
|--------|------------|
| **Initial memory** | 441.72 |
| **After model load** | 441.75 |
| **After predictions** | 614.24 |
| **Model load overhead** | 0.03 |
| **Prediction overhead** | 172.50 |

**Analysis:**
- Model loading adds minimal overhead (0.03 MB) - likely using cached model
- Prediction overhead of 172 MB over 540 predictions suggests memory accumulation
- Average memory per prediction: ~0.32 MB
- Total memory footprint is acceptable for production use

**Recommendations:**
- Monitor for memory leaks during long-running sessions
- Consider implementing periodic garbage collection
- Investigate if prediction caching is causing memory growth

## Comparison with Baseline

**Status:** Baseline results not available  
**File:** `data/benchmarks/baseline_v1.0.json` not found

To enable baseline comparison:
1. Run benchmark on v1.0: `python backend/scripts/evaluation/run_benchmark_suite.py --model-version v1.0 --output-file data/benchmarks/baseline_v1.0.json`
2. Re-run v2.0 benchmark with baseline parameter

## Requirements Validation

### Requirement 14.1: Run existing ML benchmark tests
- **Status:** ⚠ Partial - No tests matched the filter criteria
- **Action:** Review test naming conventions and update filter

### Requirement 14.2: Verify all tests pass
- **Status:** ⚠ N/A - No tests were executed
- **Action:** Identify and run appropriate ML classification tests

### Requirement 14.3: Compare performance with baseline
- **Status:** ⚠ Incomplete - Baseline not available
- **Action:** Generate baseline results for v1.0

## Conclusions

### Strengths
✓ Median latency (40ms) meets performance targets  
✓ Memory footprint is reasonable for production  
✓ Throughput is consistent with latency measurements  
✓ Model loads efficiently with minimal overhead

### Areas for Improvement
⚠ High latency outliers need investigation  
⚠ Integration tests need to be identified and executed  
⚠ Baseline comparison not yet available  
⚠ Memory growth during predictions should be monitored

### Next Steps
1. **Immediate:**
   - Investigate latency outliers (max 1.8s)
   - Identify correct ML classification test suite
   - Generate baseline results for v1.0

2. **Short-term:**
   - Implement request batching for improved throughput
   - Add memory profiling to identify leaks
   - Set up continuous benchmarking in CI/CD

3. **Long-term:**
   - Evaluate GPU acceleration benefits
   - Implement model quantization for faster inference
   - Establish performance SLAs and monitoring

## Benchmark Configuration

```json
{
  "model_version": "v2.0",
  "baseline_version": "v1.0",
  "test_samples": 1000,
  "throughput_duration": 30,
  "platform": "CPU",
  "python_version": "3.13.4",
  "benchmark_date": "2025-11-16T17:12:34"
}
```

## Raw Results

Full benchmark results are available in: `data/benchmarks/benchmark_v2.0_results.json`

---

**Report Generated:** 2025-11-16  
**Tool:** `backend/scripts/evaluation/run_benchmark_suite.py`
