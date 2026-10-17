"""
FlashScore Scraper for Basketball Fixtures
Extracts fixtures data from FlashScore website
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import re
import json

class FlashScoreScraper:
    """Scraper for FlashScore basketball data"""
    
    def __init__(self):
        self.base_url = "https://www.flashscore.com/basketball"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def _get_soup(self, url: str) -> BeautifulSoup:
        """Get BeautifulSoup object from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None
    
    def get_fixtures_by_date(self, date: str = None) -> List[Dict]:
        """
        Get basketball fixtures for a specific date
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            List of fixture dictionaries
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Convert date format for URL
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%Y%m%d')
        
        url = f"{self.base_url}/?d={formatted_date}"
        soup = self._get_soup(url)
        
        if not soup:
            return []
        
        fixtures = []
        
        # Find all match containers
        match_containers = soup.find_all('div', class_='event__match')
        
        for container in match_containers:
            try:
                fixture = self._parse_fixture(container)
                if fixture:
                    fixtures.append(fixture)
            except Exception as e:
                print(f"Error parsing fixture: {e}")
                continue
        
        return fixtures
    
    def _parse_fixture(self, container) -> Dict:
        """Parse a single fixture from HTML container"""
        # Extract match ID
        match_id = container.get('id', '')
        
        # Extract teams
        home_team_elem = container.find('div', class_='event__homeParticipant')
        away_team_elem = container.find('div', class_='event__awayParticipant')
        
        if not home_team_elem or not away_team_elem:
            return None
        
        home_team = home_team_elem.get_text(strip=True)
        away_team = away_team_elem.get_text(strip=True)
        
        # Extract time
        time_elem = container.find('div', class_='event__time')
        match_time = time_elem.get_text(strip=True) if time_elem else "TBD"
        
        # Extract league/tournament
        league_elem = container.find_previous('div', class_='event__title')
        league = league_elem.get_text(strip=True) if league_elem else "Unknown"
        
        # Extract odds if available
        odds = self._extract_odds(container)
        
        return {
            'match_id': match_id,
            'home_team': home_team,
            'away_team': away_team,
            'time': match_time,
            'league': league,
            'odds': odds
        }
    
    def _extract_odds(self, container) -> Dict:
        """Extract odds from fixture container"""
        odds = {}
        
        # Try to find odds elements
        odds_elems = container.find_all('span', class_=re.compile('odds'))
        
        for elem in odds_elems:
            text = elem.get_text(strip=True)
            if text and self._is_valid_odds(text):
                odds_type = elem.get('class', ['unknown'])[-1]
                odds[odds_type] = text
        
        return odds
    
    def _is_valid_odds(self, text: str) -> bool:
        """Check if text is a valid odds value"""
        try:
            float(text.replace(',', '.'))
            return True
        except ValueError:
            return False
    
    def get_live_matches(self) -> List[Dict]:
        """Get currently live basketball matches"""
        url = f"{self.base_url}/"
        soup = self._get_soup(url)
        
        if not soup:
            return []
        
        live_matches = []
        
        # Find live match containers
        live_containers = soup.find_all('div', class_=re.compile('event__match--live'))
        
        for container in live_containers:
            try:
                match = self._parse_live_match(container)
                if match:
                    live_matches.append(match)
            except Exception as e:
                print(f"Error parsing live match: {e}")
                continue
        
        return live_matches
    
    def _parse_live_match(self, container) -> Dict:
        """Parse a live match from HTML container"""
        base_data = self._parse_fixture(container)
        
        if not base_data:
            return None
        
        # Extract live score
        home_score_elem = container.find('div', class_='event__score--home')
        away_score_elem = container.find('div', class_='event__score--away')
        
        home_score = home_score_elem.get_text(strip=True) if home_score_elem else "0"
        away_score = away_score_elem.get_text(strip=True) if away_score_elem else "0"
        
        # Extract match status/time
        status_elem = container.find('div', class_='event__stage--block')
        status = status_elem.get_text(strip=True) if status_elem else "Live"
        
        base_data.update({
            'home_score': home_score,
            'away_score': away_score,
            'status': status,
            'is_live': True
        })
        
        return base_data
    
    def get_league_fixtures(self, league_slug: str, date: str = None) -> List[Dict]:
        """
        Get fixtures for a specific league
        
        Args:
            league_slug: League identifier (e.g., 'nba', 'euroleague')
            date: Date in YYYY-MM-DD format
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%Y%m%d')
        
        url = f"{self.base_url}/{league_slug}/?d={formatted_date}"
        soup = self._get_soup(url)
        
        if not soup:
            return []
        
        fixtures = []
        match_containers = soup.find_all('div', class_='event__match')
        
        for container in match_containers:
            try:
                fixture = self._parse_fixture(container)
                if fixture:
                    fixtures.append(fixture)
            except Exception as e:
                print(f"Error parsing fixture: {e}")
                continue
        
        return fixtures
    
    def search_matches(self, team_name: str) -> List[Dict]:
        """Search for matches by team name"""
        # This would require a search endpoint or more complex scraping
        # For now, return empty list - can be implemented with Selenium for JS-heavy pages
        return []


# Alternative: Using API-FlashScore (if available) or other free APIs
class AlternativeDataSource:
    """Alternative data sources for basketball fixtures"""
    
    @staticmethod
    def get_livescore_api_fixtures(date: str = None) -> List[Dict]:
        """
        Get fixtures from SportyBet Livescore or similar
        This is a placeholder for actual implementation
        """
        # Implementation would use SportyBet's internal API if accessible
        return []
    
    @staticmethod
    def get_sportdb_fixtures(date: str = None) -> List[Dict]:
        """
        Get fixtures from SportDB API (free tier available)
        """
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"https://sportdb.dev/api/basketball/fixtures?date={date}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('fixtures', [])
            return []
        except:
            return []


# Global scraper instance
flashscore_scraper = FlashScoreScraper()
