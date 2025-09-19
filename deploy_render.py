#!/usr/bin/env python3
"""
Script để deploy lên Render với checkpoint system
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Chạy command và hiển thị kết quả"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    print("🚀 Deploying Google Maps Crawler to Render")
    print("=" * 60)
    
    # Kiểm tra Render CLI
    if not run_command("render --version", "Checking Render CLI"):
        print("❌ Render CLI not found. Please install it first.")
        sys.exit(1)
    
    # Kiểm tra đăng nhập
    if not run_command("render whoami", "Checking Render login"):
        print("❌ Not logged in to Render. Please run 'render login' first.")
        sys.exit(1)
    
    # Push code lên GitHub
    if not run_command("git add .", "Adding files to git"):
        sys.exit(1)
    
    if not run_command("git commit -m 'Add checkpoint system for Render deployment'", "Committing changes"):
        sys.exit(1)
    
    if not run_command("git push origin main", "Pushing to GitHub"):
        sys.exit(1)
    
    print("\n🎉 Code pushed to GitHub successfully!")
    print("📋 Next steps:")
    print("1. Go to https://dashboard.render.com")
    print("2. Create PostgreSQL database")
    print("3. Create Web Service connected to GitHub repo")
    print("4. Configure environment variables")
    print("5. Deploy and monitor logs")
    
    print("\n📊 Expected results:")
    print("- 194 URLs from Quận 1 & Quận 2")
    print("- Checkpoint system prevents data loss")
    print("- Automatic resume from last processed URL")
    print("- Database accessible remotely")

if __name__ == "__main__":
    main()
