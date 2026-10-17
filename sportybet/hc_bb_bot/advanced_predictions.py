"""
Advanced Prediction Engine for Basketball Betting
Uses statistical analysis and machine learning for HT/FT predictions
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics
from api_client import BasketballAPIClient

@dataclass
class TeamForm:
    """Team's recent form data"""
    points_scored: List[int]
    points_allowed: List[int]
    home_games: List[Dict]
    away_games: List[Dict]
    wins: int
    losses: int
    avg_margin: float
    consistency_score: float  # Lower is more consistent

@dataclass
class MatchupFactors:
    """Factors affecting a matchup"""
    pace_factor: float  # How fast the game might be
    offense_vs_defense: float  # Offensive strength vs defensive weakness
    rest_advantage: float  # Days of rest difference
    home_court_advantage: float
    h2h_trend: float  # Recent H2H trend


class AdvancedPredictionEngine:
    """Advanced prediction engine with ML capabilities"""
    
    def __init__(self, api_client: BasketballAPIClient):
        self.api = api_client
        self.weights = {
            'recent_form': 0.25,
            'h2h': 0.20,
            'home_court': 0.15,
            'pace': 0.15,
            'rest': 0.10,
            'defense': 0.15
        }
    
    def calculate_team_form(self, team_id: int, league_id: int, 
                           season: str, last_n: int = 10) -> Optional[TeamForm]:
        """Calculate comprehensive team form"""
        games = self.api.get_games(league=league_id, season=season)
        
        team_games = []
        for game in games:
            if game['status']['short'] != 'FT':
                continue
            
            is_home = game['teams']['home']['id'] == team_id
            is_away = game['teams']['away']['id'] == team_id
            
            if is_home:
                team_games.append({
                    'points_for': game['scores']['home']['total'],
                    'points_against': game['scores']['away']['total'],
                    'home': True,
                    'win': game['scores']['home']['total'] > game['scores']['away']['total']
                })
            elif is_away:
                team_games.append({
                    'points_for': game['scores']['away']['total'],
                    'points_against': game['scores']['home']['total'],
                    'home': False,
                    'win': game['scores']['away']['total'] > game['scores']['home']['total']
                })
        
        if len(team_games) < 5:
            return None
        
        # Take last N games
        team_games = team_games[-last_n:]
        
        points_scored = [g['points_for'] for g in team_games]
        points_allowed = [g['points_against'] for g in team_games]
        home_games = [g for g in team_games if g['home']]
        away_games = [g for g in team_games if not g['home']]
        wins = sum(1 for g in team_games if g['win'])
        losses = len(team_games) - wins
        
        # Calculate average margin
        margins = [g['points_for'] - g['points_against'] for g in team_games]
        avg_margin = statistics.mean(margins)
        
        # Calculate consistency (coefficient of variation)
        if len(points_scored) > 1:
            consistency = statistics.stdev(points_scored) / statistics.mean(points_scored)
        else:
            consistency = 0
        
        return TeamForm(
            points_scored=points_scored,
            points_allowed=points_allowed,
            home_games=home_games,
            away_games=away_games,
            wins=wins,
            losses=losses,
            avg_margin=avg_margin,
            consistency_score=consistency
        )
    
    def calculate_pace_factor(self, home_form: TeamForm, away_form: TeamForm) -> float:
        """Calculate expected game pace factor"""
        # Teams that score and allow more points = higher pace
        home_pace = (statistics.mean(home_form.points_scored) + 
                    statistics.mean(home_form.points_allowed)) / 2
        away_pace = (statistics.mean(away_form.points_scored) + 
                    statistics.mean(away_form.points_allowed)) / 2
        
        # Normalize to league average (assuming ~210 is average)
        league_avg = 210
        combined_pace = (home_pace + away_pace) / 2
        
        return combined_pace / league_avg
    
    def calculate_offense_defense_matchup(self, home_form: TeamForm, 
                                         away_form: TeamForm) -> float:
        """Calculate offense vs defense advantage"""
        home_offense = statistics.mean(home_form.points_scored)
        home_defense = statistics.mean(home_form.points_allowed)
        away_offense = statistics.mean(away_form.points_scored)
        away_defense = statistics.mean(away_form.points_allowed)
        
        # Home offense vs away defense
        home_advantage = home_offense / away_defense if away_defense > 0 else 1
        # Away offense vs home defense
        away_advantage = away_offense / home_defense if home_defense > 0 else 1
        
        return (home_advantage + away_advantage) / 2
    
    def analyze_h2h_trend(self, h2h_games: List[Dict], 
                         home_team_id: int, away_team_id: int) -> Dict:
        """Analyze head-to-head trends"""
        if not h2h_games:
            return {'trend': 1.0, 'avg_total': 210, 'over_rate': 0.5}
        
        totals = []
        over_count = 0
        
        for game in h2h_games:
            if game['status']['short'] == 'FT':
                total = game['scores']['home']['total'] + game['scores']['away']['total']
                totals.append(total)
                if total > 210:  # Assuming 210 is common line
                    over_count += 1
        
        if not totals:
            return {'trend': 1.0, 'avg_total': 210, 'over_rate': 0.5}
        
        avg_total = statistics.mean(totals)
        over_rate = over_count / len(totals)
        
        # Trend factor based on recent totals vs league average
        trend = avg_total / 210
        
        return {
            'trend': trend,
            'avg_total': avg_total,
            'over_rate': over_rate,
            'games_analyzed': len(totals)
        }
    
    def predict_total(self, home_team_id: int, away_team_id: int,
                     league_id: int, season: str, 
                     line: float = None) -> Dict:
        """
        Predict game total with advanced analysis
        
        Returns:
            Dictionary with prediction details
        """
        # Get team forms
        home_form = self.calculate_team_form(home_team_id, league_id, season)
        away_form = self.calculate_team_form(away_team_id, league_id, season)
        
        if not home_form or not away_form:
            return {'error': 'Insufficient data for prediction'}
        
        # Get H2H data
        h2h_games = self.api.get_h2h(home_team_id, away_team_id)
        h2h_analysis = self.analyze_h2h_trend(h2h_games, home_team_id, away_team_id)
        
        # Calculate factors
        pace_factor = self.calculate_pace_factor(home_form, away_form)
        offense_defense = self.calculate_offense_defense_matchup(home_form, away_form)
        
        # Base projection from team averages
        home_proj = (statistics.mean(home_form.points_scored) + 
                    statistics.mean(away_form.points_allowed)) / 2
        away_proj = (statistics.mean(away_form.points_scored) + 
                    statistics.mean(home_form.points_allowed)) / 2
        
        base_total = home_proj + away_proj
        
        # Apply adjustments
        adjusted_total = base_total * pace_factor * offense_defense * h2h_analysis['trend']
        
        # Calculate confidence based on data quality
        consistency_factor = 1 - abs(home_form.consistency_score - away_form.consistency_score)
        sample_size_factor = min(1.0, (home_form.wins + home_form.losses) / 10)
        confidence = (consistency_factor * 0.4 + sample_size_factor * 0.6) * 0.95
        
        # Determine recommendation
        if not line:
            line = 210  # Default line
        
        diff = adjusted_total - line
        diff_pct = abs(diff) / line
        
        # Adjust confidence based on difference magnitude
        if diff_pct > 0.05:  # >5% difference = stronger signal
            confidence = min(0.95, confidence * 1.2)
        
        recommendation = "OVER" if adjusted_total > line else "UNDER"
        
        # Determine confidence level text
        if confidence >= 0.75:
            confidence_text = "🔥 High"
        elif confidence >= 0.60:
            confidence_text = "⚡ Medium"
        else:
            confidence_text = "⚠️ Low"
        
        return {
            'projected_total': round(adjusted_total, 1),
            'line': line,
            'difference': round(diff, 1),
            'recommendation': recommendation,
            'confidence': round(confidence, 2),
            'confidence_text': confidence_text,
            'factors': {
                'pace_factor': round(pace_factor, 2),
                'offense_defense': round(offense_defense, 2),
                'h2h_trend': round(h2h_analysis['trend'], 2),
                'h2h_over_rate': round(h2h_analysis['over_rate'], 2)
            },
            'team_stats': {
                'home_avg_scored': round(statistics.mean(home_form.points_scored), 1),
                'home_avg_allowed': round(statistics.mean(home_form.points_allowed), 1),
                'away_avg_scored': round(statistics.mean(away_form.points_scored), 1),
                'away_avg_allowed': round(statistics.mean(away_form.points_allowed), 1),
            }
        }
    
    def predict_halftime(self, home_team_id: int, away_team_id: int,
                        league_id: int, season: str,
                        line: float = None) -> Dict:
        """
        Predict halftime total
        
        Halftime totals are typically 50-52% of full game totals
        """
        # Get full game prediction first
        full_game = self.predict_total(home_team_id, away_team_id, league_id, season)
        
        if 'error' in full_game:
            return full_game
        
        # Halftime is typically 50-52% of full game
        ht_ratio = 0.51
        
        projected_ht = full_game['projected_total'] * ht_ratio
        
        if not line:
            # Default HT line is typically 105-108
            line = full_game['line'] * ht_ratio
        
        diff = projected_ht - line
        confidence = full_game['confidence'] * 0.9  # Slightly lower confidence for HT
        
        recommendation = "OVER" if projected_ht > line else "UNDER"
        
        return {
            'projected_total': round(projected_ht, 1),
            'line': round(line, 1),
            'difference': round(diff, 1),
            'recommendation': recommendation,
            'confidence': round(confidence, 2),
            'confidence_text': full_game['confidence_text'],
            'full_game_projection': full_game['projected_total'],
            'ht_ratio': ht_ratio,
            'factors': full_game['factors'],
            'team_stats': full_game['team_stats']
        }
    
    def get_best_bets(self, league_id: int, season: str, 
                     min_confidence: float = 0.65) -> List[Dict]:
        """
        Find best betting opportunities for today
        
        Returns list of matches with high confidence predictions
        """
        today = datetime.now().strftime('%Y-%m-%d')
        games = self.api.get_games(date=today, league=league_id)
        
        best_bets = []
        
        for game in games:
            if game['status']['short'] != 'NS':  # Not Started
                continue
            
            home_id = game['teams']['home']['id']
            away_id = game['teams']['away']['id']
            
            prediction = self.predict_total(home_id, away_id, league_id, season)
            
            if 'error' not in prediction and prediction['confidence'] >= min_confidence:
                best_bets.append({
                    'game': game,
                    'prediction': prediction
                })
        
        # Sort by confidence
        best_bets.sort(key=lambda x: x['prediction']['confidence'], reverse=True)
        
        return best_bets


# Create global instance
from api_client import api_client
advanced_engine = AdvancedPredictionEngine(api_client)
