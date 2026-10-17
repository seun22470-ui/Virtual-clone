# Prediction worker - processes jobs from queue

import json
import pandas as pd
from datetime import datetime
from app.queue.job_consumer import consume_job
from app.queue.redis_client import get_redis_client
from app.ml.training.model_saver import load_model
from app.ml.training.config import MODELS_DIR, MODEL_FILENAME
from app.ml.features.feature_builder import build_features_and_targets


def main():
    print("Starting prediction worker...\n")
    
    # Setup: Connect to Redis
    client = get_redis_client()
    print("✓ Connected to Redis")
    
    # Setup: Load ML model
    model_path = MODELS_DIR / MODEL_FILENAME
    model = load_model(model_path)
    print(f"✓ Loaded model from {model_path}")
    
    print("\nWorker ready, waiting for jobs...\n")
    
    # Main loop
    job_count = 0
    while True:
        # Pull job (blocks until available)
        job = consume_job()
        
        if job is None:
            continue
        
        job_count += 1
        
        # Extract job data
        job_id = job.get("job_id")
        team1 = job.get("team1")
        team2 = job.get("team2")
        league = job.get("league")
        
        # Generate features
        features_dict = build_features_and_targets(team1, team2, league)
        if features_dict is None:
            print(f"  ✗ Failed to generate features for {team1} vs {team2}")
            continue
        
        # Convert features dict to DataFrame (model expects 2D array)
        features_df = pd.DataFrame([features_dict["X"]])
        
        # Run model prediction
        try:
            predictions = model.predict(features_df)
        except Exception as e:
            print(f"  ✗ Model prediction failed: {e}")
            continue
        
        # Format result
        result = {
            "job_id": job_id,
            "team1": team1,
            "team2": team2,
            "league": league,
            "predictions": predictions.tolist(),
            "status": "completed",
            "completed_at": datetime.now().isoformat() + "Z"
        }
        result_json = json.dumps(result)
        
        # Store result in Redis
        result_key = f"result:{job_id}"
        try:
            client.set(result_key, result_json)
            client.expire(result_key, 3600)  # 1 hour TTL
        except Exception as e:
            print(f"  ✗ Failed to store result in Redis: {e}")
            continue
        
        # Log job info
        print(f"[Job {job_count}] Completed job: {job_id}")
        print(f"  Match: {team1} vs {team2}")
        print(f"  League: {league}")
        print(f"  Status: Completed - predictions stored in Redis")
        print(f"  Result key: {result_key}\n")


if __name__ == "__main__":
    main()
