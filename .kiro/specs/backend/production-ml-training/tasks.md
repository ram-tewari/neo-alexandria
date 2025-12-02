# Implementation Plan

## Overview

This implementation plan converts the production ML training design into a series of coding tasks. Each task builds incrementally on previous tasks, with no orphaned code. Tasks focus exclusively on writing, modifying, or testing code.

## Task List

- [x] 1. Set up project structure and dependencies





  - Create directory structure for dataset acquisition, training, and deployment scripts
  - Add required dependencies to requirements.txt (arxiv, optuna, transformers, torch, scikit-learn)
  - Create configuration files for training and retraining pipelines
  - _Requirements: 11.1, 11.2, 11.3_


- [x] 1.1 Create directory structure

  - Create `backend/scripts/dataset_acquisition/` directory
  - Create `backend/scripts/training/` directory
  - Create `backend/scripts/evaluation/` directory
  - Create `backend/scripts/deployment/` directory
  - Create `backend/data/raw/arxiv/` directory
  - Create `backend/data/processed/` directory
  - Create `backend/data/splits/` directory
  - _Requirements: 11.1_


- [x] 1.2 Add dependencies to requirements.txt

  - Add `arxiv>=1.4.0` for arXiv API access
  - Add `optuna>=3.0.0` for hyperparameter tuning
  - Add `transformers>=4.30.0` for BERT models
  - Add `torch>=2.0.0` for PyTorch
  - Add `scikit-learn>=1.3.0` for metrics and splitting
  - _Requirements: 11.2_


- [x] 1.3 Create configuration files

  - Create `backend/config/retraining_config.json` with schedule and thresholds
  - Create `backend/config/training_config.json` with default hyperparameters
  - _Requirements: 11.3_


- [x] 2. Implement arXiv dataset collector




  - Implement ArxivCollector class with rate limiting and retry logic
  - Implement methods for collecting papers by category with progress logging
  - Implement balanced dataset collection across 10 CS categories
  - Implement complete classification dataset creation with metadata
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10_

- [x] 2.1 Implement ArxivCollector class initialization


  - Create `backend/scripts/dataset_acquisition/arxiv_collector.py`
  - Implement `__init__` method with output directory parameter
  - Initialize arxiv.Client with rate limiting (0.5s delay, 3 retries)
  - Set up logging for collection progress
  - _Requirements: 1.1, 1.2_


- [x] 2.2 Implement collect_papers_by_category method

  - Implement method to fetch papers from specific arXiv category
  - Add date filtering (start_date parameter)
  - Extract paper metadata (arxiv_id, title, abstract, authors, categories, published)
  - Implement progress logging every 100 papers
  - Add error handling with retry logic
  - Save intermediate results to prevent data loss
  - _Requirements: 1.3, 1.4, 1.5, 1.8, 1.9, 1.10_


- [x] 2.3 Implement collect_balanced_dataset method

  - Implement method to collect equal papers per category
  - Iterate through list of categories
  - Call collect_papers_by_category for each category
  - Save category results to separate JSON files
  - Add rate limiting between categories (1s delay)
  - _Requirements: 1.4, 1.6, 1.10_


- [x] 2.4 Implement create_classification_dataset method

  - Define 10 CS categories (cs.AI, cs.CL, cs.CV, cs.LG, cs.CR, cs.DB, cs.DC, cs.NE, cs.RO, cs.SE)
  - Calculate papers per category (num_papers / 10)
  - Call collect_balanced_dataset with categories
  - Flatten dataset and combine title + abstract as text
  - Save complete dataset with metadata (num_samples, categories, created_at, source)
  - Log dataset statistics (size, categories, file size)
  - _Requirements: 1.7, 1.8_


- [x] 2.5 Write unit tests for ArxivCollector

  - Test rate limiting is respected (timing check)
  - Test retry logic on API errors (mock failures)
  - Test paper metadata extraction
  - Test balanced dataset collection
  - Test intermediate save functionality
  - _Requirements: 1.1, 1.2, 1.9, 1.10_




- [x] 3. Implement dataset preprocessing pipeline

  - Implement DatasetPreprocessor class with text cleaning methods
  - Implement deduplication by arXiv ID and title hash
  - Implement quality filtering (minimum words, language detection)

  - Implement stratified train/val/test splitting with fixed random seed
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 3.1 Implement DatasetPreprocessor class with text cleaning

  - Create `backend/scripts/dataset_acquisition/dataset_preprocessor.py`
  - Implement `clean_text` method to remove URLs (regex: `http\S+`)
  - Remove LaTeX commands (regex: `\\[a-zA-Z]+\{[^}]*\}`)
  - Remove inline math (regex: `\$[^$]*\$`)
  - Normalize whitespace (multiple spaces → single space)
  - Remove multiple punctuation (e.g., `...` → `.`)
  - _Requirements: 2.1, 2.2_


- [x] 3.2 Implement deduplication methods
  - Implement `compute_text_hash` method using MD5 hashing
  - Implement `deduplicate_samples` method
  - Check for duplicate arXiv IDs (exact match)
  - Check for duplicate title hashes (near-duplicates)
  - Log number of duplicates removed
  - Return list of unique samples
  - _Requirements: 2.3, 2.4, 2.5_


- [x] 3.3 Implement quality filtering
  - Implement `filter_by_quality` method with min_words parameter (default: 50)
  - Check text length (word count)
  - Check for English language (character-based detection)
  - Check for valid label field
  - Check for non-empty text
  - Log number of samples removed at each filter step

  - _Requirements: 2.6, 2.7, 2.8_

- [x] 3.4 Implement complete preprocessing pipeline
  - Implement `preprocess_dataset` method
  - Load raw dataset from JSON file
  - Apply text cleaning to all samples
  - Apply deduplication
  - Apply quality filtering
  - Save preprocessed dataset with metadata (preprocessing steps, sample count)

  - Log preprocessing statistics
  - _Requirements: 2.9, 2.10_

- [x] 3.5 Implement stratified train/val/test splitting
  - Implement `create_train_val_test_split` method
  - Use sklearn's train_test_split with stratify parameter
  - Split 80% train, 10% validation, 10% test
  - Use fixed random seed (42) for reproducibility
  - Save each split to separate JSON files (train.json, val.json, test.json)
  - Include metadata in each split file (split name, sample count, random seed)

  - Log split sizes and percentages
  - Verify no samples appear in multiple splits
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 3.6 Write unit tests for DatasetPreprocessor


  - Test text cleaning removes URLs and LaTeX
  - Test deduplication removes duplicates by ID and hash
  - Test quality filtering removes short and non-English text
  - Test stratified splitting maintains class balance
  - Test reproducibility with fixed random seed
  - _Requirements: 2.1, 2.3, 2.6, 3.1, 3.3_


- [x] 4. Implement classification model training pipeline




  - Implement ClassificationTrainer class with DistilBERT fine-tuning
  - Implement PyTorch dataset for arXiv classification
  - Implement training with Hugging Face Trainer API
  - Implement evaluation with accuracy and F1 metrics
  - Implement model checkpoint saving with label mappings
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_


- [x] 4.1 Implement ClassificationTrainer class initialization

  - Create `backend/scripts/training/train_classification.py`
  - Implement `__init__` method with model_name and output_dir parameters
  - Initialize tokenizer as None (lazy loading)
  - Initialize model as None (lazy loading)
  - Create checkpoint directory if not exists
  - Set up logging for training progress
  - _Requirements: 4.1, 4.2_


- [x] 4.2 Implement dataset loading and label mapping

  - Implement `load_datasets` method to load train/val/test splits from JSON
  - Extract unique labels from training data
  - Build bidirectional label mappings (id_to_label, label_to_id)
  - Sort labels for consistent ordering
  - Log dataset statistics (sample counts, number of classes)
  - _Requirements: 4.3, 4.4_


- [x] 4.3 Implement PyTorch dataset class

  - Create ArxivClassificationDataset class inheriting from torch.utils.data.Dataset
  - Implement `__init__` with samples, tokenizer, and label_to_id parameters
  - Implement `__len__` to return dataset size
  - Implement `__getitem__` to tokenize text and return input_ids, attention_mask, labels
  - Truncate to 512 tokens maximum
  - Use padding="max_length" for consistent batch sizes
  - _Requirements: 4.5_

- [x] 4.4 Implement training method with Hugging Face Trainer


  - Implement `train` method with train_samples, val_samples, epochs, batch_size, learning_rate parameters
  - Load tokenizer from Hugging Face (DistilBERT-base-uncased)
  - Initialize model with num_labels from label mapping
  - Create PyTorch datasets for train and validation
  - Configure TrainingArguments (epochs, batch_size, learning_rate, warmup_steps, weight_decay)
  - Enable mixed precision (fp16) if GPU available
  - Enable early stopping with patience=2
  - Set evaluation_strategy="epoch" and save_strategy="epoch"
  - Set load_best_model_at_end=True with metric_for_best_model="accuracy"
  - Initialize Trainer with model, args, datasets, and compute_metrics callback
  - Call trainer.train() and log training results
  - _Requirements: 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8_


- [x] 4.5 Implement compute_metrics callback

  - Implement `compute_metrics` method for Trainer evaluation
  - Apply sigmoid to logits to get probabilities
  - Threshold at 0.5 for binary predictions
  - Compute accuracy using sklearn
  - Return dictionary with accuracy metric
  - _Requirements: 5.1, 5.2, 5.3_


- [x] 4.6 Implement model evaluation on test set

  - Implement `evaluate` method with test_samples parameter
  - Create PyTorch dataset for test data
  - Use Trainer.predict() for inference
  - Extract predictions and labels
  - Generate classification report with sklearn (precision, recall, F1 per class)
  - Compute overall accuracy and macro F1
  - Save evaluation results to JSON file with timestamp
  - Log test metrics to console
  - _Requirements: 5.4, 5.5, 5.6, 5.7, 5.8_



- [x] 4.7 Implement checkpoint saving

  - Save model with model.save_pretrained() to checkpoint directory
  - Save tokenizer with tokenizer.save_pretrained() to checkpoint directory
  - Save label mapping to label_map.json (id_to_label and label_to_id)
  - Log checkpoint location and size
  - Verify all required files exist (pytorch_model.bin, config.json, label_map.json)
  - _Requirements: 4.12, 15.1, 15.2, 15.3, 15.4, 15.8_

- [x] 4.8 Write integration test for training pipeline


  - Test end-to-end training with small dataset (100 samples)
  - Test model achieves reasonable accuracy (>50%)
  - Test checkpoint files are created correctly
  - Test model can be loaded from checkpoint
  - Test evaluation on test set works
  - _Requirements: 4.1, 4.11, 4.12, 15.1_



- [x] 5. Implement hyperparameter search with Optuna


  - Implement HyperparameterSearch class with Optuna integration
  - Define search space for learning_rate, batch_size, warmup_steps
  - Implement objective function for Optuna trials
  - Implement search method with pruning for unpromising trials
  - Save best hyperparameters to JSON file
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10_



- [x] 5.1 Implement HyperparameterSearch class initialization
  - Create `backend/scripts/training/hyperparameter_search.py`
  - Implement `__init__` with data_dir and output_dir parameters
  - Load train/val datasets from data_dir
  - Create output directory for search results

  - Set up logging for search progress
  - _Requirements: 6.1_


- [x] 5.2 Define search space and objective function
  - Implement `objective` method for Optuna trials
  - Define search space: learning_rate (log-uniform 1e-5 to 5e-5)
  - Define search space: batch_size (categorical [8, 16, 32])
  - Define search space: warmup_steps (categorical [100, 500, 1000])
  - Initialize ClassificationTrainer with trial hyperparameters
  - Train model for 3 epochs
  - Return validation accuracy as objective value
  - _Requirements: 6.2, 6.3, 6.4_


- [x] 5.3 Implement search method with Optuna

  - Implement `search` method with n_trials and timeout parameters
  - Create Optuna study with TPE sampler
  - Add MedianPruner for early stopping of unpromising trials
  - Set optimization direction to maximize (validation accuracy)
  - Run study.optimize() with objective function
  - Log trial results (hyperparameters and metrics)
  - Save best hyperparameters to JSON file
  - Return best hyperparameters and best value
  - _Requirements: 6.5, 6.6, 6.7, 6.8, 6.9_



- [x] 5.4 Implement visualization of search results
  - Implement `visualize_results` method with Optuna study
  - Generate optimization history plot
  - Generate parameter importance plot
  - Generate parallel coordinate plot
  - Save plots to output directory

  - _Requirements: 6.10_

- [x] 5.5 Write unit test for hyperparameter search


  - Test search runs with small n_trials (3 trials)
  - Test best hyperparameters are saved
  - Test search respects timeout
  - Test pruning works for unpromising trials
  - _Requirements: 6.5, 6.7, 6.9_


- [-] 6. Implement model versioning system














  - Implement ModelVersioning class with semantic versioning
  - Implement version creation with metadata storage
  - Implement version listing and loading
  - Implement production promotion with symlink
  - Implement version comparison on test data
  - Create version registry JSON file
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10_


- [x] 6.1 Implement ModelVersioning class initialization

  - Create `backend/scripts/deployment/model_versioning.py`
  - Implement `__init__` with base_dir parameter (default: "models/classification")
  - Create base directory if not exists
  - Initialize version registry file path
  - Load existing version registry or create new one
  - Set up logging for versioning operations
  - _Requirements: 7.1, 7.5, 7.7_

- [x] 6.2 Implement version creation with metadata


  - Implement `create_version` method with model_path, version, metadata parameters
  - Validate version format (vX.Y.Z regex)
  - Check if version already exists (raise error if yes)
  - Create version directory (models/classification/arxiv_vX.Y.Z/)
  - Copy model files to version directory
  - Save metadata to metadata.json (version, created_at, model_name, dataset, hyperparameters, metrics, model_size_mb)
  - Update version registry with new version
  - Log version creation
  - _Requirements: 7.2, 7.3, 7.6, 7.10_

- [x] 6.3 Implement version listing and loading


  - Implement `list_versions` method to return all available versions from registry
  - Implement `load_version` method with version parameter
  - Load model from version directory
  - Load metadata from metadata.json
  - Return tuple of (model, metadata)
  - Handle missing version error
  - _Requirements: 7.8_

- [x] 6.4 Implement production promotion


  - Implement `promote_to_production` method with version parameter
  - Validate version exists
  - Update version registry to mark version as "production"
  - Create or update "production" symlink to version directory
  - Update production_version in registry
  - Log promotion
  - _Requirements: 7.9_

- [x] 6.5 Implement version comparison


  - Implement `compare_versions` method with version1, version2, test_data parameters
  - Load both model versions
  - Evaluate both models on test_data
  - Compute metrics for each (accuracy, F1, latency)
  - Calculate improvement (version2 - version1)
  - Return comparison dictionary with metrics and improvement
  - _Requirements: 7.8_


- [x] 6.6 Write unit tests for model versioning





  - Test version creation with valid format
  - Test version creation rejects invalid format
  - Test version creation rejects duplicate versions
  - Test version listing returns all versions
  - Test version loading works correctly
  - Test production promotion updates registry
  - _Requirements: 7.2, 7.3, 7.8, 7.9, 7.10_



- [x] 7. Implement A/B testing framework
  - Implement ABTestingFramework class for comparing model versions
  - Implement experiment creation with traffic splitting
  - Implement prediction routing based on user ID hashing
  - Implement prediction logging for analysis
  - Implement experiment analysis with statistical significance testing
  - Implement winner promotion logic
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_




- [x] 7.1 Create database tables for A/B testing



  - Create migration for ab_test_experiments table (id, name, control_version_id, treatment_version_id, traffic_split, start_date, end_date, status, results)
  - Create migration for prediction_logs table (id, experiment_id, model_version_id, input_text, predictions, latency_ms, created_at, user_id)
  - Add indexes for efficient querying (experiment_id, model_version_id, created_at)
  - _Requirements: 8.1_



- [x] 7.2 Implement ABTestingFramework class initialization

  - Create `backend/scripts/deployment/ab_testing.py`
  - Implement `__init__` with db session parameter
  - Set up logging for A/B testing operations
  - _Requirements: 8.1_




- [x] 7.3 Implement experiment creation
  - Implement `create_experiment` method with name, control_version, treatment_version, traffic_split parameters
  - Validate control and treatment versions exist
  - Validate traffic_split is between 0.0 and 1.0
  - Create ABTestExperiment record in database
  - Set status to "running"
  - Return experiment ID
  - Log experiment creation
  - _Requirements: 8.2_

- [x] 7.4 Implement prediction routing

  - Implement `route_prediction` method with experiment_id and user_id parameters
  - Hash user_id to determine assignment (consistent routing)
  - Compare hash to traffic_split threshold
  - Return "control" or "treatment" version
  - Ensure same user always gets same version
  - _Requirements: 8.3_

- [x] 7.5 Implement prediction logging

  - Implement `log_prediction` method with experiment_id, version, input_text, predictions, latency_ms parameters
  - Create PredictionLog record in database
  - Include timestamp and user_id
  - Batch insert for efficiency (every 100 predictions)
  - _Requirements: 8.4_


- [x] 7.6 Implement experiment analysis

  - Implement `analyze_experiment` method with experiment_id parameter
  - Query prediction logs for control and treatment
  - Calculate metrics for each version (accuracy, latency_p95, f1_score)
  - Perform statistical significance testing (t-test for accuracy)
  - Calculate confidence intervals
  - Determine recommendation (PROMOTE, KEEP, or INCONCLUSIVE)
  - Save results to experiment.results JSON field
  - Return analysis dictionary
  - _Requirements: 8.5, 8.6_


- [x] 7.7 Implement winner promotion

  - Implement `promote_winner` method with experiment_id parameter
  - Load experiment analysis results
  - Check if treatment is significantly better (p < 0.05 and improvement > 2%)
  - If yes, promote treatment version to production using ModelVersioning
  - Update experiment status to "completed"
  - Send notification of promotion
  - If no, keep control version and mark experiment as "completed"
  - _Requirements: 8.7_


- [x] 7.8 Write integration test for A/B testing

  - Test experiment creation
  - Test prediction routing is consistent for same user
  - Test prediction logging works
  - Test experiment analysis calculates metrics correctly
  - Test promotion logic works when treatment is better
  - _Requirements: 8.2, 8.3, 8.4, 8.5, 8.7_




- [x] 8. Implement automated retraining pipeline


  - Implement RetrainingPipeline class with scheduled checks
  - Implement new data detection from arXiv API
  - Implement retraining trigger logic (data growth threshold)
  - Implement dataset augmentation with new data
  - Implement new model version training
  - Implement improvement evaluation against production
  - Implement automatic promotion if improvement exceeds threshold
  - Implement notification system for retraining results
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 9.10_

- [x] 8.1 Create database table for retraining runs


  - Create migration for retraining_runs table (id, trigger_type, dataset_size, new_data_count, model_version_id, status, started_at, completed_at, training_time_seconds, metrics, error_message)
  - Add indexes for efficient querying (status, started_at)
  - _Requirements: 9.9_


- [x] 8.2 Implement RetrainingPipeline class initialization

  - Create `backend/scripts/training/retrain_pipeline.py`
  - Implement `__init__` with config_path parameter
  - Load configuration from JSON file (schedule, thresholds, notification settings)
  - Initialize ArxivCollector, DatasetPreprocessor, ClassificationTrainer
  - Set up logging for pipeline operations
  - _Requirements: 9.1_


- [x] 8.3 Implement new data detection

  - Implement `check_for_new_data` method
  - Get last training date from version registry
  - Query arXiv API for papers published since last training
  - Count new papers by category
  - Return dictionary with new_data_count and new_papers
  - Log new data statistics
  - _Requirements: 9.2_


- [x] 8.4 Implement retraining trigger logic

  - Implement `should_retrain` method with new_data_count and current_dataset_size parameters
  - Calculate growth rate (new_data_count / current_dataset_size)
  - Check if growth rate exceeds threshold (default: 0.10 = 10%)
  - Return boolean indicating whether to retrain
  - Log decision and reasoning
  - _Requirements: 9.4_


- [x] 8.5 Implement dataset augmentation

  - Implement `augment_dataset` method with existing_data and new_data parameters
  - Combine existing and new data
  - Preprocess new data using DatasetPreprocessor
  - Create new train/val/test splits with stratification
  - Save augmented dataset to new directory
  - Return augmented dataset
  - _Requirements: 9.3_


- [x] 8.6 Implement new version training

  - Implement `train_new_version` method with dataset and current_version parameters
  - Increment minor version (e.g., v1.1.0 → v1.2.0)
  - Train model using ClassificationTrainer with augmented dataset
  - Evaluate on validation set
  - Save model checkpoint with new version
  - Create RetrainingRun record in database
  - Return new version and metrics
  - _Requirements: 9.5_


- [x] 8.7 Implement improvement evaluation

  - Implement `evaluate_improvement` method with new_version, production_version, test_data parameters
  - Load production model
  - Load new model
  - Evaluate both models on held-out test set
  - Calculate accuracy improvement (new - production)
  - Return comparison dictionary with metrics and improvement
  - _Requirements: 9.6_


- [x] 8.8 Implement automatic promotion logic

  - Implement `promote_if_better` method with new_version and comparison parameters
  - Check if improvement exceeds promotion threshold (default: 0.02 = 2%)
  - If yes, promote new version to production using ModelVersioning
  - If no, archive new version
  - Update RetrainingRun record with decision
  - Return boolean indicating promotion
  - _Requirements: 9.7_


- [x] 8.9 Implement notification system

  - Implement `send_notification` method with subject and message parameters
  - Send email notification to configured address
  - Send Slack notification to configured webhook
  - Include retraining results (dataset size, metrics, decision)
  - Log notification sent
  - _Requirements: 9.8_


- [x] 8.10 Implement complete pipeline execution

  - Implement `run_pipeline` method
  - Check for new data
  - Determine if retraining needed
  - If yes, augment dataset, train new version, evaluate improvement, promote if better
  - Send notification with results
  - Handle errors gracefully with retry logic
  - Update RetrainingRun record with status and results
  - _Requirements: 9.10_

- [x] 8.11 Write integration test for retraining pipeline


  - Test pipeline detects new data correctly
  - Test retraining trigger logic works
  - Test dataset augmentation combines data correctly
  - Test new version training works
  - Test improvement evaluation compares models correctly
  - Test promotion logic works when improvement exceeds threshold
  - _Requirements: 9.2, 9.4, 9.5, 9.6, 9.7_




- [x] 9. Implement training optimization and error handling






  - Implement GPU detection and mixed precision training
  - Implement gradient checkpointing for memory efficiency
  - Implement OOM error handling with batch size reduction
  - Implement training divergence detection (NaN/Inf loss)
  - Implement checkpoint corruption handling with backup loading
  - Implement data validation before training
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8, 13.9, 13.10_


- [x] 9.1 Implement GPU optimization in ClassificationTrainer



  - Detect GPU availability with torch.cuda.is_available()
  - Enable mixed precision (fp16) training when GPU available
  - Enable gradient checkpointing with model.gradient_checkpointing_enable()
  - Set device to cuda or cpu
  - Log GPU memory usage during training
  - Use DataLoader with num_workers for I/O parallelism
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.8, 10.9_

- [x] 9.2 Implement OOM error handling

  - Wrap training in try-except for RuntimeError
  - Check if error message contains "out of memory"
  - If OOM, clear GPU cache with torch.cuda.empty_cache()
  - Retry training with reduced batch size (half of original)
  - Log OOM error and batch size reduction
  - Suggest further batch size reduction if still OOM
  - _Requirements: 10.5, 13.4_

- [x] 9.3 Implement training divergence detection

  - Create TrainingDivergenceError exception class
  - Implement `check_training_health` function with loss and step parameters
  - Check if loss is NaN or Inf using math.isnan() and math.isinf()
  - If diverged, raise TrainingDivergenceError with diagnostic message
  - Suggest reducing learning rate or checking data quality
  - Call check_training_health after each training step
  - _Requirements: 13.6_


- [x] 9.4 Implement checkpoint validation and backup

  - Implement `load_checkpoint_with_validation` function
  - Try to load checkpoint with torch.load()
  - Validate required keys exist (model_state_dict, metadata)
  - If validation fails, try loading from backup checkpoint (.backup file)
  - If backup also fails, raise error with clear message
  - Save backup checkpoint before overwriting existing checkpoint
  - _Requirements: 10.6, 10.7, 13.7_



- [x] 9.5 Implement data validation

  - Implement `validate_sample` function to check required fields (text, label, arxiv_id)
  - Check text is not empty and has minimum length (10 words)
  - Implement `validate_labels` function to check all labels are in expected set
  - Log validation errors with sample indices
  - Raise ValueError if validation fails with clear error message
  - Call validation before starting training
  - _Requirements: 13.8, 13.9_


- [x] 9.6 Write unit tests for error handling

  - Test OOM error handling reduces batch size
  - Test training divergence detection raises error on NaN loss
  - Test checkpoint validation detects missing keys
  - Test checkpoint backup loading works
  - Test data validation detects invalid samples
  - _Requirements: 10.5, 13.4, 13.6, 13.7, 13.8_





- [x] 10. Implement monitoring and observability
  - Implement TensorBoard logging for training metrics
  - Implement prediction monitoring with metrics tracking
  - Implement alerting for high error rate and latency
  - Implement health check endpoint for model status
  - Implement structured JSON logging

  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9, 14.10_


- [x] 10.1 Implement TensorBoard logging in ClassificationTrainer
  - Import SummaryWriter from torch.utils.tensorboard
  - Create writer with log_dir in checkpoint directory
  - Log training loss every 100 steps with writer.add_scalar("Loss/train", loss, step)
  - Log validation accuracy and F1 after each epoch
  - Log learning rate schedule
  - Log model graph with writer.add_graph(model, sample_input)
  - Close writer after training
  - _Requirements: 14.1, 14.2, 14.3_


- [x] 10.2 Implement PredictionMonitor class

  - Create `backend/app/monitoring/prediction_monitor.py`
  - Implement `__init__` to initialize prediction and latency lists
  - Implement `log_prediction` method to record predictions with timestamp, input_length, predictions, latency_ms, error
  - Implement `get_metrics` method with window_minutes parameter
  - Calculate metrics for recent predictions (total_predictions, error_rate, latency_p50/p95/p99, avg_confidence, low_confidence_rate)
  - Return metrics dictionary
  - _Requirements: 14.4, 14.5_


- [x] 10.3 Implement AlertManager class

  - Create `backend/app/monitoring/alert_manager.py`
  - Implement `__init__` with slack_webhook parameter
  - Implement `check_and_alert` method with metrics parameter
  - Check for high error rate (>5%), high latency (p95 >200ms), high low-confidence rate (>30%)
  - Collect alerts for threshold violations
  - Implement `send_slack_alert` method to POST to Slack webhook
  - Call send_slack_alert if any alerts triggered
  - _Requirements: 14.6_

- [x] 10.4 Implement model health check


  - Create `backend/app/monitoring/health_check.py`
  - Implement `check_model_health` function
  - Check model is loaded (model is not None)
  - Check checkpoint file exists and is valid
  - Check inference works with test input
  - Check latency is acceptable (<200ms)
  - Return dictionary with check results (model_loaded, checkpoint_valid, inference_working, latency_acceptable)
  - _Requirements: 14.7, 14.8_


- [x] 10.5 Implement health check API endpoint

  - Add GET /health/ml endpoint to FastAPI app
  - Call check_model_health() function
  - Return 200 with status "healthy" if all checks pass
  - Return 503 with status "unhealthy" if any check fails
  - Include check details in response
  - _Requirements: 14.8_

- [x] 10.6 Implement structured JSON logging


  - Create JSONFormatter class inheriting from logging.Formatter
  - Implement `format` method to create JSON log entries
  - Include timestamp, level, logger, message, module, function, line
  - Include exception traceback if present
  - Configure logger to use JSONFormatter
  - _Requirements: 14.9, 14.10_


- [x] 10.7 Write unit tests for monitoring


  - Test PredictionMonitor logs predictions correctly
  - Test PredictionMonitor calculates metrics correctly
  - Test AlertManager detects threshold violations
  - Test health check detects model issues
  - Test JSON logging formats correctly
  - _Requirements: 14.4, 14.5, 14.6, 14.7, 14.9_


- [x] 11. Implement deployment infrastructure




  - Implement blue-green deployment strategy
  - Implement canary deployment with gradual rollout
  - Implement automatic rollback on metric degradation
  - Implement deployment validation and smoke tests
  - Create deployment scripts and documentation
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8, 15.9, 15.10_


- [x] 11.1 Implement BlueGreenDeployment class

  - Create `backend/scripts/deployment/blue_green.py`
  - Implement `__init__` to initialize blue and green versions
  - Implement `deploy_green` method to deploy new version to green environment
  - Implement `warmup_model` method to warm up model with sample requests
  - Implement `health_check` method to verify green environment health
  - Implement `switch_to_green` method to switch traffic to green
  - Implement `rollback` method to switch back to blue
  - Implement `detect_issues` method to monitor for problems after switch
  - _Requirements: 15.1, 15.2, 15.3_


- [x] 11.2 Implement CanaryDeployment class

  - Create `backend/scripts/deployment/canary.py`
  - Implement `__init__` to initialize production and canary versions
  - Implement `gradual_rollout` method with stages [5, 10, 25, 50, 100]
  - Update traffic split at each stage
  - Monitor metrics for 1 hour at each stage
  - Implement `metrics_acceptable` method to compare canary vs production
  - Check error rate (canary < production * 1.5)
  - Check latency (canary p95 < production p95 * 1.2)
  - Rollback if metrics degrade
  - _Requirements: 15.4, 15.5_


- [x] 11.3 Implement automatic rollback monitoring

  - Create `backend/scripts/deployment/rollback_monitor.py`
  - Implement `monitor_and_rollback` function
  - Continuously monitor production metrics (error_rate, latency_p95)
  - If error rate >10%, trigger automatic rollback
  - If latency p95 >500ms, trigger automatic rollback
  - Implement `rollback_to_previous_version` function
  - Load previous production version from version registry
  - Switch traffic to previous version
  - Send alert notification
  - _Requirements: 15.6, 15.7_

- [x] 11.4 Implement deployment validation


  - Create `backend/scripts/deployment/validate.py`
  - Implement `validate_deployment` function
  - Load model from checkpoint
  - Run smoke tests (predict on sample inputs)
  - Verify predictions are reasonable
  - Check model size is within limits (<500MB)
  - Check inference latency is acceptable (<100ms)
  - Return validation results
  - _Requirements: 15.8, 15.9, 15.10_


- [x] 11.5 Create deployment scripts

  - Create `backend/scripts/deployment/deploy.sh` script
  - Implement steps: validate model, deploy to staging, run tests, deploy to production
  - Create `backend/scripts/deployment/rollback.sh` script
  - Implement steps: load previous version, switch traffic, verify health
  - Add command-line arguments for version and environment
  - _Requirements: 15.1, 15.6_


- [x] 11.6 Write integration test for deployment

  - Test blue-green deployment switches traffic correctly
  - Test canary deployment gradual rollout works
  - Test automatic rollback triggers on high error rate
  - Test deployment validation detects issues
  - _Requirements: 15.1, 15.4, 15.6, 15.8_


- [ ] 12. Create comprehensive documentation






  - Create MODEL_TRAINING.md with step-by-step training guide
  - Document dataset collection process and API usage
  - Document preprocessing steps and quality filters
  - Document training configuration and hyperparameters
  - Document evaluation metrics and benchmarks
  - Document deployment procedures and rollback
  - Create troubleshooting guide for common issues
  - Create API documentation for all classes
  - Create runbook for production incidents

  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 12.10_



- [x] 12.1 Create MODEL_TRAINING.md guide


  - Create `backend/docs/MODEL_TRAINING.md`
  - Add Quick Start section with 4-step process (install, collect, preprocess, train)
  - Add Detailed Steps section with command examples for each step
  - Include expected time and output for each step
  - Add Hyperparameter Tuning section with Optuna usage
  - Add Troubleshooting section (OOM, slow training, low accuracy)
  - Include hardware requirements (GPU, memory, disk space)
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.10_



- [x] 12.2 Create API documentation

  - Add docstrings to all classes and methods
  - Include parameter descriptions and return types
  - Add usage examples in docstrings
  - Document exceptions that can be raised
  - Use Google-style docstring format

  - _Requirements: 12.8_

- [x] 12.3 Create production runbook

  - Create `backend/docs/PRODUCTION_RUNBOOK.md`
  - Add incident response procedures (high error rate, high latency, low confidence)
  - Include diagnostic commands (health check, logs, metrics)
  - Include rollback procedures with commands
  - Add escalation procedures
  - _Requirements: 12.9_


- [x] 12.4 Create deployment checklist

  - Create `backend/docs/DEPLOYMENT_CHECKLIST.md`
  - Add pre-deployment checklist (model trained, tests passing, staging successful)
  - Add deployment checklist (create version, deploy to staging, deploy to production)
  - Add post-deployment checklist (verify metrics, monitor for 24 hours, update registry)
  - _Requirements: 12.6_

- [x] 13. Integration with existing MLClassificationService




  - Update MLClassificationService to load models from versioned checkpoints
  - Add support for loading specific model versions
  - Add support for A/B testing in prediction endpoint
  - Update prediction logging to use PredictionMonitor
  - Ensure backward compatibility with existing code
  - _Requirements: 15.1, 15.2, 15.8_

- [x] 13.1 Update MLClassificationService model loading


  - Modify `_load_model` method to check for versioned checkpoints
  - Try loading from production symlink first
  - Fall back to model_version parameter if specified
  - Fall back to base model if no checkpoint found
  - Log which model version was loaded
  - _Requirements: 15.1, 15.2_


- [x] 13.2 Add version parameter to MLClassificationService

  - Add optional `version` parameter to `__init__` method
  - If version specified, load that specific version
  - If not specified, load production version
  - Update checkpoint_dir to use version path
  - _Requirements: 15.1_


- [x] 13.3 Integrate A/B testing in prediction endpoint

  - Add A/B testing logic to predict method
  - Check if active experiment exists
  - Route prediction to control or treatment based on user_id
  - Log prediction with experiment_id and version
  - Return predictions with version metadata
  - _Requirements: 15.8_



- [x] 13.4 Integrate PredictionMonitor

  - Import PredictionMonitor in MLClassificationService
  - Initialize monitor in `__init__`
  - Call monitor.log_prediction() after each prediction
  - Expose get_metrics() method for monitoring
  - _Requirements: 15.8_

- [x] 13.5 Write integration tests


  - Test MLClassificationService loads versioned models correctly
  - Test A/B testing routes predictions correctly
  - Test prediction monitoring logs correctly
  - Test backward compatibility with existing code
  - _Requirements: 15.1, 15.2, 15.8_


-

- [-] 14. End-to-end validation and benchmarking

  - Run complete pipeline from data collection to deployment
  - Validate model achieves ≥90% accuracy on test set
  - Validate model size is <500MB
  - Validate training completes in <4 hours on GPU
  - Validate inference latency is <100ms (p95)
  - Run benchmark tests and generate report
  - Document results and performance metrics
  - _Requirements: 4.11, 4.12, 5.4, 5.5, 14.1, 14.2, 14.3, 15.3, 15.4, 15.9, 15.10_


- [x] 14.1 Run end-to-end pipeline

  - Collect 10,000 arXiv papers using ArxivCollector
  - Preprocess dataset using DatasetPreprocessor
  - Create train/val/test splits
  - Train model using ClassificationTrainer
  - Evaluate on test set
  - Create model version
  - Deploy to staging
  - Run validation tests
  - Document each step with timing and results
  - _Requirements: 1.7, 2.9, 3.5, 4.11, 4.12_


- [x] 14.2 Validate performance metrics

  - Check test accuracy ≥90%
  - Check F1 score ≥88%
  - Check model size <500MB
  - Check training time <4 hours on V100 GPU
  - Check inference latency <100ms (p95)
  - Document actual metrics achieved
  - _Requirements: 4.11, 4.12, 5.4, 5.5, 15.3, 15.4_



- [x] 14.3 Run benchmark suite





  - Run existing ML benchmark tests with new model
  - Verify all tests pass
  - Compare performance with baseline model
  - Generate benchmark report with metrics comparison

  - _Requirements: 14.1, 14.2, 14.3_








- [x] 14.4 Create performance report
  - Create `backend/docs/PRODUCTION_ML_TRAINING_RESULTS.md`
  - Document dataset statistics (size, categories, quality)
  - Document training results (accuracy, F1, training time, model size)
  - Document inference performance (latency, throughput)
  - Include comparison with baseline model
  - Include lessons learned and recommendations
  - _Requirements: 12.5, 14.1, 14.2, 14.3_

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements from requirements.md
- Tasks build incrementally - no orphaned code
- Focus on production-ready, well-tested implementations
- Testing and documentation are integral parts of each component

## Execution Order

1. **Setup** (Task 1): Project structure and dependencies
2. **Data Collection** (Task 2): arXiv dataset collector
3. **Preprocessing** (Task 3): Data cleaning and splitting
4. **Training** (Task 4): Classification model training
5. **Hyperparameter Tuning** (Task 5): Optuna search
6. **Versioning** (Task 6): Model version management
7. **A/B Testing** (Task 7): Experiment framework
8. **Retraining** (Task 8): Automated pipeline
9. **Optimization** (Task 9): Error handling and GPU optimization
10. **Monitoring** (Task 10): Observability and alerting
11. **Deployment** (Task 11): Blue-green and canary deployment
12. **Documentation** (Task 12): Comprehensive guides
13. **Integration** (Task 13): Connect with existing services
14. **Validation** (Task 14): End-to-end testing and benchmarking

## Success Criteria

- ✅ All core tasks (non-optional) completed
- ✅ Model achieves ≥90% test accuracy
- ✅ Model size <500MB
- ✅ Training time <4 hours on GPU
- ✅ Inference latency <100ms (p95)
- ✅ Automated retraining pipeline working
- ✅ Model versioning and A/B testing functional
- ✅ Documentation complete and accurate
- ✅ Integration with existing services successful
- ✅ All benchmark tests passing
