# Main feature builder

from app.services.data_process.team_cleaner import H2H_stats, latest_H2H_stats, recent_matches


def parse_stat(value):
    """Convert stat values like '45%' or '0.79' to float."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(value.replace('%', ''))
    return 0.0


def get_team_averages(matches, team_name, prefix):
    """Calculate averages from recent matches for a team."""
    stats_to_avg = [
        'Shots on Goal', 'Shots off Goal', 'Total Shots', 'Blocked Shots',
        'Shots insidebox', 'Shots outsidebox', 'Fouls', 'Corner Kicks',
        'Offsides', 'Ball Possession', 'Yellow Cards', 'Red Cards',
        'Goalkeeper Saves', 'Total passes', 'Passes accurate', 'Passes %',
        'expected_goals', 'goals_prevented'
    ]
    
    totals = {stat: 0.0 for stat in stats_to_avg}
    goals_total = 0.0
    count = len(matches)
    
    if count == 0:
        return {}
    
    for match in matches:
        team_stats = match.get(team_name, {})
        for stat in stats_to_avg:
            totals[stat] += parse_stat(team_stats.get(stat, 0))
        
        # Get goals from score
        score = match.get('score', {})
        if match.get('home_team') == team_name:
            goals_total += score.get('home', 0) or 0
        else:
            goals_total += score.get('away', 0) or 0
    
    averages = {f"{prefix}_avg_goals": goals_total / count}
    for stat in stats_to_avg:
        key = f"{prefix}_avg_{stat.lower().replace(' ', '_')}"
        averages[key] = totals[stat] / count
    
    return averages


def build_targets(match_data, team_name, prefix):
    """Extract actual stats from the target match for Y."""
    targets = {}
    team_stats = match_data.get(team_name, {})
    
    # Get goals from score
    score = match_data.get('score', {})
    if match_data.get('home_team') == team_name:
        targets[f"{prefix}_goals"] = score.get('home', 0) or 0
    else:
        targets[f"{prefix}_goals"] = score.get('away', 0) or 0
    
    targets[f"{prefix}_shots_on_goal"] = parse_stat(team_stats.get('Shots on Goal', 0))
    targets[f"{prefix}_shots_off_goal"] = parse_stat(team_stats.get('Shots off Goal', 0))
    targets[f"{prefix}_corner_kicks"] = parse_stat(team_stats.get('Corner Kicks', 0))
    targets[f"{prefix}_ball_possession"] = parse_stat(team_stats.get('Ball Possession', 0))
    targets[f"{prefix}_goalkeeper_saves"] = parse_stat(team_stats.get('Goalkeeper Saves', 0))
    targets[f"{prefix}_total_passes"] = parse_stat(team_stats.get('Total passes', 0))
    targets[f"{prefix}_total_cards"] = parse_stat(team_stats.get('Yellow Cards', 0)) + parse_stat(team_stats.get('Red Cards', 0))
    targets[f"{prefix}_goals_prevented"] = parse_stat(team_stats.get('goals_prevented', 0))
    
    return targets


def build_features_and_targets(team1, team2, league_name, country=None):
    """Build both X (features) and Y (targets) for a match between team1 and team2."""
    
    # Get recent matches for both teams (5 matches each)
    team1_matches = recent_matches(team1, league_name, 5, country)
    team2_matches = recent_matches(team2, league_name, 5, country)
    
    if not team1_matches or not team2_matches:
        return None
    
    # Split: most recent match (index 0) = Y target, rest (index 1:) = X averages
    team1_target_match = team1_matches[0]
    team2_target_match = team2_matches[0]
    team1_history = team1_matches[1:]
    team2_history = team2_matches[1:]
    
    # Get H2H stats
    h2h = H2H_stats(team1, team2, league_name, country)
    latest_h2h = latest_H2H_stats(team1, team2, league_name, country)
    
    # Build X features
    row_features = {}
    
    # Team averages from last 4 matches
    row_features.update(get_team_averages(team1_history, team1, "team1"))
    row_features.update(get_team_averages(team2_history, team2, "team2"))
    
    # H2H features
    row_features["h2h_total_games"] = h2h.get("total_games", 0)
    row_features["h2h_team1_wins"] = h2h.get("wins_team_1", 0)
    row_features["h2h_team2_wins"] = h2h.get("wins_team_2", 0)
    row_features["h2h_draws"] = h2h.get("draws", 0)
    
    # Latest H2H match stats
    if latest_h2h:
        score = latest_h2h.get("score", {})
        home_team = latest_h2h.get("home_team", "")
        
        if home_team == team1:
            t1_stats = latest_h2h.get(team1, {})
            t2_stats = latest_h2h.get(team2, {})
            row_features["latest_h2h_team1_goals"] = score.get("home", 0) or 0
            row_features["latest_h2h_team2_goals"] = score.get("away", 0) or 0
        else:
            t1_stats = latest_h2h.get(team1, {})
            t2_stats = latest_h2h.get(team2, {})
            row_features["latest_h2h_team1_goals"] = score.get("away", 0) or 0
            row_features["latest_h2h_team2_goals"] = score.get("home", 0) or 0
        
        stats_to_include = [
            'Shots on Goal', 'Shots off Goal', 'Total Shots', 'Blocked Shots',
            'Shots insidebox', 'Shots outsidebox', 'Fouls', 'Corner Kicks',
            'Offsides', 'Ball Possession', 'Yellow Cards', 'Red Cards',
            'Goalkeeper Saves', 'Total passes', 'Passes accurate', 'Passes %',
            'expected_goals', 'goals_prevented'
        ]
        
        for stat in stats_to_include:
            key1 = f"latest_h2h_team1_{stat.lower().replace(' ', '_')}"
            key2 = f"latest_h2h_team2_{stat.lower().replace(' ', '_')}"
            row_features[key1] = parse_stat(t1_stats.get(stat, 0))
            row_features[key2] = parse_stat(t2_stats.get(stat, 0))
    
    # Build Y targets from most recent match
    row_targets = {}
    row_targets.update(build_targets(team1_target_match, team1, "team1"))
    row_targets.update(build_targets(team2_target_match, team2, "team2"))
    
    return {"X": row_features, "Y": row_targets}