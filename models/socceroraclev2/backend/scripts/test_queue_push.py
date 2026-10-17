# Test script to push jobs to queue

import sys
import json
import uuid
from datetime import datetime
from pathlib import Path

# Add parent directory to path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.queue import get_redis_client


def main():
    # Get Redis client
    client = get_redis_client()
    
    # Base job template
    base_job = {
        "team1": "Manchester United",
        "team2": "Liverpool",
        "date": "2024-12-15",
        "league": "Premier League",
        "created_at": datetime.now().isoformat() + "Z"
    }
    
    # Queue name
    queue_name = "predict"
    
    # Number of jobs to push
    num_jobs = 5
    
    # Push multiple jobs
    for i in range(num_jobs):
        # Create job with unique ID
        job = base_job.copy()
        job["job_id"] = str(uuid.uuid4())
        
        # Convert to JSON string
        job_json = json.dumps(job)
        
        # Push to queue
        client.lpush(queue_name, job_json)
        
    
    # Verify queue length
    queue_length = client.llen(queue_name)
    print(f"\n✓ Success! Queue '{queue_name}' now contains {queue_length} job(s)")


if __name__ == "__main__":
    main()
