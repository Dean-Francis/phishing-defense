# Phase 1: Tier 2 Text Detection - Research

**Researched:** 2026-01-20
**Domain:** NLP Text Classification with DistilBERT
**Confidence:** HIGH

## Summary

Tier 2 text detection involves fine-tuning DistilBERT (a distilled BERT model) for binary classification of phishing vs. benign messages. DistilBERT is 40% smaller and 60% faster than BERT while retaining 97% of its performance, making it ideal for production deployment with 5K-20K training samples.

The standard approach uses Hugging Face Transformers library with PyTorch, following a pattern similar to the existing Tier 1 URL detector: data preparation → model training with early stopping → inference with confidence scoring. DistilBERT achieves 96-99% accuracy on phishing detection tasks with proper fine-tuning.

Key risks for small datasets (5K-20K samples): overfitting, class imbalance handling, and preprocessing inconsistencies between training and inference.

**Primary recommendation:** Use Hugging Face Trainer API with stratified 80/20 split, implement early stopping and dropout regularization, and mirror Tier 1's inference output structure for seamless Phase 2 integration.

## Standard Stack

The established libraries/tools for DistilBERT text classification:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| transformers | 4.36+ | Pre-trained models, tokenizers, training | Official Hugging Face library, industry standard for transformer fine-tuning |
| torch | 2.0+ | Deep learning framework | Required by transformers, GPU acceleration support |
| datasets | 2.16+ | Data loading and preprocessing | Hugging Face ecosystem integration, efficient batching |
| evaluate | 0.4+ | Model evaluation metrics | Standardized metrics (accuracy, F1, precision, recall) |
| accelerate | 0.25+ | Training optimization | Multi-GPU support, mixed precision training |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| scikit-learn | 1.3+ | Train/test split, metrics | Stratified splitting, cross-validation |
| pandas | 2.0+ | CSV data manipulation | Dataset preprocessing, analysis |
| numpy | 1.24+ | Numerical operations | Metrics computation, array operations |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| DistilBERT | BERT-base | 2x slower inference, 1-2% better accuracy |
| DistilBERT | MiniLM | Faster inference, slightly less consistent accuracy across tasks |
| DistilBERT | RoBERTa-base | Higher accuracy (99.4%), 2.5x more parameters, slower |

**Installation:**
```bash
pip install transformers datasets evaluate accelerate torch scikit-learn pandas numpy
```

**Version Notes:**
- transformers 4.36+ includes latest DistilBERT optimizations and TrainingArguments improvements
- torch 2.0+ provides significant speedups with compiled models
- Use CUDA 11.8+ for GPU acceleration

## Architecture Patterns

### Recommended Project Structure
```
tier2_text/
├── tier2_training.py          # TextDetectorTrainer class (mirrors Tier 1 pattern)
├── tier2_inference.py         # TextDetectorInference class (mirrors Tier 1 pattern)
├── tier2_preprocessing.py     # Text cleaning, dataset preparation
├── models/
│   ├── tier2_text_detector/   # Fine-tuned model directory
│   │   ├── config.json
│   │   ├── pytorch_model.bin
│   │   └── tokenizer files
│   └── training_history.json  # Metrics tracking
├── data/
│   └── phishing_text.csv      # Training dataset (text, label columns)
└── README.md                  # Model card, usage examples
```

### Pattern 1: Dataset Preparation
**What:** CSV format with standardized columns, stratified split
**When to use:** Always for text classification
**Example:**
```python
# Source: Hugging Face official docs + research findings
import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset

# CSV format: text, label columns
# label: 0 (benign), 1 (phishing)
df = pd.read_csv('data/phishing_text.csv')

# Stratified split to maintain class balance
train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df['label']  # CRITICAL for imbalanced datasets
)

# Convert to Hugging Face Dataset
train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)
```

### Pattern 2: Tokenization with Preprocessing
**What:** AutoTokenizer with truncation, padding handled by DataCollator
**When to use:** All transformer-based text classification
**Example:**
```python
# Source: https://huggingface.co/docs/transformers/tasks/sequence_classification
from transformers import AutoTokenizer, DataCollatorWithPadding

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

def preprocess_function(examples):
    # Truncate to DistilBERT's max length (512 tokens)
    return tokenizer(examples["text"], truncation=True)

# Batch tokenization for efficiency
tokenized_train = train_dataset.map(preprocess_function, batched=True)
tokenized_test = test_dataset.map(preprocess_function, batched=True)

# Dynamic padding (more efficient than padding entire dataset)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
```

### Pattern 3: Model Training with Regularization
**What:** DistilBertForSequenceClassification with dropout, early stopping
**When to use:** Fine-tuning on small datasets (5K-20K samples)
**Example:**
```python
# Source: Official Hugging Face docs + research on small dataset optimization
from transformers import (
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
import evaluate

# Initialize model with custom dropout for small datasets
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=2,
    id2label={0: "BENIGN", 1: "PHISHING"},
    label2id={"BENIGN": 0, "PHISHING": 1},
    # Increase dropout from default 0.1 to 0.2 for small datasets
    dropout=0.2,
    attention_dropout=0.2
)

# Metrics computation
accuracy = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return accuracy.compute(predictions=predictions, references=labels)

# Training configuration for 5K-20K dataset
training_args = TrainingArguments(
    output_dir="tier2_text/models/checkpoints",
    learning_rate=2e-5,              # Standard for DistilBERT
    per_device_train_batch_size=16,  # Fits most GPUs, adjust based on VRAM
    per_device_eval_batch_size=16,
    num_train_epochs=5,              # 5-15 epochs for small datasets
    weight_decay=0.01,               # L2 regularization
    eval_strategy="epoch",           # Evaluate after each epoch
    save_strategy="epoch",
    load_best_model_at_end=True,     # CRITICAL: prevents overfitting
    metric_for_best_model="accuracy",
    logging_dir="tier2_text/models/logs",
    logging_steps=50,
    warmup_steps=100,                # Gradual learning rate warmup
    fp16=True,                       # Mixed precision for faster training (GPU only)
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    processing_class=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

# Train with automatic early stopping via load_best_model_at_end
trainer.train()
```

### Pattern 4: Model Saving (Production-Ready)
**What:** Save model, tokenizer, and config for inference
**When to use:** After training completes
**Example:**
```python
# Source: Hugging Face best practices
output_dir = "tier2_text/models/tier2_text_detector"

# Save everything needed for inference
trainer.save_model(output_dir)  # Saves model + config
tokenizer.save_pretrained(output_dir)  # Saves tokenizer files

# Verify saved files
# Expected: config.json, pytorch_model.bin, tokenizer_config.json, vocab.txt, etc.
```

### Pattern 5: Inference (Mirror Tier 1 Output Structure)
**What:** Load model once, predict with confidence scoring
**When to use:** Production inference, batch processing
**Example:**
```python
# Source: Tier 1 inference pattern + Hugging Face docs
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class TextDetectorInference:
    def __init__(self, model_path='tier2_text/models/tier2_text_detector',
                 confidence_threshold=0.85):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load model and tokenizer once
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            device_map="auto"  # Automatic device placement
        )
        self.model.eval()  # Set to evaluation mode

    def predict(self, text_data):
        """
        Args:
            text_data: Dictionary with 'text' key

        Returns:
            Dictionary matching Tier 1 output structure:
                - score: float (phishing probability 0-1)
                - label: str ('phishing' or 'benign')
                - confidence: str ('high' or 'low')
                - escalate: bool (True if score in uncertainty range)
                - metadata: dict with model info
        """
        # Tokenize
        inputs = self.tokenizer(
            text_data['text'],
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)

        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        # Convert to probabilities
        probs = torch.softmax(logits, dim=-1)
        phishing_score = float(probs[0][1])  # Probability of class 1 (phishing)

        # Determine label and confidence (same logic as Tier 1)
        label = 'phishing' if phishing_score >= 0.5 else 'benign'
        confidence = 'high' if (phishing_score >= self.confidence_threshold or
                                 phishing_score <= (1 - self.confidence_threshold)) else 'low'
        escalate = confidence == 'low'

        return {
            'score': phishing_score,
            'label': label,
            'confidence': confidence,
            'escalate': escalate,
            'metadata': {
                'tier': 2,
                'model': 'DistilBERT_Text_Detector',
                'threshold': self.confidence_threshold,
                'text_length': len(text_data['text'])
            }
        }

    def predict_batch(self, text_data_list):
        """Batch inference for efficiency"""
        texts = [item['text'] for item in text_data_list]

        # Tokenize batch
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        ).to(self.device)

        # Batch inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)

        # Process each result
        results = []
        for i, phishing_score in enumerate(probs[:, 1].tolist()):
            label = 'phishing' if phishing_score >= 0.5 else 'benign'
            confidence = 'high' if (phishing_score >= self.confidence_threshold or
                                     phishing_score <= (1 - self.confidence_threshold)) else 'low'

            results.append({
                'score': phishing_score,
                'label': label,
                'confidence': confidence,
                'escalate': confidence == 'low',
                'metadata': {
                    'tier': 2,
                    'model': 'DistilBERT_Text_Detector',
                    'threshold': self.confidence_threshold,
                    'text_length': len(text_data_list[i]['text'])
                }
            })

        return results
```

### Anti-Patterns to Avoid

- **Don't preprocess differently at inference:** Same tokenizer, truncation, and preprocessing must be used during training and inference. Inconsistencies cause silent failures.
- **Don't pad entire dataset upfront:** Use DataCollatorWithPadding for dynamic padding during training (more efficient).
- **Don't skip stratified splitting:** Random split may put all minority class samples in one set, biasing results.
- **Don't ignore early stopping:** Small datasets overfit quickly. Always use `load_best_model_at_end=True`.
- **Don't use accuracy as sole metric:** For imbalanced datasets, track precision, recall, F1-score, and confusion matrix.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Text tokenization | Custom word splitter | AutoTokenizer from transformers | Handles subword tokenization (WordPiece), special tokens, padding, truncation |
| Dynamic padding | Manual padding to max length | DataCollatorWithPadding | Pads to longest sequence in batch, not dataset max (saves memory/compute) |
| Training loop | Custom PyTorch training loop | Hugging Face Trainer | Handles gradient accumulation, mixed precision, checkpointing, distributed training |
| Evaluation metrics | Manual accuracy calculation | evaluate.load("accuracy") | Standardized, tested implementations; supports multiple metrics |
| Learning rate scheduling | Manual LR decay | TrainingArguments with warmup_steps | Gradual warmup prevents unstable training on small datasets |
| Model checkpointing | Manual torch.save() logic | Trainer with save_strategy="epoch" | Automatic best model tracking, recovery from failures |

**Key insight:** Transformers have many subtle behaviors (attention masks, token type IDs, position embeddings) that custom code often gets wrong. Hugging Face abstractions handle edge cases tested across thousands of models.

## Common Pitfalls

### Pitfall 1: Overfitting on Small Datasets
**What goes wrong:** Model memorizes training data, achieves 99% training accuracy but 70% test accuracy. Especially common with 5K-10K samples.
**Why it happens:** Transformers have millions of parameters; small datasets don't provide enough diversity.
**How to avoid:**
- Increase dropout from default 0.1 to 0.2-0.3
- Use weight_decay (L2 regularization) = 0.01
- Limit epochs to 5-10 with early stopping
- Monitor validation loss; stop when it starts increasing
**Warning signs:** Large gap between train and validation accuracy (>10%), validation loss increasing while train loss decreases

### Pitfall 2: Class Imbalance Bias
**What goes wrong:** Model predicts majority class for everything (e.g., 95% benign accuracy but 0% phishing detection).
**Why it happens:** If dataset is 90% benign, model learns "always predict benign" achieves high accuracy.
**How to avoid:**
- Use stratified train/test split with `stratify=df['label']`
- Balance dataset or use class weights in loss function
- Monitor precision/recall for BOTH classes, not just accuracy
- For phishing detection, prioritize recall (catch all phishing) over precision
**Warning signs:** High overall accuracy but very low recall on minority class, confusion matrix showing one class never predicted

### Pitfall 3: Tokenization Inconsistencies
**What goes wrong:** Model performs well in training but fails mysteriously in production.
**Why it happens:** Different preprocessing during training vs. inference (e.g., lowercasing in training but not inference).
**How to avoid:**
- Use same tokenizer instance for train and inference (save with model)
- Always use `truncation=True` in both training and inference
- Don't manually clean text unless doing it everywhere
- Test inference pipeline on validation set before deployment
**Warning signs:** Large performance drop between validation (same preprocessing) and production, errors about sequence length

### Pitfall 4: Ignoring GPU Memory Limits
**What goes wrong:** Training crashes with CUDA out of memory error.
**Why it happens:** Batch size too large for GPU VRAM, or gradient accumulation not configured.
**How to avoid:**
- Start with batch_size=16, reduce to 8 if OOM occurs
- Use `fp16=True` (mixed precision) to halve memory usage on modern GPUs
- Reduce max_length from 512 to 256 if messages are typically short
- Use gradient_accumulation_steps to simulate larger batches
**Warning signs:** OOM errors during training, GPU utilization at 100% but slow training

### Pitfall 5: Not Validating Saved Models
**What goes wrong:** Model saved incorrectly, missing tokenizer files, inference fails.
**Why it happens:** Saving only model weights without config/tokenizer.
**How to avoid:**
- Always use `trainer.save_model(path)` not `torch.save(model.state_dict())`
- Save tokenizer with `tokenizer.save_pretrained(path)`
- Test loading model in fresh Python session before considering training complete
- Verify all expected files exist: config.json, pytorch_model.bin, tokenizer files
**Warning signs:** Errors when loading model, missing id2label mapping, tokenizer not found

### Pitfall 6: Removing Important Text Features
**What goes wrong:** Preprocessing removes critical phishing signals (e.g., removing "!" or all caps).
**Why it happens:** Aggressive text cleaning borrowed from other NLP tasks.
**How to avoid:**
- Minimal preprocessing for transformers (they handle raw text well)
- Don't remove punctuation (phishing often uses "!!!", "URGENT")
- Don't lowercase if case is informative ("VERIFY YOUR ACCOUNT")
- Don't remove stopwords (transformers use them for context)
**Warning signs:** Model performs worse than baseline, human-readable phishing signals missing from processed text

## Code Examples

Verified patterns from official sources:

### Complete Training Script
```python
# Source: Hugging Face official text classification tutorial
# Adapted for phishing detection with small dataset optimizations

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
import evaluate

# 1. Load and split data (stratified for balance)
df = pd.read_csv('data/phishing_text.csv')  # Columns: text, label (0/1)
train_df, test_df = train_test_split(
    df, test_size=0.2, random_state=42, stratify=df['label']
)

train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)

print(f"Train samples: {len(train_dataset)}, Test samples: {len(test_dataset)}")
print(f"Class distribution: {train_df['label'].value_counts().to_dict()}")

# 2. Tokenization
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

def preprocess_function(examples):
    return tokenizer(examples["text"], truncation=True)

tokenized_train = train_dataset.map(preprocess_function, batched=True)
tokenized_test = test_dataset.map(preprocess_function, batched=True)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# 3. Model initialization
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=2,
    id2label={0: "BENIGN", 1: "PHISHING"},
    label2id={"BENIGN": 0, "PHISHING": 1},
    dropout=0.2,  # Increased for small dataset
    attention_dropout=0.2
)

# 4. Metrics
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

# 5. Training configuration
training_args = TrainingArguments(
    output_dir="tier2_text/models/checkpoints",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=10,  # Will stop early if overfitting
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",  # Optimize F1 for balanced performance
    logging_dir="tier2_text/models/logs",
    logging_steps=50,
    warmup_steps=100,
    fp16=True,  # GPU only
)

# 6. Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    processing_class=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

print("Starting training...")
trainer.train()

# 7. Evaluate
print("\nFinal evaluation:")
results = trainer.evaluate()
print(results)

# 8. Save for production
output_dir = "tier2_text/models/tier2_text_detector"
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)
print(f"\nModel saved to {output_dir}")

# 9. Test inference
from tier2_inference import TextDetectorInference

detector = TextDetectorInference(model_path=output_dir)
test_msg = {"text": "URGENT: Your account will be suspended! Click here now: http://fake-bank.tk"}
result = detector.predict(test_msg)
print(f"\nTest prediction: {result}")
```

### Handling Class Imbalance (Advanced)
```python
# Source: Research on class imbalance in deep learning
# Use if dataset is significantly imbalanced (>70/30 split)

from torch import nn

class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")

        # Calculate class weights (inverse frequency)
        # Example: 80% benign, 20% phishing → weights [0.625, 2.5]
        class_weights = torch.tensor([0.625, 2.5]).to(self.model.device)

        loss_fct = nn.CrossEntropyLoss(weight=class_weights)
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))

        return (loss, outputs) if return_outputs else loss

# Use WeightedTrainer instead of Trainer for imbalanced datasets
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| BERT-base fine-tuning | DistilBERT fine-tuning | 2019 (DistilBERT paper) | 60% faster inference, 40% smaller, 97% accuracy retained |
| Manual training loops | Hugging Face Trainer | 2020 (Transformers 3.0) | Simplified code, automatic mixed precision, distributed training |
| Static padding to max_length | Dynamic padding with DataCollator | 2020 | 30-50% memory savings, faster training |
| Single checkpoint saving | load_best_model_at_end | 2021 | Automatic overfitting prevention |
| Manual tokenization | AutoTokenizer | 2019 | Handles special tokens, padding, truncation correctly |

**Deprecated/outdated:**
- **TFDistilBertForSequenceClassification (TensorFlow)**: PyTorch is now dominant for Transformers; TF support minimal
- **token_type_ids for DistilBERT**: DistilBERT doesn't use token_type_ids (no segment embeddings)
- **pytorch_model.bin**: Newer models use safetensors format (more secure, faster loading)

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal dataset size for 85% accuracy target**
   - What we know: Research shows DistilBERT achieves 96-99% accuracy on phishing detection; 16K samples achieved 83% accuracy in one study (emotional classification)
   - What's unclear: Minimum sample size for 85% accuracy on THIS specific phishing dataset
   - Recommendation: Start with 10K samples (5K phishing, 5K benign), monitor validation accuracy; if <85%, collect more data or use data augmentation (back-translation)

2. **Data augmentation for phishing text**
   - What we know: Back-translation and synonym replacement can help small datasets; word replacement using BERT contextual embeddings (nlpaug library)
   - What's unclear: Whether augmentation preserves phishing signals or creates unrealistic examples
   - Recommendation: Test augmentation on 10% of data first, manually review generated samples for realism

3. **Cross-domain performance (email vs. SMS vs. social media)**
   - What we know: Phishing patterns differ across domains (email has headers, SMS is shorter, social media has emojis)
   - What's unclear: Whether single DistilBERT model generalizes or needs domain-specific fine-tuning
   - Recommendation: Include diverse sources in training data; track per-domain performance during evaluation

4. **Evasion technique robustness (character substitution, homoglyphs)**
   - What we know: Attackers use techniques like "Paypa1" instead of "PayPal" or "Micr0soft"
   - What's unclear: How well DistilBERT's subword tokenization handles these evasions
   - Recommendation: Create adversarial test set with common evasions; if accuracy drops >10%, augment training data with synthetic evasions

## Sources

### Primary (HIGH confidence)
- [Hugging Face Text Classification Tutorial](https://huggingface.co/docs/transformers/tasks/sequence_classification) - Official workflow, TrainingArguments, code examples
- [Hugging Face DistilBERT Documentation](https://huggingface.co/docs/transformers/en/model_doc/distilbert) - Model architecture, configuration parameters, API details
- [Fine-Tuning DistilBERT: Step-by-Step Practical Guide](https://medium.com/@heyamit10/fine-tuning-distilbert-a-step-by-step-practical-guide-8eda046222b5) - Hyperparameter optimization, data augmentation techniques
- [Comparative Investigation of Traditional Machine-Learning Models and Transformer Models for Phishing Email Detection](https://www.mdpi.com/2079-9292/13/24/4877) - Phishing detection accuracy benchmarks, DistilBERT 98.99% accuracy
- [In-Depth Analysis of Phishing Email Detection](https://www.mdpi.com/2076-3417/15/6/3396) - NLP features, BiGRU 97.39% accuracy, TF-IDF analysis

### Secondary (MEDIUM confidence)
- [Hugging Face Transformers: Fine-tuning DistilBERT for Binary Classification Tasks](https://towardsdatascience.com/hugging-face-transformers-fine-tuning-distilbert-for-binary-classification-tasks-490f1d192379/) - Binary classification workflow
- [Fine-Tuning Transformers: Techniques for Improving Model Performance](https://medium.com/@hassaanidrees7/fine-tuning-transformers-techniques-for-improving-model-performance-4b4353e8ba93) - Regularization methods, learning rate optimization
- [Survey on deep learning with class imbalance](https://link.springer.com/article/10.1186/s40537-019-0192-5) - Class imbalance handling in deep learning
- [Train Test Validation Split: Best Practices & Examples](https://www.lightly.ai/blog/train-test-validation-split) - Stratified splitting rationale
- [How to Use DistilBERT for Production](https://mljourney.com/how-to-use-distilbert-and-other-lightweight-transformers-for-production/) - Production deployment, latency optimization
- [Fast DistilBERT on CPUs](https://arxiv.org/abs/2211.07715) - CPU optimization, 1.5-4.1x speedup techniques

### Tertiary (LOW confidence - requires validation)
- [Phishing Email Detection Using Natural Language Processing Techniques: A Literature Survey](https://www.sciencedirect.com/science/article/pii/S1877050921011741) - NLP features for phishing (older survey)
- [Text Preprocessing: Complete Guide](https://mbrenndoerfer.com/writing/text-preprocessing-nlp-tokenization-normalization) - Preprocessing common mistakes (general NLP, not phishing-specific)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Hugging Face Transformers is industry standard, verified through official docs
- Architecture patterns: HIGH - Patterns verified in official tutorials and recent research papers
- DistilBERT hyperparameters: MEDIUM - General transformer best practices verified, but 5K-20K dataset size not specifically tested in sources
- Phishing-specific features: MEDIUM - Research shows NLP works for phishing (96-99% accuracy), but specific dataset characteristics unknown
- Pitfalls: HIGH - Common pitfalls verified across multiple sources and official documentation

**Research date:** 2026-01-20
**Valid until:** ~60 days (February 2026) - Transformer best practices stable, but Hugging Face library updates frequently
**Recommended re-verification:** Before production deployment, verify DistilBERT performance on actual phishing dataset (current findings based on general phishing detection research)
