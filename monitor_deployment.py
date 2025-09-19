#!/usr/bin/env python3
"""
Script để monitor deployment trên Render
"""

import subprocess
import time
import sys

def run_render_command(command):
    """Chạy Render CLI command"""
    try:
        result = subprocess.run(f"render {command}", shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_services():
    """Kiểm tra services đang chạy"""
    success, stdout, stderr = run_render_command("services")
    if success:
        print("📊 Render Services:")
        print(stdout)
        return True
    else:
        print(f"❌ Error checking services: {stderr}")
        return False

def check_logs(service_name):
    """Kiểm tra logs của service"""
    success, stdout, stderr = run_render_command(f"logs --service {service_name}")
    if success:
        print(f"📋 Logs for {service_name}:")
        print(stdout[-1000:])  # Last 1000 characters
        return True
    else:
        print(f"❌ Error checking logs: {stderr}")
        return False

def main():
    print("🔍 Monitoring Render Deployment")
    print("=" * 50)
    
    # Kiểm tra services
    if not check_services():
        print("❌ Cannot check services. Make sure you're logged in.")
        return
    
    # Hỏi service name để monitor
    service_name = input("\n📝 Enter service name to monitor (or press Enter for 'google-maps-crawler'): ").strip()
    if not service_name:
        service_name = "google-maps-crawler"
    
    print(f"\n🔄 Monitoring {service_name}...")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            print(f"\n⏰ {time.strftime('%H:%M:%S')} - Checking logs...")
            check_logs(service_name)
            print("\n⏳ Waiting 30 seconds before next check...")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")

if __name__ == "__main__":
    main()
