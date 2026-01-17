import joblib
import pandas as pd
from typing import Dict, Any
from tier1_features import URLFeatureExtractor

class URLDetectorInference:
    """Inference module for Tier 1 URL Detector"""
    
    def __init__(self, model_path='models/tier1_url_detector.pkl', confidence_threshold=0.85):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.feature_names = None
        self.feature_extractor = URLFeatureExtractor()
        self._load_model()
    
    def _load_model(self):
        """Load trained model from disk"""
        try:
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            print(f"Model loaded from: {self.model_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Model not found at {self.model_path}. Train model first.")
    
    def predict(self, url_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict phishing probability for a single URL
        
        Args:
            url_data: Dictionary containing URL information
                Required keys: 'raw_url' or 'expanded_url'
                Optional keys: 'is_shortened', 'redirects', 'reputation_flags'
        
        Returns:
            Dictionary with:
                - score: float (phishing probability 0-1)
                - label: str ('phishing' or 'benign')
                - confidence: str ('high' or 'low')
                - escalate: bool (True if score < threshold)
                - metadata: dict with feature importance
        """
        # Extract features
        features = self.feature_extractor.extract_features(url_data)
        features_df = pd.DataFrame([features])[self.feature_names]
        
        # Get prediction
        phishing_score = float(self.model.predict(features_df)[0])
        
        # Determine label
        label = 'phishing' if phishing_score >= 0.5 else 'benign'
        
        # Check confidence
        confidence = 'high' if phishing_score >= self.confidence_threshold or phishing_score <= (1 - self.confidence_threshold) else 'low'
        escalate = confidence == 'low'
        
        # Get feature contributions (top 5)
        feature_importance = self._get_feature_contributions(features_df)
        
        return {
            'score': phishing_score,
            'label': label,
            'confidence': confidence,
            'escalate': escalate,
            'metadata': {
                'tier': 1,
                'model': 'LightGBM_URL_Detector',
                'threshold': self.confidence_threshold,
                'top_features': feature_importance
            }
        }
    
    def predict_batch(self, url_data_list):
        """Predict for multiple URLs"""
        results = []
        for url_data in url_data_list:
            result = self.predict(url_data)
            results.append(result)
        return results
    
    def _get_feature_contributions(self, features_df):
        """Get top contributing features for explanation"""
        feature_values = features_df.iloc[0].to_dict()
        feature_importance = self.model.feature_importance(importance_type='gain')
        
        # Combine feature values with model importance
        contributions = []
        for feat_name, feat_value in feature_values.items():
            feat_idx = self.feature_names.index(feat_name)
            importance = feature_importance[feat_idx]
            contributions.append({
                'feature': feat_name,
                'value': feat_value,
                'importance': float(importance)
            })
        
        # Sort by importance and return top 5
        contributions.sort(key=lambda x: x['importance'], reverse=True)
        return contributions[:5]


# Example usage
if __name__ == "__main__":
    detector = URLDetectorInference(confidence_threshold=0.85)
    
    # Test cases
    test_urls = [
        {
            'raw_url': 'https://secure-paypal-verify.tk/login',
            'is_shortened': False,
            'redirects': None,
            'reputation_flags': 'suspicious'
        },
        {
            'raw_url': 'https://www.google.com',
            'is_shortened': False,
            'redirects': None,
            'reputation_flags': None
        }
    ]
    
    print("="*60)
    print("TIER 1 URL DETECTOR - INFERENCE EXAMPLES")
    print("="*60)
    
    for i, url_data in enumerate(test_urls, 1):
        print(f"\nTest Case {i}: {url_data['raw_url']}")
        print("-"*60)
        result = detector.predict(url_data)
        print(f"Score: {result['score']:.4f}")
        print(f"Label: {result['label']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Escalate to Tier 2: {result['escalate']}")
        print(f"Top Features:")
        for feat in result['metadata']['top_features']:
            print(f"  - {feat['feature']}: {feat['value']} (importance: {feat['importance']:.2f})")
