# Technology Stack

**Analysis Date:** 2026-01-20

## Languages

**Primary:**
- Python 3.14.2 - All source code and ML training/inference

## Runtime

**Environment:**
- Python 3.14.2 from `/usr/bin/python3.14`

**Package Manager:**
- pip (bundled with Python)
- Lockfile: `requirements.txt` (pinned versions present)

## Frameworks

**Core ML/Data Processing:**
- scikit-learn 1.8.0 - Classification models, metrics, train/test split utilities
- LightGBM 4.6.0 - Gradient boosting classifier for phishing URL detection
- pandas 2.3.3 - Data loading, manipulation, and feature extraction
- NumPy 2.4.1 - Numerical computations for entropy calculations

**Feature Engineering:**
- tldextract 5.3.1 - Domain/TLD extraction from URLs
- urllib (stdlib) - URL parsing via `urllib.parse.urlparse`
- requests 2.32.5 - HTTP client (present in dependencies but not used in current codebase)

**Utilities:**
- joblib 1.5.3 - Model serialization/deserialization to disk

## Key Dependencies

**Critical:**
- LightGBM 4.6.0 - Core ML engine for binary phishing classification
- scikit-learn 1.8.0 - Provides model evaluation metrics (ROC-AUC, confusion matrix, classification reports)
- pandas 2.3.3 - Required for DataFrame-based feature extraction and data handling
- NumPy 2.4.1 - Underlying numerical operations for ML and entropy calculations

**Infrastructure:**
- certifi 2026.1.4 - SSL certificate validation for requests
- idna 3.11 - Unicode domain name handling
- urllib3 2.6.3 - HTTP library backend (used by requests)
- charset-normalizer 3.4.4 - Character encoding detection
- python-dateutil 2.9.0.post0 - Date utilities (dependency of pandas)
- pytz 2025.2 - Timezone support (dependency of pandas)
- scipy 1.17.0 - Scientific computing (dependency of scikit-learn)
- threadpoolctl 3.6.0 - Thread pool management for sklearn/LightGBM parallelization
- six 1.17.0 - Python 2/3 compatibility layer
- filelock 3.20.3 - File locking utilities
- tzdata 2025.3 - Timezone database

## Configuration

**Environment:**
- Virtual environment located at `venv/` with `include-system-site-packages = false`
- No `.env` file required currently (model paths and thresholds hardcoded in source)

**Build:**
- No build configuration files detected (pure Python scripts, no compilation)
- Model serialization uses joblib: `models/tier1_url_detector.pkl`

## Platform Requirements

**Development:**
- Python 3.14.2
- pip package manager
- Virtual environment support
- ~200MB disk space for venv + dependencies

**Production:**
- Python 3.14.2 runtime
- Trained LightGBM model file at `models/tier1_url_detector.pkl`
- No external services required for inference (models run locally)

---

*Stack analysis: 2026-01-20*
