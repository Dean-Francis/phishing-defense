# External Integrations

**Analysis Date:** 2026-01-20

## APIs & External Services

**Not Applicable:**
- No external APIs currently integrated
- Phishing detection operates entirely on local URL analysis
- No remote API calls or service integrations detected

## Data Storage

**Databases:**
- Not applicable - No database integration present

**File Storage:**
- Local filesystem only
- Training data: `/home/deanfrancis/Documents/Gradutaion_Project/phishing_defense_V2/data/` (CSV files)
- Model artifacts: `models/tier1_url_detector.pkl` (serialized LightGBM model via joblib)

**Caching:**
- None - Models loaded into memory at inference initialization

## Authentication & Identity

**Auth Provider:**
- Not applicable - No user authentication system
- No identity verification required for model inference

## Monitoring & Observability

**Error Tracking:**
- None - No error tracking service integrated

**Logs:**
- Console output only (`print()` statements)
- No centralized logging framework configured
- Training process outputs metrics to stdout:
  - Dataset statistics
  - Model training progress (LightGBM callbacks)
  - Evaluation metrics (ROC-AUC, classification reports, confusion matrix)
  - Feature importance rankings

## CI/CD & Deployment

**Hosting:**
- Not applicable - Local development environment

**CI Pipeline:**
- None - No CI/CD automation detected

## Environment Configuration

**Required env vars:**
- None - Application is self-contained with hardcoded paths

**Secrets location:**
- Not applicable - No API keys, credentials, or secrets required
- `.gitignore` excludes `.env` file for future proofing

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Data Flow

**Training Pipeline:**

1. CSV dataset loaded from `data/training_dataset_clean.csv` via pandas
2. Features extracted using `URLFeatureExtractor` from `tier1_url/tier1_features.py`:
   - URL morphological features (length, dots, hyphens, etc.)
   - Entropy calculations
   - IP address detection
   - Suspicious token matching
   - TLD risk assessment
3. Data split: 80% train, 20% test (stratified)
4. LightGBM model trained with early stopping on validation set
5. Model serialized to `models/tier1_url_detector.pkl` with feature names

**Inference Pipeline:**

1. URL data input as dictionary: `{'url': 'https://example.com'}`
2. Features extracted using same `URLFeatureExtractor`
3. LightGBM model predicts phishing probability (0-1 score)
4. Confidence threshold applied: high if score >= 0.85 or <= 0.15
5. Results returned with:
   - Phishing probability score
   - Binary label (phishing/benign)
   - Confidence level
   - Escalation flag (True if confidence low)
   - Top 5 contributing features

## Model Artifacts

**Training Model:**
- Location: `tier1_url/tier1_training.py`
- Input: CSV with `url` and `label` columns
- Output: Serialized model + feature names

**Inference Model:**
- Location: `tier1_url/tier1_inference.py`
- Loads from: `models/tier1_url_detector.pkl`
- Single URL prediction or batch prediction support
- Confidence threshold: 0.85 (configurable)

---

*Integration audit: 2026-01-20*
