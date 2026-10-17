"""
PCA model training for player embeddings.
Trains position-specific PCA models for dimensionality reduction.
"""
import json
import pickle
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path
import numpy as np
from sklearn.decomposition import PCA

from .config import (
    EMBEDDING_CONFIG,
    MODELS_DIR,
    OUTFIELD_FEATURE_NAMES,
    GOALKEEPER_FEATURE_NAMES
)


class PositionPCATrainer:
    """Trains PCA models for each position."""
    
    def __init__(self):
        self.trained_models = {}
        self.metadata = {}
    
    def group_by_position(self, players_data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group players by position.
        
        Args:
            players_data: List of player data dicts
            
        Returns:
            Dict mapping position to list of players
        """
        position_groups = {
            "Attacker": [],
            "Midfielder": [],
            "Defender": [],
            "Goalkeeper": []
        }
        
        for player in players_data:
            position = player.get('position')
            if position in position_groups:
                position_groups[position].append(player)
        
        return position_groups
    
    def prepare_feature_matrix(self, players: List[Dict], position: str) -> Tuple[np.ndarray, List[str]]:
        """
        Stack player feature vectors into a matrix.
        
        Args:
            players: List of player dicts
            position: Position name
            
        Returns:
            Tuple of (feature_matrix, feature_names)
        """
        feature_vectors = []
        
        for player in players:
            features = player.get('embedding_raw_17d', [])
            if features:
                feature_vectors.append(features)
        
        X = np.array(feature_vectors)
        
        # Get feature names
        if position == "Goalkeeper":
            feature_names = GOALKEEPER_FEATURE_NAMES
        else:
            feature_names = OUTFIELD_FEATURE_NAMES
        
        return X, feature_names
    
    def train_pca(self, position: str, players: List[Dict]) -> Tuple[PCA, Dict]:
        """
        Train PCA model for a specific position.
        
        Args:
            position: Position name
            players: List of players for this position
            
        Returns:
            Tuple of (trained_pca_model, metadata_dict)
        """
        print(f"\n🔧 Training PCA for {position}s...")
        print(f"   Players: {len(players)}")
        
        # Get config for this position
        config = EMBEDDING_CONFIG[position]
        n_components = config['n_components']
        
        # Prepare feature matrix
        X, feature_names = self.prepare_feature_matrix(players, position)
        
        print(f"   Features: {X.shape[1]}")
        print(f"   Target components: {n_components}")
        
        # Handle case where n_components > n_samples
        actual_n_components = min(n_components, X.shape[0], X.shape[1])
        if actual_n_components < n_components:
            print(f"   ⚠️  Adjusting components to {actual_n_components} (limited by sample size)")
        
        # Train PCA
        pca = PCA(n_components=actual_n_components)
        pca.fit(X)
        
        # Calculate variance metrics
        explained_variance_ratio = pca.explained_variance_ratio_.tolist()
        cumulative_variance = np.cumsum(explained_variance_ratio).tolist()
        total_variance = sum(explained_variance_ratio)
        
        # Convert NaN to None for JSON serialization
        if np.isnan(total_variance):
            total_variance = None
            explained_variance_ratio = [None if np.isnan(x) else x for x in explained_variance_ratio]
            cumulative_variance = [None if np.isnan(x) else x for x in cumulative_variance]
        
        print(f"   ✅ Model trained")
        if total_variance is not None:
            print(f"   📊 Explained variance: {total_variance*100:.1f}%")
            # Show individual component contributions
            print(f"   📊 Component breakdown:")
            for i, var in enumerate(explained_variance_ratio[:min(5, len(explained_variance_ratio))]):
                if var is not None:
                    print(f"      PC{i+1}: {var*100:.1f}%")
        else:
            print(f"   📊 Explained variance: null (insufficient samples)")
        print(f"   📊 Components: {actual_n_components} (target: {n_components})")
        
        # Create metadata
        metadata = {
            "position": position,
            "n_components": actual_n_components,
            "n_features_in": X.shape[1],
            "n_samples_trained": X.shape[0],
            "explained_variance_ratio": explained_variance_ratio,
            "cumulative_variance": cumulative_variance,
            "total_variance_explained": total_variance,
            "feature_names": feature_names,
            "trained_on": datetime.now().isoformat(),
            "model_version": f"pca_{position.lower()}_v1"
        }
        
        # Show top components
        if total_variance is not None and len(cumulative_variance) > 0:
            top_idx = min(2, len(cumulative_variance)-1)
            if cumulative_variance[top_idx] is not None:
                print(f"   📊 Top 3 components explain: {cumulative_variance[top_idx]*100:.1f}%")
        
        return pca, metadata
    
    def save_model(self, position: str, pca: PCA, metadata: Dict):
        """
        Save PCA model and metadata to disk.
        
        Args:
            position: Position name
            pca: Trained PCA model
            metadata: Model metadata
        """
        # Save model
        model_filename = f"pca_{position.lower()}.pkl"
        model_path = MODELS_DIR / model_filename
        
        with open(model_path, 'wb') as f:
            pickle.dump(pca, f)
        
        print(f"   💾 Saved model: {model_filename}")
        
        # Save metadata
        metadata_filename = f"pca_{position.lower()}_metadata.json"
        metadata_path = MODELS_DIR / metadata_filename
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"   💾 Saved metadata: {metadata_filename}")
    
    def train_all_positions(self, players_data: List[Dict]) -> Dict:
        """
        Train PCA models for all positions with players.
        
        Args:
            players_data: List of all player data
            
        Returns:
            Dict with training results
        """
        print("\n" + "="*60)
        print("STEP 2A: TRAINING PCA MODELS")
        print("="*60)
        
        # Group by position
        position_groups = self.group_by_position(players_data)
        
        results = {
            "models_trained": [],
            "metadata": {}
        }
        
        # Train for each position that has players
        for position, players in position_groups.items():
            if len(players) == 0:
                print(f"\n⏭️  Skipping {position} (no players)")
                continue
            
            # Train PCA
            pca, metadata = self.train_pca(position, players)
            
            # Save model
            self.save_model(position, pca, metadata)
            
            # Store results
            self.trained_models[position] = pca
            self.metadata[position] = metadata
            results["models_trained"].append(position)
            results["metadata"][position] = metadata
        
        print("\n" + "="*60)
        print(f"✅ PCA Training Complete!")
        print(f"   Models trained: {len(results['models_trained'])}")
        print(f"   Positions: {', '.join(results['models_trained'])}")
        
        # Show summary of each position
        print(f"\n   Summary:")
        for position in results["models_trained"]:
            meta = results["metadata"][position]
            var = meta.get("total_variance_explained")
            if var is not None:
                print(f"   - {position}: {meta['n_samples_trained']} players → {meta['n_components']}D (variance: {var*100:.1f}%)")
            else:
                print(f"   - {position}: {meta['n_samples_trained']} players → {meta['n_components']}D (variance: null)")
        
        print("="*60)
        
        return results


def train_pca_models(players_data: List[Dict]) -> Dict:
    """
    Main function to train all PCA models.
    
    Args:
        players_data: List of player data from collected_features.json
        
    Returns:
        Dict with training results
    """
    trainer = PositionPCATrainer()
    return trainer.train_all_positions(players_data)
