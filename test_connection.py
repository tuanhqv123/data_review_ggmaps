#!/usr/bin/env python3
"""
Test script để kiểm tra kết nối database từ xa
Sử dụng để verify connection sau khi deploy trên Render
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_config():
    """Lấy cấu hình database từ environment variables"""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'ggmaps'),
        'user': os.getenv('DB_USER', 'ggmaps'),
        'password': os.getenv('DB_PASSWORD', 'ggmaps')
    }

def test_connection():
    """Test kết nối database"""
    print("🔍 Testing database connection...")
    
    db_config = get_db_config()
    print(f"📊 Connecting to: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Test basic connection
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected successfully!")
        print(f"📊 PostgreSQL version: {version}")
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"📋 Tables found: {[table[0] for table in tables]}")
        
        # Check data counts
        if 'place' in [table[0] for table in tables]:
            cursor.execute("SELECT COUNT(*) FROM place;")
            place_count = cursor.fetchone()[0]
            print(f"📍 Places: {place_count} records")
        
        if 'review' in [table[0] for table in tables]:
            cursor.execute("SELECT COUNT(*) FROM review;")
            review_count = cursor.fetchone()[0]
            print(f"💬 Reviews: {review_count} records")
        
        # Show recent data
        if 'place' in [table[0] for table in tables]:
            cursor.execute("""
                SELECT name, rating, review_count, created_at 
                FROM place 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_places = cursor.fetchall()
            print(f"\n🆕 Recent places:")
            for place in recent_places:
                print(f"  - {place[0]} (Rating: {place[1]}, Reviews: {place[2]}, Created: {place[3]})")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Main function"""
    print("🌟 Database Connection Test")
    print("=" * 50)
    
    success = test_connection()
    
    if success:
        print("\n🎉 Database connection test passed!")
        print("✅ You can now connect from remote tools")
    else:
        print("\n❌ Database connection test failed!")
        print("🔧 Please check your environment variables and network settings")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
