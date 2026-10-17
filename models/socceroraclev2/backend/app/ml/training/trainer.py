"""
Main training orchestrator - runs the complete training pipeline.
"""

import pandas as pd
from .config import (
    FEATURES_FILE,
    TARGETS_FILE,
    MODELS_DIR,
    MODEL_FILENAME,
    TEST_RATIO,
    RANDOM_SEED
)
from .splitter import split_random
from .model_builder import build_model
from .evaluator import (
    calculate_rmse,
    calculate_baseline_rmse,
    print_evaluation_report
)
from .model_saver import save_model


def train_model(
    x_path: str | None = None,
    y_path: str | None = None
):
    """
    Run complete training pipeline: load → split → build → train → evaluate → save.
    
    Args:
        x_path: Optional path to features CSV (defaults to config)
        y_path: Optional path to targets CSV (defaults to config)
    
    Returns:
        Trained model object
    """
    # Step 1: Load data
    print("Loading data...")
    x_path = x_path or FEATURES_FILE
    y_path = y_path or TARGETS_FILE
    
    X = pd.read_csv(x_path)
    Y = pd.read_csv(y_path)
    
    print(f"Loaded {len(X)} matches with {len(X.columns)} features and {len(Y.columns)} targets\n")
    
    # Step 2: Split data
    print("Splitting data...")
    train_X, test_X, train_Y, test_Y = split_random(
        X, Y,
        test_ratio=TEST_RATIO,
        random_seed=RANDOM_SEED
    )
    print(f"Training set: {len(train_X)} matches, Test set: {len(test_X)} matches\n")
    
    # Step 3: Build model
    print("Building model...")
    model = build_model()
    
    # Step 4: Train (fit)
    print("Training...")
    model.fit(train_X, train_Y)
    print("Training complete\n")
    
    # Step 5: Predict on test set
    print("Making predictions on test set...")
    predictions = model.predict(test_X)
    
    # Step 6: Evaluate
    print("Evaluating...")
    target_names = Y.columns.tolist()
    model_rmse = calculate_rmse(predictions, test_Y, target_names)
    baseline_rmse = calculate_baseline_rmse(train_Y, test_Y)
    print_evaluation_report(model_rmse, baseline_rmse)
    
    # Step 7: Save model
    print("Saving model...")
    model_path = MODELS_DIR / MODEL_FILENAME
    save_model(
        model=model,
        filepath=model_path,
        feature_names=X.columns.tolist(),
        target_names=Y.columns.tolist(),
        metrics=model_rmse
    )
    print(f"Model saved to: {model_path}")
    print(f"Metadata saved to: {model_path.with_suffix('.json')}\n")
    
    # Step 8: Return trained model
    return model
