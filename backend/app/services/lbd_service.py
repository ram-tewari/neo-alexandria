"""
Stub implementation of LBDService (Literature-Based Discovery) for Phase 10 tests.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID


class LBDService:
    """Service for literature-based discovery."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def open_discovery(self, start_resource_id: str = None, end_resource_id: str = None,
                      a_resource_id: str = None, limit: int = 10, 
                      min_plausibility: float = 0.0) -> List[Dict[str, Any]]:
        """
        Perform open discovery to find potential connections from a resource.
        
        Args:
            start_resource_id: Starting resource ID (preferred parameter name)
            end_resource_id: Optional ending resource ID for compatibility
            a_resource_id: Alternative name for start_resource_id (for backward compatibility)
            limit: Maximum number of hypotheses to return
            min_plausibility: Minimum plausibility score threshold
            
        Returns:
            List of hypothesis dictionaries with A-B-C path information
        """
        from backend.app.database.models import Resource, Citation
        import numpy as np
        
        # Handle parameter name variations for backward compatibility
        resource_id = start_resource_id or a_resource_id
        if not resource_id:
            return []
        
        # Verify resource exists
        resource_a = self.db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource_a:
            return []
        
        # Find A->B citations (direct citations from A)
        citations_ab = self.db.query(Citation).filter(
            Citation.source_resource_id == resource_id
        ).all()
        
        if not citations_ab:
            return []
        
        # Get direct connections from A (to exclude from C candidates)
        direct_connections = {str(c.target_resource_id) for c in citations_ab}
        
        # For each B, find B->C citations
        hypotheses = []
        
        for citation_ab in citations_ab:
            resource_b_id = citation_ab.target_resource_id
            
            # Find B->C citations
            citations_bc = self.db.query(Citation).filter(
                Citation.source_resource_id == resource_b_id
            ).all()
            
            for citation_bc in citations_bc:
                resource_c_id = str(citation_bc.target_resource_id)
                
                # Skip if C is directly connected to A
                if resource_c_id in direct_connections:
                    continue
                
                # Skip if C is A itself
                if resource_c_id == resource_id:
                    continue
                
                # Get resource C
                resource_c = self.db.query(Resource).filter(
                    Resource.id == resource_c_id
                ).first()
                
                if not resource_c:
                    continue
                
                # Get resource B
                resource_b = self.db.query(Resource).filter(
                    Resource.id == resource_b_id
                ).first()
                
                if not resource_b:
                    continue
                
                # Calculate plausibility components
                path_strength = 1.0  # Simple path strength (could be weighted by citation counts)
                common_neighbors = 0  # Count of common neighbors between A and C
                semantic_similarity = 0.0
                
                # Calculate semantic similarity if embeddings available
                if resource_a.embedding and resource_c.embedding:
                    try:
                        vec_a = np.array(resource_a.embedding, dtype=np.float32)
                        vec_c = np.array(resource_c.embedding, dtype=np.float32)
                        
                        norm_a = np.linalg.norm(vec_a)
                        norm_c = np.linalg.norm(vec_c)
                        
                        if norm_a > 0 and norm_c > 0:
                            semantic_similarity = float(np.dot(vec_a, vec_c) / (norm_a * norm_c))
                            semantic_similarity = max(0.0, min(1.0, semantic_similarity))
                    except Exception:
                        pass
                
                # Calculate plausibility score (weighted combination)
                plausibility_score = (
                    0.4 * path_strength +
                    0.3 * semantic_similarity +
                    0.3 * min(1.0, common_neighbors / 5.0)
                )
                
                # Filter by min_plausibility
                if plausibility_score < min_plausibility:
                    continue
                
                # Create hypothesis
                hypothesis = {
                    "a_resource_id": str(resource_id),
                    "b_resource_id": str(resource_b.id),
                    "c_resource_id": str(resource_c.id),
                    "c_resource": {
                        "id": str(resource_c.id),
                        "title": resource_c.title,
                        "type": resource_c.type
                    },
                    "b_resources": [{
                        "id": str(resource_b.id),
                        "title": resource_b.title,
                        "type": resource_b.type
                    }],
                    "path_length": 2,
                    "plausibility_score": plausibility_score,
                    "path_strength": path_strength,
                    "common_neighbors": common_neighbors,
                    "semantic_similarity": semantic_similarity
                }
                
                hypotheses.append(hypothesis)
        
        # Sort by plausibility score (descending)
        hypotheses.sort(key=lambda h: h["plausibility_score"], reverse=True)
        
        # Apply limit
        return hypotheses[:limit]
    
    def closed_discovery(self, a_resource_id: str, c_resource_id: str, 
                        max_hops: int = 3) -> List[Dict[str, Any]]:
        """
        Perform closed discovery to find paths between two resources.
        
        Args:
            a_resource_id: Starting resource ID
            c_resource_id: Target resource ID
            max_hops: Maximum path length
            
        Returns:
            List of path dictionaries with connection information
        """
        from backend.app.database.models import Resource, Citation
        import numpy as np
        
        # Verify both resources exist
        resource_a = self.db.query(Resource).filter(Resource.id == a_resource_id).first()
        resource_c = self.db.query(Resource).filter(Resource.id == c_resource_id).first()
        
        if not resource_a or not resource_c:
            return []
        
        # Simple path finding: look for direct and 2-hop paths
        paths = []
        
        # Check for direct citation (1-hop)
        direct_citation = self.db.query(Citation).filter(
            Citation.source_resource_id == a_resource_id,
            Citation.target_resource_id == c_resource_id
        ).first()
        
        if direct_citation:
            # Calculate plausibility for direct path
            plausibility = 1.0  # Direct connections have highest plausibility
            
            paths.append({
                "a_resource_id": str(a_resource_id),
                "c_resource_id": str(c_resource_id),
                "b_resources": [],
                "path_length": 1,
                "plausibility_score": plausibility,
                "path": [str(a_resource_id), str(c_resource_id)]
            })
        
        # Find 2-hop paths (A -> B -> C)
        if max_hops >= 2:
            # Get all citations from A
            citations_ab = self.db.query(Citation).filter(
                Citation.source_resource_id == a_resource_id
            ).all()
            
            for citation_ab in citations_ab:
                resource_b_id = citation_ab.target_resource_id
                
                # Skip if B is the target (already handled as direct)
                if str(resource_b_id) == str(c_resource_id):
                    continue
                
                # Check if B cites C
                citation_bc = self.db.query(Citation).filter(
                    Citation.source_resource_id == resource_b_id,
                    Citation.target_resource_id == c_resource_id
                ).first()
                
                if citation_bc:
                    # Get resource B for details
                    resource_b = self.db.query(Resource).filter(
                        Resource.id == resource_b_id
                    ).first()
                    
                    if not resource_b:
                        continue
                    
                    # Calculate plausibility for 2-hop path
                    path_strength = 0.7  # 2-hop paths have lower strength
                    semantic_similarity = 0.0
                    
                    # Calculate semantic similarity if embeddings available
                    if resource_a.embedding and resource_c.embedding:
                        try:
                            vec_a = np.array(resource_a.embedding, dtype=np.float32)
                            vec_c = np.array(resource_c.embedding, dtype=np.float32)
                            
                            norm_a = np.linalg.norm(vec_a)
                            norm_c = np.linalg.norm(vec_c)
                            
                            if norm_a > 0 and norm_c > 0:
                                semantic_similarity = float(np.dot(vec_a, vec_c) / (norm_a * norm_c))
                                semantic_similarity = max(0.0, min(1.0, semantic_similarity))
                        except Exception:
                            pass
                    
                    plausibility_score = 0.6 * path_strength + 0.4 * semantic_similarity
                    
                    paths.append({
                        "a_resource_id": str(a_resource_id),
                        "b_resource_id": str(resource_b_id),
                        "c_resource_id": str(c_resource_id),
                        "b_resources": [{
                            "id": str(resource_b.id),
                            "title": resource_b.title,
                            "type": resource_b.type
                        }],
                        "path_length": 2,
                        "plausibility_score": plausibility_score,
                        "path": [str(a_resource_id), str(resource_b_id), str(c_resource_id)]
                    })
        
        # Sort by plausibility score (descending)
        paths.sort(key=lambda p: p["plausibility_score"], reverse=True)
        
        return paths
    
    def discover_abc_hypotheses(self, concept_a: str, concept_c: str, 
                                min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """Discover ABC hypotheses (A-B-C connections)."""
        return []
    
    def discover_temporal_patterns(self, resource_id: UUID, 
                                   time_window_years: int = 5) -> List[Dict[str, Any]]:
        """Discover temporal patterns in citations."""
        return []
    
    def rank_hypotheses(self, hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank discovery hypotheses by confidence."""
        return sorted(hypotheses, key=lambda h: h.get('confidence_score', 0), reverse=True)
