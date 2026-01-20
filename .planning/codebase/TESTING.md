# Testing Patterns

**Analysis Date:** 2026-01-20

## Test Framework

**Runner:**
- No formal test framework detected (pytest, unittest not configured)
- Manual test script: `test.py`
- No test configuration files (pytest.ini, setup.cfg, tox.ini)

**Assertion Library:**
- No assertion library configured
- Manual verification in inline testing

**Run Commands:**
```bash
python test.py              # Run test file (currently broken)
python tier1_training.py    # Run training with validation output
python tier1_inference.py   # Run inference with example outputs
```

## Test File Organization

**Location:**
- Co-located with source: `tier1_url/test.py` in same directory as implementation files
- No separate test/ directory structure

**Naming:**
- Single test file: `test.py`
- No test class naming convention observed
- No test function naming convention (file is incomplete)

**Current State:**
- Test file is broken/incomplete (syntax error in test.py - unpacking issue)
- Not used in development workflow

## Test Structure

**Example from Codebase:**
```python
# /home/deanfrancis/Documents/Gradutaion_Project/phishing_defense_V2/tier1_url/test.py
test_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
for a, b in test_list:
    print(a)
    print(b)
```

**Patterns Observed:**
- No established testing pattern
- Manual validation through script execution
- No setup/teardown patterns
- No test isolation mechanisms

## Validation Approach

**Training Validation:**
- Built-in model validation during training in `tier1_training.py`
- Classification report printed: `classification_report(y_test, y_pred, ...)`
- Confusion matrix output: `confusion_matrix(y_test, y_pred)`
- ROC-AUC score calculation: `roc_auc_score(y_test, y_pred_proba)`
- 5-fold cross-validation: `cross_val_score(lgb.LGBMClassifier(...), X, y, cv=5)`

**Output Structure:**
```
EVALUATION RESULTS
==================
Test Set Performance:
              precision    recall  f1-score   support
Benign         0.95      0.98      0.96      2000
Phishing       0.94      0.89      0.91      1500

ROC-AUC Score: 0.965

Confusion Matrix:
[[1960   40]
 [ 165 1335]]

5-Fold Cross-Validation AUC:
CV AUC: 0.962 (+/- 0.008)

Top 10 Important Features:
feature                    importance
suspicious_token_count     2850.2
has_risky_tld              1920.5
url_entropy                1850.3
```

## Inference Testing

**Manual Test Pattern in `tier1_inference.py`:**
```python
if __name__ == "__main__":
    detector = URLDetectorInference(confidence_threshold=0.85)

    test_urls = [
        {'url': 'https://secure-paypal-verify.tk/login'},
        {'url': 'https://www.google.com'}
    ]

    for i, url_data in enumerate(test_urls, 1):
        print(f"\nTest Case {i}: {url_data['url']}")
        result = detector.predict(url_data)
        print(f"Score: {result['score']:.4f}")
        # ... print other fields
```

**Approach:**
- Manual list of test cases
- Iterative printing of results
- Visual inspection required
- No assertion or validation

## Mocking

**Framework:** No mocking framework configured

**Patterns:** None observed

**What to Mock:**
- Model loading in tests (currently no tests)
- File I/O operations in model saving/loading
- External DataFrame operations

**What NOT to Mock:**
- Feature extraction logic (core business logic)
- Model prediction (should use trained model)
- Data validation

## Fixtures and Factories

**Test Data:**
- No fixture files detected
- Hardcoded test URLs in `tier1_inference.py`:
  - `https://secure-paypal-verify.tk/login` (suspected phishing - risky TLD, suspicious tokens)
  - `https://www.google.com` (benign - trusted domain)

**Location:**
- Inline in executable blocks under `if __name__ == "__main__":`
- No separate fixture or factory modules

## Coverage

**Requirements:** Not enforced

**Measurement:** No coverage measurement tools configured or used

**Current Coverage:** Not measured, but based on code inspection:
- Feature extraction: Has implicit validation through try-except
- Training: Has explicit evaluation metrics (AUC, classification report)
- Inference: Has manual test cases but no automated verification

## Test Types

**Manual Validation:**
- Training validation built into `tier1_training.py`: Prints evaluation metrics automatically
- Inference testing in `tier1_inference.py`: Runs example predictions with manual inspection
- Feature extraction tested implicitly through end-to-end runs

**Unit Testing:**
- No unit tests present
- Manual function-level validation would require:
  - Testing `_calculate_entropy()` with known values
  - Testing `_is_ip_address()` with IP and non-IP strings
  - Testing feature extraction with edge cases (empty URLs, malformed URLs)

**Integration Testing:**
- Training pipeline tested end-to-end: Data loading → Feature extraction → Model training → Evaluation
- Inference pipeline tested end-to-end: Model loading → Feature extraction → Prediction

**End-to-End Testing:**
- `tier1_training.py` serves as E2E test for training pipeline
- `tier1_inference.py` serves as E2E test for inference pipeline
- Manual runs verify full data flow

## How Testing is Currently Done

**Training Validation:**
```python
# From tier1_training.py
print("Loading data...")
X, y = self.load_data(csv_path)

print(f"Dataset: {len(X)} samples, {X.shape[1]} features")
print(f"Class distribution: {y.value_counts().to_dict()}")

# ... train model ...

y_pred_proba = self.model.predict(X_test)
y_pred = (y_pred_proba >= 0.5).astype(int)

print(classification_report(y_test, y_pred, target_names=['Benign', 'Phishing']))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
```

**Inference Validation:**
```python
# From tier1_inference.py
test_urls = [{'url': 'https://secure-paypal-verify.tk/login'}, ...]
for url_data in test_urls:
    result = detector.predict(url_data)
    print(f"Score: {result['score']:.4f}")
    print(f"Label: {result['label']}")
```

## Gaps and Recommendations

**Currently Missing:**
- No automated test suite (pytest/unittest)
- No test file that runs and passes
- No CI/CD test validation
- No regression testing
- No edge case testing (malformed URLs, missing fields, etc.)

**Recommended Additions:**
1. Implement pytest-based test suite with parametrized test cases
2. Add unit tests for utility functions (`_calculate_entropy`, `_is_ip_address`)
3. Add integration tests for complete pipelines
4. Add fixtures for common test URLs and datasets
5. Add test coverage measurement and reporting
6. Fix `test.py` and establish naming conventions for test functions

---

*Testing analysis: 2026-01-20*
