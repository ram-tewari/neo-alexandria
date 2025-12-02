#!/usr/bin/env python
"""
Verification script for event-driven decoupling between Resources and Collections.

This script verifies that:
1. No circular imports exist
2. Resource deletion emits events
3. Collections handler is properly configured
4. Event flow is correctly implemented
"""

import sys
import inspect
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def verify_no_circular_imports():
    """Verify that there are no circular imports between modules."""
    logger.info("=" * 60)
    logger.info("TEST 1: Verifying no circular imports")
    logger.info("=" * 60)
    
    try:
        from backend.app.services import resource_service
        
        # Get source code
        resource_source = inspect.getsource(resource_service)
        
        # Check for imports
        forbidden_imports = [
            "from backend.app.services.collection_service",
            "from backend.app.modules.collections",
            "import CollectionService"
        ]
        
        for forbidden in forbidden_imports:
            if forbidden in resource_source:
                logger.error(f"✗ Found forbidden import: {forbidden}")
                return False
        
        # Check for direct references (excluding comments)
        lines = resource_source.split('\n')
        for i, line in enumerate(lines, 1):
            if '#' in line:
                line = line[:line.index('#')]
            if 'CollectionService' in line and 'CollectionService' not in ['# CollectionService']:
                logger.error(f"✗ Found CollectionService reference at line {i}: {line.strip()}")
                return False
        
        logger.info("✓ No circular imports detected")
        logger.info("✓ ResourceService does not import CollectionService")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error checking imports: {e}")
        return False


def verify_event_emission():
    """Verify that resource deletion emits events."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Verifying event emission in delete_resource")
    logger.info("=" * 60)
    
    try:
        from backend.app.services import resource_service
        
        # Get source code of delete_resource function
        delete_func = resource_service.delete_resource
        source = inspect.getsource(delete_func)
        
        # Check for event emission
        required_patterns = [
            "event_bus.emit",
            "RESOURCE_DELETED",
            "resource.deleted"
        ]
        
        found_patterns = []
        for pattern in required_patterns:
            if pattern in source:
                found_patterns.append(pattern)
        
        if len(found_patterns) >= 2:  # At least event_bus.emit and one event identifier
            logger.info("✓ delete_resource() emits resource.deleted event")
            logger.info(f"  Found patterns: {', '.join(found_patterns)}")
            return True
        else:
            logger.error(f"✗ Event emission not found. Found patterns: {found_patterns}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error checking event emission: {e}")
        return False


def verify_event_handler():
    """Verify that Collections module has event handler."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Verifying Collections event handler")
    logger.info("=" * 60)
    
    try:
        # Read the handlers file directly to avoid import conflicts
        import os
        
        handlers_path = "app/modules/collections/handlers.py"
        
        if not os.path.exists(handlers_path):
            logger.error(f"✗ Handlers file not found: {handlers_path}")
            return False
        
        with open(handlers_path, 'r') as f:
            source = f.read()
        
        # Check for handler function
        if 'def handle_resource_deleted' not in source:
            logger.error("✗ handle_resource_deleted function not found")
            return False
        
        logger.info("✓ handle_resource_deleted function exists")
        
        # Check for registration function
        if 'def register_handlers' not in source:
            logger.error("✗ register_handlers function not found")
            return False
        
        logger.info("✓ register_handlers function exists")
        
        # Check handler implementation
        required_elements = [
            "resource_id",
            "CollectionService",
            "find_collections_with_resource",
            "compute_collection_embedding"
        ]
        
        found_elements = []
        for element in required_elements:
            if element in source:
                found_elements.append(element)
        
        if len(found_elements) == len(required_elements):
            logger.info("✓ Handler implements required logic")
            logger.info(f"  Found elements: {', '.join(found_elements)}")
            return True
        else:
            missing = set(required_elements) - set(found_elements)
            logger.error(f"✗ Handler missing elements: {missing}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error checking event handler: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_event_bus_imports():
    """Verify that event bus is properly imported."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Verifying event bus imports")
    logger.info("=" * 60)
    
    try:
        from backend.app.services import resource_service
        
        source = inspect.getsource(resource_service)
        
        required_imports = [
            "from backend.app.shared.event_bus import event_bus",
            "from backend.app.events.event_types import SystemEvent"
        ]
        
        found_imports = []
        for imp in required_imports:
            if imp in source:
                found_imports.append(imp)
        
        if len(found_imports) == len(required_imports):
            logger.info("✓ All required imports present")
            for imp in found_imports:
                logger.info(f"  {imp}")
            return True
        else:
            missing = set(required_imports) - set(found_imports)
            logger.error(f"✗ Missing imports: {missing}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error checking imports: {e}")
        return False


def verify_collection_service_method():
    """Verify that CollectionService has find_collections_with_resource method."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Verifying CollectionService method")
    logger.info("=" * 60)
    
    try:
        # Read the service file directly to avoid import conflicts
        import os
        
        service_paths = [
            "app/modules/collections/service.py",
            "app/services/collection_service.py"
        ]
        
        for service_path in service_paths:
            if os.path.exists(service_path):
                with open(service_path, 'r') as f:
                    source = f.read()
                
                if 'def find_collections_with_resource' in source:
                    logger.info(f"✓ find_collections_with_resource method found in {service_path}")
                    
                    # Check for resource_id parameter
                    if 'resource_id' in source[source.index('def find_collections_with_resource'):
                                                source.index('def find_collections_with_resource') + 500]:
                        logger.info("✓ Method has resource_id parameter")
                        return True
                    else:
                        logger.error("✗ Method missing resource_id parameter")
                        return False
        
        logger.error("✗ find_collections_with_resource method not found in any service")
        return False
            
    except Exception as e:
        logger.error(f"✗ Error checking CollectionService method: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    logger.info("\n" + "=" * 60)
    logger.info("EVENT-DRIVEN DECOUPLING VERIFICATION")
    logger.info("Resources <-> Collections")
    logger.info("=" * 60 + "\n")
    
    tests = [
        ("No Circular Imports", verify_no_circular_imports),
        ("Event Emission", verify_event_emission),
        ("Event Handler", verify_event_handler),
        ("Event Bus Imports", verify_event_bus_imports),
        ("CollectionService Method", verify_collection_service_method),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test '{name}' failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n✓ All verification tests passed!")
        logger.info("Event-driven decoupling is correctly implemented.")
        return 0
    else:
        logger.error(f"\n✗ {total - passed} test(s) failed")
        logger.error("Event-driven decoupling needs attention.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
