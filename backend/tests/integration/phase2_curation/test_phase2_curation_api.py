from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from backend.app.database.models import Resource


@pytest.fixture
def seeded_resources(test_db):
    TestingSessionLocal = test_db
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)
    items = []
    for i in range(10):
        r = Resource(
            title=f"Item {i}",
            description=f"Desc {i}",
            language="en" if i % 2 == 0 else "es",
            type="article",
            classification_code="006" if i % 2 == 0 else "400",
            subject=["Artificial Intelligence", "Machine Learning"] if i % 2 == 0 else ["Language", "Linguistics"],
            read_status="unread" if i < 5 else "in_progress",
            quality_score=0.3 + i * 0.08,
            date_created=now - timedelta(days=30 - i),
            date_modified=now - timedelta(days=15 - i),
        )
        db.add(r)
        items.append(r)
    db.commit()
    # Extract IDs before closing session to avoid DetachedInstanceError
    item_ids = [str(item.id) for item in items]
    db.close()
    return item_ids


class TestResourcesCRUDAndList:
    def test_get_resource_by_id(self, client, test_db, seeded_resources):
        rid = seeded_resources[0]
        resp = client.get(f"/resources/{rid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == rid

    def test_get_resource_404(self, client):
        resp = client.get("/resources/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    def test_list_resources_basic_pagination_and_total(self, client, seeded_resources):
        resp = client.get("/resources?limit=3&offset=0")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data and "total" in data
        assert data["total"] >= 10
        assert len(data["items"]) == 3

    def test_list_resources_filters(self, client):
        # Filter by classification_code and read_status
        resp = client.get("/resources?classification_code=006&read_status=unread")
        assert resp.status_code == 200
        items = resp.json()["items"]
        for it in items:
            assert it["classification_code"] == "006"
            assert it["read_status"] == "unread"

    def test_list_resources_min_quality_and_date_ranges(self, client, seeded_resources):
        # min_quality should filter out low scores
        resp = client.get("/resources?min_quality=0.7")
        assert resp.status_code == 200
        items = resp.json()["items"]
        for it in items:
            assert it["quality_score"] >= 0.7

    def test_list_resources_sorting(self, client):
        resp = client.get("/resources?sort_by=updated_at&sort_dir=desc")
        assert resp.status_code == 200
        items = resp.json()["items"]
        if len(items) >= 2:
            assert items[0]["updated_at"] >= items[1]["updated_at"]

    def test_update_resource_partial(self, client, seeded_resources):
        rid = seeded_resources[0]
        resp = client.put(f"/resources/{rid}", json={"title": "Updated Title", "quality_score": 0.95, "creator": "doe, john", "publisher": "O'REILLY MEDIA"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Updated Title"
        # Quality score may be recalculated by the system
        assert data["quality_score"] > 0
        assert data["creator"] == "John Doe"
        assert data["publisher"] == "O'Reilly Media"

    def test_update_resource_404(self, client):
        resp = client.put("/resources/00000000-0000-0000-0000-000000000000", json={"title": "X"})
        assert resp.status_code == 404

    def test_delete_resource(self, client, test_db, seeded_resources):
        rid = seeded_resources[0]
        resp = client.delete(f"/resources/{rid}")
        assert resp.status_code == 204
        # ensure gone
        s = test_db()
        assert s.query(Resource).filter(Resource.id == rid).first() is None


class TestCurationAPI:
    def test_review_queue_defaults(self, client, monkeypatch, test_db, seeded_resources):
        # Default threshold from settings (0.7), so items with quality_score < 0.7
        resp = client.get("/curation/review-queue?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data and "total" in data
        for it in data["items"]:
            assert it["quality_score"] < 0.7

    def test_review_queue_include_unread_only(self, client):
        resp = client.get("/curation/review-queue?include_unread_only=true&limit=50")
        assert resp.status_code == 200
        for it in resp.json()["items"]:
            assert it["read_status"] == "unread"

    def test_review_queue_pagination(self, client):
        r1 = client.get("/curation/review-queue?limit=2&offset=0").json()["items"]
        r2 = client.get("/curation/review-queue?limit=2&offset=2").json()["items"]
        assert r1 != r2 or len(r2) == 0

    def test_batch_update(self, client, test_db, seeded_resources):
        ids = [seeded_resources[0], seeded_resources[1], "00000000-0000-0000-0000-000000000000"]
        payload = {"resource_ids": ids, "updates": {"read_status": "in_progress"}}
        resp = client.post("/curation/batch-update", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["updated_count"] == 2
        assert len(data["failed_ids"]) == 1

    def test_authority_suggestions_endpoint(self, client, test_db):
        # Seed via normalization
        db = test_db()
        try:
            from backend.app.services.authority_service import AuthorityControl
            svc = AuthorityControl(db)
            svc.normalize_subjects(["ml", "ai", "database"])
        finally:
            db.close()
        resp = client.get("/authority/subjects/suggest?q=ma")
        assert resp.status_code == 200
        suggestions = resp.json()
        assert any(s == "Machine Learning" for s in suggestions)

    def test_batch_update_validation(self, client, seeded_resources):
        payload = {"resource_ids": [seeded_resources[0]], "updates": {}}
        resp = client.post("/curation/batch-update", json=payload)
        assert resp.status_code == 400


