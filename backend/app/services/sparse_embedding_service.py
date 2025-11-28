"""
Neo Alexandria 2.0 - Sparse Embedding Service (Phase 8)

This module provides sparse vector embedding generation and search capabilities
using the BGE-M3 model. Sparse embeddings complement dense vectors by providing
learned keyword representations that capture term importance beyond traditional TF-IDF.

Related files:
- app/services/ai_core.py: Dense embedding generation
- app/services/search_service.py: Search orchestration
- app/database/models.py: Resource model with sparse_embedding fields

Features:
- Sparse vector generation using BGE-M3 model
- Batch processing for efficient embedding generation
- Sparse vector similarity search
- Resource update methods for single and batch operations
- GPU acceleration with CPU fallback
- Comprehensive error handling and logging
"""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..database.models import Resource

# Lazy import transformers and torch to avoid heavy imports at module load
try:
    from transformers import AutoModel, AutoTokenizer
    import torch
except ImportError:  # pragma: no cover
    AutoModel = None
    AutoTokenizer = None
    torch = None

# Setup logging
logger = logging.getLogger(__name__)


class SparseEmbeddingService:
    """Service for generating and managing sparse vector embeddings using BGE-M3 model.
    
    Sparse embeddings provide learned keyword representations with 50-200 non-zero
    dimensions, capturing term importance for technical and keyword-focused queries.
    """
    
    def __init__(
        self,
        db: Session,
        model_name: str = "BAAI/bge-m3"
    ):
        """Initialize the sparse embedding service.
        
        Args:
            db: Database session for resource operations
            model_name: Hugging Face model identifier (default: BAAI/bge-m3)
        """
        self.db = db
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        self._model_lock = threading.Lock()
        self._device = None
    
    def _ensure_loaded(self) -> bool:
        """Lazy load the BGE-M3 model in a thread-safe manner.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        if self._model is not None:
            return True
        
        with self._model_lock:
            # Double-check locking pattern
            if self._model is not None:
                return True
            
            # Check if dependencies are available
            if AutoModel is None or AutoTokenizer is None or torch is None:
                logger.error("transformers or torch not available for sparse embeddings")
                return False
            
            try:
                logger.info(f"Loading sparse embedding model: {self.model_name}")
                
                # Determine device (GPU if available, else CPU)
                if torch.cuda.is_available():
                    self._device = "cuda"
                    logger.info("Using GPU for sparse embedding generation")
                else:
                    self._device = "cpu"
                    logger.info("Using CPU for sparse embedding generation")
                
                # Load model and tokenizer
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self._model = AutoModel.from_pretrained(self.model_name)
                self._model.to(self._device)
                self._model.eval()  # Set to evaluation mode
                
                logger.info(f"Successfully loaded {self.model_name} on {self._device}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load sparse embedding model: {e}", exc_info=True)
                self._model = None
                self._tokenizer = None
                self._device = None
                return False
    
    def generate_sparse_embedding(self, text: str) -> Dict[int, float]:
        """Generate sparse vector embedding for single text.
        
        Algorithm:
        1. Tokenize input text (max 512 tokens)
        2. Forward pass through BGE-M3 model
        3. Extract sparse representation layer
        4. Apply ReLU + log transformation (SPLADE-style)
        5. Select top-200 non-zero dimensions
        6. Normalize weights to [0, 1]
        
        Args:
            text: Input text to embed
            
        Returns:
            Dictionary mapping token IDs to normalized weights {token_id: weight}
            Returns empty dict if model unavailable or text is empty
        """
        text = (text or "").strip()
        if not text:
            return {}
        
        # Ensure model is loaded
        if not self._ensure_loaded():
            logger.warning("Sparse embedding model not available, returning empty embedding")
            return {}
        
        try:
            # Tokenize with truncation
            inputs = self._tokenizer(
                text,
                max_length=512,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Generate embeddings with no gradient computation
            with torch.no_grad():
                outputs = self._model(**inputs, return_dict=True)
                
                # Extract sparse representation
                # BGE-M3 uses last hidden state for sparse vectors
                hidden_states = outputs.last_hidden_state
                
                # Apply SPLADE-style transformation: ReLU + log(1 + x)
                # Sum over sequence length to get document-level representation
                sparse_vec = torch.sum(
                    torch.log(1 + torch.relu(hidden_states)),
                    dim=1
                ).squeeze()
                
                # Move to CPU for processing
                sparse_vec = sparse_vec.cpu()
                
                # Get top-K non-zero values (K=200)
                values, indices = torch.topk(sparse_vec, k=min(200, len(sparse_vec)))
                
                # Filter out zeros and very small values
                mask = values > 1e-6
                values = values[mask]
                indices = indices[mask]
                
                # Normalize to [0, 1] range
                if len(values) > 0:
                    min_val = values.min()
                    max_val = values.max()
                    if max_val > min_val:
                        values = (values - min_val) / (max_val - min_val)
                    else:
                        values = torch.ones_like(values)
                
                # Convert to dictionary
                sparse_dict = {
                    int(idx): float(val)
                    for idx, val in zip(indices.tolist(), values.tolist())
                }
                
                return sparse_dict
                
        except RuntimeError as e:
            # Handle GPU out of memory errors
            if "out of memory" in str(e).lower() and self._device == "cuda":
                logger.warning("GPU OOM during sparse embedding, falling back to CPU")
                torch.cuda.empty_cache()
                
                # Retry on CPU
                try:
                    self._device = "cpu"
                    self._model.to(self._device)
                    return self.generate_sparse_embedding(text)
                except Exception as retry_e:
                    logger.error(f"Failed to generate sparse embedding on CPU: {retry_e}")
                    return {}
            else:
                logger.error(f"Failed to generate sparse embedding: {e}", exc_info=True)
                return {}
                
        except Exception as e:
            logger.error(f"Failed to generate sparse embedding: {e}", exc_info=True)
            return {}
    
    def generate_sparse_embeddings_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None
    ) -> List[Dict[int, float]]:
        """Batch generate sparse embeddings for efficiency.
        
        Args:
            texts: List of input texts to embed
            batch_size: Batch size for processing (default: 32 for GPU, 8 for CPU)
            
        Returns:
            List of sparse embedding dictionaries, one per input text
        """
        if not texts:
            return []
        
        # Ensure model is loaded
        if not self._ensure_loaded():
            logger.warning("Sparse embedding model not available, returning empty embeddings")
            return [{} for _ in texts]
        
        # Determine batch size based on device
        if batch_size is None:
            batch_size = 32 if self._device == "cuda" else 8
        
        results = []
        
        try:
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                # Filter empty texts
                non_empty_indices = [j for j, t in enumerate(batch_texts) if (t or "").strip()]
                non_empty_texts = [batch_texts[j] for j in non_empty_indices]
                
                if not non_empty_texts:
                    # All texts in batch are empty
                    results.extend([{} for _ in batch_texts])
                    continue
                
                # Tokenize batch
                inputs = self._tokenizer(
                    non_empty_texts,
                    max_length=512,
                    padding=True,
                    truncation=True,
                    return_tensors="pt"
                )
                
                # Move to device
                inputs = {k: v.to(self._device) for k, v in inputs.items()}
                
                # Generate embeddings
                with torch.no_grad():
                    outputs = self._model(**inputs, return_dict=True)
                    hidden_states = outputs.last_hidden_state
                    
                    # Apply SPLADE transformation
                    sparse_vecs = torch.sum(
                        torch.log(1 + torch.relu(hidden_states)),
                        dim=1
                    )
                    
                    # Move to CPU
                    sparse_vecs = sparse_vecs.cpu()
                    
                    # Process each vector in batch
                    batch_results = []
                    for sparse_vec in sparse_vecs:
                        # Get top-K
                        values, indices = torch.topk(sparse_vec, k=min(200, len(sparse_vec)))
                        
                        # Filter and normalize
                        mask = values > 1e-6
                        values = values[mask]
                        indices = indices[mask]
                        
                        if len(values) > 0:
                            min_val = values.min()
                            max_val = values.max()
                            if max_val > min_val:
                                values = (values - min_val) / (max_val - min_val)
                            else:
                                values = torch.ones_like(values)
                        
                        sparse_dict = {
                            int(idx): float(val)
                            for idx, val in zip(indices.tolist(), values.tolist())
                        }
                        batch_results.append(sparse_dict)
                    
                    # Merge results back with empty texts
                    full_batch_results = []
                    non_empty_idx = 0
                    for j in range(len(batch_texts)):
                        if j in non_empty_indices:
                            full_batch_results.append(batch_results[non_empty_idx])
                            non_empty_idx += 1
                        else:
                            full_batch_results.append({})
                    
                    results.extend(full_batch_results)
                
                # Clear GPU cache periodically
                if self._device == "cuda" and i % (batch_size * 10) == 0:
                    torch.cuda.empty_cache()
        
        except RuntimeError as e:
            # Handle GPU OOM
            if "out of memory" in str(e).lower() and self._device == "cuda":
                logger.warning("GPU OOM during batch processing, falling back to CPU")
                torch.cuda.empty_cache()
                
                # Retry with CPU and smaller batch size
                self._device = "cpu"
                self._model.to(self._device)
                return self.generate_sparse_embeddings_batch(texts, batch_size=4)
            else:
                logger.error(f"Failed batch sparse embedding generation: {e}", exc_info=True)
                # Return empty embeddings for remaining texts
                results.extend([{} for _ in range(len(texts) - len(results))])
        
        except Exception as e:
            logger.error(f"Failed batch sparse embedding generation: {e}", exc_info=True)
            # Return empty embeddings for remaining texts
            results.extend([{} for _ in range(len(texts) - len(results))])
        
        return results

    def search_by_sparse_vector(
        self,
        query_sparse: Dict[int, float],
        limit: int = 100,
        min_score: float = 0.0
    ) -> List[Tuple[str, float]]:
        """Search resources using sparse vector similarity.
        
        Computes sparse dot product between query and resource sparse embeddings.
        
        Args:
            query_sparse: Query sparse vector as {token_id: weight} dict
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold
            
        Returns:
            List of (resource_id, similarity_score) tuples sorted by score descending
        """
        if not query_sparse:
            return []
        
        try:
            # Query all resources with sparse embeddings
            resources = self.db.query(Resource).filter(
                Resource.sparse_embedding.isnot(None)
            ).all()
            
            scores = []
            
            for resource in resources:
                try:
                    # Parse sparse embedding JSON
                    resource_sparse = json.loads(resource.sparse_embedding)
                    
                    # Compute sparse dot product (only overlapping dimensions)
                    score = 0.0
                    for token_id, query_weight in query_sparse.items():
                        # Convert token_id to string for JSON key lookup
                        resource_weight = resource_sparse.get(str(token_id), 0.0)
                        score += query_weight * resource_weight
                    
                    # Apply minimum score filter
                    if score >= min_score:
                        scores.append((str(resource.id), score))
                
                except (json.JSONDecodeError, TypeError, ValueError) as e:
                    logger.warning(f"Failed to parse sparse embedding for resource {resource.id}: {e}")
                    continue
            
            # Sort by score descending and limit
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[:limit]
        
        except Exception as e:
            logger.error(f"Failed sparse vector search: {e}", exc_info=True)
            return []
    
    def update_resource_sparse_embedding(self, resource_id: str) -> bool:
        """Generate and store sparse embedding for a single resource.
        
        Args:
            resource_id: UUID of the resource to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch resource
            resource = self.db.query(Resource).filter(
                Resource.id == resource_id
            ).first()
            
            if not resource:
                logger.warning(f"Resource {resource_id} not found")
                return False
            
            # Create composite text from resource
            text_parts = []
            if resource.title:
                text_parts.append(resource.title)
            if resource.description:
                text_parts.append(resource.description)
            if resource.subject:
                try:
                    if isinstance(resource.subject, list):
                        subjects_text = " ".join(resource.subject)
                        if subjects_text.strip():
                            text_parts.append(f"Keywords: {subjects_text}")
                except Exception:
                    pass
            
            composite_text = " ".join(text_parts)
            
            # Handle empty content gracefully
            if not composite_text.strip():
                logger.info(f"Resource {resource_id} has no content for sparse embedding")
                resource.sparse_embedding = None
                resource.sparse_embedding_model = None
                resource.sparse_embedding_updated_at = datetime.now(timezone.utc)
                self.db.commit()
                return True
            
            # Generate sparse embedding
            sparse_vec = self.generate_sparse_embedding(composite_text)
            
            # Store as JSON string
            resource.sparse_embedding = json.dumps(sparse_vec) if sparse_vec else None
            resource.sparse_embedding_model = self.model_name if sparse_vec else None
            resource.sparse_embedding_updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            logger.debug(f"Updated sparse embedding for resource {resource_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to update sparse embedding for resource {resource_id}: {e}", exc_info=True)
            self.db.rollback()
            return False
    
    def batch_update_sparse_embeddings(
        self,
        resource_ids: Optional[List[str]] = None,
        batch_size: Optional[int] = None
    ) -> Dict[str, int]:
        """Batch update sparse embeddings for multiple resources.
        
        Processes resources in batches with periodic commits for efficiency.
        Commits every 100 resources to balance performance and recoverability.
        
        Args:
            resource_ids: Optional list of specific resource IDs to update.
                         If None, updates all resources without sparse embeddings.
            batch_size: Batch size for embedding generation (default: 32 for GPU, 8 for CPU)
            
        Returns:
            Dictionary with statistics: {
                'total': total resources processed,
                'success': successfully updated,
                'failed': failed updates,
                'skipped': skipped (empty content)
            }
        """
        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        try:
            # Build query for resources to update
            query = self.db.query(Resource)
            
            if resource_ids:
                # Update specific resources
                query = query.filter(Resource.id.in_(resource_ids))
            else:
                # Update resources without sparse embeddings
                query = query.filter(
                    (Resource.sparse_embedding.is_(None)) |
                    (Resource.sparse_embedding_updated_at.is_(None))
                )
            
            resources = query.all()
            stats['total'] = len(resources)
            
            if not resources:
                logger.info("No resources to update for sparse embeddings")
                return stats
            
            logger.info(f"Starting batch sparse embedding generation for {stats['total']} resources")
            
            # Determine batch size
            if batch_size is None:
                # Use device-appropriate batch size
                if self._ensure_loaded():
                    batch_size = 32 if self._device == "cuda" else 8
                else:
                    batch_size = 8
            
            # Process in batches
            commit_counter = 0
            
            for i in range(0, len(resources), batch_size):
                batch_resources = resources[i:i + batch_size]
                
                # Prepare texts for batch generation
                texts = []
                valid_indices = []
                
                for j, resource in enumerate(batch_resources):
                    text_parts = []
                    if resource.title:
                        text_parts.append(resource.title)
                    if resource.description:
                        text_parts.append(resource.description)
                    if resource.subject:
                        try:
                            if isinstance(resource.subject, list):
                                subjects_text = " ".join(resource.subject)
                                if subjects_text.strip():
                                    text_parts.append(f"Keywords: {subjects_text}")
                        except Exception:
                            pass
                    
                    composite_text = " ".join(text_parts)
                    
                    if composite_text.strip():
                        texts.append(composite_text)
                        valid_indices.append(j)
                    else:
                        # Mark as skipped
                        stats['skipped'] += 1
                        batch_resources[j].sparse_embedding = None
                        batch_resources[j].sparse_embedding_model = None
                        batch_resources[j].sparse_embedding_updated_at = datetime.now(timezone.utc)
                
                # Generate embeddings for valid texts
                if texts:
                    sparse_embeddings = self.generate_sparse_embeddings_batch(texts, batch_size)
                    
                    # Update resources with embeddings
                    for idx, sparse_vec in zip(valid_indices, sparse_embeddings):
                        resource = batch_resources[idx]
                        try:
                            resource.sparse_embedding = json.dumps(sparse_vec) if sparse_vec else None
                            resource.sparse_embedding_model = self.model_name if sparse_vec else None
                            resource.sparse_embedding_updated_at = datetime.now(timezone.utc)
                            stats['success'] += 1
                        except Exception as e:
                            logger.error(f"Failed to update resource {resource.id}: {e}")
                            stats['failed'] += 1
                
                # Commit every 100 resources
                commit_counter += len(batch_resources)
                if commit_counter >= 100:
                    try:
                        self.db.commit()
                        logger.info(f"Progress: {i + len(batch_resources)}/{stats['total']} resources processed")
                        commit_counter = 0
                    except Exception as e:
                        logger.error(f"Failed to commit batch: {e}")
                        self.db.rollback()
                        stats['failed'] += len(batch_resources)
            
            # Final commit for remaining resources
            if commit_counter > 0:
                try:
                    self.db.commit()
                    logger.info(f"Completed: {stats['total']} resources processed")
                except Exception as e:
                    logger.error(f"Failed final commit: {e}")
                    self.db.rollback()
            
            logger.info(
                f"Batch sparse embedding generation complete. "
                f"Success: {stats['success']}, Failed: {stats['failed']}, Skipped: {stats['skipped']}"
            )
            
            return stats
        
        except Exception as e:
            logger.error(f"Failed batch sparse embedding update: {e}", exc_info=True)
            self.db.rollback()
            return stats
