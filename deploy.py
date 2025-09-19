#!/usr/bin/env python3
"""
Simple deployment script for Render
"""

import subprocess
import sys

def run_command(command, description):
    """Run command and show result"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout.strip():
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    print("🚀 Deploying Google Maps Crawler to Render")
    print("=" * 50)
    
    # Check Render CLI
    if not run_command("render --version", "Checking Render CLI"):
        print("❌ Render CLI not found. Please install it first.")
        return 1
    
    # Check login
    if not run_command("render whoami", "Checking Render login"):
        print("❌ Not logged in to Render. Please run 'render login' first.")
        return 1
    
    # Push code
    print("\n📤 Pushing code to GitHub...")
    run_command("git add .", "Adding files")
    run_command("git commit -m 'Ready for Render deployment'", "Committing changes")
    run_command("git push origin main", "Pushing to GitHub")
    
    print("\n🎉 Code pushed successfully!")
    print("\n📋 Next steps:")
    print("1. Go to https://dashboard.render.com")
    print("2. Click 'New' → 'Blueprint'")
    print("3. Connect GitHub repository: tuanhqv123/data_review_ggmaps")
    print("4. Click 'Apply' to deploy")
    print("\n✨ Render will automatically:")
    print("   - Create PostgreSQL database")
    print("   - Create Web Service")
    print("   - Configure environment variables")
    print("   - Start crawling 194 URLs")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
