# Job consumer - pulls jobs from Redis queue

import json
from app.queue.redis_client import get_redis_client


def consume_job():
    """
    Pull a job from the Redis queue (blocking).
    
    Returns:
        job dict if job available, None if connection error
    """
    # Step 1: Get Redis client
    client = get_redis_client()
    
    # Step 2: Pull job from queue (blocking - waits until job available)
    queue_name = "predict"
    result = client.brpop(queue_name, timeout=0)
    
    # Step 3: Handle result
    if result is None:
        return None
    
    # BRPOP returns tuple: (queue_name, job_json_string)
    queue, job_json = result
    
    # Step 4: Parse JSON string to Python dict
    try:
        job = json.loads(job_json)
        return job
    except json.JSONDecodeError:
        # Invalid JSON - return None
        return None
