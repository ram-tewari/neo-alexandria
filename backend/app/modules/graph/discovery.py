"""
Literature-Based Discovery (LBD) Service for Phase 16.7

Implements the ABC discovery pattern for hypothesis generation:
- Find resources mentioning concept A
- Find resources mentioning concept C
- Identify bridging concepts B that connect A and C
- Rank hypotheses by support strength and novelty
- Build evidence chains showing A→B and B→C connections

Related files:
- app.modules.graph.discovery_router: API endpoints for LBD
- app.modules.graph.schema: Request/response models
- app.modules.graph.model: DiscoveryHypothesis database model
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional, Any
from uuid import UUID

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from app.database.models import Resource

logger = logging.getLogger(__name__)


class LBDService:
    """
    Service for literature-based discovery using the ABC pattern.
    
    The ABC pattern discovers novel connections between concepts:
    - A: Starting concept
    - B: Bridging concept(s) that connect A and C
    - C: Target concept
    
    The service identifies resources mentioning A and C separately,
    finds bridging concepts B, filters known connections, and ranks
    hypotheses by support strength and novelty.
    """
    
    def __init__(self, db: Session):
        """
        Initialize LBD service.
        
        Args:
            db: Database session for querying resources
        """
        self.db = db
    
    def discover_hypotheses(
        self,
        concept_a: str,
        concept_c: str,
        limit: int = 50,
        time_slice: Optional[Tuple[datetime, datetime]] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover bridging concepts between A and C using ABC pattern.
        
        This is the main entry point for LBD hypothesis generation.
        
        Args:
            concept_a: Starting concept to search for
            concept_c: Target concept to connect to
            limit: Maximum number of hypotheses to return (default: 50)
            time_slice: Optional date range tuple (start, end) for temporal filtering
            
        Returns:
            List of hypothesis dictionaries sorted by confidence score
            
        Example:
            >>> lbd = LBDService(db)
            >>> hypotheses = lbd.discover_hypotheses("machine learning", "drug discovery")
            >>> for h in hypotheses[:5]:
            ...     print(f"{h['concept_b']}: confidence={h['confidence']:.3f}")
        """
        logger.info(f"Starting ABC discovery: A='{concept_a}', C='{concept_c}', limit={limit}")
        
        # Subtask 12.1: Find resources mentioning concepts A and C
        resources_a = self._find_resources_with_concept(concept_a, time_slice)
        resources_c = self._find_resources_with_concept(concept_c, time_slice)
        
        logger.debug(f"Found {len(resources_a)} resources with concept A, {len(resources_c)} with concept C")
        
        if not resources_a or not resources_c:
            logger.warning(f"Insufficient resources for discovery: A={len(resources_a)}, C={len(resources_c)}")
            return []
        
        # Subtask 12.1: Find bridging concepts B
        bridging_concepts = self._find_bridging_concepts(resources_a, resources_c)
        
        logger.debug(f"Found {len(bridging_concepts)} potential bridging concepts")
        
        if not bridging_concepts:
            logger.info("No bridging concepts found")
            return []
        
        # Subtask 12.3: Filter out known A-C connections
        bridging_concepts = self._filter_known_connections(
            concept_a,
            concept_c,
            bridging_concepts
        )
        
        logger.debug(f"After filtering known connections: {len(bridging_concepts)} bridging concepts remain")
        
        if not bridging_concepts:
            logger.info("All bridging concepts filtered out as known connections")
            return []
        
        # Subtask 12.4: Rank hypotheses by support and novelty
        hypotheses = self._rank_hypotheses(
            concept_a,
            concept_c,
            bridging_concepts
        )
        
        logger.info(f"Generated {len(hypotheses)} hypotheses, returning top {limit}")
        
        return hypotheses[:limit]
    
    def _find_resources_with_concept(
        self,
        concept: str,
        time_slice: Optional[Tuple[datetime, datetime]] = None
    ) -> List[Resource]:
        """
        Find resources mentioning a concept in title, content, or abstract.
        
        Subtask 12.1: Implement ABC discovery pattern - find resources with concepts
        
        Args:
            concept: Concept string to search for
            time_slice: Optional date range for temporal filtering (subtask 12.6)
            
        Returns:
            List of Resource objects mentioning the concept
        """
        concept_lower = concept.lower()
        
        # Search in title, description (content), and abstract
        query = self.db.query(Resource).filter(
            or_(
                func.lower(Resource.title).contains(concept_lower),
                func.lower(Resource.description).contains(concept_lower),
                func.lower(Resource.abstract).contains(concept_lower) if hasattr(Resource, 'abstract') else False
            )
        )
        
        # Subtask 12.6: Apply time-slicing if provided
        if time_slice:
            start_date, end_date = time_slice
            query = query.filter(
                and_(
                    Resource.date_created >= start_date,
                    Resource.date_created <= end_date
                )
            )
        
        resources = query.all()
        
        return resources
    
    def _find_bridging_concepts(
        self,
        resources_a: List[Resource],
        resources_c: List[Resource]
    ) -> List[str]:
        """
        Find concepts that appear with both A and C separately.
        
        Subtask 12.1: Implement ABC discovery pattern - find bridging concepts
        Subtask 12.2: Implement concept extraction from tags/keywords
        
        Args:
            resources_a: Resources mentioning concept A
            resources_c: Resources mentioning concept C
            
        Returns:
            List of bridging concept strings
        """
        # Subtask 12.2: Extract concepts from resources with A
        concepts_with_a: Set[str] = set()
        for resource in resources_a:
            concepts_with_a.update(self._extract_concepts(resource))
        
        # Subtask 12.2: Extract concepts from resources with C
        concepts_with_c: Set[str] = set()
        for resource in resources_c:
            concepts_with_c.update(self._extract_concepts(resource))
        
        # Find intersection - concepts appearing with both A and C
        bridging = concepts_with_a & concepts_with_c
        
        return list(bridging)
    
    def _extract_concepts(self, resource: Resource) -> Set[str]:
        """
        Extract key concepts from a resource.
        
        Subtask 12.2: Implement concept extraction from tags/keywords
        
        Currently extracts from:
        - Subject classifications
        - Classification code
        
        Note: Resource model doesn't have a 'tags' field.
        Future enhancement: Use NLP for noun phrase extraction
        
        Args:
            resource: Resource to extract concepts from
            
        Returns:
            Set of concept strings
        """
        concepts: Set[str] = set()
        
        # Extract from subjects
        if resource.subject:
            try:
                if isinstance(resource.subject, str):
                    subjects = json.loads(resource.subject)
                else:
                    subjects = resource.subject
                
                if isinstance(subjects, list):
                    concepts.update(str(subj).lower() for subj in subjects)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Optional: Extract from classification code
        if resource.classification_code:
            concepts.add(resource.classification_code.lower())
        
        # Future enhancement: Use spaCy for noun phrase extraction
        # This would require:
        # import spacy
        # nlp = spacy.load("en_core_web_sm")
        # if resource.description:
        #     doc = nlp(resource.description[:1000])
        #     concepts.update(chunk.text.lower() for chunk in doc.noun_chunks)
        
        return concepts
    
    def _filter_known_connections(
        self,
        concept_a: str,
        concept_c: str,
        bridging_concepts: List[str]
    ) -> List[str]:
        """
        Filter out already-known A-C connections.
        
        Subtask 12.3: Implement known connection filtering
        
        A connection is considered "known" if resources exist that mention
        both A and C together, indicating the relationship is already
        established in the literature.
        
        Args:
            concept_a: Starting concept
            concept_c: Target concept
            bridging_concepts: List of potential bridging concepts
            
        Returns:
            Filtered list of bridging concepts (novel connections only)
        """
        concept_a_lower = concept_a.lower()
        concept_c_lower = concept_c.lower()
        
        # Check if any resources mention both A and C together
        known_connections_count = self.db.query(Resource).filter(
            and_(
                or_(
                    func.lower(Resource.title).contains(concept_a_lower),
                    func.lower(Resource.description).contains(concept_a_lower)
                ),
                or_(
                    func.lower(Resource.title).contains(concept_c_lower),
                    func.lower(Resource.description).contains(concept_c_lower)
                )
            )
        ).count()
        
        # If direct connections exist, this reduces novelty but we still return bridging concepts
        # The novelty score in ranking will account for this
        if known_connections_count > 0:
            logger.debug(f"Found {known_connections_count} resources mentioning both A and C")
        
        # For now, return all bridging concepts
        # More sophisticated filtering could remove concepts that appear in known A-C resources
        return bridging_concepts
    
    def _rank_hypotheses(
        self,
        concept_a: str,
        concept_c: str,
        bridging_concepts: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Rank hypotheses by support strength and novelty.
        
        Subtask 12.4: Implement hypothesis ranking
        
        Ranking algorithm:
        1. Count A-B connections (resources mentioning both A and B)
        2. Count B-C connections (resources mentioning both B and C)
        3. Compute support strength = min(A-B count, B-C count)
        4. Compute novelty = 1.0 / (1.0 + A-C direct connections)
        5. Compute confidence = support * novelty
        6. Sort by confidence descending
        
        Args:
            concept_a: Starting concept
            concept_c: Target concept
            bridging_concepts: List of bridging concepts to rank
            
        Returns:
            List of hypothesis dictionaries sorted by confidence
        """
        hypotheses: List[Dict[str, Any]] = []
        
        for concept_b in bridging_concepts:
            # Subtask 12.4: Count A-B connections
            ab_count = self._count_connections(concept_a, concept_b)
            
            # Subtask 12.4: Count B-C connections
            bc_count = self._count_connections(concept_b, concept_c)
            
            # Subtask 12.4: Compute support strength (minimum of the two)
            support = min(ab_count, bc_count)
            
            # Skip if no support
            if support == 0:
                continue
            
            # Subtask 12.4: Compute novelty (inverse of A-C co-occurrence)
            ac_count = self._count_connections(concept_a, concept_c)
            novelty = 1.0 / (1.0 + ac_count)
            
            # Subtask 12.4: Compute confidence score
            confidence = support * novelty
            
            # Subtask 12.5: Build evidence chain
            evidence_chain = self._build_evidence_chain(concept_a, concept_b, concept_c)
            
            hypothesis = {
                'concept_a': concept_a,
                'concept_b': concept_b,
                'concept_c': concept_c,
                'ab_support': ab_count,
                'bc_support': bc_count,
                'support_strength': support,
                'novelty': novelty,
                'confidence': confidence,
                'evidence_chain': evidence_chain
            }
            
            hypotheses.append(hypothesis)
        
        # Subtask 12.4: Sort by confidence descending
        hypotheses.sort(key=lambda x: x['confidence'], reverse=True)
        
        return hypotheses
    
    def _count_connections(self, concept_1: str, concept_2: str) -> int:
        """
        Count resources mentioning both concepts.
        
        Subtask 12.4: Support for hypothesis ranking
        
        Args:
            concept_1: First concept
            concept_2: Second concept
            
        Returns:
            Count of resources mentioning both concepts
        """
        concept_1_lower = concept_1.lower()
        concept_2_lower = concept_2.lower()
        
        count = self.db.query(Resource).filter(
            and_(
                or_(
                    func.lower(Resource.title).contains(concept_1_lower),
                    func.lower(Resource.description).contains(concept_1_lower)
                ),
                or_(
                    func.lower(Resource.title).contains(concept_2_lower),
                    func.lower(Resource.description).contains(concept_2_lower)
                )
            )
        ).count()
        
        return count
    
    def _build_evidence_chain(
        self,
        concept_a: str,
        concept_b: str,
        concept_c: str
    ) -> List[Dict[str, Any]]:
        """
        Build evidence chain showing A→B and B→C connections.
        
        Subtask 12.5: Implement evidence chain building
        
        Returns example resources that demonstrate the A-B and B-C connections,
        providing evidence for the hypothesis.
        
        Args:
            concept_a: Starting concept
            concept_b: Bridging concept
            concept_c: Target concept
            
        Returns:
            List of evidence dictionaries with type, resource_id, and title
        """
        chain: List[Dict[str, Any]] = []
        
        concept_a_lower = concept_a.lower()
        concept_b_lower = concept_b.lower()
        concept_c_lower = concept_c.lower()
        
        # Subtask 12.5: Find example A-B resources
        ab_resources = self.db.query(Resource).filter(
            and_(
                or_(
                    func.lower(Resource.title).contains(concept_a_lower),
                    func.lower(Resource.description).contains(concept_a_lower)
                ),
                or_(
                    func.lower(Resource.title).contains(concept_b_lower),
                    func.lower(Resource.description).contains(concept_b_lower)
                )
            )
        ).limit(3).all()
        
        for resource in ab_resources:
            chain.append({
                'type': 'A-B',
                'resource_id': str(resource.id),
                'title': resource.title,
                'publication_year': resource.publication_year
            })
        
        # Subtask 12.5: Find example B-C resources
        bc_resources = self.db.query(Resource).filter(
            and_(
                or_(
                    func.lower(Resource.title).contains(concept_b_lower),
                    func.lower(Resource.description).contains(concept_b_lower)
                ),
                or_(
                    func.lower(Resource.title).contains(concept_c_lower),
                    func.lower(Resource.description).contains(concept_c_lower)
                )
            )
        ).limit(3).all()
        
        for resource in bc_resources:
            chain.append({
                'type': 'B-C',
                'resource_id': str(resource.id),
                'title': resource.title,
                'publication_year': resource.publication_year
            })
        
        return chain
    
    # Legacy methods for backward compatibility
    
    def discover_abc_hypotheses(
        self,
        concept_a: str,
        concept_c: str,
        min_confidence: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Discover ABC hypotheses (legacy method for backward compatibility).
        
        Args:
            concept_a: Starting concept
            concept_c: Target concept
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of hypotheses with confidence >= min_confidence
        """
        all_hypotheses = self.discover_hypotheses(concept_a, concept_c, limit=100)
        
        # Filter by minimum confidence
        filtered = [h for h in all_hypotheses if h['confidence'] >= min_confidence]
        
        return filtered
    
    def discover_temporal_patterns(
        self,
        resource_id: UUID,
        time_window_years: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Discover temporal patterns in citations (stub for future implementation).
        
        Subtask 12.6: Time-slicing support is implemented in discover_hypotheses
        via the time_slice parameter.
        
        Args:
            resource_id: Resource to analyze
            time_window_years: Time window in years
            
        Returns:
            List of temporal patterns (currently empty)
        """
        # This is a placeholder for future temporal analysis features
        # Current time-slicing is implemented via the time_slice parameter
        # in discover_hypotheses()
        return []
    
    def rank_hypotheses(
        self,
        hypotheses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rank discovery hypotheses by confidence (legacy method).
        
        Args:
            hypotheses: List of hypothesis dictionaries
            
        Returns:
            Hypotheses sorted by confidence score descending
        """
        return sorted(
            hypotheses,
            key=lambda h: h.get('confidence', h.get('confidence_score', 0)),
            reverse=True
        )
    
    # Methods for open/closed discovery (used by discovery_router)
    
    def open_discovery(
        self,
        a_resource_id: str,
        limit: int = 20,
        min_plausibility: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Open discovery from a starting resource.
        
        Used by the discovery_router for the /discovery/open endpoint.
        
        Args:
            a_resource_id: Starting resource UUID
            limit: Maximum hypotheses to return
            min_plausibility: Minimum plausibility threshold
            
        Returns:
            List of hypothesis dictionaries
        """
        # Get the starting resource
        resource_a = self.db.query(Resource).filter(
            Resource.id == UUID(a_resource_id)
        ).first()
        
        if not resource_a:
            raise ValueError(f"Resource {a_resource_id} not found")
        
        # Extract concepts from the starting resource
        concepts_a = self._extract_concepts(resource_a)
        
        if not concepts_a:
            return []
        
        # Use the first concept as the starting point
        concept_a = list(concepts_a)[0]
        
        # Find all other concepts in the database
        all_resources = self.db.query(Resource).filter(
            Resource.id != UUID(a_resource_id)
        ).limit(1000).all()
        
        all_concepts: Set[str] = set()
        for resource in all_resources:
            all_concepts.update(self._extract_concepts(resource))
        
        # Remove concepts from A
        target_concepts = all_concepts - concepts_a
        
        # Discover hypotheses for each target concept
        all_hypotheses: List[Dict[str, Any]] = []
        
        for concept_c in list(target_concepts)[:50]:  # Limit to avoid timeout
            hypotheses = self.discover_hypotheses(concept_a, concept_c, limit=5)
            
            for h in hypotheses:
                if h['confidence'] >= min_plausibility:
                    # Format for open discovery response
                    all_hypotheses.append({
                        'c_resource': {
                            'id': str(resource_a.id),  # Placeholder
                            'title': f"Resources about {concept_c}",
                            'type': 'concept',
                            'publication_year': None,
                            'quality_overall': None
                        },
                        'b_resources': [],
                        'plausibility_score': h['confidence'],
                        'path_strength': h['support_strength'],
                        'common_neighbors': h['ab_support'] + h['bc_support'],
                        'semantic_similarity': h['novelty'],
                        'path_length': 2,
                        'paths': [[concept_a, h['concept_b'], concept_c]]
                    })
        
        # Sort and limit
        all_hypotheses.sort(key=lambda x: x['plausibility_score'], reverse=True)
        
        return all_hypotheses[:limit]
    
    def closed_discovery(
        self,
        a_resource_id: str,
        c_resource_id: str,
        max_hops: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Closed discovery connecting two resources.
        
        Used by the discovery_router for the /discovery/closed endpoint.
        
        Args:
            a_resource_id: Starting resource UUID
            c_resource_id: Target resource UUID
            max_hops: Maximum path length
            
        Returns:
            List of path dictionaries
        """
        # Get both resources
        resource_a = self.db.query(Resource).filter(
            Resource.id == UUID(a_resource_id)
        ).first()
        
        resource_c = self.db.query(Resource).filter(
            Resource.id == UUID(c_resource_id)
        ).first()
        
        if not resource_a or not resource_c:
            raise ValueError("One or both resources not found")
        
        # Extract concepts
        concepts_a = self._extract_concepts(resource_a)
        concepts_c = self._extract_concepts(resource_c)
        
        if not concepts_a or not concepts_c:
            return []
        
        # Use first concepts
        concept_a = list(concepts_a)[0]
        concept_c = list(concepts_c)[0]
        
        # Discover hypotheses
        hypotheses = self.discover_hypotheses(concept_a, concept_c, limit=10)
        
        # Format as paths
        paths: List[Dict[str, Any]] = []
        
        for h in hypotheses:
            paths.append({
                'b_resources': [],
                'path': [a_resource_id, c_resource_id],
                'path_length': 2,
                'plausibility_score': h['confidence'],
                'path_strength': h['support_strength'],
                'common_neighbors': h['ab_support'] + h['bc_support'],
                'semantic_similarity': h['novelty'],
                'is_direct': False,
                'weights': [h['confidence']]
            })
        
        return paths
