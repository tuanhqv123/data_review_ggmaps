# 🚀 Deploy Free trên Render

## ✅ Đã tạo thành công:
- **PostgreSQL Database**: `ggmaps-db` (ID: dpg-d36e843ipnbc7393mgjg-a)
- **Database URL**: `postgres://ggmaps_db_user:password@dpg-d36e843ipnbc7393mgjg-a.singapore-postgres.render.com:5432/ggmaps_db`

## 📋 Tạo Web Service Free:

1. **Vào [Render Dashboard](https://dashboard.render.com)**
2. **Click "New" → "Web Service"**
3. **Connect GitHub repository**: `tuanhqv123/data_review_ggmaps`
4. **Cấu hình như sau:**
   ```
   Name: google-maps-crawler
   Environment: Python 3
   Plan: Free
   Region: Singapore
   Build Command: pip install -r requirements.txt && playwright install chromium
   Start Command: python main.py
   ```

5. **Environment Variables:**
   ```
   DATABASE_URL = postgres://ggmaps_db_user:password@dpg-d36e843ipnbc7393mgjg-a.singapore-postgres.render.com:5432/ggmaps_db
   PYTHONUNBUFFERED = 1
   ```

## 🔧 Fix requirements.txt:

Đã fix requirements.txt để tránh lỗi build:
```
psycopg2-binary==2.9.9
playwright==1.40.0
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
```

## 📊 Kết quả mong đợi:

- **194 places** từ Quận 1 & Quận 2
- **Hàng nghìn reviews** chi tiết
- **Checkpoint system** đảm bảo không mất dữ liệu
- **Free hosting** trên Render

## 🔍 Monitor:

Sau khi deploy, sử dụng:
```bash
python3 monitor.py
```

Hoặc vào Render Dashboard để xem logs.

---

**💡 Tip**: Free plan có giới hạn về thời gian chạy, nhưng đủ để crawl 194 URLs.
