"""
Automated retraining script for GitHub Actions.
Trains a new model, compares with production, and promotes if improvement threshold is met.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.training.trainer import train_model
from app.ml.training.mlflow_utils import (
    get_production_model_version,
    get_production_metrics,
    compare_models,
    promote_to_production
)
import mlflow


def main():
    """
    Main retraining pipeline:
    1. Train new model
    2. Compare with production model
    3. Promote if improvement >= threshold
    """
    print("=" * 80)
    print("AUTOMATED WEEKLY RETRAINING PIPELINE")
    print("=" * 80)
    
    # Step 1: Train new model
    print("\n[Step 1/3] Training new model...")
    try:
        training_results = train_model(log_to_mlflow=True)
        model = training_results["model"]
        new_metrics = training_results["metrics"]
        run_id = training_results["run_id"]
        
        if run_id is None:
            print("✗ Failed to log model to MLflow. Exiting.")
            sys.exit(1)
        
        print(f"✓ Training complete (MLflow run_id: {run_id})")
    except Exception as e:
        print(f"✗ Training failed: {e}")
        sys.exit(1)
    
    # Step 2: Get production model metrics
    print("\n[Step 2/3] Comparing with production model...")
    production_metrics = get_production_metrics()
    production_version = get_production_model_version()
    
    if production_metrics:
        print(f"Found production model version: {production_version}")
    else:
        print("No production model found. This will be the first production model.")
    
    # Step 3: Compare and promote if threshold met
    print("\n[Step 3/3] Evaluating model performance...")
    improvement_threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 0.12  # Default 12%
    
    should_promote = compare_models(new_metrics, production_metrics, improvement_threshold)
    
    if should_promote:
        print("\n✓ Model meets improvement threshold. Promoting to production...")
        try:
            # Get the model version from the latest run
            client = mlflow.tracking.MlflowClient()
            run = client.get_run(run_id)
            
            # Find the model version for this run
            model_versions = client.search_model_versions(f"run_id='{run_id}'")
            if model_versions:
                model_version = model_versions[0].version
                promote_to_production(model_version)
                print(f"\n✓ Successfully promoted model version {model_version} to Production")
                print("=" * 80)
                sys.exit(0)
            else:
                print("✗ Could not find model version for this run")
                sys.exit(1)
        except Exception as e:
            print(f"✗ Failed to promote model: {e}")
            sys.exit(1)
    else:
        print("\n✗ Model does not meet improvement threshold. Not promoting.")
        print("Current production model remains active.")
        print("=" * 80)
        sys.exit(0)


if __name__ == "__main__":
    main()
