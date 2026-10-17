# Prediction routes - API endpoints for async predictions

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.queue.job_publisher import publish_prediction_job
from app.queue.redis_client import get_redis_client
import json
from app.schemas.prediction_schema import PredictionRequest

predictions_router = APIRouter()

@predictions_router.post("/predict/match")
def create_prediction(request: PredictionRequest):
    """
    Queue a prediction job.
    
    Returns job_id immediately. Use GET /predict/result/{job_id} to retrieve results.
    """
    # Validate input
    if not request.team1 or not request.team2:
        raise HTTPException(status_code=400, detail="team1 and team2 are required")
    
    try:
        # Publish job to queue
        job_id = publish_prediction_job(
            team1=request.team1,
            team2=request.team2,
            league=request.league
        )
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Prediction job queued successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue prediction: {str(e)}")


@predictions_router.get("/predict/result/{job_id}")
def get_prediction_result(job_id: str):
    """
    Get prediction result by job_id.
    
    Returns result if completed, or status if still processing.
    """
    try:
        client = get_redis_client()
        result_key = f"result:{job_id}"
        result_json = client.get(result_key)
        
        if result_json is None:
            # Check if job might still be in queue
            queue_length = client.llen("predict")
            return {
                "job_id": job_id,
                "status": "processing",
                "message": "Job is still being processed or not found"
            }
        
        # Parse and return result
        result = json.loads(result_json)
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid result data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve result: {str(e)}")
