#!/usr/bin/env python3
"""
Simple web server để Render có thể health check
"""
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import sys

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Google Maps Crawler</h1><p>Service is running</p>')

def run_web_server():
    """Chạy web server trên port được chỉ định"""
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"🌐 Web server started on port {port}")
    server.serve_forever()

def run_crawler():
    """Chạy crawler trong background"""
    print("🚀 Starting crawler...")
    try:
        # Import và chạy main.py
        import main
        main.main()
    except Exception as e:
        print(f"❌ Crawler error: {e}")

if __name__ == "__main__":
    print("🌟 Google Maps Crawler Web Service")
    print("=" * 50)
    
    # Start crawler trong background thread
    crawler_thread = threading.Thread(target=run_crawler, daemon=True)
    crawler_thread.start()
    
    # Start web server trong main thread
    run_web_server()
