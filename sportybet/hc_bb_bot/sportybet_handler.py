"""
SportyBet Booking Code Handler
Parses and generates booking codes for SportyBet Nigeria
"""
import requests
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import config

@dataclass
class BetSelection:
    """Represents a single bet selection"""
    match_id: str
    home_team: str
    away_team: str
    league: str
    selection: str  # e.g., "Over 215.5", "Home", "Under 105.5"
    odds: float
    market: str  # e.g., "Over/Under", "1X2", "Handicap"
    match_time: str = ""

@dataclass
class BookingTicket:
    """Represents a complete booking ticket"""
    booking_code: str
    selections: List[BetSelection]
    total_odds: float
    created_at: str
    currency: str = "NGN"
    
    def calculate_total_odds(self) -> float:
        """Calculate total odds from selections"""
        total = 1.0
        for selection in self.selections:
            total *= selection.odds
        return round(total, 2)


class SportyBetAPI:
    """Handler for SportyBet API interactions"""
    
    def __init__(self):
        self.base_url = config.SPORTYBET_BASE_URL
        self.api_url = config.SPORTYBET_API_URL
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Origin': 'https://www.sportybet.com',
            'Referer': 'https://www.sportybet.com/ng/',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def parse_booking_code(self, code: str) -> Optional[BookingTicket]:
        """
        Parse a SportyBet booking code and return ticket details
        
        Args:
            code: SportyBet booking code (e.g., "ABC123XYZ")
        
        Returns:
            BookingTicket object or None if invalid
        """
        try:
            # SportyBet booking code endpoint
            url = f"{self.api_url}/bookingCode/parse"
            
            payload = {
                'code': code.upper().strip(),
                'source': 'mobile',
                'version': '1.0'
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_booking_response(data, code)
            else:
                # Fallback: Try alternative endpoint
                return self._parse_booking_code_alternative(code)
                
        except Exception as e:
            print(f"Error parsing booking code: {e}")
            return self._parse_booking_code_alternative(code)
    
    def _parse_booking_response(self, data: Dict, code: str) -> BookingTicket:
        """Parse booking code API response"""
        selections = []
        
        for item in data.get('selections', []):
            selection = BetSelection(
                match_id=str(item.get('matchId', '')),
                home_team=item.get('homeTeam', ''),
                away_team=item.get('awayTeam', ''),
                league=item.get('league', ''),
                selection=item.get('selection', ''),
                odds=float(item.get('odds', 1.0)),
                market=item.get('market', ''),
                match_time=item.get('matchTime', '')
            )
            selections.append(selection)
        
        total_odds = data.get('totalOdds', 0)
        if not total_odds and selections:
            total_odds = round(self._calculate_total_odds(selections), 2)
        
        return BookingTicket(
            booking_code=code.upper(),
            selections=selections,
            total_odds=total_odds,
            created_at=data.get('createdAt', datetime.now().isoformat())
        )
    
    def _parse_booking_code_alternative(self, code: str) -> Optional[BookingTicket]:
        """
        Alternative method to parse booking code using web scraping
        """
        try:
            # Load the booking code via SportyBet website
            url = f"{self.base_url}/?bookingCode={code.upper().strip()}"
            
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                # Extract betslip data from HTML
                html = response.text
                
                # Look for betslip data in script tags
                pattern = r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});'
                match = re.search(pattern, html, re.DOTALL)
                
                if match:
                    data = json.loads(match.group(1))
                    return self._extract_from_initial_state(data, code)
                
                return None
            
            return None
            
        except Exception as e:
            print(f"Alternative parsing error: {e}")
            return None
    
    def _extract_from_initial_state(self, data: Dict, code: str) -> Optional[BookingTicket]:
        """Extract booking data from initial state"""
        try:
            betslip = data.get('betslip', {})
            selections_data = betslip.get('selections', [])
            
            selections = []
            for sel in selections_data:
                selection = BetSelection(
                    match_id=str(sel.get('eventId', '')),
                    home_team=sel.get('event', {}).get('homeName', ''),
                    away_team=sel.get('event', {}).get('awayName', ''),
                    league=sel.get('event', {}).get('tournamentName', ''),
                    selection=sel.get('marketName', '') + ' - ' + sel.get('outcomeName', ''),
                    odds=float(sel.get('odds', 1.0)),
                    market=sel.get('marketName', ''),
                    match_time=sel.get('event', {}).get('startTime', '')
                )
                selections.append(selection)
            
            total_odds = self._calculate_total_odds(selections)
            
            return BookingTicket(
                booking_code=code.upper(),
                selections=selections,
                total_odds=round(total_odds, 2),
                created_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"Extract error: {e}")
            return None
    
    def generate_booking_code(self, selections: List[BetSelection]) -> Optional[str]:
        """
        Generate a SportyBet booking code from selections
        
        Args:
            selections: List of BetSelection objects
        
        Returns:
            Booking code string or None if failed
        """
        try:
            url = f"{self.api_url}/bookingCode/generate"
            
            payload = {
                'selections': [
                    {
                        'matchId': sel.match_id,
                        'market': sel.market,
                        'selection': sel.selection,
                        'odds': sel.odds
                    }
                    for sel in selections
                ],
                'source': 'mobile'
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('bookingCode')
            
            return None
            
        except Exception as e:
            print(f"Error generating booking code: {e}")
            return None
    
    def _calculate_total_odds(self, selections: List[BetSelection]) -> float:
        """Calculate total odds from selections"""
        total = 1.0
        for selection in selections:
            total *= selection.odds
        return total
    
    def get_available_matches(self, sport: str = "basketball") -> List[Dict]:
        """
        Get available matches from SportyBet
        """
        try:
            url = f"{self.api_url}/events"
            params = {
                'sport': sport,
                'marketType': 'Over/Under'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('events', [])
            
            return []
            
        except Exception as e:
            print(f"Error getting matches: {e}")
            return []


class BookingCodeFormatter:
    """Formatter for booking code display"""
    
    @staticmethod
    def format_ticket(ticket: BookingTicket) -> str:
        """Format a booking ticket for display"""
        lines = [
            "🏀 *SPORTYBET BOOKING TICKET* 🏀",
            "",
            f"📋 *Booking Code:* `{ticket.booking_code}`",
            f"💰 *Total Odds:* `{ticket.total_odds}`",
            f"📅 *Created:* {ticket.created_at}",
            "",
            "*SELECTIONS:*",
            "─" * 40,
        ]
        
        for i, sel in enumerate(ticket.selections, 1):
            lines.extend([
                f"",
                f"*{i}.* {sel.home_team} vs {sel.away_team}",
                f"   🏆 League: {sel.league}",
                f"   🎯 Pick: {sel.selection}",
                f"   📊 Odds: `{sel.odds}`",
            ])
            if sel.match_time:
                lines.append(f"   🕐 Time: {sel.match_time}")
        
        lines.extend([
            "",
            "─" * 40,
            f"*Total Selections:* {len(ticket.selections)}",
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_compact(ticket: BookingTicket) -> str:
        """Format ticket in compact mode"""
        lines = [
            f"🏀 Code: `{ticket.booking_code}` | Odds: `{ticket.total_odds}`",
            "",
        ]
        
        for i, sel in enumerate(ticket.selections, 1):
            lines.append(f"{i}. {sel.home_team[:15]} vs {sel.away_team[:15]} | {sel.selection} @ {sel.odds}")
        
        return "\n".join(lines)


# Global handler instance
sportybet_handler = SportyBetAPI()
booking_formatter = BookingCodeFormatter()
