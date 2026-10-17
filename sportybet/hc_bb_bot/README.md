# 🏀 Basketball Betting Analysis Bot

A comprehensive Telegram bot for basketball betting analysis, featuring HT/FT over/under predictions, SportyBet booking code parsing/generation, and FlashScore fixture integration.

## ✨ Features

### 📊 Analysis & Predictions
- **HT/FT Over/Under Predictions** - AI-powered predictions for halftime and fulltime totals
- **Team Statistics** - Detailed scoring averages and performance metrics
- **Head-to-Head Analysis** - Historical matchup data
- **Live Match Tracking** - Real-time scores and updates

### 🎫 SportyBet Integration
- **Parse Booking Codes** - Extract all games, picks, and odds from any SportyBet code
- **Generate Booking Codes** - Create new booking codes from your selections
- **Total Odds Calculation** - Automatic calculation of accumulated odds

### 🔍 Fixtures & Data
- **FlashScore Integration** - Access fixtures from FlashScore.com
- **Multiple Leagues** - NBA, Euroleague, NCAA, and more
- **Date Selection** - View fixtures for any date
- **Live Matches** - Currently playing games with scores

### 📱 Telegram Bot Commands
- `/start` - Welcome message and feature overview
- `/help` - Detailed help and examples
- `/fixtures [date/league]` - View upcoming fixtures
- `/live` - Currently live matches
- `/analyze [match_id]` - Detailed match analysis
- `/predict [team] vs [team]` - Get predictions
- `/parse [code]` - Parse SportyBet booking code
- `/generate` - Generate new booking code
- `/leagues` - List supported leagues

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip
- Telegram Bot Token (from @BotFather)
- API-Basketball Key (free tier available)

### Step 1: Clone/Download
```bash
cd basketball_bot
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Step 4: Get API Keys

#### Telegram Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the token to your `.env` file

#### API-Basketball Key (FREE)
1. Visit [API-Basketball](https://www.api-basketball.com/)
2. Sign up for a free account (100 requests/day)
3. Get your API key from the dashboard
4. Add to your `.env` file

### Step 5: Run the Bot
```bash
python bot.py
```

## 📋 Usage Examples

### Parse a Booking Code
```
/parse ABC123XYZ
```
**Output:**
```
🏀 SPORTYBET BOOKING TICKET 🏀

📋 Booking Code: ABC123XYZ
💰 Total Odds: 15.42

SELECTIONS:
────────────────────────

1. Lakers vs Warriors
   🏆 League: NBA
   🎯 Pick: Over 215.5
   📊 Odds: 1.85
   🕐 Time: 20:00

2. Celtics vs Heat
   🏆 League: NBA
   🎯 Pick: Home
   📊 Odds: 1.72
...
```

### View Fixtures
```
/fixtures NBA
/fixtures 2024-02-20
```

### Get Predictions
```
/predict Lakers vs Warriors
```

### Analyze Match
```
/analyze 12345
```

## 🏗️ Architecture

```
basketball_bot/
├── bot.py                 # Main Telegram bot
├── config.py              # Configuration settings
├── api_client.py          # API-Basketball integration
├── flashscore_scraper.py  # FlashScore web scraper
├── sportybet_handler.py   # SportyBet code handler
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## 🔌 APIs Used

### 1. API-Basketball (Free Tier)
- **URL:** https://www.api-basketball.com/
- **Limit:** 100 requests/day (free)
- **Features:**
  - Live scores
  - Team statistics
  - Odds data
  - Historical data
  - HT/FT data

### 2. FlashScore (Web Scraping)
- **URL:** https://www.flashscore.com/basketball
- **Method:** BeautifulSoup scraping
- **Features:**
  - Fixtures by date
  - Live matches
  - League standings

### 3. SportyBet (Reverse API)
- **URL:** https://www.sportybet.com/ng
- **Features:**
  - Booking code parsing
  - Booking code generation
  - Odds extraction

## 🎯 Prediction Algorithm

The bot uses a statistical approach for predictions:

1. **Team Scoring Averages** - Last 10 games analysis
2. **Home/Away Performance** - Venue-specific stats
3. **Head-to-Head History** - Previous matchups
4. **Confidence Scoring** - Based on data consistency

### Formula
```
Projected Total = (Home PF + Away PF + Home PA + Away PA) / 2
Confidence = 0.5 + (|Projected - Line| / Line) * 0.5
```

## ⚠️ Disclaimer

This bot is for **educational purposes only**. 

- Predictions are AI-generated and not guaranteed
- Past performance doesn't predict future results
- Always bet responsibly and within your means
- You must be 18+ to use betting services
- The creators are not responsible for any losses

## 🔧 Troubleshooting

### Bot not responding
- Check TELEGRAM_BOT_TOKEN is correct
- Ensure bot is running: `python bot.py`
- Check internet connection

### API errors
- Verify API_BASKETBALL_KEY is valid
- Check if you've exceeded 100 requests/day limit
- Wait and try again

### Booking code not parsing
- Ensure code is valid and not expired
- Check code format (6-12 alphanumeric characters)
- Try manual parsing with `/parse [code]`

## 📝 TODO

- [ ] Add more bookmakers (Bet9ja, BetKing, etc.)
- [ ] Implement machine learning predictions
- [ ] Add player props analysis
- [ ] Create web dashboard
- [ ] Add notifications for live matches
- [ ] Support for more sports

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - See LICENSE file

## 📞 Support

For support, questions, or feature requests:
- Open an issue on GitHub
- Contact: [your-email]

---

**🏀 Happy Betting! Remember to gamble responsibly! 🏀**
