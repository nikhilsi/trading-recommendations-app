# scripts/maintenance/database_maintenance.py
"""
Database maintenance and optimization script
"""
import psycopg2
from datetime import datetime, timedelta
import os

def connect_to_db():
    """Connect to the database"""
    return psycopg2.connect(
        host="localhost",  # Change to "postgres" if running inside Docker
        port="5432",
        database="trading_app",
        user="trading_user",
        password="trading_password123"
    )

def cleanup_old_data(days_to_keep=30):
    """Clean up old data from the database"""
    print(f"🗄️ Database Maintenance - Cleaning data older than {days_to_keep} days")
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        # Clean old stock prices
        cursor.execute("""
            DELETE FROM stock_prices 
            WHERE created_at < %s
        """, (cutoff_date,))
        old_prices = cursor.rowcount
        
        # Clean old inactive recommendations
        cursor.execute("""
            DELETE FROM recommendations 
            WHERE generated_at < %s AND is_active = FALSE
        """, (cutoff_date,))
        old_recs = cursor.rowcount
        
        conn.commit()
        print(f"✅ Removed {old_prices} old price records")
        print(f"✅ Removed {old_recs} old recommendations")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database cleanup error: {e}")

def vacuum_database():
    """Optimize database performance"""
    print("🔧 Optimizing database performance...")
    
    try:
        conn = connect_to_db()
        conn.autocommit = True
        cursor = conn.cursor()
        
        cursor.execute("VACUUM ANALYZE;")
        print("✅ Database optimized")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database optimization error: {e}")

def get_database_stats():
    """Get database statistics"""
    print("📊 Database Statistics:")
    
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        tables = ['stocks', 'stock_prices', 'recommendations', 'watchlist']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count:,} records")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Stats error: {e}")

if __name__ == "__main__":
    get_database_stats()
    cleanup_old_data(30)
    vacuum_database()
    print("✅ Database maintenance complete!")
