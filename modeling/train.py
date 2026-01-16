import pandas as pd
import numpy as np
import re
from urllib.parse import urlparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib

class Tier1Model:
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = RandomForestClassifier(n_estimators=100, random_state=42) 
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def extract_features(self, row):
        domain = row['domain'] if 'domain' in row else ''
        raw_url = row['raw_url'] if 'raw_url' in row else ''
        is_shortened = row['is_shortened'] if 'is_shortened' in row else 0
        redirects = row['redirects'] if 'redirects' in row else 0
        
        # Parse URL for additional components
        try:
            parsed = urlparse(raw_url)
            path = parsed.path
            query = parsed.query
        except:
            path = ''
            query = ''
        
        features = {
            'dot_count': domain.count('.'),
            'hyphen_count': domain.count('-'),
            'underscore_count': domain.count('_'),
            'url_length': len(raw_url),
            'domain_length': len(domain),
            
            # IP address check
            'is_ip': 1 if self._is_ip_address(domain) else 0,
            
            # Subdomain analysis
            'subdomain_count': len(domain.split('.')) - 2 if '.' in domain else 0,
            
            # Character analysis
            'digit_count': sum(c.isdigit() for c in domain),
            'digit_ratio': sum(c.isdigit() for c in domain) / len(domain) if len(domain) > 0 else 0,
            
            # Special characters
            'at_symbol': 1 if '@' in raw_url else 0,
            'double_slash_count': raw_url.count('//') - 1,  # Subtract the one from http://
            
            # Path and query analysis
            'path_length': len(path),
            'query_length': len(query),
            'query_param_count': len(query.split('&')) if query else 0,
            
            # Suspicious patterns
            'has_suspicious_tld': 1 if self._has_suspicious_tld(domain) else 0,
            'domain_entropy': self._calculate_entropy(domain),
            
            # CSV-provided features
            'is_shortened': 1 if is_shortened else 0,
            'redirect_count': redirects if isinstance(redirects, (int, float)) else 0,
        }
        
        return features
    
    def _is_ip_address(self, domain):
        """Check if domain is an IP address"""
        # Check IPv4
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ipv4_pattern, domain):
            parts = domain.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        # Check IPv6 (basic check)
        return ':' in domain and all(c in '0123456789abcdefABCDEF:' for c in domain)
    
    def _has_suspicious_tld(self, domain):
        """Check for suspicious top-level domains"""
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work', '.click']
        return any(domain.endswith(tld) for tld in suspicious_tlds)
    
    def _calculate_entropy(self, s):
        """Calculate Shannon entropy of string"""
        if not s:
            return 0
        prob = [s.count(c) / len(s) for c in set(s)]
        return -sum(p * np.log2(p) for p in prob if p > 0)
    
    def train(self, csv_path):
        """
        Train the model on the dataset
        
        Args:
            csv_path: Path to CSV file with columns: domain, raw_url, is_shortened, redirects, label
        """
        print("Loading data...")
        df = pd.read_csv(csv_path)
        
        print(f"Dataset shape: {df.shape}")
        print(f"Label distribution:\n{df['label'].value_counts()}")
        
        # Map labels: legitimate -> 0, unverified/phishing -> 1
        print("\nMapping labels (legitimate=0, unverified+phishing=1)...")
        df['binary_label'] = df['label'].apply(lambda x: 0 if x == 'legitimate' else 1)
        print(f"Binary label distribution:\n{df['binary_label'].value_counts()}")
        
        # Extract features
        print("\nExtracting features...")
        features_list = []
        for idx, row in df.iterrows():
            features_list.append(self.extract_features(row))
        
        features_df = pd.DataFrame(features_list)
        self.feature_names = features_df.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features_df, df['binary_label'], 
            test_size=0.2, 
            random_state=42,
            stratify=df['binary_label']
        )
        
        print(f"\nTrain set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")
        
        # Scale features
        print("\nScaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        print(f"\nTraining {self.model_type} model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        print("\n" + "="*50)
        print("TRAINING RESULTS")
        print("="*50)
        
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)
        
        print(f"\nTrain Accuracy: {accuracy_score(y_train, train_pred):.4f}")
        print(f"Test Accuracy: {accuracy_score(y_test, test_pred):.4f}")
        
        print("\nTest Set Classification Report:")
        print(classification_report(y_test, test_pred, 
                                   target_names=['Legitimate', 'Suspicious']))
        
        print("\nConfusion Matrix (Test Set):")
        print("                 Predicted")
        print("                 Legit  Susp")
        cm = confusion_matrix(y_test, test_pred)
        print(f"Actual Legit     {cm[0][0]:5d}  {cm[0][1]:5d}")
        print(f"Actual Susp      {cm[1][0]:5d}  {cm[1][1]:5d}")
        
        # Feature importance (if Random Forest)
        if self.model_type == 'random_forest':
            print("\nTop 10 Most Important Features:")
            importances = self.model.feature_importances_
            indices = np.argsort(importances)[::-1][:10]
            for i, idx in enumerate(indices, 1):
                print(f"{i:2d}. {self.feature_names[idx]:20s}: {importances[idx]:.4f}")
        
        return {
            'train_accuracy': accuracy_score(y_train, train_pred),
            'test_accuracy': accuracy_score(y_test, test_pred),
            'model': self.model,
            'scaler': self.scaler
        }
    
    def predict(self, url_data):
        """
        Predict if URL is suspicious
        
        Args:
            url_data: dict with 'domain', 'raw_url', 'is_shortened', 'redirects'
        
        Returns:
            dict with 'prediction' (0=legitimate, 1=suspicious) and 'confidence'
        """
        features = self.extract_features(url_data)
        features_df = pd.DataFrame([features])[self.feature_names]
        features_scaled = self.scaler.transform(features_df)
        
        prediction = self.model.predict(features_scaled)[0]
        
        # Get confidence score
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(features_scaled)[0]
            confidence = proba[prediction]
        else:
            confidence = None
        
        return {
            'prediction': int(prediction),
            'label': 'legitimate' if prediction == 0 else 'suspicious',
            'confidence': float(confidence) if confidence is not None else None,
            'send_to_tier2': bool(prediction == 1)
        }
    
    def save_model(self, path='tier1_model.pkl'):
        """Save trained model to disk"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }, path)
        print(f"Model saved to {path}")
    
    def load_model(self, path='tier1_model.pkl'):
        """Load trained model from disk"""
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.model_type = data['model_type']
        print(f"Model loaded from {path}")


# Example usage
if __name__ == "__main__":
    # Initialize model
    model = Tier1Model(model_type='random_forest')
    
    # Train on your CSV
    # model.train('your_dataset.csv')
    
    # Save model
    # model.save_model('tier1_model.pkl')
    
    # Make predictions
    # test_url = {
    #     'domain': 'example.com',
    #     'raw_url': 'https://example.com/path?query=1',
    #     'is_shortened': 0,
    #     'redirects': 0
    # }
    # result = model.predict(test_url)
    # print(result)

