"""
Player feature collection module.
Processes players through the pipeline and extracts feature vectors.
"""
import json
import csv
import time
from typing import List, Dict, Optional
from datetime import datetime

from app.ml.features.weighted_season_aggregator import fetch_weighted_player_data
from app.ml.features.stat_normalizer import normalize_stats
from app.ml.features.position_weights import (
    apply_position_weights,
    filter_excluded_features,
    get_feature_names
)
from .config import (
    COLLECTED_FEATURES_CSV,
    COLLECTED_FEATURES_JSON,
    COLLECTION_REPORT_FILE,
    API_SLEEP_SECONDS,
    API_RETRY_ATTEMPTS,
    API_RETRY_DELAY,
    OUTFIELD_FEATURE_NAMES,
    GOALKEEPER_FEATURE_NAMES
)


class PlayerFeatureCollector:
    """Collects and processes player features through the pipeline."""
    
    def __init__(self):
        self.successful_players = []
        self.failed_players = []
        self.api_calls_made = 0
        self.position_counts = {
            "Attacker": 0,
            "Midfielder": 0,
            "Defender": 0,
            "Goalkeeper": 0
        }
    
    def process_player(self, player_info: Dict) -> Optional[Dict]:
        """
        Process a single player through the feature extraction pipeline.
        
        Args:
            player_info: Dict with player_name, team_name, league_name, country
            
        Returns:
            Dict with player data and features, or None if failed
        """
        player_name = player_info.get('player_name')
        team_name = player_info.get('team_name')
        league_name = player_info.get('league_name')
        country = player_info.get('country')
        
        try:
            # Get player ID from API first
            from app.services.data_fetch.id_fetcher import get_player_id
            player_id_data = get_player_id(player_name, team_name, league_name, country, 2025)
            
            if not player_id_data:
                raise ValueError("Could not fetch player ID")
            
            player_id = player_id_data[0]  # First element is the ID
            
            # Step 1: Fetch weighted multi-season data
            weighted_data = fetch_weighted_player_data(
                player_name=player_name,
                team_name=team_name,
                league_name=league_name,
                country=country
            )
            
            # Count API calls (1-4 per player depending on valid seasons)
            if weighted_data and 'valid_seasons' in weighted_data:
                self.api_calls_made += len(weighted_data['valid_seasons'])
            
            if not weighted_data:
                raise ValueError("No valid season data found")
            
            # Extract data
            position = weighted_data.get('position')
            weighted_stats = weighted_data.get('weighted_stats')
            valid_seasons = weighted_data.get('valid_seasons', [])
            weights_used = weighted_data.get('weights_used', {})
            
            if not position or not weighted_stats:
                raise ValueError("Missing position or stats")
            
            # Step 2: Normalize stats (z-score)
            normalized_stats = normalize_stats(weighted_stats, position)
            
            # Step 3: Apply position weights
            position_weighted = apply_position_weights(normalized_stats, position)
            
            # Step 4: Filter excluded features
            filtered_features = filter_excluded_features(position_weighted)
            
            # Get feature names in sorted order
            feature_names = get_feature_names(position)
            
            # Convert to ordered list (important for PCA later)
            features_vector = [filtered_features.get(fname, 0.0) for fname in feature_names]
            
            # Store raw stats for database
            raw_data = {
                "team_name": team_name,
                "league_name": league_name,
                "country": country,
                "raw_weighted_stats": weighted_stats,
                "valid_seasons": valid_seasons,
                "weights_used": {str(k): v for k, v in weights_used.items()},  # JSON serializable
                "feature_names": feature_names
            }
            
            # Build result
            result = {
                "id": player_id,  # Add player ID from API
                "player_name": player_name,
                "team_name": team_name,
                "league_name": league_name,
                "position": position,
                "embedding_raw_17d": features_vector,
                "features_dict": filtered_features,  # Keep for debugging
                "raw_data": raw_data
            }
            
            # Update position count
            self.position_counts[position] += 1
            
            return result
            
        except Exception as e:
            error_msg = f"{player_name} ({team_name}) - {str(e)}"
            self.failed_players.append({
                "player_name": player_name,
                "team_name": team_name,
                "error": str(e)
            })
            print(f"  ❌ Error: {error_msg}")
            return None
    
    def collect_features(self, players_list: List[Dict]) -> List[Dict]:
        """
        Process all players in the list.
        
        Args:
            players_list: List of player info dicts
            
        Returns:
            List of successfully processed player data
        """
        total_players = len(players_list)
        print(f"\n🚀 Starting feature collection for {total_players} players...\n")
        
        for i, player_info in enumerate(players_list):
            player_name = player_info.get('player_name', 'Unknown')
            print(f"[{i+1}/{total_players}] Processing {player_name}...")
            
            result = self.process_player(player_info)
            
            if result:
                self.successful_players.append(result)
                print(f"  ✅ Success ({result['position']})")
            
            # Rate limiting
            if i < total_players - 1:  # Don't sleep after last player
                time.sleep(API_SLEEP_SECONDS)
        
        print(f"\n✅ Collection complete!")
        print(f"   Successful: {len(self.successful_players)}")
        print(f"   Failed: {len(self.failed_players)}")
        print(f"   API calls: {self.api_calls_made}")
        
        return self.successful_players
    
    def save_to_csv(self):
        """Save collected features to CSV file."""
        if not self.successful_players:
            print("⚠️  No data to save to CSV")
            return
        
        print(f"\n💾 Saving to CSV: {COLLECTED_FEATURES_CSV}")
        
        # Determine feature count (17 for outfield, 15 for GK)
        # For CSV, we'll use 17 columns and pad GK with 0s for missing features
        
        with open(COLLECTED_FEATURES_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            header = ['player_name', 'team_name', 'league_name', 'position']
            header.extend([f'feature_{i+1}_{name}' for i, name in enumerate(OUTFIELD_FEATURE_NAMES)])
            writer.writerow(header)
            
            # Data rows
            for player in self.successful_players:
                row = [
                    player['player_name'],
                    player['team_name'],
                    player['league_name'],
                    player['position']
                ]
                
                # Add feature values
                features = player['embedding_raw_17d']
                # Pad with zeros if needed (GK has 15, others have 17)
                while len(features) < 17:
                    features.append(0.0)
                
                row.extend(features)
                writer.writerow(row)
        
        print(f"   ✅ CSV saved: {len(self.successful_players)} players")
    
    def save_to_json(self):
        """Save collected features to JSON file."""
        if not self.successful_players:
            print("⚠️  No data to save to JSON")
            return
        
        print(f"\n💾 Saving to JSON: {COLLECTED_FEATURES_JSON}")
        
        with open(COLLECTED_FEATURES_JSON, 'w') as f:
            json.dump(self.successful_players, f, indent=2)
        
        print(f"   ✅ JSON saved: {len(self.successful_players)} players")
    
    def save_report(self):
        """Generate and save collection report."""
        print(f"\n📊 Generating report: {COLLECTION_REPORT_FILE}")
        
        report_lines = [
            "=" * 60,
            "PLAYER FEATURE COLLECTION REPORT",
            "=" * 60,
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Players Attempted: {len(self.successful_players) + len(self.failed_players)}",
            f"Successfully Processed: {len(self.successful_players)}",
            f"Failed: {len(self.failed_players)}",
            f"API Calls Made: {self.api_calls_made}",
            "",
            "POSITION BREAKDOWN:",
            f"  - Attackers: {self.position_counts['Attacker']}",
            f"  - Midfielders: {self.position_counts['Midfielder']}",
            f"  - Defenders: {self.position_counts['Defender']}",
            f"  - Goalkeepers: {self.position_counts['Goalkeeper']}",
            ""
        ]
        
        if self.failed_players:
            report_lines.append("FAILED PLAYERS:")
            for failed in self.failed_players:
                report_lines.append(f"  - {failed['player_name']} ({failed['team_name']}): {failed['error']}")
        else:
            report_lines.append("No failed players! ✅")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        
        with open(COLLECTION_REPORT_FILE, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"   ✅ Report saved")
        
        # Print summary to console
        print("\n" + "\n".join(report_lines))


def collect_player_features(players_list: List[Dict]) -> Dict:
    """
    Main function to collect player features.
    
    Args:
        players_list: List of dicts with player_name, team_name, league_name, country
        
    Returns:
        Dict with successful_players and statistics
    """
    collector = PlayerFeatureCollector()
    
    # Process all players
    successful_players = collector.collect_features(players_list)
    
    # Save outputs
    collector.save_to_csv()
    collector.save_to_json()
    collector.save_report()
    
    return {
        "successful_players": successful_players,
        "failed_players": collector.failed_players,
        "position_counts": collector.position_counts,
        "api_calls_made": collector.api_calls_made
    }
