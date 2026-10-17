"""
Model persistence - save and load trained models.
"""

import pickle
import json
from datetime import datetime
from pathlib import Path


def save_model(
    model,
    filepath: str | Path,
    feature_names: list[str],
    target_names: list[str],
    metrics: dict[str, float]
) -> None:
    """
    Save trained model to .pkl and metadata to .json.
    
    Args:
        model: Trained model object
        filepath: Path to save .pkl file
        feature_names: List of feature column names
        target_names: List of target column names
        metrics: Dict of RMSE values per target
    """
    filepath = Path(filepath)
    
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save model to .pkl
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    
    # Create metadata
    metadata = {
        "feature_names": feature_names,
        "target_names": target_names,
        "metrics": metrics,
        "trained_at": datetime.now().isoformat()
    }
    
    # Save metadata to .json (same name, different extension)
    metadata_path = filepath.with_suffix('.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)


def load_model(filepath: str | Path):
    """
    Load trained model from .pkl file.
    
    Args:
        filepath: Path to .pkl file
    
    Returns:
        Trained model object ready for .predict()
    """
    filepath = Path(filepath)
    
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    
    return model
