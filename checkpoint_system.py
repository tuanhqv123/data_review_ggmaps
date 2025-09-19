"""
Checkpoint System for Google Maps Crawler
Tracks progress and allows resuming from last processed URL
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

CHECKPOINT_FILE = "crawl_checkpoint.json"

class CrawlCheckpoint:
    def __init__(self):
        self.checkpoint_file = CHECKPOINT_FILE
        self.data = self.load_checkpoint()
    
    def load_checkpoint(self) -> Dict:
        """Load checkpoint data from file"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading checkpoint: {e}")
                return self._create_empty_checkpoint()
        return self._create_empty_checkpoint()
    
    def _create_empty_checkpoint(self) -> Dict:
        """Create empty checkpoint structure"""
        return {
            "started_at": None,
            "last_updated": None,
            "total_urls": 0,
            "processed_urls": 0,
            "current_index": 0,
            "processed_places": [],
            "failed_urls": [],
            "status": "not_started"
        }
    
    def save_checkpoint(self):
        """Save current checkpoint to file"""
        try:
            self.data["last_updated"] = datetime.now().isoformat()
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            print(f"✅ Checkpoint saved: {self.data['processed_urls']}/{self.data['total_urls']} URLs processed")
        except Exception as e:
            print(f"❌ Error saving checkpoint: {e}")
    
    def start_crawl(self, total_urls: int):
        """Initialize crawl session"""
        self.data.update({
            "started_at": datetime.now().isoformat(),
            "total_urls": total_urls,
            "processed_urls": 0,
            "current_index": 0,
            "processed_places": [],
            "failed_urls": [],
            "status": "running"
        })
        self.save_checkpoint()
        print(f"🚀 Crawl session started: {total_urls} URLs to process")
    
    def mark_url_processed(self, url: str, place_name: str, success: bool = True):
        """Mark a URL as processed"""
        if success:
            self.data["processed_places"].append({
                "url": url,
                "name": place_name,
                "processed_at": datetime.now().isoformat()
            })
            self.data["processed_urls"] += 1
        else:
            self.data["failed_urls"].append({
                "url": url,
                "failed_at": datetime.now().isoformat()
            })
        
        self.data["current_index"] += 1
        self.save_checkpoint()
    
    def get_remaining_urls(self, all_urls: List[str]) -> List[str]:
        """Get URLs that haven't been processed yet"""
        processed_urls = {place["url"] for place in self.data["processed_places"]}
        failed_urls = {failed["url"] for failed in self.data["failed_urls"]}
        
        remaining = []
        for i, url in enumerate(all_urls):
            if url not in processed_urls and url not in failed_urls:
                remaining.append(url)
        
        return remaining
    
    def get_progress_summary(self) -> Dict:
        """Get current progress summary"""
        total = self.data["total_urls"]
        processed = self.data["processed_urls"]
        failed = len(self.data["failed_urls"])
        remaining = total - processed - failed
        
        return {
            "total": total,
            "processed": processed,
            "failed": failed,
            "remaining": remaining,
            "progress_percent": round((processed / total) * 100, 2) if total > 0 else 0,
            "status": self.data["status"]
        }
    
    def complete_crawl(self):
        """Mark crawl as completed"""
        self.data["status"] = "completed"
        self.data["completed_at"] = datetime.now().isoformat()
        self.save_checkpoint()
        print("🎉 Crawl completed successfully!")
    
    def reset_checkpoint(self):
        """Reset checkpoint to start fresh"""
        self.data = self._create_empty_checkpoint()
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
        print("🔄 Checkpoint reset - ready for fresh start")

# Global checkpoint instance
checkpoint = CrawlCheckpoint()
