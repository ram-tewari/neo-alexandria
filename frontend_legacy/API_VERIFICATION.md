# Backend API Verification

This document verifies that backend endpoints match frontend expectations.

## Resources API

### ✅ GET /resources
**Frontend expects:**
```typescript
GET /api/resources?page=1&limit=20&sort_by=created_at&sort_order=desc
Response: APIListResponse<Resource> = {
  data: Resource[],
  meta: { page, limit, total, pages }
}
```

**Backend provides:**
```python
GET /resources?limit=25&offset=0&sort_by=created_at&sort_dir=desc
Response: {
  items: ResourceRead[],
  total: int
}
```

**❌ MISMATCH:**
1. Backend uses `offset` instead of `page`
2. Backend uses `sort_dir` instead of `sort_order`
3. Backend response format is `{items, total}` not `{data, meta}`
4. Backend doesn't calculate `pages`
5. No `/api` prefix in backend routes

**✅ SOLUTION:** Update frontend API client to match backend format

---

### ✅ GET /resources/{id}
**Frontend expects:**
```typescript
GET /api/resources/{id}
Response: Resource
```

**Backend provides:**
```python
GET /resources/{resource_id}
Response: ResourceRead
```

**✅ MATCH** - Works correctly (backend maps `source` to `url`)

---

### ✅ POST /resources
**Frontend expects:**
```typescript
POST /api/resources
Body: ResourceCreate
Response: Resource
```

**Backend provides:**
```python
POST /resources
Body: ResourceIngestRequest
Response: ResourceAccepted { id, status: "pending" }
Status: 202 ACCEPTED
```

**⚠️ PARTIAL MATCH:**
- Backend returns 202 with minimal data (async ingestion)
- Frontend expects full resource object
- This is actually better UX (async processing)

**✅ SOLUTION:** Frontend should handle 202 response and poll status

---

### ✅ PUT /resources/{id}
**Frontend expects:**
```typescript
PUT /api/resources/{id}
Body: ResourceUpdate
Response: Resource
```

**Backend provides:**
```python
PUT /resources/{resource_id}
Body: ResourceUpdate
Response: ResourceRead
```

**✅ MATCH** - Works correctly

---

### ✅ DELETE /resources/{id}
**Frontend expects:**
```typescript
DELETE /api/resources/{id}
Response: void
```

**Backend provides:**
```python
DELETE /resources/{resource_id}
Status: 204 NO CONTENT
```

**✅ MATCH** - Works correctly

---

### ❌ PATCH /resources/{id}/status
**Frontend expects:**
```typescript
PATCH /api/resources/{id}/status
Body: { read_status: ReadStatus }
Response: Resource
```

**Backend provides:**
```python
❌ ENDPOINT DOES NOT EXIST
```

**❌ MISSING:** Need to add this endpoint or use PUT with partial update

**✅ SOLUTION:** Use PUT /resources/{id} with ResourceUpdate

---

### ❌ POST /resources/{id}/archive
**Frontend expects:**
```typescript
POST /api/resources/{id}/archive
Response: Resource
```

**Backend provides:**
```python
❌ ENDPOINT DOES NOT EXIST
```

**❌ MISSING:** Need to add this endpoint

**✅ SOLUTION:** Use PUT /resources/{id} with `read_status: "archived"`

---

### ✅ GET /resources/{id}/status
**Frontend expects:**
```typescript
GET /api/resources/{id}/status
Response: { ingestion_status, ingestion_error }
```

**Backend provides:**
```python
GET /resources/{resource_id}/status
Response: ResourceStatus
```

**✅ MATCH** - Works correctly

---

## Collections API

### ✅ GET /collections
**Frontend expects:**
```typescript
GET /api/collections?page=1&limit=50
Response: APIListResponse<Collection>
```

**Backend provides:**
```python
GET /collections?page=1&limit=50
Response: CollectionListResponse { items, total, page, limit }
```

**✅ MATCH** - Works correctly (backend uses page-based pagination)

---

### ✅ GET /collections/{id}
**Frontend expects:**
```typescript
GET /api/collections/{id}
Response: CollectionDetail
```

**Backend provides:**
```python
GET /collections/{collection_id}
Response: CollectionDetailResponse
```

**✅ MATCH** - Works correctly

---

### ✅ POST /collections
**Frontend expects:**
```typescript
POST /api/collections
Body: CollectionCreate
Response: Collection
```

**Backend provides:**
```python
POST /collections?user_id={user_id}
Body: CollectionCreate
Response: CollectionResponse
```

**⚠️ PARTIAL MATCH:**
- Backend requires `user_id` query parameter
- Frontend needs to provide user_id

**✅ SOLUTION:** Add user_id to frontend requests (hardcode for now)

---

### ✅ PUT /collections/{id}
**Frontend expects:**
```typescript
PUT /api/collections/{id}
Body: CollectionUpdate
Response: Collection
```

**Backend provides:**
```python
PUT /collections/{collection_id}?user_id={user_id}
Body: CollectionUpdate
Response: CollectionResponse
```

**✅ MATCH** - Works correctly (needs user_id)

---

### ✅ DELETE /collections/{id}
**Frontend expects:**
```typescript
DELETE /api/collections/{id}
```

**Backend provides:**
```python
DELETE /collections/{collection_id}?user_id={user_id}
Status: 204 NO CONTENT
```

**✅ MATCH** - Works correctly (needs user_id)

---

### ✅ POST /collections/{id}/resources
**Frontend expects:**
```typescript
POST /api/collections/{id}/resources
Body: { resource_ids: string[] }
```

**Backend provides:**
```python
POST /collections/{collection_id}/resources?user_id={user_id}
Body: ResourceMembershipRequest { resource_ids }
Response: ResourceMembershipResponse
```

**✅ MATCH** - Works correctly

---

### ✅ DELETE /collections/{id}/resources
**Frontend expects:**
```typescript
DELETE /api/collections/{id}/resources
Body: { resource_ids: string[] }
```

**Backend provides:**
```python
DELETE /collections/{collection_id}/resources?user_id={user_id}
Body: ResourceMembershipRequest { resource_ids }
Response: ResourceMembershipResponse
```

**✅ MATCH** - Works correctly

---

### ✅ GET /collections/{id}/recommendations
**Frontend expects:**
```typescript
GET /api/collections/{id}/recommendations
Response: CollectionRecommendations
```

**Backend provides:**
```python
GET /collections/{collection_id}/recommendations?limit=10
Response: CollectionRecommendationsResponse
```

**✅ MATCH** - Works correctly

---

## Search & Tags API

Need to verify search and tags endpoints...

---

## Summary of Required Changes

### Critical Changes:
1. **Remove `/api` prefix** - Backend doesn't use it
2. **Resources list endpoint** - Use `offset` instead of `page`, `sort_dir` instead of `sort_order`
3. **Resources list response** - Parse `{items, total}` format, calculate pages
4. **Resource status updates** - Use PUT instead of PATCH
5. **Resource archive** - Use PUT with read_status instead of dedicated endpoint
6. **User ID** - Add user_id to collection requests (hardcode "default-user" for now)

### Nice to Have:
1. Add `/api` prefix to backend (or configure frontend base URL without it)
2. Standardize pagination (page vs offset)
3. Standardize response format ({data, meta} vs {items, total})

---

## Action Items

1. ✅ Update frontend API client to remove `/api` prefix
2. ✅ Update resources API to use backend pagination format
3. ✅ Update resources API to handle {items, total} response
4. ✅ Remove updateStatus and archive methods, use update instead
5. ✅ Add user_id to collection API calls
6. ✅ Test all endpoints with backend

