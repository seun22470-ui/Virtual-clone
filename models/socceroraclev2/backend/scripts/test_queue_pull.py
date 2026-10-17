# Test script to pull jobs from queue

import sys
import json
from pathlib import Path

# Add parent directory to path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.queue import get_redis_client


def main():
    # Step 1: Connect to Redis
    client = get_redis_client()
    print("Connected to Redis ✓")
    
    # Queue name
    queue_name = "predict"
    
    # Step 2: Check queue status
    initial_length = client.llen(queue_name)
    
    if initial_length == 0:
        num_jobs_to_pull = 1
    else:
        num_jobs_to_pull = initial_length

    
    # Step 3-6: Pull and process jobs
    jobs_pulled = 0
    for i in range(num_jobs_to_pull):
        # Step 3: Pull job using BRPOP (blocks until job available)
        result = client.brpop(queue_name, timeout=0)
        
        if result is None:
            break
        
        # BRPOP returns tuple: (queue_name, job_json_string)
        queue, job_json = result
        
        # Step 4: Parse JSON string to Python dict
        job = json.loads(job_json)
        
        jobs_pulled += 1
        
        # Step 5: Display job information
        print(f"  → Pulled job {jobs_pulled}:")
        print(f"     Job ID: {job.get('job_id', 'N/A')}")
        print(f"     Match: {job.get('team1', 'N/A')} vs {job.get('team2', 'N/A')}")
        print(f"     Date: {job.get('date', 'N/A')}")
        print(f"     League: {job.get('league', 'N/A')}")
        print(f"     Created: {job.get('created_at', 'N/A')}")
        print()
    
    # Step 7: Final verification
    final_length = client.llen(queue_name)
    
    print(f"✓ Success! Pulled {jobs_pulled} job(s)")
    print(f"  Queue '{queue_name}' now contains {final_length} job(s)")


if __name__ == "__main__":
    main()
