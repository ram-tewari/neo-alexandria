"""Tests for authority control service."""


from backend.app.services.authority_service import AuthorityControl
from backend.app.database.models import AuthoritySubject


class TestAuthorityControl:
    """Test authority control functionality."""
    
    def test_normalize_subject_basic(self):
        authority = AuthorityControl()
        result = authority.normalize_subject("machine learning")
        assert result == "Machine Learning"
    
    def test_normalize_subject_synonym_mapping(self):
        authority = AuthorityControl()
        result = authority.normalize_subject("ml")
        assert result == "Machine Learning"
    
    def test_normalize_subject_multiple_synonyms(self):
        authority = AuthorityControl()
        test_cases = [
            ("ml", "Machine Learning"),
            ("ai", "Artificial Intelligence"),
            ("nlp", "Natural Language Processing"),
            ("py", "Python"),
        ]
        for input_term, expected in test_cases:
            result = authority.normalize_subject(input_term)
            assert result == expected
    
    def test_normalize_subject_punctuation_removal(self):
        authority = AuthorityControl()
        result = authority.normalize_subject("machine, learning; ai|nlp")
        assert result == "Machine Learning Ai Nlp"
    
    def test_normalize_subject_whitespace_normalization(self):
        authority = AuthorityControl()
        result = authority.normalize_subject("  machine   learning  ")
        assert result == "Machine Learning"
    
    def test_normalize_subject_small_words_lowercase(self):
        authority = AuthorityControl()
        result = authority.normalize_subject("art of machine learning")
        assert result == "Art of Machine Learning"
    
    def test_normalize_subject_small_words_first_last(self):
        authority = AuthorityControl()
        result1 = authority.normalize_subject("of machine learning")
        assert result1 == "Of Machine Learning"
        result2 = authority.normalize_subject("machine learning and")
        assert result2 == "Machine Learning And"
    
    def test_normalize_subject_empty_string(self):
        authority = AuthorityControl()
        result = authority.normalize_subject("")
        assert result == ""
    
    def test_normalize_subject_whitespace_only(self):
        authority = AuthorityControl()
        result = authority.normalize_subject("   ")
        assert result == ""
    
    def test_normalize_subject_single_word(self):
        authority = AuthorityControl()
        result = authority.normalize_subject("python")
        assert result == "Python"
    
    def test_normalize_subject_case_insensitive_synonyms(self):
        authority = AuthorityControl()
        test_cases = ["ML", "Ml", "ml", "mL"]
        for case in test_cases:
            result = authority.normalize_subject(case)
            assert result == "Machine Learning"
    
    def test_normalize_subjects_basic(self):
        authority = AuthorityControl()
        result = authority.normalize_subjects(["machine learning", "ai", "python"])
        assert result == ["Machine Learning", "Artificial Intelligence", "Python"]
    
    def test_normalize_subjects_deduplication(self):
        authority = AuthorityControl()
        result = authority.normalize_subjects(["ml", "machine learning", "ai", "ml"])
        assert result == ["Machine Learning", "Artificial Intelligence"]
    
    def test_normalize_subjects_preserves_order(self):
        authority = AuthorityControl()
        result = authority.normalize_subjects(["python", "ai", "ml", "programming"])
        expected = ["Python", "Artificial Intelligence", "Machine Learning", "Programming"]
        assert result == expected
    
    def test_normalize_subjects_empty_list(self):
        authority = AuthorityControl()
        result = authority.normalize_subjects([])
        assert result == []
    
    def test_normalize_subjects_none_input(self):
        authority = AuthorityControl()
        result = authority.normalize_subjects(None)
        assert result == []
    
    def test_normalize_subjects_filters_empty(self):
        authority = AuthorityControl()
        result = authority.normalize_subjects(["python", "", "   ", "ai"])
        assert result == ["Python", "Artificial Intelligence"]
    
    def test_normalize_subjects_mixed_case(self):
        authority = AuthorityControl()
        result = authority.normalize_subjects(["PYTHON", "Machine Learning", "ai"])
        assert result == ["Python", "Machine Learning", "Artificial Intelligence"]
    
    def test_normalize_subjects_with_punctuation(self):
        authority = AuthorityControl()
        result = authority.normalize_subjects(["machine, learning", "ai; nlp", "python|programming"])
        assert result == ["Machine Learning", "Ai Nlp", "Python Programming"]
    
    def test_normalize_subjects_complex_scenario(self):
        authority = AuthorityControl()
        input_tags = [
            "ml",
            "machine learning",
            "ai",
            "python programming",
            "nlp",
            "data science",
            "ml",
            "",
            "   ",
        ]
        result = authority.normalize_subjects(input_tags)
        expected = [
            "Machine Learning",
            "Artificial Intelligence", 
            "Python Programming",
            "Natural Language Processing",
            "Data Science"
        ]
        assert result == expected
    
    def test_authority_control_immutable_behavior(self):
        authority = AuthorityControl()
        original_tags = ["ml", "ai", "python"]
        result = authority.normalize_subjects(original_tags)
        assert original_tags == ["ml", "ai", "python"]
        assert result == ["Machine Learning", "Artificial Intelligence", "Python"]

    def test_variant_learning_and_usage_counts(self, test_db):
        db_session_factory = test_db
        db = db_session_factory()
        try:
            svc = AuthorityControl(db)
            # Normalize with variant first
            n1 = svc.normalize_subject("ML")
            assert n1 == "Machine Learning"
            n2 = svc.normalize_subjects(["ml", "machine learning", "Ml"])  # dedup counts once
            assert n2[0] == "Machine Learning"
            # Ensure row exists and has variants learned
            row = db.query(AuthoritySubject).filter(AuthoritySubject.canonical_form == "Machine Learning").first()
            assert row is not None
            assert row.usage_count >= 1
            # Add explicit variant
            svc.add_subject_variant("Machine Learning", "ML Systems")
            row2 = db.query(AuthoritySubject).filter(AuthoritySubject.canonical_form == "Machine Learning").first()
            assert any(v.lower() == "ml systems" for v in (row2.variants or []))
        finally:
            db.close()

    def test_subject_suggestions_endpoint_logic(self, test_db):
        db_session_factory = test_db
        db = db_session_factory()
        try:
            svc = AuthorityControl(db)
            # Seed a few subjects
            svc.normalize_subjects(["ml", "ai", "database"])  # creates rows and increments usage
            suggestions = svc.get_subject_suggestions("ma")  # should match 'Machine Learning'
            assert any(s == "Machine Learning" for s in suggestions)
            # Built-in mappings also surface
            builtin = svc.get_subject_suggestions("js")
            assert any(s == "JavaScript" for s in builtin)
        finally:
            db.close()
