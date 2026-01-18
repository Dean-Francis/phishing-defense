import re
import tldextract
from urllib.parse import urlparse
import pandas as pd
import numpy as np
from typing import Dict, Any

class URLFeatureExtractor:
    
    def __init__(self) -> None:
        self.suspicious_tokens = [
            'login', 'verify', 'account', 'secure', 'update', 'confirm',
            'banking', 'paypal', 'ebay', 'amazon', 'suspended', 'locked'
        ]
        
        self.risky_tlds = [
            '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work'
        ]
    
    def extract_features(self, row: Dict[str, Any]) -> Dict[str, Any]:
        url = row.get('expanded_url', row.get('raw_url', ''))
        
        if not url or not isinstance(url, str):
            return self._get_null_features()
        
        features = {}
        features.update(self._extract_url_features(url))
        
        return features
    
    def _extract_url_features(self, url: str) -> Dict[str, Any]:
        features = {}
        
        try:
            parsed = urlparse(url)
            extracted = tldextract.extract(url)
            
            features['url_length'] = len(url)
            features['domain_length'] = len(extracted.domain) if extracted.domain else 0
            features['path_length'] = len(parsed.path)
            
            features['num_dots'] = url.count('.')
            features['num_hyphens'] = url.count('-')
            features['num_underscores'] = url.count('_')
            features['num_slashes'] = url.count('/')
            features['num_at_symbols'] = url.count('@')
            features['num_digits'] = sum(c.isdigit() for c in url)
            
            features['url_entropy'] = self._calculate_entropy(url)
            features['domain_entropy'] = self._calculate_entropy(extracted.domain) if extracted.domain else 0
            
            features['has_ip_address'] = 1 if self._is_ip_address(parsed.netloc) else 0
            features['suspicious_token_count'] = sum(1 for token in self.suspicious_tokens if token in url.lower())
            features['has_risky_tld'] = 1 if any(url.lower().endswith(tld) for tld in self.risky_tlds) else 0
            
            features['is_https'] = 1 if parsed.scheme == 'https' else 0
            features['has_port'] = 1 if ':' in parsed.netloc and not self._is_ip_address(parsed.netloc) else 0
            
            features['subdomain_count'] = len(extracted.subdomain.split('.')) if extracted.subdomain else 0
            features['domain_has_digits'] = 1 if (extracted.domain and any(c.isdigit() for c in extracted.domain)) else 0
            
        except Exception as e:
            return self._get_null_features()
        
        return features
    
    def _calculate_entropy(self, text: str) -> float:
        if not text:
            return 0
        
        prob = [text.count(c) / len(text) for c in set(text)]
        entropy = -sum(p * np.log2(p) for p in prob if p > 0)
        return entropy
    
    def _is_ip_address(self, netloc: str) -> bool:
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        return bool(re.match(ip_pattern, netloc))
    
    def _get_null_features(self) -> Dict[str, int]:
        return {
            'url_length': 0, 'domain_length': 0, 'path_length': 0,
            'num_dots': 0, 'num_hyphens': 0, 'num_underscores': 0,
            'num_slashes': 0, 'num_at_symbols': 0, 'num_digits': 0,
            'url_entropy': 0, 'domain_entropy': 0, 'has_ip_address': 0,
            'suspicious_token_count': 0, 'has_risky_tld': 0, 'is_https': 0,
            'has_port': 0, 'subdomain_count': 0, 'domain_has_digits': 0
        }
    
    def extract_from_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        features_list = []
        
        for idx, row in df.iterrows():
            features = self.extract_features(row)
            features_list.append(features)
        
        return pd.DataFrame(features_list)
