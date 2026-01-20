# Authentication Module

JWT-based authentication with OAuth2 support for Neo Alexandria 2.0.

## Overview

The Authentication module provides secure user authentication and authorization using JWT tokens. It supports traditional username/password authentication as well as OAuth2 social login via Google and GitHub.

## Features

- **JWT Authentication**: Secure token-based authentication with access and refresh tokens
- **OAuth2 Integration**: Social login via Google and GitHub
- **Token Revocation**: Redis-backed token blacklist for logout functionality
- **Password Security**: Bcrypt password hashing with salt
- **Rate Limiting**: Tiered rate limits based on user tier (free, premium, admin)
- **User Management**: User registration, authentication, and profile management

## Module Structure

```
auth/
├── __init__.py       # Public interface exports
├── router.py         # FastAPI endpoints
├── service.py        # Business logic
├── schema.py         # Pydantic models
├── model.py          # SQLAlchemy models
└── README.md         # This file
```

## Endpoints

### POST /auth/login

Authenticate with username and password.

**Request:**
```json
{
  "username": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### POST /auth/refresh

Obtain a new access token using a refresh token.

**Request:**
```http
Authorization: Bearer <refresh_token>
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### POST /auth/logout

Revoke the current access token.

**Request:**
```http
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

### GET /auth/me

Get current user information.

**Request:**
```http
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "user@example.com",
  "email": "user@example.com",
  "tier": "premium",
  "is_active": true
}
```

### GET /auth/rate-limit

Get current rate limit status.

**Request:**
```http
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "tier": "premium",
  "limit": 1000,
  "remaining": 847,
  "reset_at": "2024-01-01T13:00:00Z"
}
```

### GET /auth/google

Initiate Google OAuth2 authentication flow.

### GET /auth/google/callback

Google OAuth2 callback endpoint (handled automatically).

### GET /auth/github

Initiate GitHub OAuth2 authentication flow.

### GET /auth/github/callback

GitHub OAuth2 callback endpoint (handled automatically).

## Database Models

### User

```python
class User(Base):
    id: UUID
    username: str  # Unique, indexed
    email: str  # Unique, indexed
    hashed_password: str
    tier: str  # free, premium, admin
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### OAuthAccount

```python
class OAuthAccount(Base):
    id: UUID
    user_id: UUID  # FK to User
    provider: str  # google, github
    provider_user_id: str
    access_token: str  # Encrypted
    refresh_token: str  # Encrypted, nullable
    expires_at: datetime  # Nullable
    created_at: datetime
    updated_at: datetime
```

## Service Layer

### AuthService

Main authentication service with the following methods:

- `authenticate_user(username, password)` - Authenticate user credentials
- `get_user_by_id(user_id)` - Retrieve user by ID
- `get_user_by_username(username)` - Retrieve user by username
- `get_or_create_oauth_user(provider, provider_user_id, email)` - OAuth user management
- `create_user(username, email, password, tier)` - Create new user

## JWT Token Structure

### Access Token Claims

```json
{
  "sub": "user@example.com",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "tier": "premium",
  "scopes": ["read", "write"],
  "type": "access",
  "exp": 1704067200,
  "iat": 1704065400
}
```

### Refresh Token Claims

```json
{
  "sub": "user@example.com",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "refresh",
  "exp": 1704672000,
  "iat": 1704065400
}
```

## Configuration

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth2 Providers
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback

# Rate Limiting
RATE_LIMIT_FREE_TIER=100
RATE_LIMIT_PREMIUM_TIER=1000
RATE_LIMIT_ADMIN_TIER=10000

# Testing
TEST_MODE=false
```

### Generate Secure JWT Secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Usage Examples

### Python Client

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    data={
        "username": "user@example.com",
        "password": "password"
    }
)
tokens = response.json()
access_token = tokens["access_token"]

# Make authenticated request
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(
    "http://localhost:8000/resources",
    headers=headers
)

# Refresh token
refresh_response = requests.post(
    "http://localhost:8000/auth/refresh",
    headers={"Authorization": f"Bearer {tokens['refresh_token']}"}
)
new_access_token = refresh_response.json()["access_token"]

# Logout
requests.post(
    "http://localhost:8000/auth/logout",
    headers={"Authorization": f"Bearer {access_token}"}
)
```

### JavaScript Client

```javascript
// Login
const authResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    username: 'user@example.com',
    password: 'password'
  })
});
const tokens = await authResponse.json();

// Make authenticated request
const response = await fetch('http://localhost:8000/resources', {
  headers: { 'Authorization': `Bearer ${tokens.access_token}` }
});

// Refresh token
const refreshResponse = await fetch('http://localhost:8000/auth/refresh', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${tokens.refresh_token}` }
});
const newTokens = await refreshResponse.json();

// Logout
await fetch('http://localhost:8000/auth/logout', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${tokens.access_token}` }
});
```

## Security Considerations

### Password Security

- Passwords are hashed using bcrypt with automatic salt generation
- Minimum password requirements should be enforced at application level
- Never log or display passwords in plain text

### Token Security

- Access tokens expire in 30 minutes (configurable)
- Refresh tokens expire in 7 days (configurable)
- Tokens are revoked on logout using Redis blacklist
- Use HTTPS in production to prevent token interception
- Store tokens securely (httpOnly cookies or secure storage)

### OAuth2 Security

- OAuth2 tokens are encrypted before storage
- State parameter used for CSRF protection
- Redirect URIs must match configured values
- Provider credentials stored as environment variables

### Rate Limiting

- Rate limits enforced per user based on tier
- Sliding window algorithm prevents burst attacks
- Redis required for rate limiting
- Graceful degradation if Redis unavailable

## Testing

### Test Mode

For development and testing, bypass authentication:

```bash
TEST_MODE=true
```

**Warning:** Never enable TEST_MODE in production!

### Unit Tests

```bash
pytest tests/modules/auth/test_auth_service.py -v
```

### Integration Tests

```bash
pytest tests/modules/auth/test_auth_endpoints.py -v
```

## Dependencies

### Shared Kernel

- `app.shared.security` - JWT creation, password hashing
- `app.shared.oauth2` - OAuth2 provider integration
- `app.shared.rate_limiter` - Rate limiting service
- `app.shared.database` - Database session management

### External Services

- **Redis** - Token revocation and rate limiting
- **PostgreSQL/SQLite** - User data storage
- **Google OAuth2** - Social login (optional)
- **GitHub OAuth2** - Social login (optional)

## Related Documentation

- [Authentication API](../../../docs/api/auth.md) - Complete API reference
- [Security Module](../../shared/security.py) - JWT and password utilities
- [OAuth2 Module](../../shared/oauth2.py) - OAuth2 provider integration
- [Rate Limiter](../../shared/rate_limiter.py) - Rate limiting implementation
- [Architecture Overview](../../../docs/architecture/overview.md) - System architecture

## Troubleshooting

### Common Issues

**401 Unauthorized:**
- Check JWT_SECRET_KEY is set correctly
- Verify token hasn't expired
- Ensure token hasn't been revoked
- Check Redis is running for token revocation

**OAuth2 Callback Errors:**
- Verify redirect URIs match OAuth2 provider configuration
- Check client ID and secret are correct
- Ensure callback URL is accessible

**Rate Limiting Errors:**
- Check Redis is running
- Verify rate limit configuration
- Increase limits for development: `RATE_LIMIT_FREE_TIER=999999`

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- Multi-factor authentication (MFA)
- Password reset via email
- Account email verification
- Session management
- Additional OAuth2 providers (Microsoft, Apple)
- API key authentication for service accounts
