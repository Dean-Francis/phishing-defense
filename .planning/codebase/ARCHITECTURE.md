# Architecture

**Analysis Date:** 2026-01-20

## Pattern Overview

**Overall:** Layered ML Pipeline with Clear Separation of Concerns

**Key Characteristics:**
- Three-tier phishing detection system (Tier 1 URL-based detection implemented)
- Feature extraction abstracted from model training and inference
- Supervised learning pipeline with train/test/predict pattern
- Stateless inference with model persistence via serialization
- Single responsibility principle: each module handles one concern

## Layers

**Feature Extraction Layer:**
- Purpose: Transform raw URLs into numerical features for ML model consumption
- Location: `tier1_url/tier1_features.py`
- Contains: `URLFeatureExtractor` class with feature computation logic
- Depends on: Standard libraries (urllib, re, numpy, pandas, tldextract)
- Used by: Training and inference layers

**Training Layer:**
- Purpose: Build and train LightGBM classification model using extracted features
- Location: `tier1_url/tier1_training.py`
- Contains: `URLDetectorTrainer` class orchestrating data loading, model training, evaluation, and persistence
- Depends on: Feature extraction layer, scikit-learn, LightGBM, joblib
- Used by: Development/experimentation workflows (not production)

**Inference Layer:**
- Purpose: Load trained model and generate predictions on new URLs
- Location: `tier1_url/tier1_inference.py`
- Contains: `URLDetectorInference` class handling model loading, prediction, and confidence calculation
- Depends on: Feature extraction layer, joblib, pandas
- Used by: Production detection systems, API endpoints (future)

**Data Layer:**
- Purpose: Persistent storage of training data and artifacts
- Location: `data/` directory and `tier1_url/models/`
- Contains: CSV training datasets, serialized model artifacts (.pkl files)
- Depends on: File system
- Used by: Training and inference layers

## Data Flow

**Training Flow:**

1. Raw CSV with URL and binary label (0/1) loaded from `data/training_dataset_clean.csv`
2. `URLDetectorTrainer.load_data()` calls `URLFeatureExtractor.extract_from_dataframe()` to vectorize all URLs
3. Features DataFrame passed to scikit-learn's `train_test_split()` for 80/20 stratified split
4. LightGBM model trained on training set with validation set for early stopping
5. Model evaluated on test set (classification_report, ROC-AUC, confusion matrix)
6. Cross-validation performed on full dataset (5-fold)
7. Feature importance calculated and printed
8. Serialized model + feature_names list saved to `tier1_url/models/tier1_url_detector.pkl`

**Inference Flow:**

1. `URLDetectorInference` initialized with model path and confidence threshold (default 0.85)
2. Model and feature names deserialized from pickle file on initialization
3. Input: Dictionary with 'url' key
4. `URLFeatureExtractor.extract_features()` vectorizes single URL
5. Feature order aligned with training via `feature_names` lookup
6. Model generates probability score via `predict()`
7. Score thresholded to binary label (>=0.5 = phishing, <0.5 = benign)
8. Confidence determined: 'high' if score >= threshold or <= (1-threshold), else 'low'
9. Low confidence triggers escalation flag (escalate=True)
10. Top 5 feature contributions extracted and returned
11. Result includes score, label, confidence, escalation flag, and metadata

**State Management:**
- Training state: Maintained in `URLDetectorTrainer` instance during training session; not persisted
- Model state: Persisted in pickle format at `tier1_url/models/tier1_url_detector.pkl`
- Feature state: Feature names list stored alongside model to ensure consistent feature ordering
- Inference state: Stateless after model load (same inference engine can process multiple URLs)

## Key Abstractions

**URLFeatureExtractor:**
- Purpose: Encapsulate URL parsing and feature engineering logic
- Examples: `tier1_url/tier1_features.py` (URLFeatureExtractor class)
- Pattern: Accepts raw URL strings, returns numerical feature dictionaries; supports single-row and batch operations

**URLDetectorTrainer:**
- Purpose: Manage end-to-end model training lifecycle
- Examples: `tier1_url/tier1_training.py` (URLDetectorTrainer class)
- Pattern: Orchestrator pattern - coordinates feature extraction, data loading, model training, evaluation, and persistence

**URLDetectorInference:**
- Purpose: Provide production-ready inference interface for URL classification
- Examples: `tier1_url/tier1_inference.py` (URLDetectorInference class)
- Pattern: Lazy initialization (model loaded on __init__), single predict method for batching, metadata enrichment

## Entry Points

**Training Entry Point:**
- Location: `tier1_url/tier1_training.py` main block (lines 125-127)
- Triggers: Manual execution via `python tier1_url/tier1_training.py`
- Responsibilities: Initialize trainer, call train() with CSV path, prints results to stdout

**Inference Entry Point:**
- Location: `tier1_url/tier1_inference.py` main block (lines 91-118)
- Triggers: Manual execution via `python tier1_url/tier1_inference.py`
- Responsibilities: Initialize inference engine, predict on test URL examples, print formatted results

**Model Creation Entry Point:**
- Location: `tier1_url/tier1_training.py::URLDetectorTrainer::train()`
- Output: Serialized model saved to `tier1_url/models/tier1_url_detector.pkl`
- Precondition: Training data CSV must exist at specified path

## Error Handling

**Strategy:** Exception suppression in feature extraction with fallback to null features

**Patterns:**
- Feature extraction catches generic Exception and returns zero-valued feature dict on parse failure
- Model loading raises FileNotFoundError if pickle not found (hard fail for inference)
- Type validation on URL input (checks isinstance(url, str))
- Division by zero protection in entropy calculation (checks if p > 0)

## Cross-Cutting Concerns

**Logging:**
- Print-based logging to stdout in training and inference main blocks
- Progress indicators during model training (LightGBM log_evaluation every 50 rounds)
- Model path printed on load/save

**Validation:**
- Input type checking (url must be string)
- Null feature fallback for invalid URLs
- Feature alignment check in inference (reorders features by feature_names list)

**Model Persistence:**
- Pickle format for model serialization via joblib
- Feature names stored alongside model to prevent feature mismatch
- Model directory auto-created if missing (os.makedirs with exist_ok=True)

---

*Architecture analysis: 2026-01-20*
