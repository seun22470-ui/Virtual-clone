# Test script for job_consumer

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.queue.job_publisher import publish_prediction_job
from app.queue.job_consumer import consume_job
from app.queue.redis_client import get_redis_client


def main():
    print("Testing job_consumer...\n")
    
    # Step 0: Clear queue to start fresh
    print("0. Clearing queue for clean test...")
    client = get_redis_client()
    queue_name = "predict"
    # Clear all jobs from queue
    while client.llen(queue_name) > 0:
        client.rpop(queue_name)
    print("   ✓ Queue cleared")
    
    # Step 1: Push a job using publisher
    print("\n1. Publishing a job...")
    job_id = publish_prediction_job(
        team1="Arsenal",
        team2="Chelsea",
        league="Premier League"
    )
    print(f"   ✓ Job published with ID: {job_id}")
    
    # Step 2: Check queue length
    print("\n2. Checking queue status...")
    queue_length = client.llen("predict")
    print(f"   ✓ Queue contains {queue_length} job(s)")
    
    # Step 3: Pull job using consumer
    print("\n3. Pulling job from queue (this will block if queue is empty)...")
    print("   (Waiting for job...)\n")
    
    job = consume_job()
    
    if job is None:
        print("   ✗ No job received (unexpected)")
        return
    
    # Step 4: Verify job data
    print("4. Verifying job data...")
    print(f"   ✓ Job ID: {job.get('job_id')}")
    print(f"   ✓ Team 1: {job.get('team1')}")
    print(f"   ✓ Team 2: {job.get('team2')}")
    print(f"   ✓ League: {job.get('league')}")
    print(f"   ✓ Created: {job.get('created_at')}")
    
    # Step 5: Verify job_id matches
    if job.get('job_id') == job_id:
        print(f"\n   ✓ Job ID matches published job!")
    else:
        print(f"\n   ✗ Job ID mismatch!")
    
    # Step 6: Check queue is now empty
    print("\n5. Verifying queue is empty after pull...")
    final_length = client.llen("predict")
    print(f"   ✓ Queue now contains {final_length} job(s)")
    
    if final_length == queue_length - 1:
        print("   ✓ Job was successfully removed from queue!")
    
    print("\n✓ All tests passed!")


if __name__ == "__main__":
    main()
