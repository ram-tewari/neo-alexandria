"""
Neo Alexandria 2.0 - Personal Classification Service

This module implements the Personal Classification System for Neo Alexandria 2.0.
It provides rule-based classification using UDC-inspired codes with keyword matching
and hierarchical organization.

Related files:
- app/database/models.py: ClassificationCode model and Resource model
- app/services/resource_service.py: Uses classification during resource processing
- app/routers/classification.py: API endpoints for classification management
- app/schemas/: Pydantic schemas for classification data validation

Features:
- UDC-inspired 000-999 classification hierarchy
- Rule-based keyword matching with weighted scoring
- Hierarchical classification tree management
- Reclassification suggestions for existing resources
- Automatic seeding of top-level classification codes
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
import re

from sqlalchemy.orm import Session

from ..database.models import ClassificationCode, Resource


class PersonalClassification:
    """Rule-based personal classifier with UDC-inspired 000-999 hierarchy.

    Top-level mapping rules:
    - Programming/software keywords -> "000"
    - Language learning/linguistics -> "400"
    - Science terms -> "500"
    - History dates/names -> "900"
    Fallback code: "000".
    """

    PROGRAMMING_KEYWORDS = [
        "programming",
        "software",
        "coding",
        "developer",
        "python",
        "java",
        "javascript",
        "typescript",
        "c++",
        "c#",
        "go",
        "rust",
        "algorithm",
        "data structure",
        "artificial intelligence",
        "ai",
        "machine learning",
        "ml",
        "natural language processing",
        "nlp",
        "deep learning",
        "neural networks",
    ]

    LANGUAGE_KEYWORDS = [
        "language",
        "linguistics",
        "grammar",
        "vocabulary",
        "pronunciation",
        "syntax",
        "semantics",
        "phonetics",
        "morphology",
    ]

    SCIENCE_KEYWORDS = [
        "science",
        "physics",
        "chemistry",
        "biology",
        "mathematics",
        "math",
        "algebra",
        "calculus",
        "astronomy",
        "geology",
        "ecology",
        "zoology",
        "botany",
    ]

    HISTORY_KEYWORDS = [
        "history",
        "ancient",
        "medieval",
        "renaissance",
        "empire",
        "revolution",
        "napoleon",
        "rome",
        "greece",
        "wwi",
        "wwii",
        "cold war",
    ]

    def auto_classify(
        self, title: Optional[str], description: Optional[str], tags: Optional[List[str]]
    ) -> str:
        """Return best-fit top-level code (000, 400, 500, 900).

        Priority: title > tags > description. Ties resolved by rule order below.
        """
        safe_tags = tags or []
        title_lower = (title or "").lower()
        description_lower = (description or "").lower()
        tags_lower = " ".join([t.strip().lower() for t in safe_tags])

        scores: Dict[str, int] = {"000": 0, "400": 0, "500": 0, "900": 0}

        def score_for_keywords(text: str, keywords: List[str], code: str, weight: int) -> None:
            if not text:
                return
            for kw in keywords:
                if self._contains_keyword(text, kw):
                    scores[code] += weight

        # Title weight highest
        score_for_keywords(title_lower, self.PROGRAMMING_KEYWORDS, "000", 3)
        score_for_keywords(title_lower, self.LANGUAGE_KEYWORDS, "400", 3)
        score_for_keywords(title_lower, self.SCIENCE_KEYWORDS, "500", 3)
        score_for_keywords(title_lower, self.HISTORY_KEYWORDS, "900", 3)

        # Tags medium
        score_for_keywords(tags_lower, self.PROGRAMMING_KEYWORDS, "000", 2)
        score_for_keywords(tags_lower, self.LANGUAGE_KEYWORDS, "400", 2)
        score_for_keywords(tags_lower, self.SCIENCE_KEYWORDS, "500", 2)
        score_for_keywords(tags_lower, self.HISTORY_KEYWORDS, "900", 2)

        # Description lowest
        score_for_keywords(description_lower, self.PROGRAMMING_KEYWORDS, "000", 1)
        score_for_keywords(description_lower, self.LANGUAGE_KEYWORDS, "400", 1)
        score_for_keywords(description_lower, self.SCIENCE_KEYWORDS, "500", 1)
        score_for_keywords(description_lower, self.HISTORY_KEYWORDS, "900", 1)

        # History: boost presence of 4-digit year tokens
        if self._contains_history_year(title_lower):
            scores["900"] += 3
        if self._contains_history_year(tags_lower):
            scores["900"] += 2
        if self._contains_history_year(description_lower):
            scores["900"] += 1

        # Determine best code by score, tie-break by precedence order
        # Programming (000) has highest precedence, then language (400), science (500), history (900)
        precedence = ["000", "400", "500", "900"]
        best_code = max(precedence, key=lambda c: (scores[c], -precedence.index(c)))
        if scores[best_code] == 0:
            return "000"
        return best_code

    def get_classification_tree(self, db: Session) -> Dict[str, Any]:
        """Return classification hierarchy for UI. Ensures seed exists."""
        self._ensure_seed(db)
        rows: List[ClassificationCode] = db.query(ClassificationCode).all()
        nodes: Dict[str, Dict[str, Any]] = {}
        children_map: Dict[str | None, List[str]] = {}

        for row in rows:
            nodes[row.code] = {
                "code": row.code,
                "name": row.title,  # Use 'name' instead of 'title' to match API docs
                "description": row.description,
                "keywords": row.keywords or [],
                "children": [],
            }
            parent = row.parent_code
            children_map.setdefault(parent, []).append(row.code)

        # Attach children
        for parent_code, codes in children_map.items():
            if parent_code is None:
                continue
            if parent_code in nodes:
                nodes[parent_code]["children"] = [nodes[c] for c in codes]

        # Return top-level forest as an array wrapped in a tree property
        top_codes = children_map.get(None, [])
        tree_nodes = [nodes[c] for c in top_codes]
        return {"tree": tree_nodes}

    def suggest_reclassification(self, db: Session, resource_id) -> List[str]:
        """Return suggestion list of top codes for ML handoff.

        Uses rule scores to rank codes; returns ordered list of codes.
        """
        res: Resource | None = db.query(Resource).filter(Resource.id == resource_id).first()
        if res is None:
            return []
        candidates = self._score_all(
            title=res.title,
            description=res.description or "",
            tags=res.subject or [],
        )
        # Sort by score desc, then precedence
        precedence = ["000", "400", "500", "900"]
        ordered = sorted(candidates.items(), key=lambda kv: (kv[1], -precedence.index(kv[0])), reverse=True)
        return [code for code, score in ordered if score > 0][:5]

    def _score_all(self, title: str, description: str, tags: List[str]) -> Dict[str, int]:
        title_lower = (title or "").lower()
        description_lower = (description or "").lower()
        tags_lower = " ".join([t.strip().lower() for t in (tags or [])])

        scores: Dict[str, int] = {"000": 0, "400": 0, "500": 0, "900": 0}

        def score_kws(text: str, kws: List[str], code: str, weight: int) -> None:
            if not text:
                return
            for kw in kws:
                if self._contains_keyword(text, kw):
                    scores[code] += weight

        score_kws(title_lower, self.PROGRAMMING_KEYWORDS, "000", 3)
        score_kws(title_lower, self.LANGUAGE_KEYWORDS, "400", 3)
        score_kws(title_lower, self.SCIENCE_KEYWORDS, "500", 3)
        score_kws(title_lower, self.HISTORY_KEYWORDS, "900", 3)

        score_kws(tags_lower, self.PROGRAMMING_KEYWORDS, "000", 2)
        score_kws(tags_lower, self.LANGUAGE_KEYWORDS, "400", 2)
        score_kws(tags_lower, self.SCIENCE_KEYWORDS, "500", 2)
        score_kws(tags_lower, self.HISTORY_KEYWORDS, "900", 2)

        score_kws(description_lower, self.PROGRAMMING_KEYWORDS, "000", 1)
        score_kws(description_lower, self.LANGUAGE_KEYWORDS, "400", 1)
        score_kws(description_lower, self.SCIENCE_KEYWORDS, "500", 1)
        score_kws(description_lower, self.HISTORY_KEYWORDS, "900", 1)

        if self._contains_history_year(title_lower):
            scores["900"] += 3
        if self._contains_history_year(tags_lower):
            scores["900"] += 2
        if self._contains_history_year(description_lower):
            scores["900"] += 1

        return scores

    def _contains_keyword(self, text: str, keyword: str) -> bool:
        if not text or not keyword:
            return False
        if " " in keyword:
            return keyword in text
        pattern = r"\b" + re.escape(keyword) + r"\b"
        return bool(re.search(pattern, text))

    def _contains_history_year(self, text: str) -> bool:
        if not text:
            return False
        return bool(re.search(r"\b(1[0-9]{3}|20[01][0-9])\b", text))

    def _ensure_seed(self, db: Session) -> None:
        """Seed top-level UDC-inspired codes if table is empty (useful in tests)."""
        if db.query(ClassificationCode).count() > 0:
            return
        seeds = [
            {
                "code": "000",
                "title": "Computer Science, Information & General Works",
                "description": "General knowledge, computing, information science",
                "parent_code": None,
                "keywords": list(set(self.PROGRAMMING_KEYWORDS + ["computer", "computing", "information"]))
            },
            {"code": "100", "title": "Philosophy & Psychology", "description": None, "parent_code": None, "keywords": []},
            {"code": "200", "title": "Religion & Theology", "description": None, "parent_code": None, "keywords": []},
            {"code": "300", "title": "Social Sciences", "description": None, "parent_code": None, "keywords": []},
            {
                "code": "400",
                "title": "Language & Linguistics",
                "description": "Languages, linguistics, grammar and related topics",
                "parent_code": None,
                "keywords": self.LANGUAGE_KEYWORDS,
            },
            {
                "code": "500",
                "title": "Pure Sciences",
                "description": "Mathematics, physics, chemistry, biology, etc.",
                "parent_code": None,
                "keywords": self.SCIENCE_KEYWORDS,
            },
            {"code": "600", "title": "Technology & Applied Sciences", "description": None, "parent_code": None, "keywords": []},
            {"code": "700", "title": "Arts & Recreation", "description": None, "parent_code": None, "keywords": []},
            {"code": "800", "title": "Literature", "description": None, "parent_code": None, "keywords": []},
            {
                "code": "900",
                "title": "History & Geography",
                "description": "Historical events, figures, and geography",
                "parent_code": None,
                "keywords": list(set(self.HISTORY_KEYWORDS + ["geography"]))
            },
        ]
        for row in seeds:
            db.add(ClassificationCode(**row))
        db.commit()


