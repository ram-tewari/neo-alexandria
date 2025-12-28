"""
Search domain objects for Neo Alexandria.

This module contains domain objects for search operations,
replacing primitive obsession with rich value objects that encapsulate
validation and business logic.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from . import (
    ValueObject,
    validate_positive,
    validate_non_empty,
    validate_non_negative,
)



@dataclass
class SearchQuery(ValueObject):
    """
    Search query value object with query text and configuration.
    
    Encapsulates search query parameters including the query text,
    result limits, and search configuration options. This replaces
    primitive obsession where query parameters were passed as
    separate strings and integers.
    
    Attributes:
        query_text: The search query string
        limit: Maximum number of results to return (default: 20)
        enable_reranking: Whether to enable result reranking (default: True)
        adaptive_weights: Whether to use adaptive weight adjustment (default: True)
        search_method: Search method to use (default: "hybrid")
    """
    query_text: str
    limit: int = 20
    enable_reranking: bool = True
    adaptive_weights: bool = True
    search_method: str = "hybrid"
    
    def validate(self) -> None:
        """
        Validate search query parameters.
        
        Raises:
            ValueError: If limit is not positive or search_method is invalid
        """
        # Allow empty query_text for cases where filters are used
        validate_positive(self.limit, "limit")
        
        # Validate search method
        valid_methods = ["hybrid", "fts5", "dense", "sparse", "three_way"]
        if self.search_method not in valid_methods:
            raise ValueError(
                f"search_method must be one of {valid_methods}, "
                f"got '{self.search_method}'"
            )
    
    def is_short_query(self, threshold: int = 3) -> bool:
        """
        Check if query is short (few words).
        
        Short queries may benefit from different search strategies
        or weight adjustments.
        
        Args:
            threshold: Maximum word count for short query (default: 3)
            
        Returns:
            True if query has <= threshold words
        """
        word_count = len(self.query_text.split())
        return word_count <= threshold
    
    def is_long_query(self, threshold: int = 10) -> bool:
        """
        Check if query is long (many words).
        
        Long queries may benefit from semantic search or
        different ranking strategies.
        
        Args:
            threshold: Minimum word count for long query (default: 10)
            
        Returns:
            True if query has > threshold words
        """
        word_count = len(self.query_text.split())
        return word_count > threshold

    
    def is_medium_query(
        self,
        short_threshold: int = 3,
        long_threshold: int = 10
    ) -> bool:
        """
        Check if query is medium length.
        
        Args:
            short_threshold: Upper bound for short queries (default: 3)
            long_threshold: Lower bound for long queries (default: 10)
            
        Returns:
            True if query has word count between thresholds
        """
        word_count = len(self.query_text.split())
        return short_threshold < word_count <= long_threshold
    
    def get_word_count(self) -> int:
        """
        Get the number of words in the query.
        
        Returns:
            Number of words in query_text
        """
        return len(self.query_text.split())
    
    def is_single_word(self) -> bool:
        """
        Check if query is a single word.
        
        Single-word queries may benefit from exact matching
        or different search strategies.
        
        Returns:
            True if query contains exactly one word
        """
        return self.get_word_count() == 1
    
    def get_query_length(self) -> int:
        """
        Get the character length of the query.
        
        Returns:
            Number of characters in query_text
        """
        return len(self.query_text)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert search query to dictionary for API compatibility.
        
        Returns:
            Dictionary representation with all attributes
        """
        return {
            'query_text': self.query_text,
            'limit': self.limit,
            'enable_reranking': self.enable_reranking,
            'adaptive_weights': self.adaptive_weights,
            'search_method': self.search_method
        }



@dataclass
class SearchResult(ValueObject):
    """
    Search result with ranking and metadata.
    
    Represents a single search result with its relevance score,
    ranking position, and associated metadata. This replaces
    primitive dict representations of search results.
    
    Attributes:
        resource_id: Unique identifier of the resource
        score: Relevance score (higher is better)
        rank: Ranking position (1-based, lower is better)
        title: Resource title
        search_method: Method used to retrieve this result
        metadata: Additional metadata about the result
    """
    resource_id: str
    score: float
    rank: int
    title: str = ""
    search_method: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> None:
        """
        Validate search result attributes.
        
        Raises:
            ValueError: If resource_id is empty, score is negative,
                       or rank is not positive
        """
        validate_non_empty(self.resource_id, "resource_id")
        validate_non_negative(self.score, "score")
        validate_positive(self.rank, "rank")
    
    def is_high_score(self, threshold: float = 0.8) -> bool:
        """
        Check if result has high relevance score.
        
        Args:
            threshold: Score threshold (default: 0.8)
            
        Returns:
            True if score >= threshold
        """
        return self.score >= threshold
    
    def is_low_score(self, threshold: float = 0.3) -> bool:
        """
        Check if result has low relevance score.
        
        Args:
            threshold: Score threshold (default: 0.3)
            
        Returns:
            True if score < threshold
        """
        return self.score < threshold
    
    def is_top_result(self, top_k: int = 5) -> bool:
        """
        Check if result is in top K positions.
        
        Args:
            top_k: Number of top positions to consider (default: 5)
            
        Returns:
            True if rank <= top_k
        """
        return self.rank <= top_k
    
    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value by key.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)
    
    def has_metadata(self, key: str) -> bool:
        """
        Check if metadata contains a key.
        
        Args:
            key: Metadata key to check
            
        Returns:
            True if key exists in metadata
        """
        return key in self.metadata
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get attribute value by key (dict-like interface for backward compatibility).
        
        Args:
            key: Attribute name
            default: Default value if key not found
            
        Returns:
            Attribute value or default value
        """
        return getattr(self, key, default)
    
    def __getitem__(self, key: str) -> Any:
        """
        Get attribute value by key (dict-like interface).
        
        Args:
            key: Attribute name
            
        Returns:
            Attribute value
            
        Raises:
            KeyError: If key is not a valid attribute
        """
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"'{key}' is not a valid search result attribute")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert search result to dictionary for API compatibility.
        
        Returns:
            Dictionary representation with all attributes
        """
        return {
            'resource_id': self.resource_id,
            'score': self.score,
            'rank': self.rank,
            'title': self.title,
            'search_method': self.search_method,
            'metadata': self.metadata
        }



@dataclass
class SearchResults(ValueObject):
    """
    Collection of search results with query metadata.
    
    Represents the complete result set from a search operation,
    including all matching results, query information, and
    performance metrics.
    
    Attributes:
        results: List of search results
        query: The original search query
        total_results: Total number of results found
        search_time_ms: Time taken for search in milliseconds
        reranked: Whether results were reranked
    """
    results: List[SearchResult]
    query: SearchQuery
    total_results: int
    search_time_ms: float
    reranked: bool = False
    
    def validate(self) -> None:
        """
        Validate search results collection.
        
        Raises:
            ValueError: If total_results is negative or search_time_ms is negative
        """
        validate_non_negative(self.total_results, "total_results")
        validate_non_negative(self.search_time_ms, "search_time_ms")
        
        # Validate query
        self.query.validate()
        
        # Validate all results
        for result in self.results:
            result.validate()
    
    def get_top_k(self, k: int) -> List[SearchResult]:
        """
        Get top K results by rank.
        
        Args:
            k: Number of top results to return
            
        Returns:
            List of top K results sorted by rank
        """
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        
        return sorted(self.results, key=lambda r: r.rank)[:k]
    
    def get_high_score_results(self, threshold: float = 0.8) -> List[SearchResult]:
        """
        Get results with high relevance scores.
        
        Args:
            threshold: Score threshold (default: 0.8)
            
        Returns:
            List of results with score >= threshold
        """
        return [r for r in self.results if r.is_high_score(threshold)]
    
    def get_by_method(self, search_method: str) -> List[SearchResult]:
        """
        Get results retrieved by specific search method.
        
        Args:
            search_method: Search method to filter by
            
        Returns:
            List of results from specified method
        """
        return [r for r in self.results if r.search_method == search_method]
    
    def has_results(self) -> bool:
        """
        Check if search returned any results.
        
        Returns:
            True if results list is not empty
        """
        return len(self.results) > 0
    
    def get_result_count(self) -> int:
        """
        Get the number of results returned.
        
        Returns:
            Number of results in the results list
        """
        return len(self.results)
    
    def get_average_score(self) -> float:
        """
        Calculate average relevance score across all results.
        
        Returns:
            Average score, or 0.0 if no results
        """
        if not self.results:
            return 0.0
        return sum(r.score for r in self.results) / len(self.results)

    
    def get_score_distribution(
        self,
        low_threshold: float = 0.3,
        high_threshold: float = 0.8
    ) -> Dict[str, int]:
        """
        Get distribution of results by score level.
        
        Args:
            low_threshold: Upper bound for low scores (default: 0.3)
            high_threshold: Lower bound for high scores (default: 0.8)
            
        Returns:
            Dictionary with counts for 'low', 'medium', and 'high' scores
        """
        low_count = sum(1 for r in self.results if r.score < low_threshold)
        high_count = sum(1 for r in self.results if r.score >= high_threshold)
        medium_count = len(self.results) - low_count - high_count
        
        return {
            'low': low_count,
            'medium': medium_count,
            'high': high_count
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get attribute value by key (dict-like interface for backward compatibility).
        
        Args:
            key: Attribute name
            default: Default value if key not found
            
        Returns:
            Attribute value or default value
        """
        return getattr(self, key, default)
    
    def __getitem__(self, key: str) -> Any:
        """
        Get attribute value by key (dict-like interface).
        
        Args:
            key: Attribute name
            
        Returns:
            Attribute value
            
        Raises:
            KeyError: If key is not a valid attribute
        """
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"'{key}' is not a valid search results attribute")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert search results to dictionary for API compatibility.
        
        Returns:
            Dictionary representation with all attributes
        """
        return {
            'results': [r.to_dict() for r in self.results],
            'query': self.query.to_dict(),
            'total_results': self.total_results,
            'search_time_ms': self.search_time_ms,
            'reranked': self.reranked,
            'metadata': {
                'result_count': self.get_result_count(),
                'average_score': self.get_average_score(),
                'score_distribution': self.get_score_distribution(),
                'has_results': self.has_results()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResults':
        """
        Create search results from dictionary.
        
        Args:
            data: Dictionary with search results data
            
        Returns:
            New SearchResults instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        results_data = data.get('results', [])
        results = [
            SearchResult(
                resource_id=r['resource_id'],
                score=r['score'],
                rank=r['rank'],
                title=r.get('title', ''),
                search_method=r.get('search_method', 'unknown'),
                metadata=r.get('metadata', {})
            )
            for r in results_data
        ]
        
        query_data = data['query']
        query = SearchQuery(
            query_text=query_data['query_text'],
            limit=query_data.get('limit', 20),
            enable_reranking=query_data.get('enable_reranking', True),
            adaptive_weights=query_data.get('adaptive_weights', True),
            search_method=query_data.get('search_method', 'hybrid')
        )
        
        return cls(
            results=results,
            query=query,
            total_results=data['total_results'],
            search_time_ms=data['search_time_ms'],
            reranked=data.get('reranked', False)
        )
