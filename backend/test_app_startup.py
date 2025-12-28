"""Test script to verify application startup and route registration."""
from app import app

print("✓ Application imported successfully")
print(f"Total routes: {len(app.routes)}")

# Get API routes (exclude OpenAPI routes)
api_routes = [r for r in app.routes if hasattr(r, 'path') and not r.path.startswith('/openapi')]
print(f"API routes: {len(api_routes)}")

# Group routes by prefix
route_groups = {}
for route in api_routes:
    prefix = route.path.split('/')[1] if '/' in route.path else 'root'
    if prefix not in route_groups:
        route_groups[prefix] = []
    route_groups[prefix].append(route.path)

print("\nRoutes by module:")
for prefix in sorted(route_groups.keys()):
    print(f"  /{prefix}: {len(route_groups[prefix])} endpoints")
    for path in sorted(route_groups[prefix])[:3]:
        print(f"    - {path}")
    if len(route_groups[prefix]) > 3:
        print(f"    ... and {len(route_groups[prefix]) - 3} more")
