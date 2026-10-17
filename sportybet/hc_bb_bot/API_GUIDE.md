# API Guide for Basketball Betting Bot

## 📚 APIs Used

### 1. API-Basketball (Primary Data Source)

**Website:** https://www.api-basketball.com/

**Pricing:**
- ✅ **FREE Tier:** 100 requests/day
- Pro: $10/month - 1,000 requests/day
- Ultra: $25/month - 5,000 requests/day

**Features (Free Tier):**
- ✅ Live scores (updated every 15 seconds)
- ✅ Game schedules and fixtures
- ✅ Team statistics
- ✅ Player statistics
- ✅ Pre-match odds (1-7 days before game)
- ✅ Historical data (15+ years)
- ✅ Halftime and quarter scores
- ✅ 2,000+ competitions covered

**Endpoints Used:**
- `GET /games` - Fixtures and results
- `GET /games/statistics/teams` - Team game stats
- `GET /teams/statistics` - Season statistics
- `GET /odds` - Betting odds
- `GET /bets` - Bet types (Over/Under, etc.)
- `GET /bookmakers` - Bookmaker list
- `GET /leagues` - Available leagues
- `GET /h2h` - Head-to-head history

**Bet Types for HT/FT:**
- ID 4: "Over/Under" (Fulltime)
- ID 5: "Over/Under 1st Half" (Halftime)
- ID 16: "Over/Under 1st Qtr" (Quarter)

**Registration:**
1. Go to https://www.api-basketball.com/
2. Click "Start Now"
3. Create free account
4. Get API key from dashboard
5. 100 free requests/day

---

### 2. FlashScore (Web Scraping)

**Website:** https://www.flashscore.com/basketball

**Pricing:** ✅ FREE (web scraping)

**Features:**
- ✅ Live match scores
- ✅ Fixtures by date
- ✅ League standings
- ✅ Match statistics
- ✅ Multiple leagues (NBA, Euroleague, NCAA, etc.)

**Scraping Method:**
- BeautifulSoup4
- No API key required
- Rate limiting recommended

**Endpoints:**
- `/basketball/` - All matches
- `/basketball/?d=YYYYMMDD` - Matches by date
- `/basketball/nba/` - NBA specific
- `/basketball/euroleague/` - Euroleague

---

### 3. SportyBet (Reverse Engineering)

**Website:** https://www.sportybet.com/ng

**Pricing:** ✅ FREE (uses website API)

**Features:**
- ✅ Parse booking codes
- ✅ Generate booking codes
- ✅ Extract odds
- ✅ View available matches

**API Endpoints:**
- `POST /api/ng/bookingCode/parse` - Parse code
- `POST /api/ng/bookingCode/generate` - Generate code
- `GET /api/ng/events` - Available matches

**Note:** These endpoints are reverse-engineered and may change.

---

## 🔧 Alternative Free APIs

### Option 1: SportDB (Free Sports API)

**Website:** https://sportdb.dev/

**Pricing:** ✅ FREE tier available

**Features:**
- Live scores
- Fixtures
- Standings
- Player data

### Option 2: NBA API Free Data (RapidAPI)

**Website:** https://rapidapi.com/Creativesdev/api/nba-api-free-data

**Pricing:** ✅ FREE tier available

**Features:**
- NBA specific
- Schedules
- Standings
- Player stats
- Team stats

### Option 3: SportsbookAPI

**Website:** https://sportsbookapi.com/

**Pricing:**
- ✅ FREE: 50 requests/day
- Pro: $10/month

**Features:**
- Real-time odds
- Multiple sportsbooks
- Multiple markets

---

## 📊 Data Coverage Comparison

| API | Free Tier | HT/FT Data | Odds | Live | Historical |
|-----|-----------|------------|------|------|------------|
| API-Basketball | 100/day | ✅ | ✅ | ✅ | 15+ years |
| FlashScore | Unlimited | ✅ | ❌ | ✅ | Limited |
| SportDB | 100/day | ✅ | ❌ | ✅ | Varies |
| NBA API | Varies | ✅ | ❌ | ✅ | Limited |

---

## 🚀 API Setup Instructions

### Step 1: API-Basketball

```bash
# 1. Register at https://www.api-basketball.com/
# 2. Get your API key
# 3. Add to .env file:

echo "API_BASKETBALL_KEY=your_key_here" >> .env
```

### Step 2: Telegram Bot

```bash
# 1. Message @BotFather on Telegram
# 2. Create new bot with /newbot
# 3. Copy the token
# 4. Add to .env file:

echo "TELEGRAM_BOT_TOKEN=your_token_here" >> .env
```

---

## 📈 Rate Limiting Strategy

With 100 requests/day on free tier:

```
Recommended Usage:
- Fixtures fetch: 10 requests/day
- Live scores: 20 requests/day
- Statistics: 30 requests/day
- Odds: 20 requests/day
- Predictions: 20 requests/day
```

**Optimization Tips:**
1. Cache responses (15-minute TTL)
2. Batch requests when possible
3. Use FlashScore for fixtures (no limit)
4. Prioritize live games

---

## 🔐 Security Best Practices

1. **Never commit .env file**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Rotate API keys regularly**

3. **Monitor API usage**
   - Check dashboard daily
   - Set up alerts

4. **Use environment variables**
   - Don't hardcode keys
   - Use different keys for dev/prod

---

## 🐛 Troubleshooting

### API-Basketball Errors

**Error: 429 Too Many Requests**
- Solution: Wait and retry, or upgrade plan

**Error: 401 Unauthorized**
- Solution: Check API key is correct

**Error: No data returned**
- Solution: Check parameters (date format, league ID)

### FlashScore Scraping Errors

**Error: 403 Forbidden**
- Solution: Update User-Agent header
- Add delays between requests

**Error: No matches found**
- Solution: Check date format (YYYYMMDD)
- Verify league slug

---

## 📚 Additional Resources

- [API-Basketball Docs](https://www.api-basketball.com/documentation)
- [RapidAPI Dashboard](https://rapidapi.com/developer/dashboard)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
