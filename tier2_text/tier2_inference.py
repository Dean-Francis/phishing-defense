import joblib
import os
from typing import Dict, Any, List


class TextDetectorInference:
    """Inference class for Tier 2 text-based phishing detection

    Uses LightGBM + TF-IDF model trained in 01-01.
    Output structure matches Tier 1 (URLDetectorInference) for seamless
    integration in the Phase 2 fusion layer.
    """

    def __init__(self, model_path: str = 'tier2_text/models/tier2_text_detector',
                 confidence_threshold: float = 0.85) -> None:
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.vectorizer = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the trained LightGBM model and TF-IDF vectorizer"""
        try:
            model_file = os.path.join(self.model_path, 'model.pkl')
            model_data = joblib.load(model_file)
            self.model = model_data['model']
            self.vectorizer = model_data['vectorizer']
            print(f"Model loaded from: {self.model_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Model not found at {self.model_path}. Train model first.")

    def predict(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict phishing probability for a single text message

        Args:
            text_data: Dictionary containing text information
                Required keys: 'text'

        Returns:
            Dictionary with:
                - score: float (phishing probability 0-1)
                - label: str ('phishing' or 'benign')
                - confidence: str ('high' or 'low')
                - escalate: bool (True if low confidence)
                - metadata: dict with tier info
        """
        text = text_data.get('text', '')

        # Transform text using TF-IDF vectorizer
        X = self.vectorizer.transform([text])

        # Get phishing probability from LightGBM model
        phishing_score = float(self.model.predict(X)[0])

        # Determine label (phishing if score >= 0.5)
        label = 'phishing' if phishing_score >= 0.5 else 'benign'

        # Determine confidence (same logic as Tier 1)
        # High confidence if clearly phishing (>= threshold) or clearly benign (<= 1-threshold)
        confidence = 'high' if phishing_score >= self.confidence_threshold or phishing_score <= (1 - self.confidence_threshold) else 'low'

        # Escalate if low confidence (uncertain zone)
        escalate = confidence == 'low'

        return {
            'score': phishing_score,
            'label': label,
            'confidence': confidence,
            'escalate': escalate,
            'metadata': {
                'tier': 2,
                'model': 'LightGBM_Text_Detector',
                'threshold': self.confidence_threshold,
                'text_length': len(text)
            }
        }

    def predict_batch(self, text_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Predict phishing probability for multiple text messages

        Args:
            text_data_list: List of dictionaries, each containing 'text' key

        Returns:
            List of prediction dictionaries
        """
        # Extract texts
        texts = [td.get('text', '') for td in text_data_list]

        # Vectorize all texts at once (more efficient)
        X = self.vectorizer.transform(texts)

        # Get all predictions at once
        phishing_scores = self.model.predict(X)

        # Build result list
        results = []
        for i, text in enumerate(texts):
            score = float(phishing_scores[i])
            label = 'phishing' if score >= 0.5 else 'benign'
            confidence = 'high' if score >= self.confidence_threshold or score <= (1 - self.confidence_threshold) else 'low'
            escalate = confidence == 'low'

            results.append({
                'score': score,
                'label': label,
                'confidence': confidence,
                'escalate': escalate,
                'metadata': {
                    'tier': 2,
                    'model': 'LightGBM_Text_Detector',
                    'threshold': self.confidence_threshold,
                    'text_length': len(text)
                }
            })

        return results


def validate_output_structure(result: Dict[str, Any]) -> bool:
    """Validate that prediction output has required structure"""
    # Check top-level keys exist
    required_keys = ['score', 'label', 'confidence', 'escalate', 'metadata']
    for key in required_keys:
        assert key in result, f"Missing required key: {key}"

    # Validate types
    assert isinstance(result['score'], float), f"score must be float, got {type(result['score'])}"
    assert 0.0 <= result['score'] <= 1.0, f"score must be 0-1, got {result['score']}"
    assert result['label'] in ['phishing', 'benign'], f"label must be 'phishing' or 'benign', got {result['label']}"
    assert result['confidence'] in ['high', 'low'], f"confidence must be 'high' or 'low', got {result['confidence']}"
    assert isinstance(result['escalate'], bool), f"escalate must be bool, got {type(result['escalate'])}"

    # Validate metadata
    metadata = result['metadata']
    assert 'tier' in metadata, "metadata missing 'tier'"
    assert 'model' in metadata, "metadata missing 'model'"
    assert 'threshold' in metadata, "metadata missing 'threshold'"
    assert metadata['tier'] == 2, f"tier must be 2, got {metadata['tier']}"

    return True


if __name__ == "__main__":
    print("="*70)
    print("TIER 2 TEXT DETECTOR - COMPREHENSIVE VALIDATION")
    print("="*70)

    # Initialize detector
    detector = TextDetectorInference(confidence_threshold=0.85)

    # Test cases: 3 phishing, 3 benign
    test_messages = [
        # Clear phishing signals
        {'text': 'URGENT: Your account will be suspended! Click here to verify: http://fake-bank.tk', 'expected': 'phishing'},
        {'text': 'Congratulations! You won $1,000,000. Reply with your bank details to claim.', 'expected': 'phishing'},
        {'text': 'Your PayPal account has been limited. Log in immediately to restore access.', 'expected': 'phishing'},

        # Clear benign messages
        {'text': 'Hi, just wanted to check if you received my email about the project deadline.', 'expected': 'benign'},
        {'text': 'The meeting has been rescheduled to 3pm tomorrow. Please confirm attendance.', 'expected': 'benign'},
        {'text': 'Thank you for your order. Your package will arrive in 3-5 business days.', 'expected': 'benign'},
    ]

    # ================================================================
    # SINGLE PREDICTION TESTS
    # ================================================================
    print("\n" + "="*70)
    print("SINGLE PREDICTION TESTS")
    print("="*70)

    single_results = []
    warnings = []

    for i, test_case in enumerate(test_messages, 1):
        text_data = {'text': test_case['text']}
        expected = test_case['expected']

        result = detector.predict(text_data)
        single_results.append(result)

        # Validate output structure
        try:
            validate_output_structure(result)
            structure_ok = "OK"
        except AssertionError as e:
            structure_ok = f"FAIL: {e}"

        # Check classification accuracy
        actual_label = result['label']
        if actual_label != expected:
            warnings.append(f"Case {i}: Expected '{expected}', got '{actual_label}' (score={result['score']:.4f})")

        print(f"\nTest Case {i}: {test_case['text'][:45]}...")
        print(f"  Expected: {expected} | Actual: {actual_label} | Score: {result['score']:.4f}")
        print(f"  Confidence: {result['confidence']} | Escalate: {result['escalate']} | Structure: {structure_ok}")

    # ================================================================
    # BATCH PREDICTION TESTS
    # ================================================================
    print("\n" + "="*70)
    print("BATCH PREDICTION TESTS")
    print("="*70)

    text_data_list = [{'text': tc['text']} for tc in test_messages]
    batch_results = detector.predict_batch(text_data_list)

    # Validate batch results match single results
    batch_match = True
    for i, (single, batch) in enumerate(zip(single_results, batch_results)):
        if abs(single['score'] - batch['score']) > 1e-9:
            batch_match = False
            print(f"MISMATCH Case {i+1}: single={single['score']:.6f}, batch={batch['score']:.6f}")

    if batch_match:
        print("Batch results MATCH single prediction results (scores identical)")
    else:
        print("WARNING: Batch results do NOT match single predictions!")

    # Validate batch output structures
    batch_structure_ok = True
    for i, result in enumerate(batch_results):
        try:
            validate_output_structure(result)
        except AssertionError as e:
            batch_structure_ok = False
            print(f"Batch result {i+1} structure error: {e}")

    if batch_structure_ok:
        print("All batch results have valid output structure")

    # ================================================================
    # SUMMARY TABLE
    # ================================================================
    print("\n" + "="*70)
    print("RESULTS SUMMARY TABLE")
    print("="*70)
    print(f"| {'Message (truncated)':<40} | {'Score':<6} | {'Label':<8} | {'Conf':<5} | {'Esc':<5} |")
    print(f"|{'-'*42}|{'-'*8}|{'-'*10}|{'-'*7}|{'-'*7}|")

    for i, (tc, result) in enumerate(zip(test_messages, single_results)):
        text_short = tc['text'][:38] + ".." if len(tc['text']) > 40 else tc['text'][:40]
        label_short = "phish" if result['label'] == 'phishing' else "benign"
        esc_str = str(result['escalate'])
        print(f"| {text_short:<40} | {result['score']:.4f} | {label_short:<8} | {result['confidence']:<5} | {esc_str:<5} |")

    # ================================================================
    # CLASSIFICATION ACCURACY
    # ================================================================
    print("\n" + "="*70)
    print("CLASSIFICATION ACCURACY")
    print("="*70)

    correct = sum(1 for tc, r in zip(test_messages, single_results) if tc['expected'] == r['label'])
    total = len(test_messages)

    print(f"Correct classifications: {correct}/{total} ({100*correct/total:.1f}%)")

    if warnings:
        print("\nWarnings (unexpected classifications):")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("\nNo classification warnings - all test cases classified as expected!")

    # ================================================================
    # FINAL STATUS
    # ================================================================
    print("\n" + "="*70)
    print("VALIDATION STATUS")
    print("="*70)

    all_passed = True

    # Check minimum accuracy (4/6)
    if correct >= 4:
        print("[PASS] Classification accuracy >= 4/6")
    else:
        print(f"[FAIL] Classification accuracy {correct}/6 < 4/6 minimum")
        all_passed = False

    # Check structure validation
    if batch_structure_ok:
        print("[PASS] All output structures valid")
    else:
        print("[FAIL] Some output structures invalid")
        all_passed = False

    # Check batch consistency
    if batch_match:
        print("[PASS] Batch results match single predictions")
    else:
        print("[FAIL] Batch results differ from single predictions")
        all_passed = False

    print("\n" + "="*70)
    if all_passed:
        print("ALL VALIDATION CHECKS PASSED")
    else:
        print("SOME VALIDATION CHECKS FAILED - see details above")
    print("="*70)
