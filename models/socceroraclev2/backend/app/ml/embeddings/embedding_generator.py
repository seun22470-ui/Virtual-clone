"""
Generate player embeddings using trained PCA models.
"""
import json
import pickle
from typing import Dict, List, Optional
import numpy as np

from .config import MODELS_DIR


class EmbeddingGenerator:
    """Generates embeddings for players using trained PCA models."""
    
    def __init__(self):
        self.pca_models = {}
        self.load_all_models()
    
    def load_all_models(self):
        """Load all available PCA models from disk."""
        positions = ["Attacker", "Midfielder", "Defender", "Goalkeeper"]
        
        for position in positions:
            model_filename = f"pca_{position.lower()}.pkl"
            model_path = MODELS_DIR / model_filename
            
            if model_path.exists():
                with open(model_path, 'rb') as f:
                    self.pca_models[position] = pickle.load(f)
    
    def generate_embedding(self, player_data: Dict) -> Optional[Dict]:
        """
        Generate embedding for a single player.
        
        Args:
            player_data: Player data with 17D features
            
        Returns:
            Enhanced player data with 12D embedding
        """
        position = player_data.get('position')
        
        # Check if we have a model for this position
        if position not in self.pca_models:
            print(f"   ⚠️  No PCA model for {position}")
            return None
        
        # Get PCA model
        pca = self.pca_models[position]
        
        # Get 17D features
        features_17d = player_data.get('embedding_raw_17d', [])
        if not features_17d:
            print(f"   ⚠️  No features found")
            return None
        
        # Transform to embedding
        features_array = np.array([features_17d])
        embedding_12d = pca.transform(features_array)[0].tolist()
        
        # Add embedding to player data (preserve ID from input)
        enhanced_data = player_data.copy()
        enhanced_data['embedding_12d'] = embedding_12d
        enhanced_data['model_version'] = f"pca_{position.lower()}_v1"
        
        # Add PCA metadata
        explained_variance = pca.explained_variance_ratio_.sum()
        
        # Convert NaN to None (null in JSON)
        if np.isnan(explained_variance):
            explained_variance = None
        
        enhanced_data['pca_metadata'] = {
            "n_components": len(embedding_12d),
            "explained_variance": explained_variance
        }
        
        # Ensure ID is preserved
        if 'id' not in enhanced_data and 'id' in player_data:
            enhanced_data['id'] = player_data['id']
        
        return enhanced_data
    
    def generate_all_embeddings(self, players_data: List[Dict]) -> List[Dict]:
        """
        Generate embeddings for all players.
        
        Args:
            players_data: List of player data from collected_features.json
            
        Returns:
            List of enhanced player data with embeddings
        """
        print("\n" + "="*60)
        print("STEP 2B: GENERATING EMBEDDINGS")
        print("="*60)
        
        enhanced_players = []
        total = len(players_data)
        
        for i, player_data in enumerate(players_data):
            player_name = player_data.get('player_name', 'Unknown')
            position = player_data.get('position', 'Unknown')
            
            print(f"\n[{i+1}/{total}] {player_name} ({position})")
            
            # Show raw features (first 5 for preview)
            raw_features = player_data.get('embedding_raw_17d', [])
            if raw_features:
                preview = raw_features[:min(5, len(raw_features))]
                preview_str = ", ".join([f"{v:.3f}" for v in preview])
                if len(raw_features) > 5:
                    preview_str += ", ..."
                print(f"   📥 Input features: [{preview_str}]")
            
            # Generate embedding
            enhanced = self.generate_embedding(player_data)
            
            if enhanced:
                n_features = len(enhanced.get('embedding_raw_17d', []))
                embedding_12d = enhanced.get('embedding_12d', [])
                n_embedding = len(embedding_12d)
                
                print(f"   {n_features}D → {n_embedding}D")
                
                # Show embedding values
                if len(embedding_12d) > 0:
                    # Show all values if < 10 dimensions, otherwise show first 10
                    if len(embedding_12d) <= 10:
                        embedding_str = ", ".join([f"{v:.6f}" for v in embedding_12d])
                        print(f"   📊 Embedding: [{embedding_str}]")
                    else:
                        preview = embedding_12d[:10]
                        preview_str = ", ".join([f"{v:.6f}" for v in preview])
                        print(f"   📊 Embedding (first 10): [{preview_str}, ...]")
                        print(f"   📊 Full embedding saved to JSON")
                
                print(f"   ✅ Embedding generated")
                enhanced_players.append(enhanced)
            else:
                print(f"   ❌ Failed to generate embedding")
        
        print("\n" + "="*60)
        print(f"✅ Embedding Generation Complete!")
        print(f"   Embeddings created: {len(enhanced_players)}/{total}")
        
        # Show embedding dimensions summary
        if enhanced_players:
            print(f"\n   Embedding Dimensions:")
            position_dims = {}
            for player in enhanced_players:
                pos = player.get('position')
                dim = len(player.get('embedding_12d', []))
                if pos not in position_dims:
                    position_dims[pos] = dim
            
            for position, dim in sorted(position_dims.items()):
                print(f"   - {position}: {dim}D")
        
        print("="*60)
        
        return enhanced_players


def generate_embeddings(players_data: List[Dict]) -> List[Dict]:
    """
    Main function to generate all embeddings.
    
    Args:
        players_data: List of player data
        
    Returns:
        List of enhanced player data with embeddings
    """
    generator = EmbeddingGenerator()
    return generator.generate_all_embeddings(players_data)
