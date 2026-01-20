"""Check what routes are actually registered in the app."""
from app import create_app

app = create_app()

print("All registered routes:\n")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        methods = ','.join(route.methods) if route.methods else 'N/A'
        print(f"{methods:10} {route.path}")

print("\n\nAuth-related routes:")
for route in app.routes:
    if hasattr(route, 'path') and 'auth' in route.path.lower():
        methods = ','.join(route.methods) if hasattr(route, 'methods') and route.methods else 'N/A'
        print(f"{methods:10} {route.path}")
