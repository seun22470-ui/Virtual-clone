# Virtual-Clone: Unified Multi-Bookie Virtual Football & Prediction Engine

A consolidated, production-grade repository combining virtual sports scrapers, real-time odds tracking, color result decoders, and statistical machine learning prediction engines across major African bookmakers.

---

## 📁 Repository Structure

### 1. `sportybet/` — SportyBet Virtual Football League (VFL / GoldenRace)
* **`onimix-vfl-elite`**: 690 ELITE matchup database, high-frequency historical odds and goal outcomes `[hg, ag]`.
* **`SPORTYBET-AUTO-TRADING-Bot`**: Automated trade execution and stake management scripts.
* **`SPORTYBET-WEB-SCRAPING`**: Real-time virtual odds and live market scraper.
* **`sportybet-ai-predictor`**: Neural network and trend-based scoreline predictors.
* **`sportybot`**: Telegram and headless socket notifications for goal alerts.
* **`hc_bb_bot`**: Basketball and virtual betting handicap automation.

### 2. `betpawa/` — BetPawa Virtual
* **`vpredictor`**: Last-10 match history tracker, Over/Under 2.5 probability calculations, and Flask backend.

### 3. `bet9ja/` — Bet9ja 49ja & Color Games
* **`Bet9ja-49ja-color-result-scrapper`**: Historical color draws and high-frequency result collector.
* **`49ja_game`**: Statistical pattern tracking, hot/cold number indicators, and color sequence analysis.

### 4. `multibookie/` — Multi-Bookie Scrapers (MSport, BetPawa, SportyBet, Bet9ja)
* **`bookieskit`**: Universal parser supporting BetPawa, SportyBet, MSport, Bet9ja, and Betway.
* **`oddsafrica`**: Unified bookie scraping engine located in `engine/bookie_models/`.
* **`odds-dashboard-vincenzo`** & **`odds-dashboard-alex`**: Multi-platform odds comparison interfaces.
* **`backend-railway`**: Fast background scheduler and live odds caching microservice.

### 5. `models/` — Machine Learning & Statistical Prediction Engines
* **`soccer_prediction`**: 6 core statistical models: Poisson Distribution, Dixon-Coles, Monte Carlo simulations, and Ensemble classifiers.
* **`soccer-model`**: SQLite-backed goal expectancy and probability models.
* **`socceroraclev2`**: Machine learning feature pipeline for home advantage, xG, and streak analysis.
* **`football_result_prediction`**: Random Forest and Gradient Boosting models for 1X2 and Over/Under forecasting.
* **`prophitbet-soccer-bets-predictor`**: Advanced ML bet predictor incorporating team form and weighted momentum.
* **`football-prediction-engine`**: Statistical match outcomes engine.

---

## 🚀 Web Architecture & Functional Conversion

To convert CLI / terminal loops into web-ready production services:
1. **Scrapers**: Wrapped inside asynchronous background polling tasks (Celery / FastAPi / Edge workers).
2. **Models**: Exposed via REST endpoints (`/api/predict/sportybet`, `/api/predict/betpawa`, `/api/predict/bet9ja`, `/api/predict/msport`).
3. **Frontend**: Multi-page dashboard with dedicated views per bookmaker and real-time live indicator badges.
