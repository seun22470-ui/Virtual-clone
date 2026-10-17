"""
Database module for Basketball Betting Bot
Handles user preferences, prediction history, and betting tracking
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import os

@dataclass
class UserPreferences:
    """User preferences and settings"""
    user_id: int
    username: str
    default_league: str = "NBA"
    odds_format: str = "decimal"  # decimal or american
    notifications_enabled: bool = True
    min_confidence: float = 0.65
    created_at: str = None
    updated_at: str = None

@dataclass
class PredictionHistory:
    """Store prediction results for tracking"""
    id: int
    user_id: int
    match_id: str
    home_team: str
    away_team: str
    prediction: str  # OVER or UNDER
    line: float
    projected_total: float
    confidence: float
    actual_result: str = None  # OVER, UNDER, or PUSH
    actual_total: float = None
    correct: bool = None
    created_at: str = None
    settled_at: str = None

@dataclass
class TrackedBet:
    """User's tracked bets"""
    id: int
    user_id: int
    booking_code: str
    selections: str  # JSON string
    total_odds: float
    stake: float
    potential_win: float
    status: str = "pending"  # pending, won, lost
    created_at: str = None
    settled_at: str = None


class Database:
    """SQLite database handler"""
    
    def __init__(self, db_file: str = "basketball_bot.db"):
        self.db_file = db_file
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                default_league TEXT DEFAULT 'NBA',
                odds_format TEXT DEFAULT 'decimal',
                notifications_enabled INTEGER DEFAULT 1,
                min_confidence REAL DEFAULT 0.65,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Prediction history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                match_id TEXT,
                home_team TEXT,
                away_team TEXT,
                prediction TEXT,
                line REAL,
                projected_total REAL,
                confidence REAL,
                actual_result TEXT,
                actual_total REAL,
                correct INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                settled_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Tracked bets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracked_bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                booking_code TEXT,
                selections TEXT,
                total_odds REAL,
                stake REAL,
                potential_win REAL,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                settled_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions(match_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bets_user ON tracked_bets(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bets_code ON tracked_bets(booking_code)')
        
        conn.commit()
        conn.close()
    
    # User methods
    def get_user(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return UserPreferences(
                user_id=row['user_id'],
                username=row['username'],
                default_league=row['default_league'],
                odds_format=row['odds_format'],
                notifications_enabled=bool(row['notifications_enabled']),
                min_confidence=row['min_confidence'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        return None
    
    def create_user(self, user_id: int, username: str) -> UserPreferences:
        """Create new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (user_id, username)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                updated_at = CURRENT_TIMESTAMP
        ''', (user_id, username))
        
        conn.commit()
        conn.close()
        
        return self.get_user(user_id)
    
    def update_user_preferences(self, user_id: int, **kwargs) -> Optional[UserPreferences]:
        """Update user preferences"""
        allowed_fields = ['default_league', 'odds_format', 
                         'notifications_enabled', 'min_confidence']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [user_id]
        
        cursor.execute(f'''
            UPDATE users 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', values)
        
        conn.commit()
        conn.close()
        
        return self.get_user(user_id)
    
    # Prediction methods
    def save_prediction(self, user_id: int, match_id: str, home_team: str,
                       away_team: str, prediction: str, line: float,
                       projected_total: float, confidence: float) -> int:
        """Save a prediction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions 
            (user_id, match_id, home_team, away_team, prediction, 
             line, projected_total, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, match_id, home_team, away_team, prediction,
              line, projected_total, confidence))
        
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return prediction_id
    
    def get_user_predictions(self, user_id: int, limit: int = 50) -> List[PredictionHistory]:
        """Get user's prediction history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM predictions 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        predictions = []
        for row in rows:
            predictions.append(PredictionHistory(
                id=row['id'],
                user_id=row['user_id'],
                match_id=row['match_id'],
                home_team=row['home_team'],
                away_team=row['away_team'],
                prediction=row['prediction'],
                line=row['line'],
                projected_total=row['projected_total'],
                confidence=row['confidence'],
                actual_result=row['actual_result'],
                actual_total=row['actual_total'],
                correct=bool(row['correct']) if row['correct'] is not None else None,
                created_at=row['created_at'],
                settled_at=row['settled_at']
            ))
        
        return predictions
    
    def settle_prediction(self, prediction_id: int, actual_total: float) -> bool:
        """Settle a prediction with actual result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get prediction details
        cursor.execute('SELECT * FROM predictions WHERE id = ?', (prediction_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
        
        line = row['line']
        prediction = row['prediction']
        
        # Determine actual result
        if actual_total > line:
            actual_result = "OVER"
        elif actual_total < line:
            actual_result = "UNDER"
        else:
            actual_result = "PUSH"
        
        correct = (prediction == actual_result) or (actual_result == "PUSH")
        
        cursor.execute('''
            UPDATE predictions 
            SET actual_result = ?, actual_total = ?, correct = ?, settled_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (actual_result, actual_total, int(correct), prediction_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_prediction_accuracy(self, user_id: int) -> Dict:
        """Get user's prediction accuracy stats"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as correct,
                AVG(confidence) as avg_confidence
            FROM predictions 
            WHERE user_id = ? AND correct IS NOT NULL
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        total = row['total'] or 0
        correct = row['correct'] or 0
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy': round(accuracy, 2),
            'avg_confidence': round(row['avg_confidence'] or 0, 2)
        }
    
    # Bet tracking methods
    def track_bet(self, user_id: int, booking_code: str, 
                  selections: List[Dict], total_odds: float,
                  stake: float = 0) -> int:
        """Track a new bet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        potential_win = stake * total_odds if stake > 0 else 0
        
        cursor.execute('''
            INSERT INTO tracked_bets 
            (user_id, booking_code, selections, total_odds, stake, potential_win)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, booking_code, json.dumps(selections), 
              total_odds, stake, potential_win))
        
        bet_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return bet_id
    
    def get_tracked_bets(self, user_id: int, status: str = None) -> List[TrackedBet]:
        """Get user's tracked bets"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM tracked_bets 
                WHERE user_id = ? AND status = ?
                ORDER BY created_at DESC
            ''', (user_id, status))
        else:
            cursor.execute('''
                SELECT * FROM tracked_bets 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        bets = []
        for row in rows:
            bets.append(TrackedBet(
                id=row['id'],
                user_id=row['user_id'],
                booking_code=row['booking_code'],
                selections=row['selections'],
                total_odds=row['total_odds'],
                stake=row['stake'],
                potential_win=row['potential_win'],
                status=row['status'],
                created_at=row['created_at'],
                settled_at=row['settled_at']
            ))
        
        return bets
    
    def update_bet_status(self, bet_id: int, status: str) -> bool:
        """Update bet status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tracked_bets 
            SET status = ?, settled_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, bet_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_bet_stats(self, user_id: int) -> Dict:
        """Get user's betting statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_bets,
                SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as won,
                SUM(CASE WHEN status = 'lost' THEN 1 ELSE 0 END) as lost,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'won' THEN potential_win ELSE 0 END) as total_won,
                SUM(CASE WHEN status = 'lost' THEN stake ELSE 0 END) as total_lost
            FROM tracked_bets 
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        total = row['total_bets'] or 0
        won = row['won'] or 0
        win_rate = (won / total * 100) if total > 0 else 0
        
        return {
            'total_bets': total,
            'won': won,
            'lost': row['lost'] or 0,
            'pending': row['pending'] or 0,
            'win_rate': round(win_rate, 2),
            'total_won': round(row['total_won'] or 0, 2),
            'total_lost': round(row['total_lost'] or 0, 2),
            'profit': round((row['total_won'] or 0) - (row['total_lost'] or 0), 2)
        }


# Global database instance
db = Database()
