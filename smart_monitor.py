#!/usr/bin/env python3
"""
Smart Monitor cho Render Deployment
Tự động phát hiện services và monitor progress
"""

import subprocess
import time
import json
import re
from datetime import datetime

def run_render_command(command):
    """Chạy Render CLI command"""
    try:
        result = subprocess.run(f"render {command}", shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def get_services():
    """Lấy danh sách services"""
    success, stdout, stderr = run_render_command("services")
    if success:
        return stdout
    return None

def get_logs(service_name):
    """Lấy logs của service"""
    success, stdout, stderr = run_render_command(f"logs --service {service_name}")
    if success:
        return stdout
    return None

def analyze_logs(logs):
    """Phân tích logs để tìm progress"""
    if not logs:
        return {}
    
    analysis = {
        "database_connected": False,
        "tables_created": False,
        "checkpoint_initialized": False,
        "urls_processed": 0,
        "total_urls": 0,
        "progress_percent": 0,
        "last_processed_url": "",
        "errors": [],
        "status": "unknown"
    }
    
    # Tìm database connection
    if "Database connected successfully" in logs:
        analysis["database_connected"] = True
    
    # Tìm table creation
    if "Database tables created successfully" in logs or "Database tables already exist" in logs:
        analysis["tables_created"] = True
    
    # Tìm checkpoint info
    if "Checkpoint saved" in logs:
        analysis["checkpoint_initialized"] = True
    
    # Tìm progress info
    progress_match = re.search(r"Progress: (\d+\.?\d*)%", logs)
    if progress_match:
        analysis["progress_percent"] = float(progress_match.group(1))
    
    # Tìm URLs processed
    processed_match = re.search(r"Successfully processed: (\d+)", logs)
    if processed_match:
        analysis["urls_processed"] = int(processed_match.group(1))
    
    # Tìm total URLs
    total_match = re.search(r"Total URLs: (\d+)", logs)
    if total_match:
        analysis["total_urls"] = int(total_match.group(1))
    
    # Tìm last processed URL
    url_match = re.search(r"Processing URL \d+/\d+: (https://[^\s]+)", logs)
    if url_match:
        analysis["last_processed_url"] = url_match.group(1)
    
    # Tìm errors
    error_lines = [line for line in logs.split('\n') if '❌' in line or 'Error' in line]
    analysis["errors"] = error_lines[-5:]  # Last 5 errors
    
    # Xác định status
    if analysis["urls_processed"] > 0:
        if analysis["progress_percent"] >= 100:
            analysis["status"] = "completed"
        else:
            analysis["status"] = "running"
    elif analysis["database_connected"] and analysis["tables_created"]:
        analysis["status"] = "starting"
    else:
        analysis["status"] = "initializing"
    
    return analysis

def print_status(service_name, analysis):
    """In status của service"""
    print(f"\n📊 Status for {service_name}:")
    print("=" * 50)
    
    status_emoji = {
        "initializing": "🔄",
        "starting": "🚀", 
        "running": "⚡",
        "completed": "🎉",
        "error": "❌"
    }
    
    status = analysis.get("status", "unknown")
    print(f"{status_emoji.get(status, '❓')} Status: {status.upper()}")
    
    if analysis.get("database_connected"):
        print("✅ Database: Connected")
    else:
        print("❌ Database: Not connected")
    
    if analysis.get("tables_created"):
        print("✅ Tables: Created")
    else:
        print("❌ Tables: Not created")
    
    if analysis.get("checkpoint_initialized"):
        print("✅ Checkpoint: Initialized")
    else:
        print("❌ Checkpoint: Not initialized")
    
    if analysis.get("total_urls", 0) > 0:
        print(f"📊 Progress: {analysis['urls_processed']}/{analysis['total_urls']} URLs ({analysis['progress_percent']:.1f}%)")
    
    if analysis.get("last_processed_url"):
        print(f"📍 Last URL: {analysis['last_processed_url'][:50]}...")
    
    if analysis.get("errors"):
        print(f"⚠️  Recent errors: {len(analysis['errors'])}")
        for error in analysis["errors"][-2:]:  # Show last 2 errors
            print(f"   - {error.strip()}")

def monitor_services():
    """Monitor tất cả services"""
    print("🔍 Smart Monitor for Render Services")
    print("=" * 50)
    
    # Lấy danh sách services
    services_output = get_services()
    if not services_output:
        print("❌ Cannot get services list")
        return
    
    print("📋 Available services:")
    print(services_output)
    
    # Tìm services liên quan
    services = []
    if "ggmaps-db" in services_output:
        services.append("ggmaps-db")
    if "google-maps-crawler" in services_output:
        services.append("google-maps-crawler")
    
    if not services:
        print("❌ No relevant services found")
        print("📋 Please create services first:")
        print("   1. PostgreSQL database: ggmaps-db")
        print("   2. Web service: google-maps-crawler")
        return
    
    print(f"\n🎯 Monitoring {len(services)} services: {', '.join(services)}")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Checking services...")
            
            for service in services:
                logs = get_logs(service)
                if logs:
                    analysis = analyze_logs(logs)
                    print_status(service, analysis)
                else:
                    print(f"❌ Cannot get logs for {service}")
            
            print("\n⏳ Waiting 60 seconds before next check...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")

def main():
    print("🚀 Smart Monitor for Google Maps Crawler")
    print("=" * 50)
    
    # Kiểm tra Render CLI
    success, _, _ = run_render_command("--version")
    if not success:
        print("❌ Render CLI not found. Please install it first.")
        return
    
    # Kiểm tra đăng nhập
    success, _, _ = run_render_command("whoami")
    if not success:
        print("❌ Not logged in to Render. Please run 'render login' first.")
        return
    
    # Bắt đầu monitor
    monitor_services()

if __name__ == "__main__":
    main()
