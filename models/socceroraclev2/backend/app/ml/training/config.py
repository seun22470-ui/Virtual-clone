"""
Configuration constants for training pipeline.
"""

from pathlib import Path

# Base directory for ML module
ML_DIR = Path(__file__).parent.parent

# Data paths
DATA_DIR = ML_DIR / "data"
FEATURES_FILE = DATA_DIR / "features_X.csv"
TARGETS_FILE = DATA_DIR / "targets_Y.csv"

# Models directory
MODELS_DIR = ML_DIR / "models"

# Training settings
TEST_RATIO = 0.2  # 20% for testing
RANDOM_SEED = 42  # For reproducibility

# Model filename
MODEL_FILENAME = "match_predictor.pkl"
METADATA_FILENAME = "match_predictor.json"
