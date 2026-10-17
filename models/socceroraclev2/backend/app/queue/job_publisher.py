# Job publisher - creates and pushes jobs to Redis queue

import json
import uuid
from datetime import datetime
from app.queue.redis_client import get_redis_client


def publish_prediction_job(team1: str, team2: str, league: str | None = None) -> str:
    """
    Create a prediction job and push it to the Redis queue.
    
    Args:
        team1: Name of first team
        team2: Name of second team
        league: League name (optional)
    
    Returns:
        job_id: Unique identifier for the job (UUID string)
    """
    # Step 1: Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Step 2: Create job payload
    job = {
        "job_id": job_id,
        "team1": team1,
        "team2": team2,
        "league": league,
        "created_at": datetime.now().isoformat() + "Z"
    }
    
    # Step 3: Convert to JSON string
    job_json = json.dumps(job)
    
    # Step 4: Get Redis client
    client = get_redis_client()
    
    # Step 5: Push to queue
    queue_name = "predict"
    client.lpush(queue_name, job_json)
    
    # Step 6: Return job ID
    return job_id
