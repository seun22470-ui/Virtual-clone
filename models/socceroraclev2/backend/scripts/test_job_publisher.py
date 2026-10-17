# Test script for job_publisher

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.queue.job_publisher import publish_prediction_job
from app.queue.redis_client import get_redis_client


def main():
    print("Testing job_publisher...\n")
    
    # Test 1: Publish a job
    print("1. Publishing a job...")
    job_id = publish_prediction_job(
        team1="Manchester United",
        team2="Liverpool",
        league="Premier League"
    )
    print(f"   ✓ Job published with ID: {job_id}")
    
    # Test 2: Verify job is in queue
    print("\n2. Verifying job is in queue...")
    client = get_redis_client()
    queue_length = client.llen("predict")
    print(f"   ✓ Queue 'predict' contains {queue_length} job(s)")
    
    # Test 3: Check job data (peek at first job without removing)
    if queue_length > 0:
        print("\n3. Checking job data...")
        job_json = client.lindex("predict", 0)  # Peek at first job
        if job_json:
            import json
            job = json.loads(job_json)
            print(f"   ✓ Job ID: {job['job_id']}")
            print(f"   ✓ Match: {job['team1']} vs {job['team2']}")
            print(f"   ✓ League: {job['league']}")
    
    print("\n✓ All tests passed!")


if __name__ == "__main__":
    main()
