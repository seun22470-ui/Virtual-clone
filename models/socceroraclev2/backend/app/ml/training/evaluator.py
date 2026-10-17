"""
Model evaluation metrics.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error


def calculate_rmse(
    predictions: np.ndarray | pd.DataFrame,
    actuals: pd.DataFrame,
    target_names: list[str]
) -> dict[str, float]:
    """
    Calculate RMSE per target across all test samples.
    
    Args:
        predictions: Model predictions (n_samples × n_targets)
        actuals: Actual target values (n_samples × n_targets)
        target_names: List of target column names
    
    Returns:
        Dict mapping target name to RMSE value
    """
    rmse_dict = {}
    
    for i, target_name in enumerate(target_names):
        pred_col = predictions[:, i] if isinstance(predictions, np.ndarray) else predictions.iloc[:, i]
        actual_col = actuals.iloc[:, i]
        
        rmse = np.sqrt(mean_squared_error(actual_col, pred_col))
        rmse_dict[target_name] = rmse
    
    return rmse_dict


def calculate_baseline_rmse(
    train_Y: pd.DataFrame,
    test_Y: pd.DataFrame
) -> dict[str, float]:
    """
    Calculate baseline RMSE (predicting mean from training data).
    
    Args:
        train_Y: Training target values (used to compute means)
        test_Y: Test target values (used to compute baseline RMSE)
    
    Returns:
        Dict mapping target name to baseline RMSE value
    """
    baseline_rmse_dict = {}
    
    for target_name in test_Y.columns:
        # Compute mean from training data
        mean_value = train_Y[target_name].mean()
        
        # Predict that mean for all test rows
        baseline_predictions = np.full(len(test_Y), mean_value)
        
        # Calculate RMSE
        rmse = np.sqrt(mean_squared_error(test_Y[target_name], baseline_predictions))
        baseline_rmse_dict[target_name] = rmse
    
    return baseline_rmse_dict


def print_evaluation_report(
    model_rmse: dict[str, float],
    baseline_rmse: dict[str, float]
) -> None:
    """
    Print formatted evaluation report comparing model to baseline.
    
    Args:
        model_rmse: Dict of model RMSE per target
        baseline_rmse: Dict of baseline RMSE per target
    """
    print("\n" + "=" * 80)
    print("EVALUATION REPORT")
    print("=" * 80)
    print(f"{'Target':<30} {'Model RMSE':<15} {'Baseline RMSE':<15} {'Improvement':<15}")
    print("-" * 80)
    
    for target_name in model_rmse.keys():
        model_val = model_rmse[target_name]
        baseline_val = baseline_rmse[target_name]
        
        # Calculate improvement percentage
        if baseline_val > 0:
            improvement = ((baseline_val - model_val) / baseline_val) * 100
            improvement_str = f"+{improvement:.1f}%"
        else:
            improvement_str = "N/A"
        
        print(f"{target_name:<30} {model_val:<15.3f} {baseline_val:<15.3f} {improvement_str:<15}")
    
    print("=" * 80 + "\n")
