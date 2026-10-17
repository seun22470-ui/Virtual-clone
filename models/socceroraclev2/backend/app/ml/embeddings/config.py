"""
Configuration for embedding generation pipeline.
"""
from pathlib import Path

# Directories
ML_DIR = Path(__file__).parent.parent
EMBEDDINGS_DIR = Path(__file__).parent
DATA_DIR = ML_DIR / "data"
MODELS_DIR = ML_DIR / "models"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Input/Output files
PLAYERS_INPUT_FILE = DATA_DIR / "players_input.json"
COLLECTED_FEATURES_CSV = DATA_DIR / "collected_features.csv"
COLLECTED_FEATURES_JSON = DATA_DIR / "collected_features.json"
COLLECTION_REPORT_FILE = DATA_DIR / "collection_report.txt"

# PCA Configuration per position
EMBEDDING_CONFIG = {
    "Attacker": {
        "n_components": 12,
        "n_features": 17,
        "min_variance_explained": 0.90
    },
    "Midfielder": {
        "n_components": 12,
        "n_features": 17,
        "min_variance_explained": 0.90
    },
    "Defender": {
        "n_components": 12,
        "n_features": 17,
        "min_variance_explained": 0.90
    },
    "Goalkeeper": {
        "n_components": 10,  # GKs have different feature set
        "n_features": 15,    # goals_conceded, goals_saves (not goals_total, etc.)
        "min_variance_explained": 0.85
    }
}

# Minimum players required per position for PCA training
MIN_PLAYERS_FOR_PCA = {
    "Attacker": 50,
    "Midfielder": 50,
    "Defender": 50,
    "Goalkeeper": 30  # Fewer GKs in dataset
}

# API rate limiting
API_SLEEP_SECONDS = 5  # Sleep between players to avoid rate limits (5s for API quota)
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 5  # seconds

# Feature names (in order) - these match position_weights.py
OUTFIELD_FEATURE_NAMES = [
    'cards_red',
    'cards_yellow',
    'dribbles_attempts',
    'dribbles_success',
    'duels_total',
    'duels_won',
    'fouls_committed',
    'fouls_drawn',
    'goals_assists',
    'goals_shotsongoal',
    'goals_total',
    'goals_totalshots',
    'passes_key',
    'passes_total',
    'tackles_blocks',
    'tackles_interceptions',
    'tackles_total'
]

GOALKEEPER_FEATURE_NAMES = [
    'cards_red',
    'cards_yellow',
    'dribbles_attempts',
    'dribbles_success',
    'duels_total',
    'duels_won',
    'fouls_committed',
    'fouls_drawn',
    'goals_conceded',
    'goals_saves',
    'passes_key',
    'passes_total',
    'tackles_blocks',
    'tackles_interceptions',
    'tackles_total'
]
