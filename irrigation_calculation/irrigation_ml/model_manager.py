import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from .models import IrrigationPredictor
from .data_generator import IrrigationDataGenerator

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages model persistence, versioning, and retraining"""
    
    def __init__(self, model_dir: str = "models", data_dir: str = "data"):
        self.model_dir = model_dir
        self.data_dir = data_dir
        self.metadata_file = os.path.join(model_dir, "model_metadata.json")
        
        # Create directories
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        
        self.predictor = IrrigationPredictor(model_dir)
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load model metadata"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load metadata: {e}")
        
        return {
            "version": "1.0.0",
            "last_trained": None,
            "training_samples": 0,
            "model_performance": {},
            "retrain_threshold_days": 30,
            "min_new_samples": 100
        }
    
    def _save_metadata(self):
        """Save model metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save metadata: {e}")
    
    def should_retrain(self) -> bool:
        """Check if models should be retrained"""
        
        # Check if models exist
        if not self.predictor.is_trained:
            logger.info("Models not trained - retraining required")
            return True
        
        # Check last training date
        if self.metadata["last_trained"]:
            last_trained = datetime.fromisoformat(self.metadata["last_trained"])
            days_since_training = (datetime.now() - last_trained).days
            
            if days_since_training >= self.metadata["retrain_threshold_days"]:
                logger.info(f"Models are {days_since_training} days old - retraining recommended")
                return True
        
        # Check if enough new data is available
        new_samples = self._count_new_samples()
        if new_samples >= self.metadata["min_new_samples"]:
            logger.info(f"{new_samples} new samples available - retraining recommended")
            return True
        
        return False
    
    def _count_new_samples(self) -> int:
        """Count new training samples since last training"""
        # In a real application, this would count actual user feedback data
        # For now, we'll simulate this
        return 0
    
    def train_initial_models(self, n_samples: int = 10000):
        """Train models for the first time"""
        logger.info("Training initial models...")
        
        self.predictor.train_models(n_samples=n_samples, retrain=False)
        
        # Update metadata
        self.metadata.update({
            "last_trained": datetime.now().isoformat(),
            "training_samples": n_samples,
            "version": "1.0.0"
        })
        self._save_metadata()
        
        logger.info("Initial model training completed")
    
    def retrain_models(self, n_samples: int = 15000):
        """Retrain models with fresh data"""
        logger.info("Retraining models with fresh data...")
        
        # Generate new training data (in production, this would include real user data)
        self.predictor.train_models(n_samples=n_samples, retrain=True)
        
        # Update version
        current_version = self.metadata["version"]
        version_parts = current_version.split(".")
        version_parts[1] = str(int(version_parts[1]) + 1)
        new_version = ".".join(version_parts)
        
        # Update metadata
        self.metadata.update({
            "last_trained": datetime.now().isoformat(),
            "training_samples": n_samples,
            "version": new_version
        })
        self._save_metadata()
        
        logger.info(f"Model retraining completed - new version: {new_version}")
    
    def backup_models(self):
        """Create backup of current models"""
        if not self.predictor.is_trained:
            logger.warning("No trained models to backup")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(self.model_dir, f"backup_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy model files
        import shutil
        for filename in os.listdir(self.model_dir):
            if filename.endswith(('.joblib', '.json')):
                src = os.path.join(self.model_dir, filename)
                dst = os.path.join(backup_dir, filename)
                shutil.copy2(src, dst)
        
        logger.info(f"Models backed up to {backup_dir}")
    
    def get_model_info(self) -> Dict:
        """Get information about current models"""
        return {
            "is_trained": self.predictor.is_trained,
            "version": self.metadata["version"],
            "last_trained": self.metadata["last_trained"],
            "training_samples": self.metadata["training_samples"],
            "should_retrain": self.should_retrain(),
            "model_files": [f for f in os.listdir(self.model_dir) if f.endswith('.joblib')]
        }
    
    def collect_feedback(self, prediction_data: Dict, actual_outcome: Dict):
        """Collect user feedback for model improvement"""
        
        # In a production system, this would store feedback data
        # for use in model retraining
        
        feedback_file = os.path.join(self.data_dir, "user_feedback.jsonl")
        
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "prediction": prediction_data,
            "actual": actual_outcome,
            "user_satisfaction": actual_outcome.get("satisfaction", None)
        }
        
        try:
            with open(feedback_file, 'a') as f:
                f.write(json.dumps(feedback_entry) + '\n')
            
            logger.info("User feedback collected")
            
        except Exception as e:
            logger.error(f"Could not save feedback: {e}")
    
    def load_feedback_data(self) -> List[Dict]:
        """Load collected feedback data"""
        feedback_file = os.path.join(self.data_dir, "user_feedback.jsonl")
        
        if not os.path.exists(feedback_file):
            return []
        
        feedback_data = []
        try:
            with open(feedback_file, 'r') as f:
                for line in f:
                    feedback_data.append(json.loads(line.strip()))
            
            logger.info(f"Loaded {len(feedback_data)} feedback entries")
            return feedback_data
            
        except Exception as e:
            logger.error(f"Could not load feedback data: {e}")
            return []
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """Clean up old model backups"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        for item in os.listdir(self.model_dir):
            if item.startswith("backup_"):
                backup_path = os.path.join(self.model_dir, item)
                if os.path.isdir(backup_path):
                    # Extract timestamp from backup folder name
                    try:
                        timestamp_str = item.replace("backup_", "")
                        backup_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        
                        if backup_date < cutoff_date:
                            import shutil
                            shutil.rmtree(backup_path)
                            logger.info(f"Removed old backup: {item}")
                            
                    except Exception as e:
                        logger.warning(f"Could not process backup {item}: {e}")

# Global model manager instance
model_manager = ModelManager()
