"""
Neo Alexandria 2.0 - Personal Classification Service

This module implements the Personal Classification System for Neo Alexandria 2.0.
It provides rule-based classification using UDC-inspired codes with keyword matching
and hierarchical organization, with optional ML-based classification integration.

Related files:
- app/database/models.py: ClassificationCode model and Resource model
- app/services/resource_service.py: Uses classification during resource processing
- app/routers/classification.py: API endpoints for classification management
- app/schemas/: Pydantic schemas for classification data validation
- app/services/ml_classification_service.py: ML classification integration
- app/services/taxonomy_service.py: Taxonomy-based classification storage

Features:
- UDC-inspired 000-999 classification hierarchy
- Rule-based keyword matching with weighted scoring
- ML-based classification with confidence scores (Phase 8.5)
- Hierarchical classification tree management
- Reclassification suggestions for existing resources
- Automatic seeding of top-level classification codes
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
import re
import uuid

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


class ClassificationService:
    """
    Unified classification service integrating ML and rule-based approaches.
    
    This service provides a unified interface for resource classification,
    supporting both ML-based classification (using transformer models) and
    rule-based classification (using keyword matching). The service can be
    configured to use either approach via the use_ml flag.
    
    Features:
    - ML-based classification with confidence scores
    - Rule-based classification fallback
    - Confidence threshold filtering (>=0.3)
    - Integration with TaxonomyService for storing classifications
    - Automatic flagging of low-confidence predictions for review
    
    Requirements: 6.5, 12.4, 12.5
    """
    
    def __init__(
        self,
        db: Session,
        use_ml: bool = True,
        confidence_threshold: float = 0.3
    ):
        """
        Initialize the classification service.
        
        Args:
            db: SQLAlchemy database session
            use_ml: Whether to use ML classifier (True) or rule-based (False)
            confidence_threshold: Minimum confidence for predictions (default: 0.3)
        """
        self.db = db
        self.use_ml = use_ml
        self.confidence_threshold = confidence_threshold
        
        # Initialize rule-based classifier
        self.rule_based_classifier = PersonalClassification()
        
        # Lazy-load ML classifier and taxonomy service
        self._ml_classifier = None
        self._taxonomy_service = None
    
    @property
    def ml_classifier(self):
        """Lazy-load ML classification service."""
        if self._ml_classifier is None and self.use_ml:
            try:
                from .ml_classification_service import MLClassificationService
                self._ml_classifier = MLClassificationService(
                    db=self.db,
                    model_name="distilbert-base-uncased",
                    model_version="v1.0"
                )
            except Exception as e:
                print(f"Warning: Failed to load ML classifier: {e}")
                # Fall back to rule-based
                self.use_ml = False
        return self._ml_classifier
    
    @property
    def taxonomy_service(self):
        """Lazy-load taxonomy service."""
        if self._taxonomy_service is None:
            try:
                from .taxonomy_service import TaxonomyService
                self._taxonomy_service = TaxonomyService(db=self.db)
            except Exception as e:
                print(f"Warning: Failed to load taxonomy service: {e}")
        return self._taxonomy_service
    
    def classify_resource(
        self,
        resource_id: uuid.UUID,
        use_ml: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Classify a resource using ML or rule-based approach.
        
        This method retrieves resource content, performs classification using
        either the ML classifier or rule-based classifier, filters predictions
        by confidence threshold, and stores the results using TaxonomyService.
        
        Algorithm:
        1. Query resource by ID
        2. Extract content (title, description, tags)
        3. If use_ml is True:
           a. Use ML classifier to predict taxonomy nodes
           b. Filter predictions by confidence threshold (>=0.3)
           c. Store classifications with TaxonomyService
        4. Else:
           a. Use rule-based classifier
           b. Store with confidence 1.0 (rule-based is deterministic)
        5. Return classification results
        
        Args:
            resource_id: UUID of resource to classify
            use_ml: Override instance use_ml setting (optional)
            
        Returns:
            Dictionary with classification results:
            {
                "resource_id": str,
                "method": "ml" or "rule_based",
                "classifications": [
                    {
                        "taxonomy_node_id": str,
                        "confidence": float,
                        "needs_review": bool
                    },
                    ...
                ],
                "filtered_count": int  # Number of predictions below threshold
            }
            
        Raises:
            ValueError: If resource not found
            
        Requirements: 6.5, 12.4, 12.5
        """
        # Determine which classifier to use
        use_ml_classifier = use_ml if use_ml is not None else self.use_ml
        
        # Query resource
        resource = self.db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            raise ValueError(f"Resource with id {resource_id} not found")
        
        # Extract content for classification
        title = resource.title or ""
        description = resource.description or ""
        tags = resource.subject or []
        
        # Combine content for ML classification
        content = f"{title}. {description}"
        
        classifications = []
        filtered_count = 0
        method = "rule_based"
        
        if use_ml_classifier and self.ml_classifier:
            # Use ML classifier
            method = "ml"
            try:
                # Predict taxonomy nodes
                predictions = self.ml_classifier.predict(text=content, top_k=5)
                
                # Filter by confidence threshold
                filtered_predictions = {}
                for node_id, confidence in predictions.items():
                    if confidence >= self.confidence_threshold:
                        filtered_predictions[node_id] = confidence
                    else:
                        filtered_count += 1
                
                # Prepare classifications for TaxonomyService
                if filtered_predictions and self.taxonomy_service:
                    classification_list = [
                        {
                            "taxonomy_node_id": uuid.UUID(node_id),
                            "confidence": confidence
                        }
                        for node_id, confidence in filtered_predictions.items()
                    ]
                    
                    # Store classifications
                    stored = self.taxonomy_service.classify_resource(
                        resource_id=resource_id,
                        classifications=classification_list,
                        predicted_by=f"ml_model_{self.ml_classifier.model_version}"
                    )
                    
                    # Build response
                    for rt in stored:
                        classifications.append({
                            "taxonomy_node_id": str(rt.taxonomy_node_id),
                            "confidence": rt.confidence,
                            "needs_review": rt.needs_review
                        })
                
            except Exception as e:
                print(f"ML classification failed: {e}, falling back to rule-based")
                # Fall back to rule-based
                use_ml_classifier = False
        
        if not use_ml_classifier:
            # Use rule-based classifier
            method = "rule_based"
            try:
                # Get classification code
                code = self.rule_based_classifier.auto_classify(
                    title=title,
                    description=description,
                    tags=tags
                )
                
                # For rule-based, we return the code with confidence 1.0
                # Note: This doesn't integrate with taxonomy service yet
                # as rule-based uses ClassificationCode, not TaxonomyNode
                classifications.append({
                    "classification_code": code,
                    "confidence": 1.0,
                    "needs_review": False
                })
                
            except Exception as e:
                print(f"Rule-based classification failed: {e}")
                raise
        
        return {
            "resource_id": str(resource_id),
            "method": method,
            "classifications": classifications,
            "filtered_count": filtered_count
        }


