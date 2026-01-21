import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
import lightgbm as lgb
import joblib
import os

class TextDetectorTrainer:
    """Train LightGBM model with TF-IDF features for text-based phishing detection

    This is a pragmatic alternative to DistilBERT for CPU-constrained environments.
    Uses TF-IDF + LightGBM instead of transformers for much faster training while
    maintaining good accuracy (typically 85-95% for phishing detection tasks).
    """

    def __init__(self, model_path='models/tier2_text_detector'):
        self.model_path = model_path
        self.model = None
        self.vectorizer = None

    def load_data(self, csv_path, sample_size=None):
        """Load and prepare dataset from CSV"""
        df = pd.read_csv(csv_path)

        # Ensure required columns exist
        if 'text' not in df.columns or 'label' not in df.columns:
            raise ValueError("CSV must contain 'text' and 'label' columns")

        # Clean data: remove empty texts
        df = df.dropna(subset=['text'])
        df = df[df['text'].str.strip() != '']

        # Ensure labels are integers
        df['label'] = df['label'].astype(int)

        # Sample dataset if specified (stratified by label)
        if sample_size is not None and len(df) > sample_size:
            print(f"Sampling {sample_size} examples from {len(df)} total samples...")
            # Sample equally from each class
            df_sampled = []
            for label_val in df['label'].unique():
                df_label = df[df['label'] == label_val]
                n_samples = min(len(df_label), sample_size // 2)
                df_sampled.append(df_label.sample(n=n_samples, random_state=42))
            df = pd.concat(df_sampled, ignore_index=True)

        return df

    def train(self, csv_path, test_size=0.2, random_state=42, sample_size=10000):
        """Train the LightGBM model with TF-IDF features"""
        print("="*60)
        print("TIER 2 TEXT DETECTION TRAINING")
        print("(LightGBM + TF-IDF - CPU-optimized alternative)")
        print("="*60)

        print("\nLoading data...")
        df = self.load_data(csv_path, sample_size=sample_size)

        print(f"Dataset: {len(df)} samples")
        print(f"Class distribution:")
        print(df['label'].value_counts().to_dict())

        # Stratified train/test split
        train_df, test_df = train_test_split(
            df,
            test_size=test_size,
            random_state=random_state,
            stratify=df['label']
        )

        print(f"\nTrain samples: {len(train_df)}")
        print(f"Test samples: {len(test_df)}")

        # TF-IDF Vectorization
        print("\nExtracting TF-IDF features...")
        self.vectorizer = TfidfVectorizer(
            max_features=5000,  # Limit features for faster training
            min_df=2,  # Ignore terms that appear in fewer than 2 documents
            max_df=0.8,  # Ignore terms that appear in more than 80% of documents
            ngram_range=(1, 2),  # Unigrams and bigrams
            strip_accents='unicode',
            lowercase=True,
            stop_words='english'
        )

        X_train = self.vectorizer.fit_transform(train_df['text'])
        X_test = self.vectorizer.transform(test_df['text'])
        y_train = train_df['label'].values
        y_test = test_df['label'].values

        print(f"Feature dimensions: {X_train.shape[1]} features")

        # Train LightGBM model
        print("\nTraining LightGBM model...")
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
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        print(f"[TN={cm[0,0]}, FP={cm[0,1]}]")
        print(f"[FN={cm[1,0]}, TP={cm[1,1]}]")

        # Skip cross-validation for faster training
        # (Can be added back if needed, but takes significant time on large datasets)

        # Save model
        self._save_model()

        return self.model

    def _save_model(self):
        """Save trained model and vectorizer to disk"""
        output_dir = f"tier2_text/{self.model_path}"
        os.makedirs(output_dir, exist_ok=True)

        model_data = {
            'model': self.model,
            'vectorizer': self.vectorizer
        }

        model_file = os.path.join(output_dir, 'model.pkl')
        joblib.dump(model_data, model_file)

        # Save a simple config file for compatibility
        config = {
            "model_type": "lightgbm_tfidf",
            "num_labels": 2,
            "id2label": {"0": "BENIGN", "1": "PHISHING"},
            "label2id": {"BENIGN": 0, "PHISHING": 1},
            "max_features": 5000,
            "note": "TF-IDF + LightGBM model (CPU-optimized alternative to DistilBERT)"
        }

        import json
        config_file = os.path.join(output_dir, 'config.json')
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"\nModel saved to: {output_dir}")
        print("Saved files:")
        for f in os.listdir(output_dir):
            print(f"  - {f}")

if __name__ == "__main__":
    trainer = TextDetectorTrainer()
    # Use 10K samples for reasonable training time while maintaining good accuracy
    trainer.train("tier2_text/data/phishing_text.csv", sample_size=10000)
