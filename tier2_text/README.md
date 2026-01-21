# Tier 2 Text Detection

## Model Architecture

**Current Implementation:** LightGBM + TF-IDF
**Alternative (not used):** DistilBERT (in tier2_training_distilbert.py)

### Why LightGBM + TF-IDF?

The original plan specified DistilBERT for text classification. However, due to GPU incompatibility (GTX 1080 with CUDA 6.1 not supported by PyTorch 2.x which requires CUDA 7.0+) and CPU training being prohibitively slow (~40 seconds per training step), a pragmatic decision was made to use LightGBM with TF-IDF features instead.

**Performance Comparison:**
- DistilBERT (CPU): Would take 8-10 hours to train on minimal dataset
- LightGBM + TF-IDF (CPU): Trains in ~2 minutes

**Accuracy:**
- Target: >85%
- Achieved: 94% accuracy, 98.8% ROC-AUC

This approach delivers superior performance in a fraction of the time, making it the better choice for this CPU-constrained environment.

## Training

### Quick Start

```bash
python tier2_text/tier2_training.py
```

This trains on 10,000 balanced samples (5K phishing, 5K benign) from the combined SMS spam + Enron email dataset.

### Model Output

Trained model saved to: `tier2_text/models/tier2_text_detector/`
- `model.pkl`: LightGBM model + TF-IDF vectorizer
- `config.json`: Model configuration

### Performance Metrics

```
Accuracy: 94%
Precision (Benign): 93%
Precision (Phishing): 96%
Recall (Benign): 96%
Recall (Phishing): 92%
F1-Score: 0.94
ROC-AUC: 0.988
```

### Confusion Matrix

```
                  Predicted
                Benign  Phishing
Actual Benign     964       36
       Phishing    77      923
```

## Future Work

If GPU becomes available or a more powerful CPU is used, the DistilBERT implementation in `tier2_training_distilbert.py` can be trained for potentially higher accuracy (96-99% based on research). However, the current LightGBM model already exceeds requirements and is production-ready.

## Dataset

See `data/README.md` for dataset information (37K samples from SMS spam + Enron email datasets).
