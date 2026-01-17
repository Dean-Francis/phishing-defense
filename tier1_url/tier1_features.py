import re
import tldextract
from urllib.parse import urlparse
import pandas as pd
import numpy as np

class URLFeatureExtractor:
    """Extract features from URLs for phishing detection"""
    
    def __init__(self):
        self.suspicious_tokens = [
            'login', 'verify', 'account', 'secure', 'update', 'confirm',
            'banking', 'paypal', 'ebay', 'amazon', 'suspended', 'locked'
        ]
        
        self.risky_tlds = [
            '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work'
        ]
    
    def extract_features(self, row):
        """Extract all features from a single row"""
        # Use expanded_url if available, otherwise raw_url
        url = row.get('expanded_url', row.get('raw_url', ''))
        
        if not url or not isinstance(url, str):
            return self._get_null_features()
        
        features = {}
        
        # URL-based features
        features.update(self._extract_url_features(url))
        
        # CSV column features
        features['is_shortened'] = 1 if row.get('is_shortened') == True or row.get('is_shortened') == 'TRUE' else 0
        features['has_redirects'] = 1 if pd.notna(row.get('redirects')) and row.get('redirects') != 0 else 0
        features['reputation_flagged'] = 1 if pd.notna(row.get('reputation_flags')) and str(row.get('reputation_flags')).lower() != 'none' else 0
        
        return features
    
    def _extract_url_features(self, url):
        """Extract features from URL string"""
        features = {}
        
        try:
            parsed = urlparse(url)
            extracted = tldextract.extract(url)
            
            # Length features
            features['url_length'] = len(url)
            features['domain_length'] = len(extracted.domain) if extracted.domain else 0
            features['path_length'] = len(parsed.path)
            
            # Character composition
            features['num_dots'] = url.count('.')
            features['num_hyphens'] = url.count('-')
            features['num_underscores'] = url.count('_')
            features['num_slashes'] = url.count('/')
            features['num_at_symbols'] = url.count('@')
            features['num_digits'] = sum(c.isdigit() for c in url)
            
            # Entropy (randomness measure)
            features['url_entropy'] = self._calculate_entropy(url)
            features['domain_entropy'] = self._calculate_entropy(extracted.domain) if extracted.domain else 0
            
            # Suspicious patterns
            features['has_ip_address'] = 1 if self._is_ip_address(parsed.netloc) else 0
            features['suspicious_token_count'] = sum(1 for token in self.suspicious_tokens if token in url.lower())
            features['has_risky_tld'] = 1 if any(url.lower().endswith(tld) for tld in self.risky_tlds) else 0
            
            # Protocol and port
            features['is_https'] = 1 if parsed.scheme == 'https' else 0
            features['has_port'] = 1 if ':' in parsed.netloc and not self._is_ip_address(parsed.netloc) else 0
            
            # Domain features
            features['subdomain_count'] = len(extracted.subdomain.split('.')) if extracted.subdomain else 0
            features['domain_has_digits'] = 1 if (extracted.domain and any(c.isdigit() for c in extracted.domain)) else 0
            
        except Exception as e:
            return self._get_null_features()
        
        return features
    
    def _calculate_entropy(self, text):
        """Calculate Shannon entropy of text"""
        if not text:
            return 0
        
        prob = [text.count(c) / len(text) for c in set(text)]
        entropy = -sum(p * np.log2(p) for p in prob if p > 0)
        return entropy
    
    def _is_ip_address(self, netloc):
        """Check if netloc is an IP address"""
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        return bool(re.match(ip_pattern, netloc))
    
    def _get_null_features(self):
        """Return default null features"""
        return {
            'url_length': 0, 'domain_length': 0, 'path_length': 0,
            'num_dots': 0, 'num_hyphens': 0, 'num_underscores': 0,
            'num_slashes': 0, 'num_at_symbols': 0, 'num_digits': 0,
            'url_entropy': 0, 'domain_entropy': 0, 'has_ip_address': 0,
            'suspicious_token_count': 0, 'has_risky_tld': 0, 'is_https': 0,
            'has_port': 0, 'subdomain_count': 0, 'domain_has_digits': 0,
            'is_shortened': 0, 'has_redirects': 0, 'reputation_flagged': 0
        }
    
    def extract_from_dataframe(self, df):
        """Extract features from entire dataframe"""
        features_list = []
        
        for idx, row in df.iterrows():
            features = self.extract_features(row)
            features_list.append(features)
        
        return pd.DataFrame(features_list)
