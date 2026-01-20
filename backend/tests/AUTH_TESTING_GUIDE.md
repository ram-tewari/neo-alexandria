# Authentication Testing Guide

## Overview

Phase 17 introduced global authentication middleware. This guide explains how to write tests that work with the new authentication system.

## Available Fixtures

### 1. `test_user` - Test User Object
Creates a test user in the database with:
- Username: `testuser`
- Email: `test@example.com`
- Password: `testpassword123`
- Role: `user`
- Status: Active and verified

```python
def test_something(test_user):
    assert test_user.username == "testuser"
    assert test_user.is_active is True
```

### 2. `auth_token` - JWT Access Token
Generates a valid JWT token for the test user.

```python
def test_with_token(auth_token):
    assert auth_token.startswith("eyJ")  # JWT tokens start with this
```

### 3. `auth_headers` - Authorization Headers
Provides ready-to-use headers with Bearer token.

```python
def test_with_headers(authenticated_client, auth_headers):
    response = authenticated_client.get("/protected", headers=auth_headers)
    assert response.status_code == 200
```

### 4. `client` - Default Test Client (Auth Bypassed)
**Most common fixture** - Bypasses authentication for convenience.

```python
def test_resource_creation(client):
    # Authentication is automatically handled
    response = client.post("/resources/", json={...})
    assert response.status_code == 201
```

**Use this for:**
- Testing business logic
- Testing endpoints that require authentication
- Most integration tests

### 5. `authenticated_client` - Real Auth Test Client
Uses actual JWT authentication (does NOT bypass middleware).

```python
def test_auth_flow(authenticated_client, auth_headers):
    # Must provide auth_headers explicitly
    response = authenticated_client.get("/me", headers=auth_headers)
    assert response.status_code == 200
```

**Use this for:**
- Testing authentication flows
- Testing token validation
- Testing auth error handling

### 6. `unauthenticated_client` - No Auth Test Client
Client without any authentication.

```python
def test_public_endpoint(unauthenticated_client):
    response = unauthenticated_client.get("/health")
    assert response.status_code == 200
```

**Use this for:**
- Testing public endpoints
- Testing 401 error responses
- Testing endpoints that should work without auth

## Common Patterns

### Pattern 1: Testing Protected Endpoints (Recommended)
```python
def test_create_resource(client):
    """Use default client - auth is handled automatically"""
    response = client.post("/resources/", json={
        "title": "Test",
        "source": "https://example.com"
    })
    assert response.status_code == 201
```

### Pattern 2: Testing Authentication Errors
```python
def test_missing_token(unauthenticated_client):
    """Use unauthenticated_client to test 401 errors"""
    response = unauthenticated_client.get("/resources/")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
```

### Pattern 3: Testing Token Validation
```python
def test_invalid_token(authenticated_client):
    """Use authenticated_client with custom headers"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = authenticated_client.get("/resources/", headers=headers)
    assert response.status_code == 401
```

### Pattern 4: Testing with Valid Token
```python
def test_with_valid_token(authenticated_client, auth_headers):
    """Use authenticated_client + auth_headers fixture"""
    response = authenticated_client.get("/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
```

### Pattern 5: Testing User-Specific Data
```python
def test_user_resources(client, test_user):
    """Access test_user for assertions"""
    response = client.get("/resources/")
    # The client is authenticated as test_user
    assert response.status_code == 200
```

## Migration Guide

### Old Code (Pre-Phase 17)
```python
def test_create_resource(client):
    response = client.post("/resources/", json={...})
    assert response.status_code == 201
```

### New Code (Phase 17)
**No changes needed!** The default `client` fixture now handles auth automatically.

```python
def test_create_resource(client):
    # Works exactly the same - auth is handled
    response = client.post("/resources/", json={...})
    assert response.status_code == 201
```

### If You Need Real Auth Testing
```python
def test_auth_required(authenticated_client, auth_headers):
    # Now you're testing actual JWT validation
    response = authenticated_client.post(
        "/resources/", 
        json={...},
        headers=auth_headers
    )
    assert response.status_code == 201
```

## Excluded Endpoints

These endpoints are excluded from authentication:
- `/health` - Health check
- `/docs` - API documentation
- `/openapi.json` - OpenAPI schema
- `/redoc` - ReDoc documentation

Test these with `unauthenticated_client`:

```python
def test_health_check(unauthenticated_client):
    response = unauthenticated_client.get("/health")
    assert response.status_code == 200
```

## Troubleshooting

### Error: "401: Not authenticated"
**Problem:** Test is using `authenticated_client` without providing headers.

**Solution:** Either:
1. Use default `client` fixture (recommended)
2. Add `auth_headers` parameter and pass to request

```python
# Option 1: Use default client
def test_something(client):
    response = client.get("/resources/")  # Auth handled automatically

# Option 2: Use authenticated_client with headers
def test_something(authenticated_client, auth_headers):
    response = authenticated_client.get("/resources/", headers=auth_headers)
```

### Error: "Could not validate credentials"
**Problem:** Token is invalid or expired.

**Solution:** Use the `auth_token` or `auth_headers` fixture instead of creating your own.

```python
# ❌ Don't do this
def test_something(authenticated_client):
    headers = {"Authorization": "Bearer fake_token"}
    response = authenticated_client.get("/resources/", headers=headers)

# ✅ Do this
def test_something(authenticated_client, auth_headers):
    response = authenticated_client.get("/resources/", headers=auth_headers)
```

### Error: "User not found"
**Problem:** Test user doesn't exist in database.

**Solution:** Add `test_user` fixture to ensure user is created.

```python
def test_something(client, test_user):
    # test_user ensures user exists in DB
    response = client.get("/resources/")
```

## Best Practices

1. **Use `client` for most tests** - It's the simplest and handles auth automatically
2. **Use `authenticated_client` only for auth testing** - When you need to test actual JWT validation
3. **Use `unauthenticated_client` for public endpoints** - Health checks, docs, etc.
4. **Don't create tokens manually** - Use `auth_token` or `auth_headers` fixtures
5. **Add `test_user` if you need user data** - Ensures user exists for assertions

## Examples

### Example 1: Resource CRUD Test
```python
def test_resource_crud(client, test_user):
    # Create
    response = client.post("/resources/", json={
        "title": "Test Resource",
        "source": "https://example.com"
    })
    assert response.status_code == 201
    resource_id = response.json()["id"]
    
    # Read
    response = client.get(f"/resources/{resource_id}")
    assert response.status_code == 200
    
    # Update
    response = client.put(f"/resources/{resource_id}", json={
        "title": "Updated Title"
    })
    assert response.status_code == 200
    
    # Delete
    response = client.delete(f"/resources/{resource_id}")
    assert response.status_code == 204
```

### Example 2: Authentication Flow Test
```python
def test_login_flow(authenticated_client, test_user):
    # Login
    response = authenticated_client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Use token
    headers = {"Authorization": f"Bearer {token}"}
    response = authenticated_client.get("/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
```

### Example 3: Public Endpoint Test
```python
def test_health_check(unauthenticated_client):
    response = unauthenticated_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

## Summary

- **Default `client`**: Use for 95% of tests - auth handled automatically
- **`authenticated_client`**: Use for testing actual JWT validation
- **`unauthenticated_client`**: Use for public endpoints and 401 error tests
- **`auth_headers`**: Use with `authenticated_client` for protected endpoints
- **`test_user`**: Use when you need to assert on user data

Most tests should just use `client` and work without any changes!
