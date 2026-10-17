"""
MLflow utilities for model tracking and registry management.
"""

import os
import mlflow
import mlflow.sklearn
from typing import Dict, Optional
from pathlib import Path


# MLflow configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
MLFLOW_EXPERIMENT_NAME = "soccer_match_prediction"
MODEL_NAME = "match_predictor"


def setup_mlflow():
    """
    Initialize MLflow tracking with experiment name.
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)


def get_production_model_version() -> Optional[str]:
    """
    Get the current production model version from MLflow Model Registry.
    
    Returns:
        Model version string if production model exists, None otherwise
    """
    try:
        client = mlflow.tracking.MlflowClient()
        latest_versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])
        
        if latest_versions:
            return latest_versions[0].version
        return None
    except Exception as e:
        print(f"Warning: Could not fetch production model version: {e}")
        return None


def get_production_metrics() -> Optional[Dict[str, float]]:
    """
    Get metrics from the current production model.
    
    Returns:
        Dict of metrics if production model exists, None otherwise
    """
    try:
        client = mlflow.tracking.MlflowClient()
        latest_versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])
        
        if not latest_versions:
            return None
        
        production_version = latest_versions[0]
        run_id = production_version.run_id
        
        run = client.get_run(run_id)
        
        # Extract RMSE metrics
        metrics = {}
        for key, value in run.data.metrics.items():
            if key.startswith("rmse_"):
                metrics[key] = value
        
        return metrics
    except Exception as e:
        print(f"Warning: Could not fetch production metrics: {e}")
        return None


def compare_models(new_metrics: Dict[str, float], production_metrics: Optional[Dict[str, float]], improvement_threshold: float = 0.12) -> bool:
    """
    Compare new model metrics against production model.
    
    Args:
        new_metrics: Dict of RMSE metrics from new model
        production_metrics: Dict of RMSE metrics from production model (None if no production model)
        improvement_threshold: Minimum improvement percentage (default 12%)
    
    Returns:
        True if new model should be promoted, False otherwise
    """
    if production_metrics is None:
        # No production model exists, promote first model
        return True
    
    # Calculate average RMSE for comparison
    def avg_rmse(metrics: Dict[str, float]) -> float:
        rmse_values = [v for k, v in metrics.items() if k.startswith("rmse_")]
        return sum(rmse_values) / len(rmse_values) if rmse_values else float('inf')
    
    new_avg = avg_rmse(new_metrics)
    prod_avg = avg_rmse(production_metrics)
    
    if prod_avg == 0:
        return True
    
    improvement = (prod_avg - new_avg) / prod_avg
    
    print(f"\nModel Comparison:")
    print(f"  Production avg RMSE: {prod_avg:.4f}")
    print(f"  New model avg RMSE: {new_avg:.4f}")
    print(f"  Improvement: {improvement*100:.2f}%")
    print(f"  Threshold: {improvement_threshold*100:.2f}%")
    
    return improvement >= improvement_threshold


def promote_to_production(model_version: str):
    """
    Promote a model version to Production stage in MLflow Registry.
    
    Args:
        model_version: Version string of the model to promote
    """
    try:
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=model_version,
            stage="Production",
            archive_existing_versions=True  # Archive old production versions
        )
        print(f"✓ Promoted model version {model_version} to Production")
    except Exception as e:
        print(f"✗ Failed to promote model to production: {e}")
        raise
