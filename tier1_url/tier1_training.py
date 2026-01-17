import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import lightgbm as lgb
import joblib
import os
from tier1_features import URLFeatureExtractor

class URLDetectorTrainer:
    """Train LightGBM model for URL-based phishing detection"""
    
    def __init__(self, model_path='models/tier1_url_detector.pkl'):
        self.model_path = model_path
        self.model = None
        self.feature_extractor = URLFeatureExtractor()
        self.feature_names = None
        
    def load_data(self, csv_path):
        """Load and prepare training data"""
        df = pd.read_csv(csv_path)
        
        # Extract features
        X = self.feature_extractor.extract_from_dataframe(df)
        self.feature_names = X.columns.tolist()
        
        # Extract labels (assuming 'label' column with 'phishing'/'benign')
        y = df['label'].apply(lambda x: 1 if str(x).lower() == 'phishing' else 0)
        
        return X, y
    
    def train(self, csv_path, test_size=0.2, random_state=42):
        """Train the LightGBM model"""
        print("Loading data...")
        X, y = self.load_data(csv_path)
        
        print(f"Dataset: {len(X)} samples, {X.shape[1]} features")
        print(f"Class distribution: {y.value_counts().to_dict()}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print("\nTraining LightGBM model...")
        
        # Configure LightGBM for generalization (prevent overfitting)
        params = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'min_data_in_leaf': 20,
            'min_gain_to_split': 0.01,
            'lambda_l1': 0.1,
            'lambda_l2': 0.1,
            'max_depth': 6,
            'verbose': -1
        }
        
        # Train model with early stopping
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=500,
            valid_sets=[train_data, valid_data],
            valid_names=['train', 'valid'],
            callbacks=[
                lgb.early_stopping(stopping_rounds=50),
                lgb.log_evaluation(period=50)
            ]
        )
        
        # Evaluate
        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)
        
        y_pred_proba = self.model.predict(X_test)
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        print("\nTest Set Performance:")
        print(classification_report(y_test, y_pred, target_names=['Benign', 'Phishing']))
        print(f"\nROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
        
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        # Cross-validation
        print("\n5-Fold Cross-Validation AUC:")
        cv_scores = cross_val_score(
            lgb.LGBMClassifier(**params, n_estimators=self.model.num_trees()),
            X, y, cv=5, scoring='roc_auc'
        )
        print(f"CV AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Feature importance
        print("\nTop 10 Important Features:")
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importance(importance_type='gain')
        }).sort_values('importance', ascending=False)
        print(importance_df.head(10).to_string(index=False))
        
        # Save model
        self._save_model()
        
        return self.model
    
    def _save_model(self):
        """Save trained model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, self.model_path)
        print(f"\nModel saved to: {self.model_path}")

if __name__ == "__main__":
    trainer = URLDetectorTrainer()
    trainer.train("/home/deanfrancis/Documents/Gradutaion_Project/phishing_defense_V2/data/Golden_Sheet.csv")
 
