"""
Random train/test splitting for match data.
"""

import pandas as pd
from sklearn.model_selection import train_test_split


def split_random(
    X: pd.DataFrame,
    Y: pd.DataFrame,
    test_ratio: float = 0.2,
    random_seed: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split data randomly - 80% train, 20% test.
    
    Args:
        X: Feature matrix (n_samples × n_features)
        Y: Target matrix (n_samples × n_targets)
        test_ratio: Fraction of data to use for testing (default 0.2 = 20%)
        random_seed: Seed for reproducibility
    
    Returns:
        train_X, test_X, train_Y, test_Y
    """
    train_X, test_X, train_Y, test_Y = train_test_split(
        X, Y,
        test_size=test_ratio,
        random_state=random_seed
    )
    
    return train_X, test_X, train_Y, test_Y
