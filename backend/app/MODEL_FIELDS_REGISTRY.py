"""
Model Fields Registry
Generated from backend/app/database/models.py

This registry maps model names to their valid field names for validation.
Use this to ensure all model instantiations use only valid fields.
"""

MODEL_FIELDS = {
    "Resource": [
        # Primary key
        "id",
        
        # Dublin Core required fields
        "title",
        
        # Dublin Core optional fields
        "description",
        "creator",
        "publisher",
        "contributor",
        "date_created",
        "date_modified",
        "type",
        "format",
        "identifier",
        "source",
        "language",
        "coverage",
        "rights",
        
        # JSON arrays for multi-valued fields
        "subject",
        "relation",
        
        # Custom fields
        "classification_code",
        "read_status",
        "quality_score",
        
        # Phase 9: Multi-Dimensional Quality Assessment Fields
        "quality_accuracy",
        "quality_completeness",
        "quality_consistency",
        "quality_timeliness",
        "quality_relevance",
        "quality_overall",
        "quality_weights",
        
        # Summarization quality metrics
        "summary_coherence",
        "summary_consistency",
        "summary_fluency",
        "summary_relevance",
        "summary_completeness",
        "summary_conciseness",
        "summary_bertscore",
        "summary_quality_overall",
        
        # Anomaly detection fields
        "is_quality_outlier",
        "outlier_score",
        "outlier_reasons",
        
        # Quality metadata
        "quality_last_computed",
        "quality_computation_version",
        "needs_quality_review",
        
        # Ingestion workflow fields
        "ingestion_status",
        "ingestion_error",
        "ingestion_started_at",
        "ingestion_completed_at",
        
        # Vector embedding for Phase 4 hybrid search
        "embedding",
        
        # Phase 8: Sparse vector embeddings
        "sparse_embedding",
        "sparse_embedding_model",
        "sparse_embedding_updated_at",
        
        # Phase 6.5: Scholarly Metadata Fields
        "authors",
        "affiliations",
        "doi",
        "pmid",
        "arxiv_id",
        "isbn",
        "journal",
        "conference",
        "volume",
        "issue",
        "pages",
        "publication_year",
        "funding_sources",
        "acknowledgments",
        
        # Content Structure Counts
        "equation_count",
        "table_count",
        "figure_count",
        "reference_count",
        
        # Structured Content Storage
        "equations",
        "tables",
        "figures",
        
        # Metadata Quality
        "metadata_completeness_score",
        "extraction_confidence",
        "requires_manual_review",
        
        # OCR Metadata
        "is_ocr_processed",
        "ocr_confidence",
        "ocr_corrections_applied",
        
        # Audit fields
        "created_at",
        "updated_at",
        
        # Relationships (not direct fields, but included for reference)
        # "collections",
        # "annotations",
    ],
    
    "TaxonomyNode": [
        # Primary key
        "id",
        
        # Core metadata
        "name",
        "slug",
        
        # Hierarchical structure
        "parent_id",
        "level",
        "path",
        
        # Additional metadata
        "description",
        "keywords",
        
        # Cached resource counts
        "resource_count",
        "descendant_resource_count",
        
        # Metadata flags
        "is_leaf",
        "allow_resources",
        
        # Audit fields
        "created_at",
        "updated_at",
        
        # Relationships (not direct fields, but included for reference)
        # "parent",
        # "children",
    ],
    
    "Citation": [
        # Primary key
        "id",
        
        # Foreign keys
        "source_resource_id",
        "target_resource_id",
        
        # Citation metadata
        "target_url",
        "citation_type",
        "context_snippet",
        "position",
        
        # Computed fields
        "importance_score",
        
        # Audit fields
        "created_at",
        "updated_at",
    ],
    
    "Collection": [
        # Primary key
        "id",
        
        # Core metadata
        "name",
        "description",
        
        # Ownership and access control
        "owner_id",
        "visibility",
        
        # Hierarchical structure
        "parent_id",
        
        # Semantic representation
        "embedding",
        
        # Audit fields
        "created_at",
        "updated_at",
        
        # Relationships (not direct fields)
        # "parent",
        # "subcollections",
        # "resources",
    ],
    
    "CollectionResource": [
        # Composite primary key
        "collection_id",
        "resource_id",
        
        # Timestamp
        "added_at",
    ],
    
    "ClassificationCode": [
        "code",
        "title",
        "description",
        "parent_code",
        "keywords",
    ],
    
    "AuthoritySubject": [
        "id",
        "canonical_form",
        "variants",
        "usage_count",
    ],
    
    "AuthorityCreator": [
        "id",
        "canonical_form",
        "variants",
        "usage_count",
    ],
    
    "AuthorityPublisher": [
        "id",
        "canonical_form",
        "variants",
        "usage_count",
    ],
    
    "ResourceTaxonomy": [
        "id",
        "resource_id",
        "taxonomy_node_id",
        "confidence",
        "is_predicted",
        "predicted_by",
        "needs_review",
        "review_priority",
        "created_at",
        "updated_at",
    ],
    
    "Annotation": [
        "id",
        "resource_id",
        "user_id",
        "start_offset",
        "end_offset",
        "highlighted_text",
        "note",
        "tags",
        "color",
        "embedding",
        "context_before",
        "context_after",
        "is_shared",
        "collection_ids",
        "created_at",
        "updated_at",
    ],
    
    "GraphEdge": [
        "id",
        "source_id",
        "target_id",
        "edge_type",
        "weight",
        "edge_metadata",
        "created_by",
        "confidence",
        "created_at",
        "updated_at",
    ],
    
    "GraphEmbedding": [
        "id",
        "resource_id",
        "structural_embedding",
        "fusion_embedding",
        "embedding_method",
        "embedding_version",
        "hnsw_index_id",
        "created_at",
        "updated_at",
    ],
    
    "DiscoveryHypothesis": [
        "id",
        "a_resource_id",
        "c_resource_id",
        "b_resource_ids",
        "hypothesis_type",
        "plausibility_score",
        "path_strength",
        "path_length",
        "common_neighbors",
        "discovered_at",
        "user_id",
        "is_validated",
        "validation_notes",
    ],
}


# Common invalid fields that should NOT be used
INVALID_FIELDS = {
    "Resource": [
        "summary",  # Use "description" instead
        "resource_type",  # Use "type" instead
        "content",  # Not a field in the model
        "url",  # Use "source" or "identifier" instead
        "content_type",  # Use "format" instead
    ],
    "TaxonomyNode": [
        "title",  # Use "name" instead
    ],
    "Citation": [
        "resource_id",  # Use "source_resource_id" instead
        "cited_resource_id",  # Use "target_resource_id" instead
    ],
}
