# Dataset builder script
import csv
import time
import os
from app.ml.features.feature_builder import build_features_and_targets

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
FEATURES_CSV = os.path.join(DATA_DIR, 'features_X.csv')
TARGETS_CSV = os.path.join(DATA_DIR, 'targets_Y.csv')


def append_to_csv(file_path, row_dict):
    """Append a single row to a CSV file."""
    with open(file_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=row_dict.keys())
        writer.writerow(row_dict)


def build_dataset(matchups: list[tuple[str, str, str, str]]):
    """
    Build dataset from a list of matchups.
    
    Args:
        matchups: List of tuples [(team1, team2, league_name, country), ...]
    """
    total = len(matchups)
    
    for i, (team1, team2, league_name, country) in enumerate(matchups):
        print(f"[{i+1}/{total}] Processing: {team1} vs {team2} ({league_name}, {country})")
        
        try:
            result = build_features_and_targets(team1, team2, league_name, country)
            
            if result is None:
                print(f"  Skipped - no data returned")
                continue
            
            append_to_csv(FEATURES_CSV, result["X"])
            append_to_csv(TARGETS_CSV, result["Y"])
            print(f"  Success")
            
        except Exception as e:
            print(f"  Error: {e}")
        
        # Rate limit: 5 second delay between calls
        if i < total - 1:
            time.sleep(6)
    
    print(f"\nDone. Processed {total} matchups.")

if __name__ == "__main__":
    matchups = [
        ("Arsenal", "Chelsea", "Premier League", "England"), #HIGH VS HIGH =====
        ("Arsenal", "Manchester City", "Premier League", "England"),
        ("Arsenal", "Aston Villa", "Premier League", "England"),
        ("Chelsea", "Manchester City", "Premier League", "England"),
        ("Chelsea", "Aston Villa", "Premier League", "England"),
        ("Chelsea", "Crystal Palace", "Premier League", "England"),
        ("Manchester City", "Aston Villa", "Premier League", "England"),
        ("Manchester City", "Crystal Palace", "Premier League", "England"),
        ("Aston Villa", "Crystal Palace", "Premier League", "England"),
        ("Aston Villa", "Brighton", "Premier League", "England"),
        ("Arsenal", "Bournemouth", "Premier League", "England"), #HIGH VS MID
        ("Chelsea", "Tottenham", "Premier League", "England"),
        ("Manchester City", "Manchester United", "Premier League", "England"),
        ("Aston Villa", "Everton", "Premier League", "England"),
        ("Crystal Palace", "Liverpool", "Premier League", "England"),
        ("Arsenal", "Brentford", "Premier League", "England"),
        ("Manchester City", "Newcastle", "Premier League", "England"),
        ("Brighton", "Manchester United", "Premier League", "England"),
        ("Brighton", "Everton", "Premier League", "England"),
        ("Crystal Palace", "Tottenham", "Premier League", "England"),
        ("Arsenal", "Leeds", "Premier League", "England"), #HIGH VS LOW
        ("Chelsea", "Burnley", "Premier League", "England"),
        ("Manchester City", "Wolves", "Premier League", "England"),
        ("Aston Villa", "West Ham", "Premier League", "England"),
        ("Crystal Palace", "Nottingham Forest", "Premier League", "England"),
        ("Brighton", "Leeds", "Premier League", "England"),
        ("Arsenal", "Burnley", "Premier League", "England"),
        ("Manchester City", "West Ham", "Premier League", "England"),
        ("Aston Villa", "Wolves", "Premier League", "England"),
        ("Chelsea", "Nottingham Forest", "Premier League", "England"),
        ("Bournemouth", "Tottenham", "Premier League", "England"), #MID VS MID
        ("Bournemouth", "Manchester United", "Premier League", "England"),
        ("Tottenham", "Manchester United", "Premier League", "England"),
        ("Everton", "Liverpool", "Premier League", "England"),
        ("Everton", "Brentford", "Premier League", "England"),
        ("Liverpool", "Brentford", "Premier League", "England"),
        ("Manchester United", "Everton", "Premier League", "England"),
        ("Tottenham", "Liverpool", "Premier League", "England"),
        ("Bournemouth", "Brentford", "Premier League", "England"),
        ("Manchester United", "Newcastle", "Premier League", "England"),
        ("Bournemouth", "West Ham", "Premier League", "England"), #MID VS LOW
        ("Tottenham", "Leeds", "Premier League", "England"),
        ("Manchester United", "Burnley", "Premier League", "England"),
        ("Everton", "Wolves", "Premier League", "England"),
        ("Liverpool", "Nottingham Forest", "Premier League", "England"),
        ("Brentford", "West Ham", "Premier League", "England"),
        ("Newcastle", "Leeds", "Premier League", "England"),
        ("Tottenham", "Wolves", "Premier League", "England"),
        ("Brentford", "Burnley", "Premier League", "England"),
        ("Everton", "Nottingham Forest", "Premier League", "England"),
        ("Nottingham Forest", "West Ham", "Premier League", "England"), #LOW VS LOW
        ("Nottingham Forest", "Leeds", "Premier League", "England"),
        ("West Ham", "Leeds", "Premier League", "England"),
        ("Nottingham Forest", "Burnley", "Premier League", "England"),
        ("West Ham", "Burnley", "Premier League", "England"),
        ("Leeds", "Burnley", "Premier League", "England"),
        ("Real Madrid", "Barcelona", "La Liga", "Spain"), #HIGH VS HIGH =====
        ("Real Madrid", "Villarreal", "La Liga", "Spain"),
        ("Real Madrid", "Atletico Madrid", "La Liga", "Spain"),
        ("Barcelona", "Villarreal", "La Liga", "Spain"),
        ("Barcelona", "Atletico Madrid", "La Liga", "Spain"),
        ("Barcelona", "Real Betis", "La Liga", "Spain"),
        ("Villarreal", "Atletico Madrid", "La Liga", "Spain"),
        ("Villarreal", "Real Betis", "La Liga", "Spain"),
        ("Atletico Madrid", "Real Betis", "La Liga", "Spain"),
        ("Atletico Madrid", "Espanyol", "La Liga", "Spain"),
        ("Real Madrid", "Athletic Club", "La Liga", "Spain"), #HIGH VS MID
        ("Barcelona", "Real Sociedad", "La Liga", "Spain"),
        ("Villarreal", "Elche", "La Liga", "Spain"),
        ("Atletico Madrid", "Sevilla", "La Liga", "Spain"),
        ("Real Betis", "Celta Vigo", "La Liga", "Spain"),
        ("Real Madrid", "Rayo Vallecano", "La Liga", "Spain"),
        ("Villarreal", "Alaves", "La Liga", "Spain"),
        ("Espanyol", "Elche", "La Liga", "Spain"),
        ("Espanyol", "Sevilla", "La Liga", "Spain"),
        ("Real Betis", "Real Sociedad", "La Liga", "Spain"),
        ("Real Madrid", "Girona", "La Liga", "Spain"), #HIGH VS LOW
        ("Barcelona", "Levante", "La Liga", "Spain"),
        ("Villarreal", "Oviedo", "La Liga", "Spain"),
        ("Atletico Madrid", "Osasuna", "La Liga", "Spain"),
        ("Real Betis", "Mallorca", "La Liga", "Spain"),
        ("Espanyol", "Girona", "La Liga", "Spain"),
        ("Real Madrid", "Levante", "La Liga", "Spain"),
        ("Villarreal", "Osasuna", "La Liga", "Spain"),
        ("Atletico Madrid", "Oviedo", "La Liga", "Spain"),
        ("Barcelona", "Mallorca", "La Liga", "Spain"),
        ("Athletic Club", "Real Sociedad", "La Liga", "Spain"), #MID VS MID
        ("Athletic Club", "Elche", "La Liga", "Spain"),
        ("Real Sociedad", "Elche", "La Liga", "Spain"),
        ("Sevilla", "Celta Vigo", "La Liga", "Spain"),
        ("Sevilla", "Rayo Vallecano", "La Liga", "Spain"),
        ("Celta Vigo", "Rayo Vallecano", "La Liga", "Spain"),
        ("Elche", "Sevilla", "La Liga", "Spain"),
        ("Real Sociedad", "Celta Vigo", "La Liga", "Spain"),
        ("Athletic Club", "Rayo Vallecano", "La Liga", "Spain"),
        ("Elche", "Alaves", "La Liga", "Spain"),
        ("Athletic Club", "Osasuna", "La Liga", "Spain"), #MID VS LOW
        ("Real Sociedad", "Girona", "La Liga", "Spain"),
        ("Elche", "Levante", "La Liga", "Spain"),
        ("Sevilla", "Oviedo", "La Liga", "Spain"),
        ("Celta Vigo", "Mallorca", "La Liga", "Spain"),
        ("Rayo Vallecano", "Osasuna", "La Liga", "Spain"),
        ("Alaves", "Girona", "La Liga", "Spain"),
        ("Real Sociedad", "Oviedo", "La Liga", "Spain"),
        ("Rayo Vallecano", "Levante", "La Liga", "Spain"),
        ("Sevilla", "Mallorca", "La Liga", "Spain"),
        ("Mallorca", "Osasuna", "La Liga", "Spain"), #LOW VS LOW
        ("Mallorca", "Girona", "La Liga", "Spain"),
        ("Osasuna", "Girona", "La Liga", "Spain"),
        ("Mallorca", "Levante", "La Liga", "Spain"),
        ("Osasuna", "Levante", "La Liga", "Spain"),
        ("Girona", "Levante", "La Liga", "Spain"),
        ("Bayern München", "RB Leipzig", "Bundesliga", "Germany"), #HIGH VS HIGH =====
        ("Bayern München", "Bayer Leverkusen", "Bundesliga", "Germany"),
        ("Bayern München", "Borussia Dortmund", "Bundesliga", "Germany"),
        ("RB Leipzig", "Bayer Leverkusen", "Bundesliga", "Germany"),
        ("RB Leipzig", "Borussia Dortmund", "Bundesliga", "Germany"),
        ("RB Leipzig", "VfB Stuttgart", "Bundesliga", "Germany"),
        ("Bayer Leverkusen", "Borussia Dortmund", "Bundesliga", "Germany"),
        ("Bayer Leverkusen", "VfB Stuttgart", "Bundesliga", "Germany"),
        ("Borussia Dortmund", "VfB Stuttgart", "Bundesliga", "Germany"),
        ("Borussia Dortmund", "Eintracht Frankfurt", "Bundesliga", "Germany"),
        ("Bayern München", "Union Berlin", "Bundesliga", "Germany"), #HIGH VS MID
        ("RB Leipzig", "Werder Bremen", "Bundesliga", "Germany"),
        ("Bayer Leverkusen", "1.FC Köln", "Bundesliga", "Germany"),
        ("Borussia Dortmund", "SC Freiburg", "Bundesliga", "Germany"),
        ("VfB Stuttgart", "Borussia Mönchengladbach", "Bundesliga", "Germany"),
        ("Bayern München", "FC Augsburg", "Bundesliga", "Germany"),
        ("Bayer Leverkusen", "Hamburger SV", "Bundesliga", "Germany"),
        ("Eintracht Frankfurt", "1.FC Köln", "Bundesliga", "Germany"),
        ("Eintracht Frankfurt", "SC Freiburg", "Bundesliga", "Germany"),
        ("VfB Stuttgart", "Werder Bremen", "Bundesliga", "Germany"),
        ("Bayern München", "1. FC Heidenheim", "Bundesliga", "Germany"), #HIGH VS LOW
        ("RB Leipzig", "FSV Mainz 05", "Bundesliga", "Germany"),
        ("Bayer Leverkusen", "FC St. Pauli", "Bundesliga", "Germany"),
        ("Borussia Dortmund", "VfL Wolfsburg", "Bundesliga", "Germany"),
        ("VfB Stuttgart", "FC St. Pauli", "Bundesliga", "Germany"),
        ("Eintracht Frankfurt", "1. FC Heidenheim", "Bundesliga", "Germany"),
        ("Bayern München", "FSV Mainz 05", "Bundesliga", "Germany"),
        ("Bayer Leverkusen", "VfL Wolfsburg", "Bundesliga", "Germany"),
        ("Borussia Dortmund", "FC St. Pauli", "Bundesliga", "Germany"),
        ("RB Leipzig", "1. FC Heidenheim", "Bundesliga", "Germany"),
        ("Union Berlin", "Werder Bremen", "Bundesliga", "Germany"), #MID VS MID
        ("Union Berlin", "1.FC Köln", "Bundesliga", "Germany"),
        ("Werder Bremen", "1.FC Köln", "Bundesliga", "Germany"),
        ("SC Freiburg", "Borussia Mönchengladbach", "Bundesliga", "Germany"),
        ("SC Freiburg", "FC Augsburg", "Bundesliga", "Germany"),
        ("Borussia Mönchengladbach", "FC Augsburg", "Bundesliga", "Germany"),
        ("1.FC Köln", "SC Freiburg", "Bundesliga", "Germany"),
        ("Werder Bremen", "Borussia Mönchengladbach", "Bundesliga", "Germany"),
        ("Union Berlin", "FC Augsburg", "Bundesliga", "Germany"),
        ("1.FC Köln", "Hamburger SV", "Bundesliga", "Germany"),
        ("Union Berlin", "VfL Wolfsburg", "Bundesliga", "Germany"), #MID VS LOW
        ("Werder Bremen", "1. FC Heidenheim", "Bundesliga", "Germany"),
        ("1.FC Köln", "FSV Mainz 05", "Bundesliga", "Germany"),
        ("SC Freiburg", "FC St. Pauli", "Bundesliga", "Germany"),
        ("Borussia Mönchengladbach", "FC St. Pauli", "Bundesliga", "Germany"),
        ("FC Augsburg", "VfL Wolfsburg", "Bundesliga", "Germany"),
        ("Hamburger SV", "1. FC Heidenheim", "Bundesliga", "Germany"),
        ("Werder Bremen", "FC St. Pauli", "Bundesliga", "Germany"),
        ("FC Augsburg", "FSV Mainz 05", "Bundesliga", "Germany"),
        ("SC Freiburg", "VfL Wolfsburg", "Bundesliga", "Germany"),
        ("FC St. Pauli", "VfL Wolfsburg", "Bundesliga", "Germany"), #LOW VS LOW
        ("FC St. Pauli", "1. FC Heidenheim", "Bundesliga", "Germany"),
        ("VfL Wolfsburg", "1. FC Heidenheim", "Bundesliga", "Germany"),
        ("FC St. Pauli", "FSV Mainz 05", "Bundesliga", "Germany"),
        ("VfL Wolfsburg", "FSV Mainz 05", "Bundesliga", "Germany"),
        ("1. FC Heidenheim", "FSV Mainz 05", "Bundesliga", "Germany"),
        ("AS Roma", "AC Milan", "Serie A", "Italy"), #HIGH VS HIGH =====
        ("AS Roma", "Napoli", "Serie A", "Italy"),
        ("AS Roma", "Inter", "Serie A", "Italy"),
        ("AC Milan", "Napoli", "Serie A", "Italy"),
        ("AC Milan", "Inter", "Serie A", "Italy"),
        ("AC Milan", "Bologna", "Serie A", "Italy"),
        ("Napoli", "Inter", "Serie A", "Italy"),
        ("Napoli", "Bologna", "Serie A", "Italy"),
        ("Inter", "Bologna", "Serie A", "Italy"),
        ("Inter", "Como", "Serie A", "Italy"),
        ("AS Roma", "Lazio", "Serie A", "Italy"), #HIGH VS MID
        ("AC Milan", "Sassuolo", "Serie A", "Italy"),
        ("Napoli", "Udinese", "Serie A", "Italy"),
        ("Inter", "Cremonese", "Serie A", "Italy"),
        ("Bologna", "Torino", "Serie A", "Italy"),
        ("AS Roma", "Atalanta", "Serie A", "Italy"),
        ("Napoli", "Cagliari", "Serie A", "Italy"),
        ("Como", "Udinese", "Serie A", "Italy"),
        ("Como", "Cremonese", "Serie A", "Italy"),
        ("Bologna", "Sassuolo", "Serie A", "Italy"),
        ("AS Roma", "Genoa", "Serie A", "Italy"), #HIGH VS LOW
        ("AC Milan", "Fiorentina", "Serie A", "Italy"),
        ("Napoli", "Verona", "Serie A", "Italy"),
        ("Inter", "Lecce", "Serie A", "Italy"),
        ("Bologna", "Pisa", "Serie A", "Italy"),
        ("Como", "Genoa", "Serie A", "Italy"),
        ("AS Roma", "Fiorentina", "Serie A", "Italy"),
        ("Napoli", "Lecce", "Serie A", "Italy"),
        ("Inter", "Verona", "Serie A", "Italy"),
        ("AC Milan", "Pisa", "Serie A", "Italy"),
        ("Lazio", "Sassuolo", "Serie A", "Italy"), #MID VS MID
        ("Lazio", "Udinese", "Serie A", "Italy"),
        ("Sassuolo", "Udinese", "Serie A", "Italy"),
        ("Cremonese", "Torino", "Serie A", "Italy"),
        ("Cremonese", "Atalanta", "Serie A", "Italy"),
        ("Torino", "Atalanta", "Serie A", "Italy"),
        ("Udinese", "Cremonese", "Serie A", "Italy"),
        ("Sassuolo", "Torino", "Serie A", "Italy"),
        ("Lazio", "Atalanta", "Serie A", "Italy"),
        ("Udinese", "Cagliari", "Serie A", "Italy"),
        ("Lazio", "Lecce", "Serie A", "Italy"), #MID VS LOW
        ("Sassuolo", "Genoa", "Serie A", "Italy"),
        ("Udinese", "Fiorentina", "Serie A", "Italy"),
        ("Cremonese", "Verona", "Serie A", "Italy"),
        ("Torino", "Pisa", "Serie A", "Italy"),
        ("Atalanta", "Lecce", "Serie A", "Italy"),
        ("Cagliari", "Genoa", "Serie A", "Italy"),
        ("Sassuolo", "Verona", "Serie A", "Italy"),
        ("Atalanta", "Fiorentina", "Serie A", "Italy"),
        ("Cremonese", "Pisa", "Serie A", "Italy"),
        ("Pisa", "Lecce", "Serie A", "Italy"), #LOW VS LOW
        ("Pisa", "Genoa", "Serie A", "Italy"),
        ("Lecce", "Genoa", "Serie A", "Italy"),
        ("Pisa", "Fiorentina", "Serie A", "Italy"),
        ("Lecce", "Fiorentina", "Serie A", "Italy"),
        ("Genoa", "Fiorentina", "Serie A", "Italy"),
        ("Paris Saint Germain", "Marseille", "Ligue 1", "France"), #HIGH VS HIGH =====
        ("Paris Saint Germain", "Lens", "Ligue 1", "France"),
        ("Paris Saint Germain", "Lille", "Ligue 1", "France"),
        ("Marseille", "Lens", "Ligue 1", "France"),
        ("Marseille", "Lille", "Ligue 1", "France"),
        ("Marseille", "Strasbourg", "Ligue 1", "France"),
        ("Lens", "Lille", "Ligue 1", "France"),
        ("Lens", "Strasbourg", "Ligue 1", "France"),
        ("Lille", "Strasbourg", "Ligue 1", "France"),
        ("Lille", "Rennes", "Ligue 1", "France"),
        ("Paris Saint Germain", "Monaco", "Ligue 1", "France"), #HIGH VS MID
        ("Marseille", "Nice", "Ligue 1", "France"),
        ("Lens", "Toulouse", "Ligue 1", "France"),
        ("Lille", "Angers", "Ligue 1", "France"),
        ("Strasbourg", "Paris FC", "Ligue 1", "France"),
        ("Paris Saint Germain", "Le Havre", "Ligue 1", "France"),
        ("Lens", "Stade Brestois 29", "Ligue 1", "France"),
        ("Rennes", "Toulouse", "Ligue 1", "France"),
        ("Rennes", "Angers", "Ligue 1", "France"),
        ("Strasbourg", "Nice", "Ligue 1", "France"),
        ("Paris Saint Germain", "Auxerre", "Ligue 1", "France"), #HIGH VS LOW
        ("Marseille", "Metz", "Ligue 1", "France"),
        ("Lens", "Lorient", "Ligue 1", "France"),
        ("Lille", "Nantes", "Ligue 1", "France"),
        ("Strasbourg", "Lorient", "Ligue 1", "France"),
        ("Rennes", "Auxerre", "Ligue 1", "France"),
        ("Paris Saint Germain", "Metz", "Ligue 1", "France"),
        ("Lens", "Nantes", "Ligue 1", "France"),
        ("Lille", "Lorient", "Ligue 1", "France"),
        ("Marseille", "Auxerre", "Ligue 1", "France"),
        ("Monaco", "Nice", "Ligue 1", "France"), #MID VS MID
        ("Monaco", "Toulouse", "Ligue 1", "France"),
        ("Nice", "Toulouse", "Ligue 1", "France"),
        ("Angers", "Paris FC", "Ligue 1", "France"),
        ("Angers", "Le Havre", "Ligue 1", "France"),
        ("Paris FC", "Le Havre", "Ligue 1", "France"),
        ("Toulouse", "Angers", "Ligue 1", "France"),
        ("Nice", "Paris FC", "Ligue 1", "France"),
        ("Monaco", "Le Havre", "Ligue 1", "France"),
        ("Toulouse", "Stade Brestois 29", "Ligue 1", "France"),
        ("Monaco", "Nantes", "Ligue 1", "France"), #MID VS LOW
        ("Nice", "Auxerre", "Ligue 1", "France"),
        ("Toulouse", "Metz", "Ligue 1", "France"),
        ("Angers", "Lorient", "Ligue 1", "France"),
        ("Paris FC", "Lorient", "Ligue 1", "France"),
        ("Le Havre", "Nantes", "Ligue 1", "France"),
        ("Stade Brestois 29", "Auxerre", "Ligue 1", "France"),
        ("Nice", "Lorient", "Ligue 1", "France"),
        ("Le Havre", "Metz", "Ligue 1", "France"),
        ("Angers", "Nantes", "Ligue 1", "France"),
        ("Lorient", "Nantes", "Ligue 1", "France"), #LOW VS LOW
        ("Lorient", "Metz", "Ligue 1", "France"),
        ("Nantes", "Metz", "Ligue 1", "France"),
        ("Lorient", "Auxerre", "Ligue 1", "France"),
        ("Nantes", "Auxerre", "Ligue 1", "France"),
    ]
    build_dataset(matchups)
