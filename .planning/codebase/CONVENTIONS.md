# Coding Conventions

**Analysis Date:** 2026-01-20

## Naming Patterns

**Files:**
- Snake_case with descriptive prefixes: `tier1_features.py`, `tier1_training.py`, `tier1_inference.py`
- Pattern: `{tier}_{component}.py`
- Test files: `test.py` (minimal naming convention)

**Functions:**
- Snake_case for all functions: `extract_features()`, `_calculate_entropy()`, `_load_model()`
- Private/internal functions prefixed with single underscore: `_extract_url_features()`, `_get_null_features()`, `_save_model()`
- Public methods without underscore prefix: `predict()`, `train()`, `load_data()`

**Variables:**
- Snake_case for all local variables: `features`, `phishing_score`, `importance_df`, `feature_names`, `url_length`
- Constants as uppercase with underscores: `ip_pattern` (pattern strings), `suspicious_tokens`, `risky_tlds`
- Descriptive naming for model state: `model`, `feature_extractor`, `confidence_threshold`

**Classes:**
- PascalCase for all classes: `URLFeatureExtractor`, `URLDetectorTrainer`, `URLDetectorInference`
- Descriptive, purpose-driven naming with clear role indicators

**Type Hints:**
- Full type annotations used throughout: `Dict[str, Any]`, `List[Dict[str, Any]]`, `float`, `int`
- Return type annotations on all methods: `-> Dict[str, Any]`, `-> None`
- Parameter type hints: `url: str`, `csv_path`, `model_path: str`

## Code Style

**Formatting:**
- No explicit formatter configured (not Black, not autopep8)
- Indentation: 4 spaces (Python standard)
- Line length: ~80-90 characters (no strict enforcement)
- Spacing around operators and after commas

**Linting:**
- No linter configuration detected (no .flake8, .pylintrc)
- Code follows standard Python conventions organically

**Docstrings:**
- Class-level docstrings: Present in trainer and inference classes
- Method-level docstrings: Used for public methods with complex behavior
- Example: `"""Train the LightGBM model"""`, `"""Predict phishing probability for a single URL"""`
- Parameter documentation in docstrings with Args/Returns format

## Import Organization

**Order:**
1. Standard library imports: `import re`, `import os`
2. Third-party library imports: `import pandas`, `import numpy`, `import lightgbm`
3. Data science libraries: `from sklearn.model_selection import...`, `import joblib`
4. Local/project imports: `from tier1_features import URLFeatureExtractor`

**Path Aliases:**
- Used for third-party packages: `import lightgbm as lgb`, `import numpy as np`, `import pandas as pd`
- No local path aliases or relative imports observed
- Explicit imports from modules: `from tier1_features import URLFeatureExtractor`

**Grouping:**
- Import statements at top of file
- Blank line separating standard library from third-party
- Blank line separating imports from code

## Error Handling

**Patterns:**
- Try-except blocks for risky operations: `try: urlparse(), tldextract.extract() except Exception`
- Generic `Exception` catching in feature extraction to return null features on parse failure
- FileNotFoundError handling for model loading: `except FileNotFoundError: raise FileNotFoundError(...)`
- No exception logging or custom exception types
- Recovery through sensible defaults: `_get_null_features()` returns zero-filled feature dict

**Strategy:**
- Silent failures with default returns in feature extraction (catch all, return zeros)
- Explicit failures with informative messages for critical operations (model loading)
- Graceful degradation when input is malformed or missing

## Logging

**Framework:** No logging framework configured

**Approach:** Direct print() statements for status and diagnostics
- Training progress: `print("Loading data...")`, `print(f"Dataset: {len(X)} samples...")`
- Model evaluation: `print("\n" + "="*60)`, formatted output sections
- Inference examples: Print predictions and feature contributions
- No structured logging, timestamps, or log levels

**Patterns:**
- Print statements for user-facing output during training
- Formatted separators for visual organization: `"="*60`
- Conditional printing in model loading: `print(f"Model loaded from: {self.model_path}")`

## Comments

**When to Comment:**
- Minimal comments in production code
- No inline comments explaining logic
- Comments used mainly for section headers in configuration: `# Split data`, `# Configure LightGBM...`, `# Evaluate`
- Configuration comments explain purpose of settings, not implementation

**Documentation:**
- Class-level docstrings for trainer and inference classes
- Method-level docstrings for complex public methods
- Docstrings include Args, Returns, and purpose
- Type hints serve as inline documentation

## Function Design

**Size:**
- Small, focused functions (15-40 lines typical)
- Feature extraction functions: 30-40 lines
- Utility functions: 5-15 lines

**Parameters:**
- Typed parameters with meaningful names
- Dictionary parameters for passing complex data: `url_data: Dict[str, Any]`
- Row objects extracted from DataFrames using `.get()` or `.iterrows()`
- Optional parameters with defaults: `confidence_threshold: float = 0.85`

**Return Values:**
- Consistent return types: Functions return dict, dataframe, or typed data structures
- Dictionaries for complex results with multiple fields: `{'score': float, 'label': str, 'metadata': dict}`
- DataFrames for tabular results: `extract_from_dataframe()` returns `pd.DataFrame`
- None for void operations: `_load_model() -> None`, `_save_model() -> None`

## Module Design

**Exports:**
- Classes as main exports: `URLFeatureExtractor`, `URLDetectorTrainer`, `URLDetectorInference`
- `if __name__ == "__main__":` blocks for executable modules with examples
- Direct imports: `from tier1_features import URLFeatureExtractor`

**Barrel Files:**
- No barrel/init files observed
- Direct module imports used throughout
- Single responsibility per module: features, training, inference are separate

## Data Structures

**Configuration:**
- Model parameters as dictionaries: `params = {'objective': 'binary', 'metric': 'auc', ...}`
- Feature lists as hardcoded lists in `__init__`: `suspicious_tokens`, `risky_tlds`
- No config files (YAML, JSON, .env used for config)

**State Management:**
- Class instance variables in `__init__`: `self.model`, `self.feature_extractor`, `self.feature_names`
- Lazy initialization: Model loaded in `_load_model()` called from `__init__`
- Stateful classes maintain context: trainer keeps model and feature names across operations

---

*Convention analysis: 2026-01-20*
