#!/usr/bin/env python3
"""
Database module for Irrigation Calculator
Handles storing and retrieving irrigation calculation results
"""

import sqlite3
import json
from datetime import datetime
import os

class IrrigationDB:
    def __init__(self, db_path="irrigation_calculations.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create irrigation_calculations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS irrigation_calculations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop TEXT NOT NULL,
                    field_size_acres REAL NOT NULL,
                    soil_type TEXT NOT NULL,
                    irrigation_type TEXT NOT NULL,
                    last_irrigation_date TEXT NOT NULL,
                    location TEXT NOT NULL,
                    water_liters REAL NOT NULL,
                    water_per_sqm REAL NOT NULL,
                    next_irrigation TEXT NOT NULL,
                    irrigation_priority TEXT,
                    irrigation_frequency TEXT,
                    days_since_last INTEGER,
                    efficiency_percent INTEGER,
                    temperature REAL,
                    humidity REAL,
                    rainfall_forecast REAL,
                    weather_condition TEXT,
                    recommendations TEXT,  -- JSON string
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT DEFAULT 'anonymous'
                )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_crop ON irrigation_calculations(crop)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_location ON irrigation_calculations(location)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_date ON irrigation_calculations(analysis_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_irrigation_type ON irrigation_calculations(irrigation_type)')
            
            conn.commit()
            conn.close()
            print("✅ Irrigation database initialized successfully")
            
        except Exception as e:
            print(f"❌ Irrigation database initialization error: {e}")
    
    def save_calculation(self, calculation_data):
        """Save irrigation calculation result to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract data from calculation result
            water_req = calculation_data.get('water_requirement', {})
            schedule = calculation_data.get('irrigation_schedule', {})
            efficiency = calculation_data.get('efficiency', {})
            weather = calculation_data.get('weatherInfo', {})
            
            # Insert calculation result
            cursor.execute('''
                INSERT INTO irrigation_calculations (
                    crop, field_size_acres, soil_type, irrigation_type, last_irrigation_date,
                    location, water_liters, water_per_sqm, next_irrigation,
                    irrigation_priority, irrigation_frequency, days_since_last,
                    efficiency_percent, temperature, humidity, rainfall_forecast,
                    weather_condition, recommendations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                calculation_data.get('crop', 'unknown'),
                calculation_data.get('field_size_acres', 0),
                calculation_data.get('soil_type', 'unknown'),
                calculation_data.get('irrigation_type', 'unknown'),
                calculation_data.get('last_irrigation_date', ''),
                calculation_data.get('location', 'unknown'),
                calculation_data.get('waterLiters', 0),
                water_req.get('liters_per_sqm', 0),
                calculation_data.get('nextIrrigationDate', ''),
                schedule.get('priority', ''),
                schedule.get('frequency', ''),
                schedule.get('days_since_last', 0),
                efficiency.get('efficiency_percent', 0),
                weather.get('temperature', 0),
                weather.get('humidity', 0),
                weather.get('rainfall_forecast_3day', 0),
                weather.get('weather_condition', ''),
                json.dumps(calculation_data.get('recommendations', []))
            ))
            
            calculation_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Irrigation calculation saved to database with ID: {calculation_id}")
            return calculation_id
            
        except Exception as e:
            print(f"❌ Database save error: {e}")
            return None
    
    def get_calculation_history(self, crop=None, location=None, limit=10):
        """Get calculation history from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT * FROM irrigation_calculations'
            params = []
            conditions = []
            
            if crop:
                conditions.append('crop = ?')
                params.append(crop)
            if location:
                conditions.append('location LIKE ?')
                params.append(f'%{location}%')
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY analysis_date DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            columns = [
                'id', 'crop', 'field_size_acres', 'soil_type', 'irrigation_type',
                'last_irrigation_date', 'location', 'water_liters', 'water_per_sqm',
                'next_irrigation', 'irrigation_priority', 'irrigation_frequency',
                'days_since_last', 'efficiency_percent', 'temperature', 'humidity',
                'rainfall_forecast', 'weather_condition', 'recommendations',
                'analysis_date', 'user_id'
            ]
            
            history = []
            for row in results:
                calculation = dict(zip(columns, row))
                # Parse JSON fields
                calculation['recommendations'] = json.loads(calculation['recommendations'])
                history.append(calculation)
            
            return history
            
        except Exception as e:
            print(f"❌ Database query error: {e}")
            return []
    
    def get_statistics(self):
        """Get irrigation calculation statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total calculations
            cursor.execute('SELECT COUNT(*) FROM irrigation_calculations')
            total_calculations = cursor.fetchone()[0]
            
            # Calculations by crop
            cursor.execute('''
                SELECT crop, COUNT(*) 
                FROM irrigation_calculations 
                GROUP BY crop 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            ''')
            crop_stats = dict(cursor.fetchall())
            
            # Calculations by irrigation type
            cursor.execute('''
                SELECT irrigation_type, COUNT(*) 
                FROM irrigation_calculations 
                GROUP BY irrigation_type
            ''')
            irrigation_type_stats = dict(cursor.fetchall())
            
            # Average water usage by crop
            cursor.execute('''
                SELECT crop, AVG(water_liters) 
                FROM irrigation_calculations 
                GROUP BY crop 
                ORDER BY AVG(water_liters) DESC
            ''')
            avg_water_by_crop = {crop: round(water, 1) for crop, water in cursor.fetchall()}
            
            # Recent locations
            cursor.execute('''
                SELECT location, COUNT(*) 
                FROM irrigation_calculations 
                GROUP BY location 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            ''')
            location_stats = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_calculations': total_calculations,
                'popular_crops': crop_stats,
                'irrigation_methods': irrigation_type_stats,
                'average_water_by_crop': avg_water_by_crop,
                'popular_locations': location_stats
            }
            
        except Exception as e:
            print(f"❌ Database statistics error: {e}")
            return {}

# Global database instance
db = IrrigationDB()

def save_calculation_to_db(calculation_data):
    """Convenience function to save calculation"""
    return db.save_calculation(calculation_data)

def get_calculation_history_from_db(crop=None, location=None, limit=10):
    """Convenience function to get history"""
    return db.get_calculation_history(crop, location, limit)

def get_db_statistics():
    """Convenience function to get statistics"""
    return db.get_statistics()

if __name__ == "__main__":
    # Test the database
    print("🧪 Testing Irrigation Database...")
    
    # Test data
    test_calculation = {
        'crop': 'rice',
        'field_size_acres': 2.0,
        'soil_type': 'loam',
        'irrigation_type': 'drip',
        'last_irrigation_date': '2025-08-05',
        'location': 'Tamil Nadu',
        'waterLiters': 92502.9,
        'nextIrrigationDate': 'Within 3-4 days',
        'water_requirement': {'liters_per_sqm': 11.43},
        'irrigation_schedule': {
            'priority': 'low',
            'frequency': 'Every 5-7 days',
            'days_since_last': 2
        },
        'efficiency': {'efficiency_percent': 90},
        'weatherInfo': {
            'temperature': 31,
            'humidity': 78,
            'rainfall_forecast_3day': 1.5,
            'weather_condition': 'Sunny'
        },
        'recommendations': ['Apply 11.4 liters per square meter']
    }
    
    # Save test calculation
    calc_id = save_calculation_to_db(test_calculation)
    print(f"Test calculation saved with ID: {calc_id}")
    
    # Get history
    history = get_calculation_history_from_db(limit=5)
    print(f"Found {len(history)} calculations in history")
    
    # Get statistics
    stats = get_db_statistics()
    print(f"Database statistics: {stats}")
    
    print("✅ Database test completed")
