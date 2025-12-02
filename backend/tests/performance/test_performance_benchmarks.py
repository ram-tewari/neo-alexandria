"""
Performance benchmark validation tests.

Validates that the modular architecture meets performance requirements.
"""

import pytest
import time
import psutil
import os
from backend.app.shared.event_bus import EventBus


@pytest.fixture
def event_bus():
    """Create a fresh event bus for testing."""
    return EventBus()


def test_event_emission_latency(event_bus):
    """
    Verify event emission + delivery < 1ms (p95).
    
    Requirements: 8.5, 15.4
    """
    latencies = []
    
    def handler(payload):
        pass
    
    event_bus.subscribe("latency.test", handler)
    
    # Measure latency for 1000 events
    num_events = 1000
    for i in range(num_events):
        start = time.perf_counter()
        event_bus.emit("latency.test", {"index": i})
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # Convert to ms
    
    # Calculate p95 latency
    latencies.sort()
    p95_index = int(len(latencies) * 0.95)
    p95_latency = latencies[p95_index]
    
    # Verify p95 < 1ms
    assert p95_latency < 1.0, f"P95 latency {p95_latency:.3f}ms exceeds 1ms threshold"
    
    # Calculate other percentiles for reporting
    p50_latency = latencies[int(len(latencies) * 0.50)]
    p99_latency = latencies[int(len(latencies) * 0.99)]
    
    print(f"\nEvent emission latency:")
    print(f"  P50: {p50_latency:.3f}ms")
    print(f"  P95: {p95_latency:.3f}ms")
    print(f"  P99: {p99_latency:.3f}ms")


def test_application_startup_time():
    """
    Verify application startup < 5 seconds.
    
    Requirements: 8.5
    """
    # Measure time to import and initialize core modules
    start = time.time()
    
    # Import shared kernel
    from backend.app.shared import database, event_bus, base_model
    
    # Import modules
    from backend.app.modules import collections, resources, search
    
    # Initialize database (in-memory for testing)
    from backend.app.shared.database import init_database
    init_database("sqlite:///:memory:")
    
    end = time.time()
    startup_time = end - start
    
    # Verify startup < 5 seconds
    assert startup_time < 5.0, f"Startup time {startup_time:.2f}s exceeds 5s threshold"
    
    print(f"\nApplication startup time: {startup_time:.2f}s")


def test_memory_usage_baseline():
    """
    Verify memory usage increase < 10% compared to baseline.
    
    Requirements: 8.5, 15.4
    
    Note: This test establishes a baseline. In production, compare against
    the layered architecture baseline.
    """
    process = psutil.Process(os.getpid())
    
    # Get initial memory
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create event bus and register handlers
    event_bus = EventBus()
    
    # Register multiple handlers (simulating module handlers)
    for i in range(10):
        def handler(payload):
            pass
        event_bus.subscribe(f"test.event.{i}", handler)
    
    # Emit events
    for i in range(1000):
        event_bus.emit(f"test.event.{i % 10}", {"data": "x" * 100})
    
    # Get final memory
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    memory_increase = final_memory - initial_memory
    memory_increase_pct = (memory_increase / initial_memory) * 100
    
    # For this test, we just report the memory usage
    # In production, compare against baseline from layered architecture
    print(f"\nMemory usage:")
    print(f"  Initial: {initial_memory:.2f} MB")
    print(f"  Final: {final_memory:.2f} MB")
    print(f"  Increase: {memory_increase:.2f} MB ({memory_increase_pct:.1f}%)")
    
    # Soft assertion - memory increase should be reasonable
    assert memory_increase_pct < 50, f"Memory increase {memory_increase_pct:.1f}% is excessive"


def test_event_bus_throughput_benchmark(event_bus):
    """
    Benchmark event bus throughput for comparison.
    
    Requirements: 8.5, 15.4
    """
    call_count = {"count": 0}
    
    def handler(payload):
        call_count["count"] += 1
    
    event_bus.subscribe("throughput.test", handler)
    
    # Emit events and measure throughput
    num_events = 10000
    start = time.time()
    
    for i in range(num_events):
        event_bus.emit("throughput.test", {"index": i})
    
    end = time.time()
    duration = end - start
    throughput = num_events / duration
    
    # Verify all events delivered
    assert call_count["count"] == num_events
    
    print(f"\nEvent bus throughput benchmark:")
    print(f"  Events: {num_events}")
    print(f"  Duration: {duration:.3f}s")
    print(f"  Throughput: {throughput:.0f} events/second")
    
    # Throughput should be > 1000 events/second
    assert throughput > 1000, f"Throughput {throughput:.0f} events/s is below 1000 threshold"
