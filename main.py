#!/usr/bin/env python3
"""
Google Maps Places Crawler - Main Entry Point for Render Deployment
Tự động tạo database tables và crawl dữ liệu từ Google Maps
"""

import os
import sys
import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import importlib.util

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

def create_tables():
    """Tạo các bảng trong database nếu chưa tồn tại"""
    print("🔧 Creating database tables...")
    
    conn = None
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Kiểm tra tables đã tồn tại chưa
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        if 'place' in existing_tables and 'review' in existing_tables:
            print("✅ Database tables already exist!")
            print(f"📊 Existing tables: {existing_tables}")
            return
        
        # Đọc file SQL và tạo tables
        with open('create_tables.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Thực thi SQL để tạo tables
        cursor.execute(sql_content)
        conn.commit()
        
        print("✅ Database tables created successfully!")
        
        # Kiểm tra tables đã tạo
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        print(f"📊 Tables created: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            cursor.close()
            conn.close()

def check_database_connection():
    """Kiểm tra kết nối database"""
    print("🔍 Checking database connection...")
    
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Database connected successfully!")
        print(f"📊 PostgreSQL version: {version}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def load_crawler_module():
    """Load crawler module từ file có tên đặc biệt"""
    try:
        spec = importlib.util.spec_from_file_location("crawl_info_place", "crawl_info_place (1).py")
        crawl_module = importlib.util.module_from_spec(spec)
        sys.modules["crawl_info_place"] = crawl_module
        spec.loader.exec_module(crawl_module)
        return crawl_module
    except Exception as e:
        print(f"❌ Error loading crawler module: {e}")
        return None

async def run_crawler():
    """Chạy crawler để thu thập dữ liệu"""
    print("🚀 Starting Google Maps Places Crawler...")
    print("📍 Target: Quận 1 & Quận 2")
    print("=" * 60)
    
    # Load crawler module
    crawl_module = load_crawler_module()
    if not crawl_module:
        print("❌ Failed to load crawler module")
        return
    
    # Load URLs từ CSV files
    urls = crawl_module.load_urls_from_specific_files()
    
    if not urls:
        print("❌ No URLs found in CSV files!")
        return
    
    print(f"📊 Total URLs to process: {len(urls)}")
    print(f"⏱️  Estimated time: {len(urls)} minutes (1 minute per URL)")
    print("=" * 60)
    
    # Import playwright functions
    from playwright.async_api import async_playwright
    
    async with async_playwright() as playwright:
        data = await crawl_module.open_place_pages(playwright, urls)
    
    # Thống kê kết quả
    print("\n" + "=" * 60)
    print("🎉 Crawling completed!")
    print("=" * 60)
    print(f"📊 Total places processed: {len(data)}")
    
    successful = len([r for r in data if 'error' not in r])
    errors = len([r for r in data if 'error' in r])
    print(f"✅ Successfully processed: {successful}")
    print(f"❌ Errors: {errors}")
    
    if successful > 0:
        print(f"💾 All data has been saved to PostgreSQL database")
        db_config = get_db_config()
        print(f"🔗 Database: {db_config['host']}:{db_config['port']}/{db_config['database']}")

def main():
    """Main function - entry point cho Render"""
    print("🌟 Google Maps Places Crawler - Render Deployment")
    print("=" * 60)
    
    # Kiểm tra environment variables
    print("🔍 Checking environment variables...")
    db_config = get_db_config()
    print(f"📊 Database config: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    # Kiểm tra kết nối database
    if not check_database_connection():
        print("❌ Cannot connect to database. Please check your environment variables.")
        sys.exit(1)
    
    # Tạo tables
    try:
        create_tables()
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        sys.exit(1)
    
    # Chạy crawler
    try:
        asyncio.run(run_crawler())
    except Exception as e:
        print(f"❌ Crawler failed: {e}")
        sys.exit(1)
    
    print("\n🎉 All tasks completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
