#!/usr/bin/env python3
"""
Database module for Crop Yield Prediction
Handles storing and retrieving crop prediction results
"""

import sqlite3
import json
from datetime import datetime
import os

class CropPredictionDB:
    def __init__(self, db_path="crop_predictions.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create crop_predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crop_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop TEXT NOT NULL,
                    field_size_acres REAL NOT NULL,
                    season TEXT NOT NULL,
                    soil_type TEXT NOT NULL,
                    irrigation_type TEXT NOT NULL,
                    expected_yield_tons REAL NOT NULL,
                    yield_per_acre_tons REAL NOT NULL,
                    total_quintals REAL NOT NULL,
                    current_price_per_quintal REAL NOT NULL,
                    estimated_revenue REAL NOT NULL,
                    estimated_cost REAL NOT NULL,
                    estimated_profit REAL NOT NULL,
                    profit_margin_percent REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    soil_suitability TEXT,
                    irrigation_efficiency TEXT,
                    seasonal_factor TEXT,
                    confidence_score REAL NOT NULL,
                    recommendations TEXT,  -- JSON string
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT DEFAULT 'anonymous'
                )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_crop ON crop_predictions(crop)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_season ON crop_predictions(season)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_date ON crop_predictions(analysis_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_soil_type ON crop_predictions(soil_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_risk_level ON crop_predictions(risk_level)')
            
            conn.commit()
            conn.close()
            print("✅ Crop prediction database initialized successfully")
            
        except Exception as e:
            print(f"❌ Crop prediction database initialization error: {e}")
    
    def save_prediction(self, prediction_data):
        """Save crop prediction result to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract data from prediction result
            predictions = prediction_data.get('predictions', {})
            market_analysis = prediction_data.get('market_analysis', {})
            risk_assessment = prediction_data.get('risk_assessment', {})
            risk_factors = risk_assessment.get('factors', {})
            
            # Insert prediction result
            cursor.execute('''
                INSERT INTO crop_predictions (
                    crop, field_size_acres, season, soil_type, irrigation_type,
                    expected_yield_tons, yield_per_acre_tons, total_quintals,
                    current_price_per_quintal, estimated_revenue, estimated_cost,
                    estimated_profit, profit_margin_percent, risk_level,
                    soil_suitability, irrigation_efficiency, seasonal_factor,
                    confidence_score, recommendations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction_data.get('crop', 'unknown'),
                prediction_data.get('field_size_acres', 0),
                prediction_data.get('season', 'unknown'),
                prediction_data.get('soil_type', 'unknown'),
                prediction_data.get('irrigation_type', 'unknown'),
                predictions.get('expected_yield_tons', 0),
                predictions.get('yield_per_acre_tons', 0),
                predictions.get('total_quintals', 0),
                market_analysis.get('current_price_per_quintal', 0),
                market_analysis.get('estimated_revenue', 0),
                market_analysis.get('estimated_cost', 0),
                market_analysis.get('estimated_profit', 0),
                market_analysis.get('profit_margin_percent', 0),
                risk_assessment.get('risk_level', 'Medium'),
                risk_factors.get('soil_suitability', ''),
                risk_factors.get('irrigation_efficiency', ''),
                risk_factors.get('seasonal_factor', ''),
                prediction_data.get('confidence_score', 0),
                json.dumps(prediction_data.get('recommendations', []))
            ))
            
            prediction_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Crop prediction saved to database with ID: {prediction_id}")
            return prediction_id
            
        except Exception as e:
            print(f"❌ Database save error: {e}")
            return None
    
    def get_prediction_history(self, crop=None, season=None, limit=10):
        """Get prediction history from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT * FROM crop_predictions'
            params = []
            conditions = []
            
            if crop:
                conditions.append('crop = ?')
                params.append(crop)
            if season:
                conditions.append('season = ?')
                params.append(season)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY analysis_date DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            columns = [
                'id', 'crop', 'field_size_acres', 'season', 'soil_type', 'irrigation_type',
                'expected_yield_tons', 'yield_per_acre_tons', 'total_quintals',
                'current_price_per_quintal', 'estimated_revenue', 'estimated_cost',
                'estimated_profit', 'profit_margin_percent', 'risk_level',
                'soil_suitability', 'irrigation_efficiency', 'seasonal_factor',
                'confidence_score', 'recommendations', 'analysis_date', 'user_id'
            ]
            
            history = []
            for row in results:
                prediction = dict(zip(columns, row))
                # Parse JSON fields
                prediction['recommendations'] = json.loads(prediction['recommendations'])
                history.append(prediction)
            
            return history
            
        except Exception as e:
            print(f"❌ Database query error: {e}")
            return []
    
    def get_statistics(self):
        """Get crop prediction statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total predictions
            cursor.execute('SELECT COUNT(*) FROM crop_predictions')
            total_predictions = cursor.fetchone()[0]
            
            # Predictions by crop
            cursor.execute('''
                SELECT crop, COUNT(*) 
                FROM crop_predictions 
                GROUP BY crop 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            ''')
            crop_stats = dict(cursor.fetchall())
            
            # Predictions by season
            cursor.execute('''
                SELECT season, COUNT(*) 
                FROM crop_predictions 
                GROUP BY season
            ''')
            season_stats = dict(cursor.fetchall())
            
            # Average yield by crop
            cursor.execute('''
                SELECT crop, AVG(expected_yield_tons) 
                FROM crop_predictions 
                GROUP BY crop 
                ORDER BY AVG(expected_yield_tons) DESC
            ''')
            avg_yield_by_crop = {crop: round(yield_val, 2) for crop, yield_val in cursor.fetchall()}
            
            # Average profit margin by crop
            cursor.execute('''
                SELECT crop, AVG(profit_margin_percent) 
                FROM crop_predictions 
                GROUP BY crop 
                ORDER BY AVG(profit_margin_percent) DESC
            ''')
            avg_profit_by_crop = {crop: round(profit, 1) for crop, profit in cursor.fetchall()}
            
            # Risk level distribution
            cursor.execute('''
                SELECT risk_level, COUNT(*) 
                FROM crop_predictions 
                GROUP BY risk_level
            ''')
            risk_distribution = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_predictions': total_predictions,
                'popular_crops': crop_stats,
                'seasonal_distribution': season_stats,
                'average_yield_by_crop': avg_yield_by_crop,
                'average_profit_by_crop': avg_profit_by_crop,
                'risk_distribution': risk_distribution
            }
            
        except Exception as e:
            print(f"❌ Database statistics error: {e}")
            return {}

# Global database instance
db = CropPredictionDB()

def save_prediction_to_db(prediction_data):
    """Convenience function to save prediction"""
    return db.save_prediction(prediction_data)

def get_prediction_history_from_db(crop=None, season=None, limit=10):
    """Convenience function to get history"""
    return db.get_prediction_history(crop, season, limit)

def get_db_statistics():
    """Convenience function to get statistics"""
    return db.get_statistics()

if __name__ == "__main__":
    # Test the database
    print("🧪 Testing Crop Prediction Database...")
    
    # Test data
    test_prediction = {
        'crop': 'Rice',
        'field_size_acres': 3.0,
        'season': 'Kharif',
        'soil_type': 'Loam',
        'irrigation_type': 'Drip',
        'predictions': {
            'expected_yield_tons': 15.85,
            'yield_per_acre_tons': 5.28,
            'total_quintals': 158.5
        },
        'market_analysis': {
            'current_price_per_quintal': 1822.0,
            'estimated_revenue': 288854.0,
            'estimated_cost': 90000.0,
            'estimated_profit': 198854.0,
            'profit_margin_percent': 68.8
        },
        'risk_assessment': {
            'risk_level': 'Low',
            'factors': {
                'soil_suitability': '100%',
                'irrigation_efficiency': '114%',
                'seasonal_factor': 'Good'
            }
        },
        'confidence_score': 77.9,
        'recommendations': ['Test recommendation 1', 'Test recommendation 2']
    }
    
    # Save test prediction
    pred_id = save_prediction_to_db(test_prediction)
    print(f"Test prediction saved with ID: {pred_id}")
    
    # Get history
    history = get_prediction_history_from_db(limit=5)
    print(f"Found {len(history)} predictions in history")
    
    # Get statistics
    stats = get_db_statistics()
    print(f"Database statistics: {stats}")
    
    print("✅ Database test completed")
