import joblib
import pandas as pd
from typing import Dict, Any, List
from tier1_features import URLFeatureExtractor

class URLDetectorInference:
    
    def __init__(self, model_path: str = 'models/tier1_url_detector.pkl', confidence_threshold: float = 0.85) -> None:
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.feature_names = None
        self.feature_extractor = URLFeatureExtractor()
        self._load_model()
    
    def _load_model(self) -> None:
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
        
        Returns:
            Dictionary with:
                - score: float (phishing probability 0-1)
                - label: str ('phishing' or 'benign')
                - confidence: str ('high' or 'low')
                - escalate: bool (True if score < threshold)
                - metadata: dict with feature importance
        """
        features = self.feature_extractor.extract_features(url_data)
        features_df = pd.DataFrame([features])[self.feature_names]
        
        phishing_score = float(self.model.predict(features_df)[0])
        
        label = 'phishing' if phishing_score >= 0.5 else 'benign'
        
        confidence = 'high' if phishing_score >= self.confidence_threshold or phishing_score <= (1 - self.confidence_threshold) else 'low'
        escalate = confidence == 'low'
        
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
    
    def predict_batch(self, url_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for url_data in url_data_list:
            result = self.predict(url_data)
            results.append(result)
        return results
    
    def _get_feature_contributions(self, features_df: pd.DataFrame) -> List[Dict[str, Any]]:
        feature_values = features_df.iloc[0].to_dict()
        feature_importance = self.model.feature_importance(importance_type='gain')
        
        contributions = []
        for feat_name, feat_value in feature_values.items():
            feat_idx = self.feature_names.index(feat_name)
            importance = feature_importance[feat_idx]
            contributions.append({
                'feature': feat_name,
                'value': feat_value,
                'importance': float(importance)
            })
        
        contributions.sort(key=lambda x: x['importance'], reverse=True)
        return contributions[:5]


if __name__ == "__main__":
    detector = URLDetectorInference(confidence_threshold=0.85)
    
    test_urls = [
        {
            'raw_url': 'https://secure-paypal-verify.tk/login'
        },
        {
            'raw_url': 'https://www.google.com'
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
