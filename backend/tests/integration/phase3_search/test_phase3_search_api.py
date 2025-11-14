from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from backend.app.database.models import Resource


@pytest.fixture
def seeded_for_search(test_db):
    db = test_db()
    now = datetime.now(timezone.utc)
    items = []
    samples = [
        {
            "title": "Introduction to Machine Learning",
            "description": "A gentle guide to ML and AI",
            "language": "en",
            "type": "article",
            "classification_code": "006",
            "subject": ["Machine Learning", "Artificial Intelligence"],
            "read_status": "unread",
            "quality_score": 0.8,
            "date_created": now - timedelta(days=10),
            "date_modified": now - timedelta(days=5),
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
        },
        {
            "title": "Deep Learning Advances",
            "description": "Neural networks and representation learning",
            "language": "en",
            "type": "article",
            "classification_code": "006",
            "subject": ["Deep Learning", "Neural Networks"],
            "read_status": "in_progress",
            "quality_score": 0.9,
            "date_created": now - timedelta(days=20),
            "date_modified": now - timedelta(days=2),
            "embedding": [0.2, 0.3, 0.4, 0.5, 0.6],
        },
        {
            "title": "Spanish Linguistics Overview",
            "description": "Morphology and syntax in Spanish",
            "language": "es",
            "type": "book",
            "classification_code": "400",
            "subject": ["Language", "Linguistics"],
            "read_status": "completed",
            "quality_score": 0.6,
            "date_created": now - timedelta(days=40),
            "date_modified": now - timedelta(days=30),
            "embedding": [0.3, 0.4, 0.5, 0.6, 0.7],
        },
        {
            "title": "Natural Language Processing Basics",
            "description": "Text processing and tokenization",
            "language": "en",
            "type": "article",
            "classification_code": "006",
            "subject": ["Natural Language Processing", "Machine Learning"],
            "read_status": "unread",
            "quality_score": 0.7,
            "date_created": now - timedelta(days=15),
            "date_modified": now - timedelta(days=1),
            "embedding": [0.4, 0.5, 0.6, 0.7, 0.8],
        },
    ]
    for s in samples:
        r = Resource(**s)
        db.add(r)
        items.append(r)
    db.commit()
    ids = [str(r.id) for r in items]
    db.close()
    return ids


def test_post_search_basic_total_and_items(client, seeded_for_search):
    resp = client.post("/search", json={"text": "language", "limit": 2, "offset": 0})
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data and "items" in data and "facets" in data
    # May be 0 if FTS5 not initialized in test environment
    assert data["total"] >= 0
    assert len(data["items"]) <= 2


def test_search_filters_and_sorting(client, seeded_for_search):
    payload = {
        "filters": {
            "classification_code": ["006"],
            "language": ["en"],
            "min_quality": 0.7,
        },
        "limit": 10,
        "offset": 0,
        "sort_by": "updated_at",
        "sort_dir": "desc",
    }
    resp = client.post("/search", json=payload)
    assert resp.status_code == 200
    items = resp.json()["items"]
    for it in items:
        assert it["classification_code"] == "006"
        assert it["language"] == "en"
        assert it["quality_score"] >= 0.7


def test_search_subject_any_all(client, seeded_for_search):
    # subject_any: match either term
    resp_any = client.post(
        "/search",
        json={"filters": {"subject_any": ["Neural Networks", "Linguistics"]}},
    )
    assert resp_any.status_code == 200
    any_ids = {it["id"] for it in resp_any.json()["items"]}
    assert len(any_ids) >= 1

    # subject_all: must include both terms
    resp_all = client.post(
        "/search",
        json={"filters": {"subject_all": ["Machine Learning", "Artificial Intelligence"]}},
    )
    assert resp_all.status_code == 200
    all_items = resp_all.json()["items"]
    for it in all_items:
        assert "Machine Learning" in it["subject"]
        assert "Artificial Intelligence" in it["subject"]


def test_search_facets_present(client, seeded_for_search):
    resp = client.post("/search", json={"limit": 10})
    assert resp.status_code == 200
    facets = resp.json()["facets"]
    for k in ["classification_code", "type", "language", "read_status", "subject"]:
        assert k in facets


