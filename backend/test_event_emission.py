"""
Test to verify resource.created event is emitted and received
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_event_flow():
    print("="*60)
    print("🧪 EVENT EMISSION TEST")
    print("="*60)
    
    # Test 1: Check event bus initially
    print("\n📡 Test 1: Event Bus Initial Check")
    try:
        from app.shared.event_bus import event_bus
        print("✅ Event bus imported")
        
        # Check handlers
        handlers = event_bus._handlers.get("resource.created", [])
        print(f"   Handlers registered initially: {len(handlers)}")
        
        if len(handlers) == 0:
            print("   ℹ️  No handlers yet (will be registered on first use)")
        else:
            for i, handler in enumerate(handlers):
                handler_name = handler.__name__ if hasattr(handler, '__name__') else str(handler)
                print(f"   Handler {i+1}: {handler_name}")
        
    except Exception as e:
        print(f"❌ Event bus check failed: {e}")
        return False
    
    # Test 2: Manually trigger handler
    print("\n🔧 Test 2: Manual Handler Trigger")
    try:
        from app.modules.resources.handlers import handle_resource_created
        from app.events.event_types import SystemEvent
        
        # Create a mock event
        class MockEvent:
            def __init__(self, data):
                self.data = data
                self.event_type = "resource.created"
        
        # Test with a fake resource ID
        test_event = MockEvent({
            "resource_id": "test-123",
            "title": "Test Resource",
            "source": "https://example.com/test"
        })
        
        print("   Calling handle_resource_created...")
        try:
            handle_resource_created(test_event)
            print("   ✅ Handler executed (check for errors above)")
        except Exception as handler_error:
            print(f"   ⚠️  Handler error: {handler_error}")
            # This is expected if resource doesn't exist
            
    except Exception as e:
        print(f"❌ Manual trigger failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Create actual resource and check event
    print("\n📝 Test 3: Create Resource and Check Event")
    try:
        from app.modules.resources.service import create_pending_resource
        from sqlalchemy.orm import sessionmaker
        from app.shared.database import sync_engine
        import time
        
        Session = sessionmaker(bind=sync_engine)
        db = Session()
        
        # Track if event was emitted
        event_received = []
        
        def test_handler(event):
            event_received.append(event)
            print(f"   🎉 EVENT RECEIVED: {event.data}")
        
        # Subscribe test handler
        event_bus.subscribe("resource.created", test_handler)
        
        # Create resource
        payload = {
            "url": f"https://example.com/event-test-{int(time.time())}",
            "title": "Event Test Resource",
            "description": "Testing event emission" * 100  # Long enough for chunking
        }
        
        print("   Creating resource...")
        resource = create_pending_resource(db, payload)
        print(f"   ✅ Resource created: {resource.id}")
        
        # Give event bus a moment to process
        time.sleep(0.5)
        
        if len(event_received) > 0:
            print(f"   ✅ Event was emitted and received!")
            print(f"   Event data: {event_received[0].data}")
        else:
            print(f"   ❌ Event was NOT received")
            print(f"   This means event emission failed")
        
        db.close()
        return len(event_received) > 0
        
    except Exception as e:
        print(f"❌ Resource creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\nThis test verifies the event emission chain:")
    print("1. Event bus has handlers registered")
    print("2. Handler can be called manually")
    print("3. Resource creation emits event")
    print()
    
    success = test_event_flow()
    
    print("\n" + "="*60)
    if success:
        print("✅ EVENT FLOW WORKS!")
    else:
        print("❌ EVENT FLOW BROKEN - Check details above")
    print("="*60)
    
    sys.exit(0 if success else 1)
