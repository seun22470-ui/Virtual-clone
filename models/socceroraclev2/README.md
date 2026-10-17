# SoccerOracleV2

A FastAPI-based football statistics and prediction API system that provides match predictions, player statistics, team comparisons, and league standings using machine learning models.

## Features

- Match predictions using LightGBM models
- Player statistics and similarity analysis
- Team head-to-head statistics and recent matches
- League standings
- Asynchronous prediction processing with Redis queue

## Prerequisites

- Python 3.11+
- Redis server
- PostgreSQL database (Supabase)
- Football data API key

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd SoccerOracleV2
```

2. **Set up Python environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Install and start Redis**
```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt-get install redis-server
sudo systemctl start redis
```

4. **Configure environment**
   
Create `backend/app/core/settings.py`:
```python
import os

api_key = os.getenv("API_KEY", "your_api_key")
supabase_connection_uri = os.getenv("SUPABASE_CONNECTION_URI", "postgresql://...")
```

## Running the Application

### 1. Start Redis (if not running as service)
```bash
redis-server
```

### 2. Start the API Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 3. Start the Prediction Worker (separate terminal)
```bash
cd backend
python -m app.workers.prediction_worker
```

## API Endpoints

- `GET /` - Health check
- `GET /standings/{league_name}` - Get league standings
- `POST /team_id` - Get team information
- `POST /H2H_stats` - Get head-to-head statistics
- `POST /player_id` - Get player information
- `POST /player_season_stats` - Get player season statistics
- `POST /similar` - Find similar players
- `POST /predict/match` - Queue a prediction job
- `GET /predict/result/{job_id}` - Get prediction result

See http://localhost:8000/docs for interactive API documentation.

## Machine Learning

### Train Model
```bash
cd backend
python scripts/retrain.py [improvement_threshold]
```

### Generate Player Embeddings
```bash
python scripts/collect_player_features.py
python scripts/train_and_generate_embeddings.py
python scripts/upload_to_supabase.py
```

## Project Structure

```
backend/
├── app/
│   ├── api/routes/      # API endpoints
│   ├── ml/              # ML models and training
│   ├── queue/           # Redis queue management
│   ├── workers/         # Background workers
│   └── main.py          # FastAPI app
└── scripts/             # Utility scripts
```
