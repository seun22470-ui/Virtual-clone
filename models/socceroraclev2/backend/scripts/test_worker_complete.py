# Test script for complete worker flow

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.queue.job_publisher import publish_prediction_job
from app.queue.redis_client import get_redis_client


def main():
    print("Testing complete worker flow...\n")
    
    # Step 1: Publish a job
    print("1. Publishing a job...")
    job_id = publish_prediction_job(
        team1="Manchester United",
        team2="Liverpool",
        league="Premier League"
    )
    print(f"   ✓ Job published with ID: {job_id}")
    print(f"   → Worker should pick this up automatically\n")
    
    # Step 2: Wait a moment (give worker time to process)
    print("2. Waiting for worker to process job...")
    print("   (Run worker in another terminal: python3 -m app.workers.prediction_worker)")
    print("   (Press Enter after worker completes the job)")
    input()
    
    # Step 3: Check if result is stored in Redis
    print("\n3. Checking if result is stored in Redis...")
    client = get_redis_client()
    result_key = f"result:{job_id}"
    result_json = client.get(result_key)
    
    if result_json is None:
        print("   ✗ Result not found in Redis")
        print("   → Worker may not have processed the job yet")
        return
    
    # Step 4: Parse and display result
    print("   ✓ Result found in Redis!")
    result = json.loads(result_json)
    
    print("\n4. Result details:")
    print(f"   Job ID: {result.get('job_id')}")
    print(f"   Match: {result.get('team1')} vs {result.get('team2')}")
    print(f"   League: {result.get('league')}")
    print(f"   Status: {result.get('status')}")
    print(f"   Completed at: {result.get('completed_at')}")
    print(f"   Predictions: {result.get('predictions')}")
    
    # Step 5: Check TTL
    ttl = client.ttl(result_key)
    print(f"\n5. Result TTL: {ttl} seconds (will expire in {ttl // 60} minutes)")
    
    print("\n✓ Complete worker flow test passed!")


if __name__ == "__main__":
    main()
