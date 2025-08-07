#!/usr/bin/env python3
"""
Database module for Soil Analysis
Handles storing and retrieving soil analysis results
"""

import sqlite3
import json
from datetime import datetime
import os

class SoilAnalysisDB:
    def __init__(self, db_path="soil_analysis.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create soil_analyses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS soil_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop_name TEXT NOT NULL,
                    ph REAL NOT NULL,
                    salinity REAL NOT NULL,
                    texture TEXT NOT NULL,
                    bulk_density REAL NOT NULL,
                    nutrients TEXT NOT NULL,  -- JSON string
                    suitability_score REAL NOT NULL,
                    category TEXT NOT NULL,
                    message TEXT NOT NULL,
                    recommendations TEXT,  -- JSON string
                    fertilizer_recommendations TEXT,  -- JSON string
                    alternative_crops TEXT,  -- JSON string
                    cultivation_tips TEXT,  -- JSON string
                    analysis_method TEXT DEFAULT 'Machine Learning',
                    model_version TEXT DEFAULT '1.0.0',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT DEFAULT 'anonymous'
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_crop_name ON soil_analyses(crop_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON soil_analyses(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON soil_analyses(category)')
            
            conn.commit()
            conn.close()
            print("✅ Database initialized successfully")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def save_analysis(self, analysis_data):
        """Save soil analysis result to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract data from analysis result
            crop_name = analysis_data.get('crop_name', analysis_data.get('crop', 'unknown'))
            soil_params = analysis_data.get('soil_parameters', {})
            
            # Insert analysis result
            cursor.execute('''
                INSERT INTO soil_analyses (
                    crop_name, ph, salinity, texture, bulk_density, nutrients,
                    suitability_score, category, message, recommendations,
                    fertilizer_recommendations, alternative_crops, cultivation_tips,
                    analysis_method, model_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                crop_name,
                soil_params.get('ph', 7.0),
                soil_params.get('salinity', 1.0),
                soil_params.get('texture', 'loam'),
                soil_params.get('bulk_density', 1.3),
                json.dumps(soil_params.get('nutrients', {})),
                analysis_data.get('suitability_score', 0),
                analysis_data.get('category', 'unknown'),
                analysis_data.get('message', ''),
                json.dumps(analysis_data.get('recommendations', [])),
                json.dumps(analysis_data.get('fertilizer_recommendations', [])),
                json.dumps(analysis_data.get('alternative_crops', [])),
                json.dumps(analysis_data.get('cultivation_tips', [])),
                analysis_data.get('analysis_method', 'Machine Learning'),
                analysis_data.get('model_version', '1.0.0')
            ))
            
            analysis_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Analysis saved to database with ID: {analysis_id}")
            return analysis_id
            
        except Exception as e:
            print(f"❌ Database save error: {e}")
            return None
    
    def get_analysis_history(self, crop_name=None, limit=10):
        """Get analysis history from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if crop_name:
                cursor.execute('''
                    SELECT * FROM soil_analyses 
                    WHERE crop_name = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (crop_name, limit))
            else:
                cursor.execute('''
                    SELECT * FROM soil_analyses 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            columns = [
                'id', 'crop_name', 'ph', 'salinity', 'texture', 'bulk_density',
                'nutrients', 'suitability_score', 'category', 'message',
                'recommendations', 'fertilizer_recommendations', 'alternative_crops',
                'cultivation_tips', 'analysis_method', 'model_version', 'created_at', 'user_id'
            ]
            
            history = []
            for row in results:
                analysis = dict(zip(columns, row))
                # Parse JSON fields
                analysis['nutrients'] = json.loads(analysis['nutrients'])
                analysis['recommendations'] = json.loads(analysis['recommendations'])
                analysis['fertilizer_recommendations'] = json.loads(analysis['fertilizer_recommendations'])
                analysis['alternative_crops'] = json.loads(analysis['alternative_crops'])
                analysis['cultivation_tips'] = json.loads(analysis['cultivation_tips'])
                history.append(analysis)
            
            return history
            
        except Exception as e:
            print(f"❌ Database query error: {e}")
            return []
    
    def get_statistics(self):
        """Get analysis statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total analyses
            cursor.execute('SELECT COUNT(*) FROM soil_analyses')
            total_analyses = cursor.fetchone()[0]
            
            # Analyses by category
            cursor.execute('''
                SELECT category, COUNT(*) 
                FROM soil_analyses 
                GROUP BY category
            ''')
            category_stats = dict(cursor.fetchall())
            
            # Analyses by crop
            cursor.execute('''
                SELECT crop_name, COUNT(*) 
                FROM soil_analyses 
                GROUP BY crop_name 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            ''')
            crop_stats = dict(cursor.fetchall())
            
            # Average scores by crop
            cursor.execute('''
                SELECT crop_name, AVG(suitability_score) 
                FROM soil_analyses 
                GROUP BY crop_name 
                ORDER BY AVG(suitability_score) DESC
            ''')
            avg_scores = {crop: round(score, 1) for crop, score in cursor.fetchall()}
            
            conn.close()
            
            return {
                'total_analyses': total_analyses,
                'category_distribution': category_stats,
                'popular_crops': crop_stats,
                'average_scores_by_crop': avg_scores
            }
            
        except Exception as e:
            print(f"❌ Database statistics error: {e}")
            return {}

# Global database instance
db = SoilAnalysisDB()

def save_analysis_to_db(analysis_data):
    """Convenience function to save analysis"""
    return db.save_analysis(analysis_data)

def get_analysis_history_from_db(crop_name=None, limit=10):
    """Convenience function to get history"""
    return db.get_analysis_history(crop_name, limit)

def get_db_statistics():
    """Convenience function to get statistics"""
    return db.get_statistics()

if __name__ == "__main__":
    # Test the database
    print("🧪 Testing Soil Analysis Database...")
    
    # Test data
    test_analysis = {
        'crop_name': 'tomato',
        'soil_parameters': {
            'ph': 6.5,
            'salinity': 1.2,
            'texture': 'loam',
            'bulk_density': 1.3,
            'nutrients': {'nitrogen': 120, 'phosphorus': 25, 'potassium': 45}
        },
        'suitability_score': 88.9,
        'category': 'excellent',
        'message': 'Test analysis',
        'recommendations': ['Test recommendation'],
        'fertilizer_recommendations': [],
        'alternative_crops': [],
        'cultivation_tips': ['Test tip']
    }
    
    # Save test analysis
    analysis_id = save_analysis_to_db(test_analysis)
    print(f"Test analysis saved with ID: {analysis_id}")
    
    # Get history
    history = get_analysis_history_from_db(limit=5)
    print(f"Found {len(history)} analyses in history")
    
    # Get statistics
    stats = get_db_statistics()
    print(f"Database statistics: {stats}")
    
    print("✅ Database test completed")
