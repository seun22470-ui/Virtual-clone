"""
Configuration file for Basketball Betting Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# API-Basketball Configuration (Free tier: 100 requests/day)
API_BASKETBALL_KEY = os.getenv('API_BASKETBALL_KEY', 'YOUR_API_BASKETBALL_KEY')
API_BASKETBALL_URL = "https://v1.basketball.api-sports.io"
RAPIDAPI_HOST = "api-basketball.p.rapidapi.com"

# SportyBet Configuration
SPORTYBET_BASE_URL = "https://www.sportybet.com/ng"
SPORTYBET_API_URL = "https://www.sportybet.com/api/ng"

# FlashScore Configuration
FLASHSCORE_BASE_URL = "https://www.flashscore.com"
FLASHSCORE_BASKETBALL_URL = "https://www.flashscore.com/basketball"

# Bet Types for Over/Under
BET_TYPES = {
    "over_under_fulltime": 4,  # Over/Under
    "over_under_halftime": 5,  # Over/Under 1st Half
    "over_under_quarter": 16,  # Over/Under 1st Qtr
}

# Supported Leagues (with their API-Basketball IDs)
SUPPORTED_LEAGUES = {
    "NBA": 12,
    "Euroleague": 117,
    "NCAA": 116,
    "Eurocup": 194,
    "Liga ACB": 132,
    "Serie A": 134,
    "BBL": 130,
    "NBB": 141,
    "Pro A": 138,
    "KBL": 155,
    "LNB": 142,
}

# Bookmaker IDs
BOOKMAKERS = {
    "Bet365": 4,
    "Bwin": 1,
    "1xBet": 3,
    "Pinnacle": 12,
}

# Prediction thresholds
PREDICTION_CONFIDENCE_THRESHOLD = 0.65

# Database configuration (using SQLite for simplicity)
DATABASE_FILE = "basketball_bot.db"
