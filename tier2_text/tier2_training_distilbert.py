import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
import evaluate
import torch
import os

class TextDetectorTrainer:
    """Train DistilBERT model for text-based phishing detection"""

    def __init__(self, model_path='models/tier2_text_detector'):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.trainer = None

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

        # Sample dataset if specified (for faster training on CPU)
        if sample_size is not None and len(df) > sample_size:
            print(f"Sampling {sample_size} examples from {len(df)} total samples...")
            df = df.groupby('label', group_keys=False).apply(
                lambda x: x.sample(min(len(x), sample_size // 2), random_state=42)
            ).reset_index(drop=True)

        return df

    def train(self, csv_path, test_size=0.2, random_state=42, sample_size=10000):
        """Train the DistilBERT model"""
        print("="*60)
        print("TIER 2 TEXT DETECTION TRAINING")
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
        print(f"Train class distribution: {train_df['label'].value_counts().to_dict()}")
        print(f"Test class distribution: {test_df['label'].value_counts().to_dict()}")

        # Convert to Hugging Face Dataset
        train_dataset = Dataset.from_pandas(train_df[['text', 'label']])
        test_dataset = Dataset.from_pandas(test_df[['text', 'label']])

        # Initialize tokenizer
        print("\nInitializing DistilBERT tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

        # Tokenization function
        def preprocess_function(examples):
            return self.tokenizer(examples["text"], truncation=True, max_length=512)

        # Tokenize datasets
        print("Tokenizing datasets...")
        tokenized_train = train_dataset.map(preprocess_function, batched=True)
        tokenized_test = test_dataset.map(preprocess_function, batched=True)

        # Data collator for dynamic padding
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)

        # Initialize model
        print("\nInitializing DistilBERT model...")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "distilbert-base-uncased",
            num_labels=2,
            id2label={0: "BENIGN", 1: "PHISHING"},
            label2id={"BENIGN": 0, "PHISHING": 1},
            # Increased dropout for regularization on small datasets
            dropout=0.2,
            attention_dropout=0.2
        )

        # Metrics
        accuracy_metric = evaluate.load("accuracy")
        precision_metric = evaluate.load("precision")
        recall_metric = evaluate.load("recall")
        f1_metric = evaluate.load("f1")

        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            predictions = np.argmax(predictions, axis=1)

            return {
                "accuracy": accuracy_metric.compute(predictions=predictions, references=labels)["accuracy"],
                "precision": precision_metric.compute(predictions=predictions, references=labels)["precision"],
                "recall": recall_metric.compute(predictions=predictions, references=labels)["recall"],
                "f1": f1_metric.compute(predictions=predictions, references=labels)["f1"],
            }

        # Check GPU availability and compatibility
        # GTX 1080 (CUDA 6.1) not compatible with PyTorch 2.x (requires CUDA 7.0+)
        # Force CPU mode for compatibility
        use_cuda = False
        print(f"Using device: CPU (GPU disabled for compatibility)")

        # Training configuration (maximally optimized for CPU constraints)
        training_args = TrainingArguments(
            output_dir="tier2_text/models/checkpoints",
            learning_rate=5e-5,  # Higher LR for faster convergence with fewer steps
            per_device_train_batch_size=128,  # Maximum batch size for CPU
            per_device_eval_batch_size=128,
            num_train_epochs=1,  # Single epoch for minimum training time
            weight_decay=0.01,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            logging_dir="tier2_text/models/logs",
            logging_steps=5,
            warmup_steps=10,  # Minimal warmup
            fp16=use_cuda,  # Mixed precision only on GPU
            dataloader_num_workers=0,  # Disable multiprocessing on CPU
        )

        # Initialize trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_train,
            eval_dataset=tokenized_test,
            processing_class=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=compute_metrics,
        )

        # Train
        print("\n" + "="*60)
        print("TRAINING")
        print("="*60 + "\n")
        self.trainer.train()

        # Final evaluation
        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)

        eval_results = self.trainer.evaluate()
        print("\nTest Set Performance:")
        for metric, value in eval_results.items():
            print(f"{metric}: {value:.4f}")

        # Detailed metrics with predictions
        predictions = self.trainer.predict(tokenized_test)
        y_pred_proba = torch.softmax(torch.tensor(predictions.predictions), dim=-1)[:, 1].numpy()
        y_pred = np.argmax(predictions.predictions, axis=1)
        y_test = predictions.label_ids

        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Benign', 'Phishing']))

        print(f"\nROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")

        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        print(f"[TN={cm[0,0]}, FP={cm[0,1]}]")
        print(f"[FN={cm[1,0]}, TP={cm[1,1]}]")

        # Save model
        self._save_model()

        return self.model

    def _save_model(self):
        """Save trained model and tokenizer to disk"""
        output_dir = f"tier2_text/{self.model_path}"
        os.makedirs(output_dir, exist_ok=True)

        # Save model and config
        self.trainer.save_model(output_dir)

        # Save tokenizer
        self.tokenizer.save_pretrained(output_dir)

        print(f"\nModel saved to: {output_dir}")
        print("Saved files:")
        for f in os.listdir(output_dir):
            print(f"  - {f}")

if __name__ == "__main__":
    import sys

    trainer = TextDetectorTrainer()
    # Use 2K samples for CPU training (minimal viable dataset)
    # This is a pragmatic choice given CPU-only environment and timeline constraints
    sample_size = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    print(f"\nTraining with {sample_size} samples for CPU compatibility")
    trainer.train("tier2_text/data/phishing_text.csv", sample_size=sample_size)
