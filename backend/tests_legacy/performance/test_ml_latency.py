"""
ML Performance Latency Benchmark Tests (Phase 11.5)

This module implements performance benchmark tests for ML service inference latency.
Tests measure prediction time and ensure real-time performance requirements are met.

Test Metrics:
- Classification inference: p95 < 100ms
- NCF prediction: p95 < 50ms per user
- Search query: p95 < 200ms (three-way hybrid)
- Embedding generation: p95 < 500ms

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

import time

import pytest
import numpy as np


class TestMLLatency:
    """
    Test suite for ML service latency benchmarking.
    
    This class measures inference latency for all ML services to ensure
    real-time performance requirements are met. Each test executes 100
    predictions and reports p50, p95, and p99 latency percentiles.
    """
    
    def test_classification_latency(self, trained_classifier):
        """
        Test classification inference latency.
        
        Executes 100 classification predictions with sample texts and records
        latency for each prediction in milliseconds. Computes p50, p95, p99
        latency percentiles and asserts p95 latency < 100ms.
        
        Args:
            trained_classifier: Pre-trained classification model fixture
        
        Requirements: 6.1, 6.5
        """
        print("\n" + "="*80)
        print("TEST: Classification Inference Latency")
        print("="*80)
        
        # Sample texts for latency testing
        # Use diverse text lengths to simulate real-world scenarios
        sample_texts = [
            # Short texts (50-100 words)
            "Machine learning is a subset of artificial intelligence that enables "
            "computers to learn from data without being explicitly programmed. "
            "It uses algorithms to identify patterns and make predictions.",
            
            # Medium texts (100-200 words)
            "Deep learning is a specialized branch of machine learning that uses "
            "neural networks with multiple layers to process complex patterns in data. "
            "These networks are inspired by the structure of the human brain and can "
            "automatically learn hierarchical representations of features. Deep learning "
            "has revolutionized fields like computer vision, natural language processing, "
            "and speech recognition. Popular architectures include convolutional neural "
            "networks for image processing and recurrent neural networks for sequential data.",
            
            # Long texts (200-300 words)
            "Natural language processing (NLP) is a field at the intersection of computer "
            "science, artificial intelligence, and linguistics. It focuses on enabling "
            "computers to understand, interpret, and generate human language in a valuable way. "
            "NLP combines computational linguistics with statistical, machine learning, and "
            "deep learning models. Modern NLP systems can perform tasks such as machine "
            "translation, sentiment analysis, named entity recognition, question answering, "
            "and text summarization. The field has seen tremendous advances with the "
            "introduction of transformer architectures like BERT, GPT, and T5, which use "
            "attention mechanisms to capture long-range dependencies in text. These models "
            "are pre-trained on massive text corpora and can be fine-tuned for specific tasks "
            "with relatively small amounts of labeled data. NLP applications are now ubiquitous "
            "in virtual assistants, chatbots, search engines, and content recommendation systems.",
            
            # Very short texts (20-50 words)
            "Quantum computing uses quantum mechanical phenomena like superposition and "
            "entanglement to perform computations that would be infeasible for classical computers.",
            
            # Technical texts
            "The backpropagation algorithm is used to train neural networks by computing "
            "gradients of the loss function with respect to network weights. It applies "
            "the chain rule of calculus to efficiently propagate errors backward through "
            "the network layers, enabling gradient descent optimization.",
        ]
        
        # Number of predictions to execute
        num_predictions = 100
        print(f"Number of predictions: {num_predictions}")
        print(f"Sample text variations: {len(sample_texts)}")
        
        # Warm-up runs (exclude from measurements)
        print("\nPerforming warm-up runs...")
        for i in range(5):
            text = sample_texts[i % len(sample_texts)]
            trained_classifier.predict(text, top_k=5)
        
        print("Warm-up complete. Starting latency measurements...")
        
        # Execute predictions and record latencies
        latencies = []
        
        for i in range(num_predictions):
            # Cycle through sample texts
            text = sample_texts[i % len(sample_texts)]
            
            # Measure prediction time
            start_time = time.time()
            trained_classifier.predict(text, top_k=5)
            end_time = time.time()
            
            # Record latency in milliseconds
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
            
            # Progress indicator every 20 predictions
            if (i + 1) % 20 == 0:
                print(f"  Completed {i + 1}/{num_predictions} predictions...")
        
        # Convert to numpy array for percentile calculations
        latencies_array = np.array(latencies)
        
        # Compute percentiles
        p50 = np.percentile(latencies_array, 50)
        p95 = np.percentile(latencies_array, 95)
        p99 = np.percentile(latencies_array, 99)
        mean_latency = np.mean(latencies_array)
        std_latency = np.std(latencies_array)
        min_latency = np.min(latencies_array)
        max_latency = np.max(latencies_array)
        
        # Performance threshold
        p95_threshold = 100.0  # milliseconds
        
        # Display results
        print("\n" + "-"*80)
        print("Latency Statistics:")
        print("-"*80)
        print(f"  Mean:     {mean_latency:>8.2f} ms")
        print(f"  Std Dev:  {std_latency:>8.2f} ms")
        print(f"  Min:      {min_latency:>8.2f} ms")
        print(f"  Max:      {max_latency:>8.2f} ms")
        print(f"  p50:      {p50:>8.2f} ms")
        print(f"  p95:      {p95:>8.2f} ms")
        print(f"  p99:      {p99:>8.2f} ms")
        print("-"*80)
        
        print("\nPerformance Threshold:")
        print(f"  p95 Target:   {p95_threshold:.2f} ms")
        print(f"  p95 Actual:   {p95:.2f} ms")
        
        if p95 < p95_threshold:
            margin = p95_threshold - p95
            margin_pct = (margin / p95_threshold) * 100
            print(f"  Status: ✅ PASSING (margin: {margin:.2f}ms / {margin_pct:.1f}%)")
        else:
            excess = p95 - p95_threshold
            excess_pct = (excess / p95_threshold) * 100
            print(f"  Status: ❌ FAILING (excess: {excess:.2f}ms / {excess_pct:.1f}%)")
        
        # Latency distribution analysis
        print("\nLatency Distribution:")
        bins = [
            (0, 50, "< 50ms (Excellent)"),
            (50, 75, "50-75ms (Good)"),
            (75, 100, "75-100ms (Acceptable)"),
            (100, 150, "100-150ms (Slow)"),
            (150, float('inf'), "> 150ms (Very Slow)")
        ]
        
        for min_lat, max_lat, label in bins:
            if max_lat == float('inf'):
                count = np.sum(latencies_array >= min_lat)
            else:
                count = np.sum((latencies_array >= min_lat) & (latencies_array < max_lat))
            
            percentage = (count / num_predictions) * 100
            bar_length = int(percentage / 2)  # Scale to 50 chars max
            bar = "█" * bar_length
            
            print(f"  {label:<25} {count:>4} ({percentage:>5.1f}%) {bar}")
        
        print("="*80)
        
        # Assert p95 latency threshold
        assert p95 < p95_threshold, (
            f"p95 latency {p95:.2f}ms exceeds threshold {p95_threshold:.2f}ms. "
            f"Classification inference is too slow for real-time requirements."
        )

    def test_ncf_prediction_latency(self, trained_ncf_model):
        """
        Test NCF prediction latency.
        
        Executes 100 NCF predictions for user-item pairs and records latency
        for each prediction in milliseconds. Computes p50, p95, p99 latency
        percentiles and asserts p95 latency < 50ms per user.
        
        Args:
            trained_ncf_model: Pre-trained NCF model fixture
        
        Requirements: 6.2, 6.5
        """
        print("\n" + "="*80)
        print("TEST: NCF Prediction Latency")
        print("="*80)
        
        # Sample user IDs and item IDs for latency testing
        sample_user_ids = [f"user_{i}" for i in range(20)]
        sample_item_ids = [f"item_{i}" for i in range(50)]
        
        # Number of predictions to execute
        num_predictions = 100
        print(f"Number of predictions: {num_predictions}")
        print(f"Sample users: {len(sample_user_ids)}")
        print(f"Sample items: {len(sample_item_ids)}")
        
        # Warm-up runs
        print("\nPerforming warm-up runs...")
        for i in range(5):
            user_id = sample_user_ids[i % len(sample_user_ids)]
            item_ids = sample_item_ids[:10]
            trained_ncf_model.predict_batch(user_id, item_ids)
        
        print("Warm-up complete. Starting latency measurements...")
        
        # Execute predictions and record latencies
        latencies = []
        
        for i in range(num_predictions):
            # Cycle through users
            user_id = sample_user_ids[i % len(sample_user_ids)]
            
            # Get 10 random items for prediction
            item_ids = sample_item_ids[(i*10) % len(sample_item_ids):(i*10 + 10) % len(sample_item_ids)]
            if not item_ids:
                item_ids = sample_item_ids[:10]
            
            # Measure prediction time
            start_time = time.time()
            trained_ncf_model.predict_batch(user_id, item_ids)
            end_time = time.time()
            
            # Record latency in milliseconds
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
            
            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"  Completed {i + 1}/{num_predictions} predictions...")
        
        # Convert to numpy array
        latencies_array = np.array(latencies)
        
        # Compute percentiles
        p50 = np.percentile(latencies_array, 50)
        p95 = np.percentile(latencies_array, 95)
        p99 = np.percentile(latencies_array, 99)
        mean_latency = np.mean(latencies_array)
        std_latency = np.std(latencies_array)
        min_latency = np.min(latencies_array)
        max_latency = np.max(latencies_array)
        
        # Performance threshold
        p95_threshold = 50.0  # milliseconds
        
        # Display results
        print("\n" + "-"*80)
        print("Latency Statistics:")
        print("-"*80)
        print(f"  Mean:     {mean_latency:>8.2f} ms")
        print(f"  Std Dev:  {std_latency:>8.2f} ms")
        print(f"  Min:      {min_latency:>8.2f} ms")
        print(f"  Max:      {max_latency:>8.2f} ms")
        print(f"  p50:      {p50:>8.2f} ms")
        print(f"  p95:      {p95:>8.2f} ms")
        print(f"  p99:      {p99:>8.2f} ms")
        print("-"*80)
        
        print("\nPerformance Threshold:")
        print(f"  p95 Target:   {p95_threshold:.2f} ms")
        print(f"  p95 Actual:   {p95:.2f} ms")
        
        if p95 < p95_threshold:
            margin = p95_threshold - p95
            margin_pct = (margin / p95_threshold) * 100
            print(f"  Status: ✅ PASSING (margin: {margin:.2f}ms / {margin_pct:.1f}%)")
        else:
            excess = p95 - p95_threshold
            excess_pct = (excess / p95_threshold) * 100
            print(f"  Status: ❌ FAILING (excess: {excess:.2f}ms / {excess_pct:.1f}%)")
        
        print("="*80)
        
        # Assert p95 latency threshold
        assert p95 < p95_threshold, (
            f"p95 latency {p95:.2f}ms exceeds threshold {p95_threshold:.2f}ms. "
            f"NCF prediction is too slow for real-time recommendations."
        )
    
    def test_search_query_latency(self, isolated_test_db):
        """
        Test search query latency for three-way hybrid search.
        
        Executes 100 search queries with diverse query texts and records latency
        for each query in milliseconds. Computes p50, p95, p99 latency percentiles
        and asserts p95 latency < 200ms.
        
        Args:
            isolated_test_db: Isolated test database session
        
        Requirements: 6.3, 6.5
        """
        print("\n" + "="*80)
        print("TEST: Search Query Latency (Three-Way Hybrid)")
        print("="*80)
        
        from backend.app.services.search_service import AdvancedSearchService
        from backend.app.schemas.search import SearchQuery, SearchFilters
        from backend.app.database.models import Resource
        
        # Create test resources for search
        print("Creating test resources...")
        test_resources = []
        for i in range(50):
            resource = Resource(
                id=f"resource_{i}",
                title=f"Test Resource {i}: Machine Learning and AI",
                description=f"This is a test resource about machine learning, artificial intelligence, "
                           f"and data science. It covers topics like neural networks, deep learning, "
                           f"and natural language processing. Resource number {i}.",
                type="article",
                classification_code="000"
            )
            isolated_test_db.add(resource)
            test_resources.append(resource)
        
        try:
            isolated_test_db.commit()
        except Exception:
            isolated_test_db.rollback()
        
        # Sample search queries
        sample_queries = [
            "machine learning algorithms",
            "deep learning neural networks",
            "natural language processing",
            "artificial intelligence applications",
            "data science techniques",
            "computer vision models",
            "reinforcement learning",
            "supervised learning methods",
            "unsupervised clustering",
            "neural network architectures",
            "transformer models",
            "convolutional networks",
            "recurrent neural networks",
            "gradient descent optimization",
            "backpropagation algorithm",
        ]
        
        # Number of queries to execute
        num_queries = 100
        print(f"Number of queries: {num_queries}")
        print(f"Sample query variations: {len(sample_queries)}")
        
        # Warm-up runs
        print("\nPerforming warm-up runs...")
        for i in range(5):
            query_text = sample_queries[i % len(sample_queries)]
            search_query = SearchQuery(
                text=query_text,
                filters=SearchFilters(),
                limit=20,
                offset=0,
                sort_by="relevance",
                sort_dir="desc"
            )
            try:
                AdvancedSearchService.search(isolated_test_db, search_query)
            except Exception:
                pass
        
        print("Warm-up complete. Starting latency measurements...")
        
        # Execute queries and record latencies
        latencies = []
        
        for i in range(num_queries):
            # Cycle through queries
            query_text = sample_queries[i % len(sample_queries)]
            
            # Create search query
            search_query = SearchQuery(
                text=query_text,
                filters=SearchFilters(),
                limit=20,
                offset=0,
                sort_by="relevance",
                sort_dir="desc"
            )
            
            # Measure query time
            start_time = time.time()
            try:
                AdvancedSearchService.search(isolated_test_db, search_query)
            except Exception:
                # If search fails, record a high latency to penalize failures
                latency_ms = 1000.0
            else:
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
            
            latencies.append(latency_ms)
            
            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"  Completed {i + 1}/{num_queries} queries...")
        
        # Convert to numpy array
        latencies_array = np.array(latencies)
        
        # Compute percentiles
        p50 = np.percentile(latencies_array, 50)
        p95 = np.percentile(latencies_array, 95)
        p99 = np.percentile(latencies_array, 99)
        mean_latency = np.mean(latencies_array)
        std_latency = np.std(latencies_array)
        min_latency = np.min(latencies_array)
        max_latency = np.max(latencies_array)
        
        # Performance threshold
        p95_threshold = 200.0  # milliseconds
        
        # Display results
        print("\n" + "-"*80)
        print("Latency Statistics:")
        print("-"*80)
        print(f"  Mean:     {mean_latency:>8.2f} ms")
        print(f"  Std Dev:  {std_latency:>8.2f} ms")
        print(f"  Min:      {min_latency:>8.2f} ms")
        print(f"  Max:      {max_latency:>8.2f} ms")
        print(f"  p50:      {p50:>8.2f} ms")
        print(f"  p95:      {p95:>8.2f} ms")
        print(f"  p99:      {p99:>8.2f} ms")
        print("-"*80)
        
        print("\nPerformance Threshold:")
        print(f"  p95 Target:   {p95_threshold:.2f} ms")
        print(f"  p95 Actual:   {p95:.2f} ms")
        
        if p95 < p95_threshold:
            margin = p95_threshold - p95
            margin_pct = (margin / p95_threshold) * 100
            print(f"  Status: ✅ PASSING (margin: {margin:.2f}ms / {margin_pct:.1f}%)")
        else:
            excess = p95 - p95_threshold
            excess_pct = (excess / p95_threshold) * 100
            print(f"  Status: ❌ FAILING (excess: {excess:.2f}ms / {excess_pct:.1f}%)")
        
        print("="*80)
        
        # Assert p95 latency threshold
        assert p95 < p95_threshold, (
            f"p95 latency {p95:.2f}ms exceeds threshold {p95_threshold:.2f}ms. "
            f"Search queries are too slow for acceptable user experience."
        )
    
    def test_embedding_generation_latency(self):
        """
        Test embedding generation latency for sparse embeddings.
        
        Executes 100 embedding generations with sample texts and records latency
        for each generation in milliseconds. Computes p50, p95, p99 latency
        percentiles and asserts p95 latency < 500ms.
        
        Requirements: 6.4, 6.5
        """
        print("\n" + "="*80)
        print("TEST: Embedding Generation Latency")
        print("="*80)
        
        # Import embedding service
        try:
            from backend.app.shared.ai_core import AICore
        except ImportError:
            pytest.skip("AICore service not available")
        
        # Initialize AI core
        ai_core = AICore()
        
        # Sample texts for embedding generation
        sample_texts = [
            "Machine learning is transforming how we process and analyze data.",
            "Deep learning models have achieved remarkable success in computer vision tasks.",
            "Natural language processing enables computers to understand human language.",
            "Reinforcement learning agents learn through trial and error interactions.",
            "Transfer learning allows models to leverage knowledge from related tasks.",
            "Attention mechanisms have revolutionized sequence-to-sequence models.",
            "Generative adversarial networks can create realistic synthetic data.",
            "Convolutional neural networks excel at processing grid-like data structures.",
            "Recurrent neural networks are designed for sequential data processing.",
            "Transformer architectures have become the foundation of modern NLP.",
        ]
        
        # Number of embeddings to generate
        num_generations = 100
        print(f"Number of embeddings: {num_generations}")
        print(f"Sample text variations: {len(sample_texts)}")
        
        # Warm-up runs
        print("\nPerforming warm-up runs...")
        for i in range(5):
            text = sample_texts[i % len(sample_texts)]
            try:
                ai_core.generate_embedding(text)
            except Exception:
                pass
        
        print("Warm-up complete. Starting latency measurements...")
        
        # Execute embedding generations and record latencies
        latencies = []
        
        for i in range(num_generations):
            # Cycle through texts
            text = sample_texts[i % len(sample_texts)]
            
            # Measure generation time
            start_time = time.time()
            try:
                ai_core.generate_embedding(text)
            except Exception:
                # If generation fails, record a high latency
                latency_ms = 2000.0
            else:
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
            
            latencies.append(latency_ms)
            
            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"  Completed {i + 1}/{num_generations} embeddings...")
        
        # Convert to numpy array
        latencies_array = np.array(latencies)
        
        # Compute percentiles
        p50 = np.percentile(latencies_array, 50)
        p95 = np.percentile(latencies_array, 95)
        p99 = np.percentile(latencies_array, 99)
        mean_latency = np.mean(latencies_array)
        std_latency = np.std(latencies_array)
        min_latency = np.min(latencies_array)
        max_latency = np.max(latencies_array)
        
        # Performance threshold
        p95_threshold = 500.0  # milliseconds
        
        # Display results
        print("\n" + "-"*80)
        print("Latency Statistics:")
        print("-"*80)
        print(f"  Mean:     {mean_latency:>8.2f} ms")
        print(f"  Std Dev:  {std_latency:>8.2f} ms")
        print(f"  Min:      {min_latency:>8.2f} ms")
        print(f"  Max:      {max_latency:>8.2f} ms")
        print(f"  p50:      {p50:>8.2f} ms")
        print(f"  p95:      {p95:>8.2f} ms")
        print(f"  p99:      {p99:>8.2f} ms")
        print("-"*80)
        
        print("\nPerformance Threshold:")
        print(f"  p95 Target:   {p95_threshold:.2f} ms")
        print(f"  p95 Actual:   {p95:.2f} ms")
        
        if p95 < p95_threshold:
            margin = p95_threshold - p95
            margin_pct = (margin / p95_threshold) * 100
            print(f"  Status: ✅ PASSING (margin: {margin:.2f}ms / {margin_pct:.1f}%)")
        else:
            excess = p95 - p95_threshold
            excess_pct = (excess / p95_threshold) * 100
            print(f"  Status: ❌ FAILING (excess: {excess:.2f}ms / {excess_pct:.1f}%)")
        
        # Throughput analysis
        total_time_seconds = np.sum(latencies_array) / 1000
        throughput = num_generations / total_time_seconds
        
        print("\nThroughput Analysis:")
        print(f"  Total time: {total_time_seconds:.2f} seconds")
        print(f"  Throughput: {throughput:.2f} embeddings/second")
        
        print("="*80)
        
        # Assert p95 latency threshold
        assert p95 < p95_threshold, (
            f"p95 latency {p95:.2f}ms exceeds threshold {p95_threshold:.2f}ms. "
            f"Embedding generation is too slow for batch processing requirements."
        )
