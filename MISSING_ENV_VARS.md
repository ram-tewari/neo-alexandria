# Missing Environment Variables for Render

## Add These Variables

Click "Add Environment Variable" in Render and add each of these:

### 1. FRONTEND_URL
```
https://pharos.onrender.com
```

### 2. JWT_SECRET_KEY
```
lnEKzBLmVjP5sqwfbZ6Jo71WDNgkicaIAUR3dx802CMTyhXQu9tSvYOr4FpHGe
```
**Note:** This is a randomly generated 64-character secret. Use this or generate your own.

### 3. ENV
```
prod
```

### 4. JWT_ALGORITHM (Optional - has default)
```
HS256
```

### 5. JWT_ACCESS_TOKEN_EXPIRE_MINUTES (Optional - has default)
```
30
```

### 6. JWT_REFRESH_TOKEN_EXPIRE_DAYS (Optional - has default)
```
7
```

## Quick Copy-Paste Format

For easy adding in Render:

| Key | Value |
|-----|-------|
| `FRONTEND_URL` | `https://pharos.onrender.com` |
| `JWT_SECRET_KEY` | `lnEKzBLmVjP5sqwfbZ6Jo71WDNgkicaIAUR3dx802CMTyhXQu9tSvYOr4FpHGe` |
| `ENV` | `prod` |

## After Adding

1. Click "Save Changes"
2. Render will automatically redeploy (3-5 minutes)
3. Monitor deployment logs for success

## Verify DATABASE_URL

**CRITICAL:** Click the eye icon (👁️) next to `DATABASE_URL` to check its value:

- ❌ **If PostgreSQL:** `postgresql://neondb_owner:...`
  - Delete it and add: `sqlite:///./backend.db`
  
- ✅ **If SQLite:** `sqlite:///./backend.db`
  - Perfect! No action needed.

## Expected Total

After adding these, you should have **15-18 environment variables** total.
