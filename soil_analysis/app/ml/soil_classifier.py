"""
Soil suitability classification model
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from typing import Tuple, Dict, Any
from loguru import logger

from app.data.crop_requirements import CROP_REQUIREMENTS, get_all_crops
from app.models.soil import SoilParameters, SoilTexture

class SoilSuitabilityClassifier:
    """Machine learning model for soil suitability classification"""
    
    def __init__(self, model_path: str = "models/"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.texture_encoder = LabelEncoder()
        self.crop_encoder = LabelEncoder()
        self.feature_names = []
        
        # Create models directory if it doesn't exist
        os.makedirs(model_path, exist_ok=True)
    
    def _generate_training_data(self, n_samples: int = 10000) -> Tuple[pd.DataFrame, np.ndarray]:
        """Generate synthetic training data based on crop requirements"""
        data = []
        labels = []
        
        crops = get_all_crops()
        textures = [texture.value for texture in SoilTexture]
        
        for _ in range(n_samples):
            # Randomly select a crop
            crop = np.random.choice(crops)
            requirements = CROP_REQUIREMENTS[crop]
            
            # Generate soil parameters with some variation
            ph_min, ph_max = requirements["ph_range"]
            
            # Generate samples with different suitability levels
            suitability = np.random.choice(["excellent", "average", "bad"], p=[0.3, 0.4, 0.3])
            
            if suitability == "excellent":
                # Generate parameters within optimal range
                ph = np.random.uniform(ph_min + 0.1, ph_max - 0.1)
                salinity = np.random.uniform(0, requirements["salinity_tolerance"] * 0.5)
                texture = np.random.choice(requirements["preferred_textures"])
                bulk_density = np.random.uniform(*requirements["bulk_density_range"])
                
                # Generate optimal nutrient levels
                nutrients = {}
                for nutrient, values in requirements["nutrients"].items():
                    optimal = values["optimal"]
                    nutrients[nutrient] = np.random.normal(optimal, optimal * 0.1)
                    
            elif suitability == "average":
                # Generate parameters slightly outside optimal range
                ph = np.random.choice([
                    np.random.uniform(ph_min - 0.5, ph_min),
                    np.random.uniform(ph_max, ph_max + 0.5)
                ])
                salinity = np.random.uniform(requirements["salinity_tolerance"] * 0.5, 
                                           requirements["salinity_tolerance"] * 0.8)
                texture = np.random.choice(textures)
                bulk_density = np.random.uniform(requirements["bulk_density_range"][0] - 0.1,
                                               requirements["bulk_density_range"][1] + 0.1)
                
                # Generate suboptimal nutrient levels
                nutrients = {}
                for nutrient, values in requirements["nutrients"].items():
                    min_val, max_val = values["min"], values["max"]
                    nutrients[nutrient] = np.random.uniform(min_val * 0.7, max_val * 1.3)
                    
            else:  # bad
                # Generate parameters well outside optimal range
                ph = np.random.choice([
                    np.random.uniform(3.0, ph_min - 0.5),
                    np.random.uniform(ph_max + 0.5, 9.0)
                ])
                salinity = np.random.uniform(requirements["salinity_tolerance"], 
                                           requirements["salinity_tolerance"] * 2)
                texture = np.random.choice(textures)
                bulk_density = np.random.uniform(0.8, 2.0)
                
                # Generate poor nutrient levels
                nutrients = {}
                for nutrient, values in requirements["nutrients"].items():
                    min_val = values["min"]
                    nutrients[nutrient] = np.random.uniform(0, min_val * 0.5)
            
            # Create feature vector
            features = {
                "ph": max(0, min(14, ph)),
                "salinity": max(0, salinity),
                "texture": texture,
                "bulk_density": max(0.5, min(2.5, bulk_density)),
                "crop": crop,
                **nutrients
            }
            
            data.append(features)
            labels.append(suitability)
        
        df = pd.DataFrame(data)
        return df, np.array(labels)
    
    def _prepare_features(self, df: pd.DataFrame, fit_encoders: bool = False) -> np.ndarray:
        """Prepare features for training/prediction"""
        
        # Handle categorical variables
        if fit_encoders:
            df["texture_encoded"] = self.texture_encoder.fit_transform(df["texture"])
            df["crop_encoded"] = self.crop_encoder.fit_transform(df["crop"])
        else:
            df["texture_encoded"] = self.texture_encoder.transform(df["texture"])
            df["crop_encoded"] = self.crop_encoder.transform(df["crop"])
        
        # Select numerical features
        feature_columns = ["ph", "salinity", "bulk_density", "texture_encoded", "crop_encoded",
                          "nitrogen", "phosphorus", "potassium", "calcium", "magnesium",
                          "sulfur", "iron", "manganese", "zinc"]
        
        self.feature_names = feature_columns
        return df[feature_columns].values
    
    def train(self, n_samples: int = 10000) -> Dict[str, Any]:
        """Train the soil suitability classification model"""
        logger.info(f"Generating {n_samples} training samples...")
        
        # Generate training data
        df, labels = self._generate_training_data(n_samples)
        
        # Prepare features
        X = self._prepare_features(df, fit_encoders=True)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        logger.info("Training Random Forest classifier...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight="balanced"
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Model accuracy: {accuracy:.3f}")
        logger.info("Classification report:")
        logger.info(f"\n{classification_report(y_test, y_pred)}")
        
        # Save model and preprocessors
        self.save_model()
        
        return {
            "accuracy": accuracy,
            "classification_report": classification_report(y_test, y_pred, output_dict=True)
        }
    
    def predict(self, soil_params: SoilParameters, crop: str) -> Tuple[str, float]:
        """Predict soil suitability for a given crop"""
        if self.model is None:
            self.load_model()
        
        # Prepare input data
        input_data = {
            "ph": soil_params.ph,
            "salinity": soil_params.salinity,
            "texture": soil_params.texture.value,
            "bulk_density": soil_params.bulk_density,
            "crop": crop.lower(),
            "nitrogen": soil_params.nutrients.nitrogen,
            "phosphorus": soil_params.nutrients.phosphorus,
            "potassium": soil_params.nutrients.potassium,
            "calcium": soil_params.nutrients.calcium,
            "magnesium": soil_params.nutrients.magnesium,
            "sulfur": soil_params.nutrients.sulfur,
            "iron": soil_params.nutrients.iron,
            "manganese": soil_params.nutrients.manganese,
            "zinc": soil_params.nutrients.zinc
        }
        
        df = pd.DataFrame([input_data])
        X = self._prepare_features(df, fit_encoders=False)
        X_scaled = self.scaler.transform(X)
        
        # Get prediction and probability
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        # Get confidence score
        max_prob = max(probabilities)
        
        return prediction, max_prob
    
    def save_model(self):
        """Save trained model and preprocessors"""
        joblib.dump(self.model, os.path.join(self.model_path, "soil_classifier.pkl"))
        joblib.dump(self.scaler, os.path.join(self.model_path, "scaler.pkl"))
        joblib.dump(self.texture_encoder, os.path.join(self.model_path, "texture_encoder.pkl"))
        joblib.dump(self.crop_encoder, os.path.join(self.model_path, "crop_encoder.pkl"))
        
        logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model and preprocessors"""
        try:
            self.model = joblib.load(os.path.join(self.model_path, "soil_classifier.pkl"))
            self.scaler = joblib.load(os.path.join(self.model_path, "scaler.pkl"))
            self.texture_encoder = joblib.load(os.path.join(self.model_path, "texture_encoder.pkl"))
            self.crop_encoder = joblib.load(os.path.join(self.model_path, "crop_encoder.pkl"))
            
            logger.info("Model loaded successfully")
        except FileNotFoundError:
            logger.warning("Model files not found. Training new model...")
            self.train()
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the trained model"""
        if self.model is None:
            self.load_model()
        
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))
