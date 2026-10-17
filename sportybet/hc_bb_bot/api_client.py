"""
API Client for Basketball Data
Handles all interactions with API-Basketball (free tier)
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import config

class BasketballAPIClient:
    """Client for API-Basketball (API-Sports)"""
    
    def __init__(self):
        self.api_key = config.API_BASKETBALL_KEY
        self.base_url = config.API_BASKETBALL_URL
        self.headers = {
            'x-rapidapi-host': config.RAPIDAPI_HOST,
            'x-rapidapi-key': self.api_key
        }
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {e}")
            return {"errors": [str(e)], "response": []}
    
    def get_games(self, date: str = None, league: int = None, 
                  season: str = None, team: int = None) -> List[Dict]:
        """
        Get games/fixtures for a specific date, league, or team
        
        Args:
            date: Date in YYYY-MM-DD format
            league: League ID
            season: Season (e.g., "2023-2024")
            team: Team ID
        """
        params = {}
        if date:
            params['date'] = date
        if league:
            params['league'] = league
        if season:
            params['season'] = season
        if team:
            params['team'] = team
            
        data = self._make_request('games', params)
        return data.get('response', [])
    
    def get_live_games(self) -> List[Dict]:
        """Get currently live games"""
        # Get today's games and filter by live status
        today = datetime.now().strftime('%Y-%m-%d')
        games = self.get_games(date=today)
        live_statuses = ['Q1', 'Q2', 'Q3', 'Q4', 'OT', 'BT', 'HT']
        return [g for g in games if g.get('status', {}).get('short') in live_statuses]
    
    def get_game_statistics(self, game_id: int) -> List[Dict]:
        """Get detailed statistics for a specific game"""
        params = {'id': game_id}
        data = self._make_request('games/statistics/teams', params)
        return data.get('response', [])
    
    def get_team_statistics(self, team_id: int, season: str, league: int) -> Dict:
        """Get team statistics for a season"""
        params = {
            'team': team_id,
            'season': season,
            'league': league
        }
        data = self._make_request('teams/statistics', params)
        return data.get('response', {})
    
    def get_odds(self, game_id: int = None, league_id: int = None, 
                 bet_id: int = None, bookmaker_id: int = None) -> List[Dict]:
        """
        Get odds for games
        
        Args:
            game_id: Specific game ID
            league_id: League ID
            bet_id: Bet type ID (4=Over/Under FT, 5=Over/Under HT)
            bookmaker_id: Bookmaker ID
        """
        params = {}
        if game_id:
            params['game'] = game_id
        if league_id:
            params['league'] = league_id
        if bet_id:
            params['bet'] = bet_id
        if bookmaker_id:
            params['bookmaker'] = bookmaker_id
            
        data = self._make_request('odds', params)
        return data.get('response', [])
    
    def get_leagues(self) -> List[Dict]:
        """Get all available leagues"""
        data = self._make_request('leagues')
        return data.get('response', [])
    
    def get_teams(self, league_id: int, season: str) -> List[Dict]:
        """Get teams in a league"""
        params = {
            'league': league_id,
            'season': season
        }
        data = self._make_request('teams', params)
        return data.get('response', [])
    
    def get_h2h(self, team1_id: int, team2_id: int) -> List[Dict]:
        """Get head-to-head matches between two teams"""
        params = {
            'h2h': f"{team1_id}-{team2_id}"
        }
        data = self._make_request('games', params)
        return data.get('response', [])
    
    def get_bet_types(self) -> List[Dict]:
        """Get all available bet types"""
        data = self._make_request('bets')
        return data.get('response', [])
    
    def get_bookmakers(self) -> List[Dict]:
        """Get all available bookmakers"""
        data = self._make_request('bookmakers')
        return data.get('response', [])


class PredictionEngine:
    """Engine for predicting HT/FT over/under outcomes"""
    
    def __init__(self, api_client: BasketballAPIClient):
        self.api = api_client
    
    def calculate_team_scoring_avg(self, team_id: int, league_id: int, 
                                    season: str, last_n_games: int = 10) -> Dict:
        """Calculate team's scoring averages from recent games"""
        games = self.api.get_games(league=league_id, season=season)
        
        team_games = []
        for game in games:
            if game['status']['short'] != 'FT':
                continue
                
            if game['teams']['home']['id'] == team_id:
                team_games.append({
                    'points_for': game['scores']['home']['total'],
                    'points_against': game['scores']['away']['total'],
                    'home': True
                })
            elif game['teams']['away']['id'] == team_id:
                team_games.append({
                    'points_for': game['scores']['away']['total'],
                    'points_against': game['scores']['home']['total'],
                    'home': False
                })
        
        # Sort by date and take last N games
        team_games = team_games[-last_n_games:]
        
        if not team_games:
            return None
        
        avg_points_for = sum(g['points_for'] for g in team_games) / len(team_games)
        avg_points_against = sum(g['points_against'] for g in team_games) / len(team_games)
        avg_total = avg_points_for + avg_points_against
        
        return {
            'avg_points_for': round(avg_points_for, 2),
            'avg_points_against': round(avg_points_against, 2),
            'avg_total': round(avg_total, 2),
            'games_analyzed': len(team_games)
        }
    
    def predict_over_under(self, home_team_id: int, away_team_id: int, 
                          league_id: int, season: str, line: float) -> Dict:
        """
        Predict over/under for a matchup
        
        Returns prediction with confidence score
        """
        # Get team statistics
        home_stats = self.calculate_team_scoring_avg(home_team_id, league_id, season)
        away_stats = self.calculate_team_scoring_avg(away_team_id, league_id, season)
        
        if not home_stats or not away_stats:
            return None
        
        # Calculate projected total
        projected_total = (home_stats['avg_points_for'] + away_stats['avg_points_for'] + 
                          home_stats['avg_points_against'] + away_stats['avg_points_against']) / 2
        
        # Calculate confidence based on consistency (using standard deviation would be better)
        diff = abs(projected_total - line)
        confidence = min(0.95, 0.5 + (diff / line) * 0.5)
        
        recommendation = "OVER" if projected_total > line else "UNDER"
        
        return {
            'projected_total': round(projected_total, 2),
            'line': line,
            'recommendation': recommendation,
            'confidence': round(confidence, 2),
            'home_team_stats': home_stats,
            'away_team_stats': away_stats
        }
    
    def analyze_matchup(self, game_id: int) -> Dict:
        """Comprehensive analysis of a matchup for betting"""
        # Get game details
        games = self.api.get_games()
        game = None
        for g in games:
            if g['id'] == game_id:
                game = g
                break
        
        if not game:
            return None
        
        home_team = game['teams']['home']
        away_team = game['teams']['away']
        league_id = game['league']['id']
        season = game['league']['season']
        
        # Get H2H history
        h2h_games = self.api.get_h2h(home_team['id'], away_team['id'])
        
        # Get odds
        odds = self.api.get_odds(game_id=game_id, bet_id=config.BET_TYPES['over_under_fulltime'])
        
        # Calculate team stats
        home_stats = self.calculate_team_scoring_avg(home_team['id'], league_id, season)
        away_stats = self.calculate_team_scoring_avg(away_team['id'], league_id, season)
        
        # Analyze H2H
        h2h_analysis = self._analyze_h2h(h2h_games, home_team['id'], away_team['id'])
        
        return {
            'game': game,
            'home_stats': home_stats,
            'away_stats': away_stats,
            'h2h_analysis': h2h_analysis,
            'odds': odds,
            'recommendation': self._generate_recommendation(home_stats, away_stats, h2h_analysis, odds)
        }
    
    def _analyze_h2h(self, games: List[Dict], home_team_id: int, away_team_id: int) -> Dict:
        """Analyze head-to-head matchups"""
        if not games:
            return None
        
        totals = []
        for game in games:
            if game['status']['short'] == 'FT':
                total = game['scores']['home']['total'] + game['scores']['away']['total']
                totals.append(total)
        
        if not totals:
            return None
        
        avg_total = sum(totals) / len(totals)
        return {
            'games_played': len(totals),
            'avg_total': round(avg_total, 2),
            'highest_total': max(totals),
            'lowest_total': min(totals)
        }
    
    def _generate_recommendation(self, home_stats: Dict, away_stats: Dict, 
                                  h2h_analysis: Dict, odds: List[Dict]) -> Dict:
        """Generate betting recommendation"""
        if not home_stats or not away_stats:
            return {'error': 'Insufficient data'}
        
        projected_total = (home_stats['avg_points_for'] + away_stats['avg_points_for'] + 
                          home_stats['avg_points_against'] + away_stats['avg_points_against']) / 2
        
        # Extract line from odds if available
        line = None
        if odds and len(odds) > 0:
            bet_values = odds[0].get('values', [])
            for val in bet_values:
                if 'handicap' in val:
                    line = float(val['handicap'])
                    break
        
        if not line:
            line = projected_total  # Use projected as line if no odds available
        
        prediction = self.predict_over_under(
            home_stats.get('team_id'), 
            away_stats.get('team_id'),
            0,  # league_id not needed here
            "",  # season not needed here
            line
        )
        
        return prediction


# Global API client instance
api_client = BasketballAPIClient()
prediction_engine = PredictionEngine(api_client)
