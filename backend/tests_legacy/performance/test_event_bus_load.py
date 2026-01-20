"""
Load testing for event bus under high load.

Tests event bus performance with 1000+ events/second.
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from backend.app.shared.event_bus import EventBus


@pytest.fixture
def event_bus():
    """Create a fresh event bus for testing."""
    return EventBus()


def test_event_bus_high_load_sync(event_bus):
    """
    Test event bus under high load (1000+ events/second).

    Requirements: 8.5
    """
    # Register a simple handler
    call_count = {"count": 0}

    def handler(payload):
        call_count["count"] += 1

    event_bus.subscribe("test.event", handler)

    # Emit 1000 events and measure time
    num_events = 1000
    start_time = time.time()

    for i in range(num_events):
        event_bus.emit("test.event", {"index": i})

    end_time = time.time()
    duration = end_time - start_time
    events_per_second = num_events / duration

    # Verify all events were delivered
    assert call_count["count"] == num_events

    # Verify throughput > 1000 events/second
    assert events_per_second > 1000, f"Only {events_per_second:.0f} events/second"

    print(f"\nEvent bus throughput: {events_per_second:.0f} events/second")
    print(f"Total time: {duration:.3f} seconds")


def test_event_bus_concurrent_operations(event_bus):
    """
    Test concurrent module operations through event bus.

    Requirements: 8.5
    """
    results = {"count": 0}

    def handler(payload):
        results["count"] += 1
        # Simulate some work
        time.sleep(0.001)

    event_bus.subscribe("concurrent.test", handler)

    # Emit events from multiple threads
    num_threads = 10
    events_per_thread = 100

    def emit_events(thread_id):
        for i in range(events_per_thread):
            event_bus.emit("concurrent.test", {"thread": thread_id, "index": i})

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(emit_events, i) for i in range(num_threads)]
        for future in futures:
            future.result()

    end_time = time.time()
    duration = end_time - start_time

    # Give handlers time to complete
    time.sleep(0.5)

    expected_count = num_threads * events_per_thread
    assert results["count"] == expected_count

    print(f"\nConcurrent operations completed in {duration:.3f} seconds")
    print(f"Total events: {expected_count}")


def test_event_bus_error_isolation(event_bus):
    """
    Test that handler errors don't affect other handlers.

    Requirements: 4.4
    """
    successful_calls = {"count": 0}

    def failing_handler(payload):
        raise ValueError("Intentional error")

    def successful_handler(payload):
        successful_calls["count"] += 1

    event_bus.subscribe("test.error", failing_handler)
    event_bus.subscribe("test.error", successful_handler)

    # Emit events - successful handler should still work
    num_events = 100
    for i in range(num_events):
        event_bus.emit("test.error", {"index": i})

    # Verify successful handler was called despite failing handler
    assert successful_calls["count"] == num_events

    # Verify metrics tracked the errors
    metrics = event_bus.get_metrics()
    assert metrics["handler_errors"] == num_events

    print("\nError isolation test passed")
    print(f"Successful calls: {successful_calls['count']}")
    print(f"Handler errors: {metrics['handler_errors']}")


def test_event_bus_metrics_tracking(event_bus):
    """
    Test event bus metrics tracking under load.

    Requirements: 12.1, 12.2, 12.3, 12.4
    """

    def handler(payload):
        pass

    event_bus.subscribe("metrics.test", handler)

    # Emit events
    num_events = 500
    for i in range(num_events):
        event_bus.emit("metrics.test", {"index": i})

    # Check metrics
    metrics = event_bus.get_metrics()

    assert metrics["events_emitted"] == num_events
    assert metrics["events_delivered"] == num_events
    assert metrics["handler_errors"] == 0

    print("\nMetrics tracking test passed")
    print(f"Events emitted: {metrics['events_emitted']}")
    print(f"Events delivered: {metrics['events_delivered']}")
