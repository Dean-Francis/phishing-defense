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


if __name__ == "__main__":
    # Demo with test cases
    detector = TextDetectorInference(confidence_threshold=0.85)

    test_messages = [
        # Clear phishing signals
        {'text': 'URGENT: Your account will be suspended! Click here to verify: http://fake-bank.tk'},
        {'text': 'Congratulations! You won $1,000,000. Reply with your bank details to claim.'},

        # Clear benign messages
        {'text': 'Hi, just wanted to check if you received my email about the project deadline.'},
        {'text': 'The meeting has been rescheduled to 3pm tomorrow. Please confirm attendance.'},
    ]

    print("="*60)
    print("TIER 2 TEXT DETECTOR - INFERENCE EXAMPLES")
    print("="*60)

    for i, text_data in enumerate(test_messages, 1):
        print(f"\nTest Case {i}: {text_data['text'][:50]}...")
        print("-"*60)
        result = detector.predict(text_data)
        print(f"Score: {result['score']:.4f}")
        print(f"Label: {result['label']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Escalate to Tier 3: {result['escalate']}")
        print(f"Metadata: tier={result['metadata']['tier']}, text_length={result['metadata']['text_length']}")
