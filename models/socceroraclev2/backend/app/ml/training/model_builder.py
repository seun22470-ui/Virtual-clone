"""
Model construction for match prediction.
"""

import lightgbm as lgb
from sklearn.multioutput import MultiOutputRegressor


def get_default_params() -> dict:
    """
    Returns sensible LightGBM hyperparameters for ~280 row dataset.
    """
    return {
        "n_estimators": 100,
        "learning_rate": 0.05,
        "num_leaves": 20,
        "min_child_samples": 25,
        "max_depth": 4,
        "subsample": 1.0,
        "colsample_bytree": 0.8,
        "reg_lambda": 1.0,
        "random_state": 42,
        "verbosity": -1,
    }


def build_model(params: dict | None = None):
    """
    Builds an untrained MultiOutputRegressor wrapping LightGBM.
    
    Args:
        params: Optional dict of hyperparameters. If None, uses defaults.
    
    Returns:
        Untrained MultiOutputRegressor ready for .fit()
    """
    if params is None:
        params = get_default_params()
    
    lgb_model = lgb.LGBMRegressor(**params)
    
    wrapped_model = MultiOutputRegressor(lgb_model)
    
    return wrapped_model
