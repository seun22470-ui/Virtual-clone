"""
Basketball Betting Analysis Telegram Bot
Main bot implementation with advanced features
"""
import logging
import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler
)

from config import TELEGRAM_BOT_TOKEN, SUPPORTED_LEAGUES, BET_TYPES
from api_client import api_client, prediction_engine
from advanced_predictions import advanced_engine
from flashscore_scraper import flashscore_scraper
from sportybet_handler import sportybet_handler, booking_formatter, BetSelection
from database import db

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when /start is issued"""
    user = update.effective_user
    
    # Create/update user in database
    db.create_user(user.id, user.username or user.first_name)
    
    welcome_message = f"""
🏀 *Welcome to Basketball Betting Bot, {user.first_name}!* 🏀

I'm your AI assistant for basketball betting analysis. I can help you with:

📊 *Features:*
• Analyze HT/FT Over/Under predictions
• Parse SportyBet booking codes
• Generate SportyBet booking codes
• View fixtures from FlashScore
• Get live match updates
• Track your betting history

🔧 *Commands:*
/start - Show this welcome message
/help - Show detailed help
/fixtures - View upcoming fixtures
/live - View live matches
/analyze - Analyze a specific match
/parse - Parse SportyBet booking code
/predict - Get HT/FT predictions
/leagues - List supported leagues
/stats - Your prediction statistics
/bestbets - Today's best betting opportunities

💡 *Quick Tips:*
• Send me a SportyBet booking code to parse it
• Use /fixtures to see today's games
• Use /predict for AI-powered predictions

⚠️ *Disclaimer:* Predictions are for educational purposes only. Bet responsibly!
    """
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message"""
    help_text = """
🏀 *Basketball Betting Bot - Help* 🏀

*📊 ANALYSIS COMMANDS:*
/analyze [match_id] - Analyze a specific match
/predict [home_team] vs [away_team] - Get prediction
/stats [team_name] - Get team statistics
/h2h [team1] vs [team2] - Head-to-head analysis
/bestbets - Today's best opportunities

*🔍 FIXTURE COMMANDS:*
/fixtures - Today's fixtures
/fixtures [YYYY-MM-DD] - Fixtures for specific date
/fixtures [league] - Fixtures for specific league
/live - Currently live matches

*🎫 BOOKING CODE COMMANDS:*
/parse [code] - Parse SportyBet booking code
/generate - Generate new booking code
/mybets - View your tracked bets

*📊 STATISTICS COMMANDS:*
/mystats - Your prediction accuracy
/leaderboard - Top predictors

*📋 INFORMATION COMMANDS:*
/leagues - List supported leagues
/odds [match_id] - Get match odds
/standings [league] - League standings
/settings - Your preferences

*💡 EXAMPLES:*
`/fixtures NBA`
`/predict Lakers vs Warriors`
`/parse ABC123XYZ`
`/analyze 12345`
`/bestbets`

*⚠️ IMPORTANT:*
• All predictions are AI-generated
• Past performance doesn't predict future results
• Bet responsibly and within your means
• 18+ only

Need more help? Use /support
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def leagues_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List supported leagues"""
    leagues_text = "🏀 *Supported Leagues:*\n\n"
    
    for league_name, league_id in SUPPORTED_LEAGUES.items():
        leagues_text += f"• *{league_name}* (ID: `{league_id}`)\n"
    
    leagues_text += "\n💡 Use league name with /fixtures command"
    
    await update.message.reply_text(leagues_text, parse_mode='Markdown')


async def fixtures_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get fixtures for a date or league"""
    args = context.args
    
    date = None
    league = None
    
    if args:
        arg = args[0]
        # Check if it's a date
        if len(arg) == 10 and arg[4] == '-' and arg[7] == '-':
            date = arg
        # Check if it's a league
        elif arg.upper() in SUPPORTED_LEAGUES:
            league = SUPPORTED_LEAGUES[arg.upper()]
        else:
            await update.message.reply_text(
                "❌ Invalid argument. Use date (YYYY-MM-DD) or league name.\n"
                "Example: /fixtures 2024-02-20 or /fixtures NBA",
                parse_mode='Markdown'
            )
            return
    
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Show loading message
    loading_msg = await update.message.reply_text("🔍 Fetching fixtures...")
    
    try:
        # Get fixtures from API
        fixtures = api_client.get_games(date=date, league=league)
        
        if not fixtures:
            # Try FlashScore as backup
            fixtures = flashscore_scraper.get_fixtures_by_date(date)
        
        if not fixtures:
            await loading_msg.edit_text(
                f"❌ No fixtures found for {date}",
                parse_mode='Markdown'
            )
            return
        
        # Format fixtures
        fixtures_text = f"🏀 *Fixtures for {date}*\n\n"
        
        for i, fixture in enumerate(fixtures[:20], 1):  # Limit to 20
            if isinstance(fixture, dict):
                if 'teams' in fixture:  # API format
                    home = fixture['teams']['home']['name']
                    away = fixture['teams']['away']['name']
                    time = fixture.get('time', 'TBD')
                    league_name = fixture['league']['name']
                    match_id = fixture['id']
                else:  # FlashScore format
                    home = fixture.get('home_team', 'TBD')
                    away = fixture.get('away_team', 'TBD')
                    time = fixture.get('time', 'TBD')
                    league_name = fixture.get('league', 'Unknown')
                    match_id = fixture.get('match_id', '')
                
                fixtures_text += (
                    f"*{i}.* {home} vs {away}\n"
                    f"    🕐 {time} | 🏆 {league_name}\n"
                    f"    🆔 `{match_id}`\n\n"
                )
        
        if len(fixtures) > 20:
            fixtures_text += f"_... and {len(fixtures) - 20} more matches_"
        
        await loading_msg.edit_text(fixtures_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error fetching fixtures: {e}")
        await loading_msg.edit_text(
            f"❌ Error fetching fixtures: {str(e)}",
            parse_mode='Markdown'
        )


async def live_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get live matches"""
    loading_msg = await update.message.reply_text("🔍 Fetching live matches...")
    
    try:
        # Get live games from API
        live_games = api_client.get_live_games()
        
        if not live_games:
            # Try FlashScore
            live_games = flashscore_scraper.get_live_matches()
        
        if not live_games:
            await loading_msg.edit_text(
                "❌ No live matches currently",
                parse_mode='Markdown'
            )
            return
        
        live_text = "🔴 *LIVE MATCHES*\n\n"
        
        for game in live_games[:15]:  # Limit to 15
            if 'teams' in game:  # API format
                home = game['teams']['home']['name']
                away = game['teams']['away']['name']
                status = game['status']['long']
                home_score = game['scores']['home']['total']
                away_score = game['scores']['away']['total']
            else:  # FlashScore format
                home = game.get('home_team', 'TBD')
                away = game.get('away_team', 'TBD')
                status = game.get('status', 'Live')
                home_score = game.get('home_score', 0)
                away_score = game.get('away_score', 0)
            
            live_text += (
                f"🏀 {home} {home_score} - {away_score} {away}\n"
                f"    ⏱️ {status}\n\n"
            )
        
        await loading_msg.edit_text(live_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error fetching live matches: {e}")
        await loading_msg.edit_text(
            f"❌ Error: {str(e)}",
            parse_mode='Markdown'
        )


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Analyze a specific match"""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a match ID\n"
            "Example: /analyze 12345\n\n"
            "Use /fixtures to find match IDs",
            parse_mode='Markdown'
        )
        return
    
    match_id = context.args[0]
    
    loading_msg = await update.message.reply_text("🔍 Analyzing match...")
    
    try:
        # Get match details
        games = api_client.get_games()
        match = None
        for g in games:
            if str(g['id']) == match_id:
                match = g
                break
        
        if not match:
            await loading_msg.edit_text(
                f"❌ Match ID {match_id} not found",
                parse_mode='Markdown'
            )
            return
        
        home_team = match['teams']['home']
        away_team = match['teams']['away']
        league_id = match['league']['id']
        season = match['league']['season']
        
        # Get advanced analysis
        prediction = advanced_engine.predict_total(
            home_team['id'], away_team['id'], 
            league_id, season
        )
        
        # Get HT prediction
        ht_prediction = advanced_engine.predict_halftime(
            home_team['id'], away_team['id'],
            league_id, season
        )
        
        # Format analysis
        analysis_text = f"""
🏀 *MATCH ANALYSIS* 🏀

*{home_team['name']} vs {away_team['name']}*
🏆 {match['league']['name']}
🕐 {match.get('time', 'TBD')} | {match['date']}

*📊 TEAM STATISTICS:*

*{home_team['name']} (Home):*
• Avg Points Scored: {prediction['team_stats']['home_avg_scored']}
• Avg Points Allowed: {prediction['team_stats']['home_avg_allowed']}

*{away_team['name']} (Away):*
• Avg Points Scored: {prediction['team_stats']['away_avg_scored']}
• Avg Points Allowed: {prediction['team_stats']['away_avg_allowed']}

*🎯 FULL GAME PREDICTION:*
• Projected Total: {prediction['projected_total']}
• Recommendation: *{prediction['recommendation']}*
• Confidence: {prediction['confidence_text']} ({prediction['confidence']*100:.0f}%)

*⏱️ HALFTIME PREDICTION:*
• Projected HT Total: {ht_prediction['projected_total']}
• Recommendation: *{ht_prediction['recommendation']}*
• Confidence: {ht_prediction['confidence_text']} ({ht_prediction['confidence']*100:.0f}%)

*📈 FACTORS:*
• Pace Factor: {prediction['factors']['pace_factor']}
• H2H Trend: {prediction['factors']['h2h_trend']}
• Offense/Defense: {prediction['factors']['offense_defense']}
"""
        
        await loading_msg.edit_text(analysis_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error analyzing match: {e}")
        await loading_msg.edit_text(
            f"❌ Error analyzing match: {str(e)}",
            parse_mode='Markdown'
        )


async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get prediction for a matchup"""
    if not context.args or 'vs' not in ' '.join(context.args).lower():
        await update.message.reply_text(
            "❌ Please provide teams in format: Team A vs Team B\n"
            "Example: /predict Lakers vs Warriors",
            parse_mode='Markdown'
        )
        return
    
    # Parse teams
    full_text = ' '.join(context.args)
    parts = full_text.lower().split('vs')
    home_team = parts[0].strip()
    away_team = parts[1].strip()
    
    loading_msg = await update.message.reply_text("🔍 Generating prediction...")
    
    try:
        # Search for teams in recent games
        today = datetime.now().strftime('%Y-%m-%d')
        games = api_client.get_games(date=today)
        
        found_match = None
        for game in games:
            home_name = game['teams']['home']['name'].lower()
            away_name = game['teams']['away']['name'].lower()
            
            if (home_team in home_name or home_team in away_name) and \
               (away_team in home_name or away_team in away_name):
                found_match = game
                break
        
        if found_match:
            # Use the found match for prediction
            home_team_name = found_match['teams']['home']['name']
            away_team_name = found_match['teams']['away']['name']
            
            prediction = advanced_engine.predict_total(
                found_match['teams']['home']['id'],
                found_match['teams']['away']['id'],
                found_match['league']['id'],
                found_match['league']['season']
            )
            
            prediction_text = f"""
🏀 *PREDICTION* 🏀

*{home_team_name} vs {away_team_name}*
🏆 {found_match['league']['name']}

*🎯 PREDICTION:*
• Projected Total: {prediction['projected_total']}
• Recommendation: *{prediction['recommendation']}*
• Confidence: {prediction['confidence_text']} ({prediction['confidence']*100:.0f}%)

*📊 KEY STATS:*
• {home_team_name} avg scored: {prediction['team_stats']['home_avg_scored']}
• {away_team_name} avg scored: {prediction['team_stats']['away_avg_scored']}

💡 Use /analyze {found_match['id']} for detailed analysis
"""
        else:
            prediction_text = f"""
🏀 *PREDICTION* 🏀

*{home_team.title()} vs {away_team.title()}*

❌ Could not find this matchup in today's fixtures.

💡 Try:
• Check team names spelling
• Use /fixtures to see available matches
• Use /analyze [match_id] for specific match
"""
        
        await loading_msg.edit_text(prediction_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        await loading_msg.edit_text(
            f"❌ Error: {str(e)}",
            parse_mode='Markdown'
        )


async def bestbets_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get today's best betting opportunities"""
    loading_msg = await update.message.reply_text("🔍 Finding best opportunities...")
    
    try:
        # Get best bets for NBA (league 12)
        best_bets = advanced_engine.get_best_bets(12, "2023-2024", min_confidence=0.65)
        
        if not best_bets:
            await loading_msg.edit_text(
                "❌ No high-confidence opportunities found today.",
                parse_mode='Markdown'
            )
            return
        
        bets_text = "🔥 *TODAY'S BEST OPPORTUNITIES* 🔥\n\n"
        
        for i, bet in enumerate(best_bets[:5], 1):
            game = bet['game']
            pred = bet['prediction']
            
            bets_text += f"""
*{i}.* {game['teams']['home']['name']} vs {game['teams']['away']['name']}
    🎯 {pred['recommendation']} {pred['line']}
    📊 Projected: {pred['projected_total']}
    ⚡ Confidence: {pred['confidence']*100:.0f}%
    🆔 `{game['id']}`
"""
        
        bets_text += "\n💡 Use /analyze [match_id] for detailed analysis"
        
        await loading_msg.edit_text(bets_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error finding best bets: {e}")
        await loading_msg.edit_text(
            f"❌ Error: {str(e)}",
            parse_mode='Markdown'
        )


async def parse_booking_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parse SportyBet booking code"""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a booking code\n"
            "Example: /parse ABC123XYZ",
            parse_mode='Markdown'
        )
        return
    
    code = context.args[0].upper().strip()
    
    loading_msg = await update.message.reply_text("🔍 Parsing booking code...")
    
    try:
        ticket = sportybet_handler.parse_booking_code(code)
        
        if not ticket or not ticket.selections:
            await loading_msg.edit_text(
                f"❌ Could not parse booking code: {code}\n\n"
                f"Please make sure:\n"
                f"• The code is correct\n"
                f"• The code hasn't expired\n"
                f"• It's a valid SportyBet code",
                parse_mode='Markdown'
            )
            return
        
        formatted = booking_formatter.format_ticket(ticket)
        
        # Track the bet for the user
        user = update.effective_user
        selections_data = [
            {
                'match': f"{s.home_team} vs {s.away_team}",
                'pick': s.selection,
                'odds': s.odds
            }
            for s in ticket.selections
        ]
        db.track_bet(user.id, code, selections_data, ticket.total_odds)
        
        await loading_msg.edit_text(formatted, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error parsing booking code: {e}")
        await loading_msg.edit_text(
            f"❌ Error parsing code: {str(e)}",
            parse_mode='Markdown'
        )


async def mybets_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's tracked bets"""
    user = update.effective_user
    
    bets = db.get_tracked_bets(user.id)
    
    if not bets:
        await update.message.reply_text(
            "📭 You haven't tracked any bets yet.\n\n"
            "Use /parse [code] to track a bet automatically!",
            parse_mode='Markdown'
        )
        return
    
    bets_text = "🎫 *YOUR TRACKED BETS*\n\n"
    
    for bet in bets[:10]:
        status_emoji = {
            'pending': '⏳',
            'won': '✅',
            'lost': '❌'
        }.get(bet.status, '⏳')
        
        bets_text += f"""
{status_emoji} *{bet.booking_code}*
   💰 Odds: {bet.total_odds}
   📊 Status: {bet.status.title()}
   🕐 {bet.created_at[:10]}
"""
    
    # Add stats
    stats = db.get_bet_stats(user.id)
    bets_text += f"""
📈 *YOUR STATS:*
• Total Bets: {stats['total_bets']}
• Win Rate: {stats['win_rate']}%
• Profit: ${stats['profit']}
"""
    
    await update.message.reply_text(bets_text, parse_mode='Markdown')


async def mystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's prediction statistics"""
    user = update.effective_user
    
    stats = db.get_prediction_accuracy(user.id)
    
    stats_text = f"""
📊 *YOUR PREDICTION STATISTICS* 📊

*📈 Accuracy:*
• Total Predictions: {stats['total_predictions']}
• Correct: {stats['correct_predictions']}
• Accuracy: {stats['accuracy']}%
• Avg Confidence: {stats['avg_confidence']*100:.0f}%

*💡 Tip:* Use /bestbets to see high-confidence opportunities!
"""
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')


async def generate_booking_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a new booking code"""
    await update.message.reply_text(
        "🎫 *Generate Booking Code*\n\n"
        "To generate a booking code, please provide selections in this format:\n\n"
        "`/generate [MatchID:Selection:Odds, MatchID:Selection:Odds, ...]`\n\n"
        "Example:\n"
        "`/generate 12345:Over 215.5:1.85, 12346:Home:1.92`\n\n"
        "Use /fixtures to find match IDs",
        parse_mode='Markdown'
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages - check if it's a booking code"""
    text = update.message.text.upper().strip()
    
    # Check if it looks like a booking code (alphanumeric, 6-12 chars)
    if re.match(r'^[A-Z0-9]{6,12}$', text):
        # Try to parse as booking code
        loading_msg = await update.message.reply_text("🔍 Checking booking code...")
        
        try:
            ticket = sportybet_handler.parse_booking_code(text)
            
            if ticket and ticket.selections:
                formatted = booking_formatter.format_ticket(ticket)
                
                # Track the bet
                user = update.effective_user
                selections_data = [
                    {
                        'match': f"{s.home_team} vs {s.away_team}",
                        'pick': s.selection,
                        'odds': s.odds
                    }
                    for s in ticket.selections
                ]
                db.track_bet(user.id, text, selections_data, ticket.total_odds)
                
                await loading_msg.edit_text(formatted, parse_mode='Markdown')
                return
            else:
                await loading_msg.delete()
                await update.message.reply_text(
                    f"'{text}' doesn't appear to be a valid booking code.\n"
                    f"Use /parse [code] to manually parse a code.",
                    parse_mode='Markdown'
                )
                return
                
        except Exception as e:
            await loading_msg.delete()
            logger.error(f"Error in text handler: {e}")
    
    # Default response
    await update.message.reply_text(
        "🤖 I didn't understand that.\n\n"
        "Send me a SportyBet booking code to parse it,\n"
        "or use /help to see available commands.",
        parse_mode='Markdown'
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred. Please try again later.",
            parse_mode='Markdown'
        )


def main() -> None:
    """Start the bot"""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("leagues", leagues_command))
    application.add_handler(CommandHandler("fixtures", fixtures_command))
    application.add_handler(CommandHandler("live", live_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(CommandHandler("predict", predict_command))
    application.add_handler(CommandHandler("bestbets", bestbets_command))
    application.add_handler(CommandHandler("parse", parse_booking_code))
    application.add_handler(CommandHandler("generate", generate_booking_code))
    application.add_handler(CommandHandler("mybets", mybets_command))
    application.add_handler(CommandHandler("mystats", mystats_command))
    
    # Add message handler for text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Run the bot
    print("🏀 Basketball Betting Bot is starting...")
    print("✅ Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
