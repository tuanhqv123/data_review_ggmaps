#!/usr/bin/env python3
"""
Script tự động deploy lên Render với tất cả services cần thiết
"""

import subprocess
import json
import time
import sys

def run_command(command, description):
    """Chạy command và hiển thị kết quả"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False, e.stderr

def create_postgres_db():
    """Tạo PostgreSQL database trên Render"""
    print("\n🗄️ Creating PostgreSQL Database...")
    print("=" * 50)
    
    # Tạo database với render CLI
    db_command = """
    render services create --type pserv \\
        --name ggmaps-db \\
        --plan starter \\
        --region singapore \\
        --database ggmaps \\
        --user ggmaps \\
        --password $(openssl rand -base64 32)
    """
    
    success, output = run_command(db_command, "Creating PostgreSQL database")
    
    if success:
        print("✅ PostgreSQL database created successfully!")
        print("📋 Database details:")
        print(f"   Name: ggmaps-db")
        print(f"   Database: ggmaps")
        print(f"   User: ggmaps")
        print(f"   Region: Singapore")
        return True
    else:
        print("❌ Failed to create database via CLI")
        print("📋 Please create manually:")
        print("   1. Go to https://dashboard.render.com")
        print("   2. Click 'New' → 'PostgreSQL'")
        print("   3. Configure as shown in RENDER_DEPLOY_GUIDE.md")
        return False

def create_web_service():
    """Tạo Web Service trên Render"""
    print("\n🌐 Creating Web Service...")
    print("=" * 50)
    
    # Tạo web service với render CLI
    web_command = """
    render services create --type web \\
        --name google-maps-crawler \\
        --env python \\
        --region singapore \\
        --build-command "pip install -r requirements.txt && playwright install chromium" \\
        --start-command "python main.py" \\
        --plan starter \\
        --repo https://github.com/tuanhqv123/data_review_ggmaps.git
    """
    
    success, output = run_command(web_command, "Creating Web Service")
    
    if success:
        print("✅ Web Service created successfully!")
        print("📋 Service details:")
        print(f"   Name: google-maps-crawler")
        print(f"   Environment: Python")
        print(f"   Region: Singapore")
        print(f"   Repository: https://github.com/tuanhqv123/data_review_ggmaps.git")
        return True
    else:
        print("❌ Failed to create web service via CLI")
        print("📋 Please create manually:")
        print("   1. Go to https://dashboard.render.com")
        print("   2. Click 'New' → 'Web Service'")
        print("   3. Connect GitHub repository")
        print("   4. Configure as shown in RENDER_DEPLOY_GUIDE.md")
        return False

def configure_environment_variables():
    """Cấu hình environment variables"""
    print("\n⚙️ Configuring Environment Variables...")
    print("=" * 50)
    
    # Lấy database connection info
    print("📋 Please configure environment variables manually:")
    print("   In Web Service settings, add:")
    print("   DB_HOST=<database-host-from-postgres-service>")
    print("   DB_PORT=5432")
    print("   DB_NAME=ggmaps")
    print("   DB_USER=ggmaps")
    print("   DB_PASSWORD=<password-from-postgres-service>")
    print("   PYTHONUNBUFFERED=1")
    
    return True

def monitor_deployment():
    """Monitor deployment progress"""
    print("\n📊 Monitoring Deployment...")
    print("=" * 50)
    
    # Kiểm tra services
    success, output = run_command("render services", "Checking services")
    
    if success:
        print("📋 Available services:")
        print(output)
    
    # Hỏi user có muốn monitor logs không
    monitor = input("\n❓ Do you want to monitor logs? (y/N): ").strip().lower()
    
    if monitor in ['y', 'yes']:
        service_name = input("Enter service name to monitor (default: google-maps-crawler): ").strip()
        if not service_name:
            service_name = "google-maps-crawler"
        
        print(f"\n🔄 Monitoring {service_name} logs...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                success, logs = run_command(f"render logs --service {service_name}", f"Getting logs for {service_name}")
                if success and logs:
                    print(f"\n⏰ {time.strftime('%H:%M:%S')} - Latest logs:")
                    print(logs[-500:])  # Last 500 characters
                print("\n⏳ Waiting 30 seconds...")
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")

def main():
    print("🚀 Auto Deploy Google Maps Crawler to Render")
    print("=" * 60)
    
    # Kiểm tra Render CLI
    success, _ = run_command("render --version", "Checking Render CLI")
    if not success:
        print("❌ Render CLI not found. Please install it first.")
        sys.exit(1)
    
    # Kiểm tra đăng nhập
    success, _ = run_command("render whoami", "Checking Render login")
    if not success:
        print("❌ Not logged in to Render. Please run 'render login' first.")
        sys.exit(1)
    
    # Push code lên GitHub
    print("\n📤 Pushing code to GitHub...")
    run_command("git add .", "Adding files")
    run_command("git commit -m 'Ready for Render deployment'", "Committing changes")
    run_command("git push origin main", "Pushing to GitHub")
    
    # Tạo services
    db_created = create_postgres_db()
    web_created = create_web_service()
    
    # Cấu hình environment variables
    configure_environment_variables()
    
    # Monitor deployment
    if db_created and web_created:
        monitor_deployment()
    
    print("\n🎉 Deployment process completed!")
    print("📋 Next steps:")
    print("   1. Configure environment variables in Web Service")
    print("   2. Deploy the service")
    print("   3. Monitor logs for progress")
    print("   4. Check database for crawled data")

if __name__ == "__main__":
    main()
