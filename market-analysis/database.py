#!/usr/bin/env python3
"""
Database module for Market Analysis
Handles storing and retrieving market analysis results
"""

import sqlite3
import json
from datetime import datetime
import os

class MarketAnalysisDB:
    def __init__(self, db_path="market_analysis.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create market_analyses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop TEXT NOT NULL,
                    state TEXT NOT NULL,
                    district TEXT,
                    state_avg_price REAL NOT NULL,
                    district_avg_price REAL,
                    price_trend TEXT NOT NULL,
                    trend_percentage REAL NOT NULL,
                    recommendation TEXT NOT NULL,
                    prediction_confidence REAL NOT NULL,
                    min_price REAL,
                    max_price REAL,
                    modal_price REAL,
                    market_data TEXT,  -- JSON string
                    price_volatility REAL,
                    seasonal_factor REAL,
                    demand_supply_ratio REAL,
                    quality_grade TEXT,
                    transportation_cost REAL,
                    storage_recommendation TEXT,
                    best_selling_time TEXT,
                    risk_level TEXT,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT DEFAULT 'anonymous'
                )
            ''')
            
            # Create price_history table for tracking price changes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop TEXT NOT NULL,
                    state TEXT NOT NULL,
                    district TEXT,
                    price REAL NOT NULL,
                    price_type TEXT NOT NULL,  -- 'state_avg', 'district_avg', 'modal', 'min', 'max'
                    recorded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_crop ON market_analyses(crop)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_state ON market_analyses(state)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_date ON market_analyses(analysis_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_trend ON market_analyses(price_trend)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_crop ON price_history(crop)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(recorded_date)')
            
            conn.commit()
            conn.close()
            print("✅ Market analysis database initialized successfully")
            
        except Exception as e:
            print(f"❌ Market analysis database initialization error: {e}")
    
    def save_analysis(self, analysis_data):
        """Save market analysis result to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract market data
            market_data = analysis_data.get('market_data', [])
            first_market = market_data[0] if market_data else {}
            
            # Insert analysis result
            cursor.execute('''
                INSERT INTO market_analyses (
                    crop, state, district, state_avg_price, district_avg_price,
                    price_trend, trend_percentage, recommendation, prediction_confidence,
                    min_price, max_price, modal_price, market_data,
                    price_volatility, seasonal_factor, demand_supply_ratio,
                    quality_grade, transportation_cost, storage_recommendation,
                    best_selling_time, risk_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_data.get('crop', 'unknown'),
                analysis_data.get('state', 'unknown'),
                analysis_data.get('district', ''),
                analysis_data.get('state_avg_price', 0),
                analysis_data.get('district_avg_price', 0),
                analysis_data.get('price_trend', 'stable'),
                analysis_data.get('trend_percentage', 0),
                analysis_data.get('recommendation', ''),
                analysis_data.get('prediction_confidence', 0),
                float(first_market.get('min_price', 0)) if first_market.get('min_price') else 0,
                float(first_market.get('max_price', 0)) if first_market.get('max_price') else 0,
                float(first_market.get('modal_price', 0)) if first_market.get('modal_price') else 0,
                json.dumps(market_data),
                analysis_data.get('price_volatility', 0),
                analysis_data.get('seasonal_factor', 1.0),
                analysis_data.get('demand_supply_ratio', 1.0),
                analysis_data.get('quality_grade', 'A'),
                analysis_data.get('transportation_cost', 0),
                analysis_data.get('storage_recommendation', ''),
                analysis_data.get('best_selling_time', ''),
                analysis_data.get('risk_level', 'Medium')
            ))
            
            analysis_id = cursor.lastrowid
            
            # Also save to price history
            crop = analysis_data.get('crop', 'unknown')
            state = analysis_data.get('state', 'unknown')
            district = analysis_data.get('district', '')
            
            price_entries = [
                (crop, state, district, analysis_data.get('state_avg_price', 0), 'state_avg'),
            ]
            
            if analysis_data.get('district_avg_price'):
                price_entries.append((crop, state, district, analysis_data.get('district_avg_price', 0), 'district_avg'))
            
            if first_market:
                if first_market.get('modal_price'):
                    price_entries.append((crop, state, district, float(first_market.get('modal_price', 0)), 'modal'))
                if first_market.get('min_price'):
                    price_entries.append((crop, state, district, float(first_market.get('min_price', 0)), 'min'))
                if first_market.get('max_price'):
                    price_entries.append((crop, state, district, float(first_market.get('max_price', 0)), 'max'))
            
            cursor.executemany('''
                INSERT INTO price_history (crop, state, district, price, price_type)
                VALUES (?, ?, ?, ?, ?)
            ''', price_entries)
            
            conn.commit()
            conn.close()
            
            print(f"✅ Market analysis saved to database with ID: {analysis_id}")
            return analysis_id
            
        except Exception as e:
            print(f"❌ Database save error: {e}")
            return None
    
    def get_analysis_history(self, crop=None, state=None, limit=10):
        """Get analysis history from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT * FROM market_analyses'
            params = []
            conditions = []
            
            if crop:
                conditions.append('crop = ?')
                params.append(crop)
            if state:
                conditions.append('state = ?')
                params.append(state)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY analysis_date DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            columns = [
                'id', 'crop', 'state', 'district', 'state_avg_price', 'district_avg_price',
                'price_trend', 'trend_percentage', 'recommendation', 'prediction_confidence',
                'min_price', 'max_price', 'modal_price', 'market_data',
                'price_volatility', 'seasonal_factor', 'demand_supply_ratio',
                'quality_grade', 'transportation_cost', 'storage_recommendation',
                'best_selling_time', 'risk_level', 'analysis_date', 'user_id'
            ]
            
            history = []
            for row in results:
                analysis = dict(zip(columns, row))
                # Parse JSON fields
                analysis['market_data'] = json.loads(analysis['market_data'])
                history.append(analysis)
            
            return history
            
        except Exception as e:
            print(f"❌ Database query error: {e}")
            return []
    
    def get_price_trends(self, crop, state, days=30):
        """Get price trends for a specific crop and state"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT price, price_type, recorded_date
                FROM price_history
                WHERE crop = ? AND state = ? AND recorded_date >= datetime('now', '-{} days')
                ORDER BY recorded_date DESC
            '''.format(days), (crop, state))
            
            results = cursor.fetchall()
            conn.close()
            
            trends = []
            for price, price_type, date in results:
                trends.append({
                    'price': price,
                    'type': price_type,
                    'date': date
                })
            
            return trends
            
        except Exception as e:
            print(f"❌ Price trends query error: {e}")
            return []
    
    def get_statistics(self):
        """Get market analysis statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total analyses
            cursor.execute('SELECT COUNT(*) FROM market_analyses')
            total_analyses = cursor.fetchone()[0]
            
            # Analyses by crop
            cursor.execute('''
                SELECT crop, COUNT(*) 
                FROM market_analyses 
                GROUP BY crop 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            ''')
            crop_stats = dict(cursor.fetchall())
            
            # Analyses by state
            cursor.execute('''
                SELECT state, COUNT(*) 
                FROM market_analyses 
                GROUP BY state 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            ''')
            state_stats = dict(cursor.fetchall())
            
            # Price trend distribution
            cursor.execute('''
                SELECT price_trend, COUNT(*) 
                FROM market_analyses 
                GROUP BY price_trend
            ''')
            trend_distribution = dict(cursor.fetchall())
            
            # Average prices by crop
            cursor.execute('''
                SELECT crop, AVG(state_avg_price) 
                FROM market_analyses 
                GROUP BY crop 
                ORDER BY AVG(state_avg_price) DESC
            ''')
            avg_prices = {crop: round(price, 2) for crop, price in cursor.fetchall()}
            
            # Risk level distribution
            cursor.execute('''
                SELECT risk_level, COUNT(*) 
                FROM market_analyses 
                GROUP BY risk_level
            ''')
            risk_distribution = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_analyses': total_analyses,
                'popular_crops': crop_stats,
                'popular_states': state_stats,
                'trend_distribution': trend_distribution,
                'average_prices_by_crop': avg_prices,
                'risk_distribution': risk_distribution
            }
            
        except Exception as e:
            print(f"❌ Database statistics error: {e}")
            return {}

# Global database instance
db = MarketAnalysisDB()

def save_analysis_to_db(analysis_data):
    """Convenience function to save analysis"""
    return db.save_analysis(analysis_data)

def get_analysis_history_from_db(crop=None, state=None, limit=10):
    """Convenience function to get history"""
    return db.get_analysis_history(crop, state, limit)

def get_price_trends_from_db(crop, state, days=30):
    """Convenience function to get price trends"""
    return db.get_price_trends(crop, state, days)

def get_db_statistics():
    """Convenience function to get statistics"""
    return db.get_statistics()

if __name__ == "__main__":
    # Test the database
    print("🧪 Testing Market Analysis Database...")
    
    # Test data
    test_analysis = {
        'crop': 'tomato',
        'state': 'tamil nadu',
        'district': 'coimbatore',
        'state_avg_price': 2691.89,
        'district_avg_price': 2919.18,
        'price_trend': 'decreasing',
        'trend_percentage': -3.86,
        'recommendation': 'Monitor for 1-2 days',
        'prediction_confidence': 0.73,
        'market_data': [{
            'market': 'Tamil Nadu Market',
            'district': 'coimbatore',
            'modal_price': '2691',
            'min_price': '2422',
            'max_price': '2961'
        }],
        'price_volatility': 0.15,
        'risk_level': 'Medium'
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
