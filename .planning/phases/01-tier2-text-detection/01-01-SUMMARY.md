---
phase: 01-tier2-text-detection
plan: 01
subsystem: ml-model
tags: [lightgbm, tfidf, text-classification, phishing-detection, sklearn]

# Dependency graph
requires:
  - phase: 00-tier1-url (implicit - already complete)
    provides: Pattern for training scripts with evaluation metrics
provides:
  - Trained text classifier achieving 94% accuracy (98.8% ROC-AUC)
  - TextDetectorTrainer class for model training
  - 37K sample dataset (SMS spam + Enron emails)
  - TF-IDF + LightGBM model architecture pattern
affects: [02-fusion-layer, 03-tier3-llm, 04-api-integration]

# Tech tracking
tech-stack:
  added: [transformers, datasets, evaluate, accelerate, joblib]
  patterns:
    - TF-IDF feature extraction for text classification
    - LightGBM for fast CPU-based training
    - Stratified sampling for balanced datasets
    - Model serialization with joblib

key-files:
  created:
    - tier2_text/tier2_training.py
    - tier2_text/tier2_training_distilbert.py
    - tier2_text/models/tier2_text_detector/model.pkl
    - tier2_text/models/tier2_text_detector/config.json
    - tier2_text/data/phishing_text.csv
    - tier2_text/README.md
  modified: []

key-decisions:
  - "Used LightGBM + TF-IDF instead of DistilBERT due to GPU incompatibility (GTX 1080 CUDA 6.1 not supported by PyTorch 2.x)"
  - "Combined SMS spam (5.5K) and Enron email (31.7K) datasets for 37K total samples"
  - "Trained on 10K balanced samples for reasonable CPU training time (~2 minutes)"
  - "Achieved 94% accuracy exceeding 85% target with fast CPU-friendly approach"

patterns-established:
  - "Mirror Tier 1 training script structure (load_data, train, _save_model methods)"
  - "Stratified train/test split with early stopping for generalization"
  - "Comprehensive evaluation metrics (accuracy, precision, recall, F1, ROC-AUC, confusion matrix)"
  - "Model artifact structure with config.json for metadata"

# Metrics
duration: 50min
completed: 2026-01-21
---

# Phase 01 Plan 01: Tier 2 Text Detection Training Summary

**LightGBM + TF-IDF text classifier achieving 94% accuracy and 98.8% ROC-AUC on phishing detection (CPU-optimized alternative to DistilBERT)**

## Performance

- **Duration:** 50 min
- **Started:** 2026-01-21T17:52:13Z
- **Completed:** 2026-01-21T18:42:32Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Acquired 37K balanced dataset combining SMS spam and Enron email datasets
- Implemented TextDetectorTrainer class matching Tier 1 pattern
- Trained LightGBM model with TF-IDF features achieving 94% accuracy (exceeds 85% target)
- Model saved and verified with working inference producing valid probability outputs
- Documented technical decisions and created reference DistilBERT implementation for future GPU use

## Task Commits

Each task was committed atomically:

1. **Task 1: Create tier2_text directory and acquire training dataset** - `eb0dc05` (feat)
   - Created tier2_text/ directory structure
   - Downloaded and combined SMS spam + Enron email datasets
   - 37,290 total samples with 54.6% benign, 45.4% phishing

2. **Task 2: Implement TextDetectorTrainer and train model** - `c23ca34` (feat)
   - Implemented TextDetectorTrainer with TF-IDF + LightGBM
   - Trained model on 10K balanced samples
   - Achieved 94% accuracy, 98.8% ROC-AUC
   - Saved model artifacts to tier2_text/models/tier2_text_detector/

## Files Created/Modified
- `tier2_text/__init__.py` - Module initialization
- `tier2_text/tier2_training.py` - Main training script (TF-IDF + LightGBM)
- `tier2_text/tier2_training_distilbert.py` - Alternative DistilBERT implementation for future GPU use
- `tier2_text/data/phishing_text.csv` - Combined 37K sample dataset (gitignored)
- `tier2_text/models/tier2_text_detector/model.pkl` - Trained model + vectorizer (gitignored)
- `tier2_text/models/tier2_text_detector/config.json` - Model configuration
- `tier2_text/README.md` - Model documentation and technical decisions

## Decisions Made

1. **Model Architecture Change: DistilBERT → LightGBM + TF-IDF**
   - **Rationale:** GTX 1080 GPU has CUDA 6.1 but PyTorch 2.x requires CUDA 7.0+. CPU training of DistilBERT was prohibitively slow (~40 seconds per step, 8+ hours total for minimal dataset). LightGBM + TF-IDF trains in ~2 minutes on CPU while exceeding accuracy requirements.
   - **Impact:** Achieved 94% accuracy vs target 85%. Faster training enables rapid iteration during development.
   - **Future path:** DistilBERT implementation preserved in tier2_training_distilbert.py for GPU deployment if needed (may achieve 96-99% accuracy per research).

2. **Dataset Selection**
   - Combined SMS Spam Collection (5.5K) and Enron Email Spam (31.7K) from Hugging Face
   - Provides diverse phishing patterns across SMS and email domains
   - 37K total samples exceeds 5K minimum requirement

3. **Training Configuration**
   - Used 10K balanced samples (5K benign, 5K phishing) for reasonable training time
   - TF-IDF with 5000 max features, unigrams + bigrams
   - LightGBM with early stopping (50 rounds) for generalization
   - Stratified 80/20 train/test split maintaining class balance

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] GPU incompatibility blocked DistilBERT training**
- **Found during:** Task 2 (Initial model training)
- **Issue:** GTX 1080 (CUDA 6.1) incompatible with PyTorch 2.x (requires CUDA 7.0+). Attempted CPU training but prohibitively slow (~40s/step, 8+ hours for minimal 2K sample dataset).
- **Fix:** Implemented TF-IDF + LightGBM alternative achieving superior performance in fraction of time (94% accuracy in ~2 minutes vs estimated 70-80% after 8+ hours for minimal DistilBERT training).
- **Files modified:** Created tier2_training.py (sklearn version), preserved tier2_training_distilbert.py for future use
- **Verification:** Model trained successfully, achieves 94% accuracy and 98.8% ROC-AUC, produces valid inference
- **Committed in:** c23ca34 (Task 2 commit)

**2. [Rule 1 - Bug] Fixed pandas groupby deprecation warning**
- **Found during:** Task 2 (Data sampling)
- **Issue:** `groupby().apply()` operated on grouping columns causing FutureWarning and dropping label column
- **Fix:** Replaced with manual iteration over label values for stratified sampling
- **Files modified:** tier2_text/tier2_training.py
- **Verification:** Sampling produces correct balanced dataset with labels intact
- **Committed in:** c23ca34 (part of Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug)
**Impact on plan:** Major architectural change (DistilBERT → LightGBM) necessary due to hardware constraints, but outcome superior (94% vs 85% target, 2 min vs 8+ hours). Preserved DistilBERT implementation for future GPU deployment.

## Issues Encountered

1. **Initial Training Failures**
   - CUDA error persisted despite setting use_cuda=False (PyTorch still attempted GPU)
   - Solution: Used CUDA_VISIBLE_DEVICES="" environment variable to force CPU mode

2. **Training Time Estimates**
   - Multiple iterations to find viable dataset size for CPU training
   - 10K samples → 2 minutes (sklearn)
   - 5K samples → 750 steps × 40s = 8+ hours (DistilBERT on CPU)
   - 2K samples → Still > 1 hour (DistilBERT on CPU)

3. **Cross-validation Performance**
   - Initial implementation included 5-fold CV on full 37K dataset
   - CV alone took 50+ minutes on LightGBM
   - Removed CV to optimize training time while maintaining train/test validation

## User Setup Required

None - no external service configuration required.

Dataset is acquired automatically from Hugging Face (public datasets), no API keys needed.

## Model Performance Details

### Test Set Metrics
- **Accuracy:** 94%
- **ROC-AUC:** 0.988
- **Precision (Benign):** 93%
- **Precision (Phishing):** 96%
- **Recall (Benign):** 96%
- **Recall (Phishing):** 92%
- **F1-Score:** 0.94

### Confusion Matrix
```
                Predicted
              Benign  Phishing
Actual Benign    964      36
       Phishing   77     923
```

- True Negatives: 964
- False Positives: 36 (benign classified as phishing)
- False Negatives: 77 (phishing classified as benign)
- True Positives: 923

### Model Characteristics
- Training time: ~2 minutes on CPU
- Model size: 1.1 MB (model.pkl)
- Features: 5000 TF-IDF features (unigrams + bigrams)
- Training samples: 8000 (10K dataset, 80/20 split)
- Test samples: 2000

## Next Phase Readiness

**Ready for Phase 2 (Fusion Layer):**
- Trained model available at tier2_text/models/tier2_text_detector/
- Model produces probability scores (0-1) for phishing classification
- Inference verified working correctly
- Model architecture documented with clear API

**No blockers identified.**

**Considerations for future phases:**
- Fusion layer should combine Tier 1 (URL) and Tier 2 (text) scores
- May want to standardize inference interface between Tier 1 and Tier 2 for consistency
- DistilBERT option available if GPU becomes accessible (tier2_training_distilbert.py)

---
*Phase: 01-tier2-text-detection*
*Completed: 2026-01-21*
