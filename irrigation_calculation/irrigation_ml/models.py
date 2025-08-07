import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import os
from typing import Dict, Tuple, Optional
import logging

from .data_generator import IrrigationDataGenerator
from .data_model import IrrigationFeatures, CropType, SoilType, IrrigationMethod

logger = logging.getLogger(__name__)

class IrrigationPredictor:
    """Machine learning models for irrigation prediction"""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
        # Try to load existing models
        self._load_models()
    
    def train_models(self, n_samples: int = 10000, retrain: bool = False):
        """Train all irrigation prediction models"""
        
        if self.is_trained and not retrain:
            logger.info("Models already trained. Use retrain=True to retrain.")
            return
        
        logger.info(f"Generating {n_samples} training samples...")
        
        # Generate training data
        data_generator = IrrigationDataGenerator()
        features_df, targets_df = data_generator.generate_training_data(n_samples)
        
        logger.info("Training models...")
        
        # Train timing prediction model
        self._train_timing_model(features_df, targets_df)
        
        # Train water requirement model
        self._train_water_model(features_df, targets_df)
        
        # Train priority classification model
        self._train_priority_model(features_df, targets_df)
        
        # Save models
        self._save_models()
        
        self.is_trained = True
        logger.info("Model training completed successfully!")
    
    def _train_timing_model(self, features_df: pd.DataFrame, targets_df: pd.DataFrame):
        """Train model to predict days until next irrigation"""
        
        X = features_df.values
        y = targets_df['days_until_next_irrigation'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train_scaled, y_train)
        
        # Train XGBoost
        xgb_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        xgb_model.fit(X_train_scaled, y_train)
        
        # Evaluate models
        rf_pred = rf_model.predict(X_test_scaled)
        xgb_pred = xgb_model.predict(X_test_scaled)
        
        rf_mae = mean_absolute_error(y_test, rf_pred)
        xgb_mae = mean_absolute_error(y_test, xgb_pred)
        
        logger.info(f"Timing Model - RF MAE: {rf_mae:.3f}, XGB MAE: {xgb_mae:.3f}")
        
        # Choose best model
        if rf_mae <= xgb_mae:
            self.models['timing'] = rf_model
            logger.info("Selected Random Forest for timing prediction")
        else:
            self.models['timing'] = xgb_model
            logger.info("Selected XGBoost for timing prediction")
        
        self.scalers['timing'] = scaler
    
    def _train_water_model(self, features_df: pd.DataFrame, targets_df: pd.DataFrame):
        """Train model to predict water requirements"""
        
        X = features_df.values
        y = targets_df['water_requirement_per_hectare'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train_scaled, y_train)
        
        # Train XGBoost
        xgb_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        xgb_model.fit(X_train_scaled, y_train)
        
        # Evaluate models
        rf_pred = rf_model.predict(X_test_scaled)
        xgb_pred = xgb_model.predict(X_test_scaled)
        
        rf_mae = mean_absolute_error(y_test, rf_pred)
        xgb_mae = mean_absolute_error(y_test, xgb_pred)
        
        logger.info(f"Water Model - RF MAE: {rf_mae:.0f}, XGB MAE: {xgb_mae:.0f}")
        
        # Choose best model
        if rf_mae <= xgb_mae:
            self.models['water'] = rf_model
            logger.info("Selected Random Forest for water prediction")
        else:
            self.models['water'] = xgb_model
            logger.info("Selected XGBoost for water prediction")
        
        self.scalers['water'] = scaler
    
    def _train_priority_model(self, features_df: pd.DataFrame, targets_df: pd.DataFrame):
        """Train model to predict irrigation priority"""
        
        X = features_df.values
        y = targets_df['irrigation_priority'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest Classifier
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train_scaled, y_train)
        
        # Train XGBoost Classifier
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        xgb_model.fit(X_train_scaled, y_train)
        
        # Evaluate models
        rf_pred = rf_model.predict(X_test_scaled)
        xgb_pred = xgb_model.predict(X_test_scaled)
        
        rf_acc = accuracy_score(y_test, rf_pred)
        xgb_acc = accuracy_score(y_test, xgb_pred)
        
        logger.info(f"Priority Model - RF Accuracy: {rf_acc:.3f}, XGB Accuracy: {xgb_acc:.3f}")
        
        # Choose best model
        if rf_acc >= xgb_acc:
            self.models['priority'] = rf_model
            logger.info("Selected Random Forest for priority classification")
        else:
            self.models['priority'] = xgb_model
            logger.info("Selected XGBoost for priority classification")
        
        self.scalers['priority'] = scaler
    
    def predict(self, features: IrrigationFeatures) -> Dict:
        """Make irrigation predictions"""
        
        if not self.is_trained:
            raise ValueError("Models not trained. Call train_models() first.")
        
        # Convert features to array
        X = features.to_array().reshape(1, -1)
        
        # Make predictions
        predictions = {}
        
        # Predict timing
        X_scaled = self.scalers['timing'].transform(X)
        days_until = self.models['timing'].predict(X_scaled)[0]
        predictions['days_until_irrigation'] = max(0, int(round(days_until)))
        
        # Predict water requirement
        X_scaled = self.scalers['water'].transform(X)
        water_per_hectare = self.models['water'].predict(X_scaled)[0]
        predictions['water_per_hectare'] = max(1000, float(water_per_hectare))
        
        # Predict priority
        X_scaled = self.scalers['priority'].transform(X)
        priority = self.models['priority'].predict(X_scaled)[0]
        predictions['priority'] = int(priority)
        
        return predictions
    
    def _save_models(self):
        """Save trained models and scalers"""
        for name, model in self.models.items():
            model_path = os.path.join(self.model_dir, f"{name}_model.joblib")
            joblib.dump(model, model_path)
            
        for name, scaler in self.scalers.items():
            scaler_path = os.path.join(self.model_dir, f"{name}_scaler.joblib")
            joblib.dump(scaler, scaler_path)
        
        logger.info(f"Models saved to {self.model_dir}")
    
    def _load_models(self):
        """Load existing models and scalers"""
        try:
            model_types = ['timing', 'water', 'priority']
            
            for model_type in model_types:
                model_path = os.path.join(self.model_dir, f"{model_type}_model.joblib")
                scaler_path = os.path.join(self.model_dir, f"{model_type}_scaler.joblib")
                
                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    self.models[model_type] = joblib.load(model_path)
                    self.scalers[model_type] = joblib.load(scaler_path)
            
            if len(self.models) == 3:
                self.is_trained = True
                logger.info("Loaded existing trained models")
            
        except Exception as e:
            logger.warning(f"Could not load existing models: {e}")
            self.models = {}
            self.scalers = {}
            self.is_trained = False
