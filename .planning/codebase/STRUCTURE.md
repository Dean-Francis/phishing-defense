# Codebase Structure

**Analysis Date:** 2026-01-20

## Directory Layout

```
phishing_defense_V2/
├── tier1_url/                  # Tier 1 URL-based phishing detector
│   ├── models/                 # Serialized ML models
│   │   └── tier1_url_detector.pkl
│   ├── tier1_features.py       # Feature extraction logic
│   ├── tier1_training.py       # Model training orchestration
│   ├── tier1_inference.py      # Production inference engine
│   └── test.py                 # Test/sandbox file (unused)
├── data/                        # Training datasets and ground truth
│   ├── training_dataset_clean.csv
│   └── Golden_Sheet.csv
├── .planning/                   # GSD planning documents
│   └── codebase/
├── requirements.txt             # Python dependencies
└── .gitignore                   # Git ignore rules
```

## Directory Purposes

**tier1_url/**
- Purpose: First-stage phishing detection based on URL structural features
- Contains: Feature extraction, model training, and inference logic
- Key files: `tier1_features.py`, `tier1_training.py`, `tier1_inference.py`
- Status: Active development (Tier 1 implementation complete, Tier 2+ to follow)

**tier1_url/models/**
- Purpose: Store serialized LightGBM classification models
- Contains: Pickled model artifacts with embedded feature information
- Key files: `tier1_url_detector.pkl` (1.1 MB binary)
- Generated: Yes (via tier1_training.py)
- Committed: No (listed in .gitignore as *.pkl)

**data/**
- Purpose: Store training data and reference datasets
- Contains: CSV files with URLs and phishing/benign labels
- Key files: `training_dataset_clean.csv` (583KB), `Golden_Sheet.csv` (68KB)
- Generated: External (sourced from phishing databases)
- Committed: No (listed in .gitignore as data/)

**.planning/codebase/**
- Purpose: Architecture and implementation reference documents
- Contains: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md
- Generated: Yes (via gsd:map-codebase command)
- Committed: Yes (contains guidance for future development)

## Key File Locations

**Entry Points:**
- `tier1_url/tier1_training.py`: Training entry point (lines 125-127)
- `tier1_url/tier1_inference.py`: Inference entry point (lines 91-118)

**Configuration:**
- `requirements.txt`: Python package dependencies (19 packages)

**Core Logic:**
- `tier1_url/tier1_features.py`: URLFeatureExtractor class with 18 features extracted from URLs
- `tier1_url/tier1_training.py`: URLDetectorTrainer orchestrator with LightGBM configuration
- `tier1_url/tier1_inference.py`: URLDetectorInference API with batch support

**Models:**
- `tier1_url/models/tier1_url_detector.pkl`: Trained LightGBM model + feature names (binary pickle)

**Testing:**
- `tier1_url/test.py`: Unused test file (likely sandbox for development)

## Naming Conventions

**Files:**
- Python modules: `tier<N>_<focus>.py` (e.g., tier1_features.py, tier1_training.py)
- Model artifacts: `tier<N>_<detector_type>.pkl` (e.g., tier1_url_detector.pkl)
- Data files: `<dataset_name>.csv` (e.g., training_dataset_clean.csv)

**Directories:**
- Tier-based organization: `tier1_url`, `tier2_*` (planned), `tier3_*` (planned)
- Functional grouping: `models/` for artifacts, `data/` for datasets

**Classes:**
- Detector classes: `<Tier><Focus>Detector` or `<Focus>Detector<Tier>` (e.g., URLDetectorTrainer)
- Feature classes: `<Input>FeatureExtractor` (e.g., URLFeatureExtractor)

**Functions/Methods:**
- Public methods: `snake_case` (e.g., extract_features, predict_batch)
- Private methods: `_snake_case` prefix (e.g., _get_null_features, _load_model)
- Action verbs: extract, predict, train, load, save

**Variables:**
- Model/feature names: lowercase with underscores (e.g., feature_names, model_path)
- Data structures: descriptive plural for collections (e.g., features_list, results)
- Scores/probabilities: `_score`, `_proba` suffix (e.g., phishing_score, y_pred_proba)

**Types:**
- No explicit type annotation files (uses inline type hints via PEP 484 comments and ->)

## Where to Add New Code

**New Tier (e.g., Tier 2 - Content-based detection):**
- Create directory: `tier2_content/`
- Implement structure: `tier2_content/tier2_features.py`, `tier2_content/tier2_training.py`, `tier2_content/tier2_inference.py`
- Store models: `tier2_content/models/`
- Follow same class naming pattern: `ContentFeatureExtractor`, `ContentDetectorTrainer`, `ContentDetectorInference`

**New Feature Extractor:**
- Location: Create new class in existing tier (e.g., `EmailFeatureExtractor` in tier1_url if adding email features)
- Or: Create new tier directory if orthogonal concern (e.g., `tier1_email/`)
- Pattern: Follow URLFeatureExtractor structure (extract_features, extract_from_dataframe, private helper methods)

**New Model Training Script:**
- Location: `tier<N>_<focus>/<focus>_training.py`
- Pattern: Inherit URLDetectorTrainer structure if same model framework, otherwise replicate pattern
- Must: Store model + feature names together in pickle
- Must: Implement _save_model() with os.makedirs for models/ directory

**New Inference/Prediction Service:**
- Location: `tier<N>_<focus>/<focus>_inference.py`
- Pattern: Follow URLDetectorInference (lazy model load, predict method, metadata enrichment)
- Must: Return standard result format with score, label, confidence, escalate flag, metadata

**Test Utilities:**
- Location: `tier<N>_<focus>/test.py` or new `tests/` directory if formalized
- Pattern: Currently ad-hoc main block; consider pytest structure for shared test utilities

**Shared Utilities (future):**
- Location: Create `utils/` directory at project root
- Modules: validation.py, constants.py, metrics.py, etc.
- Pattern: Import from utils in all tiers

**Data Files:**
- Location: `data/<descriptive_name>.csv`
- Pattern: CSV format with minimal columns (url, label minimum)
- Naming: Include data source or preprocessing stage (e.g., training_dataset_clean.csv)

## Special Directories

**__pycache__/**
- Purpose: Python bytecode cache (auto-generated)
- Generated: Yes
- Committed: No (in .gitignore as __pycache__/)

**venv/**
- Purpose: Python virtual environment with pinned dependencies
- Generated: Yes (via python -m venv)
- Committed: No (standard practice)

**.git/**
- Purpose: Git repository metadata and history
- Generated: Yes (via git init)
- Committed: N/A (internal)

**.planning/codebase/**
- Purpose: Architecture and quality reference documents
- Generated: Yes (via gsd:map-codebase)
- Committed: Yes

---

*Structure analysis: 2026-01-20*
