# 🚀 Hướng dẫn Deploy Thủ công lên Render

## ✅ Code đã sẵn sàng:
- ✅ GitHub Repository: [https://github.com/tuanhqv123/data_review_ggmaps.git](https://github.com/tuanhqv123/data_review_ggmaps.git)
- ✅ Checkpoint System: Tự động resume từ điểm dừng
- ✅ Optimized for Render: Headless mode, reduced delays

## 📋 Bước 1: Tạo PostgreSQL Database

1. **Vào [Render Dashboard](https://dashboard.render.com)**
2. **Click "New" → "PostgreSQL"**
3. **Cấu hình như sau:**
   ```
   Name: ggmaps-db
   Database: ggmaps
   User: ggmaps
   Password: [Tạo password mạnh - LƯU LẠI!]
   Plan: Starter ($7/month)
   Region: Singapore
   ```
4. **Click "Create Database"**
5. **Lưu lại thông tin kết nối:**
   - Host: `dpg-xxxxx-a.singapore-postgres.render.com`
   - Port: `5432`
   - Database: `ggmaps`
   - User: `ggmaps`
   - Password: `[password bạn đã tạo]`

## 📋 Bước 2: Tạo Web Service

1. **Click "New" → "Web Service"**
2. **Connect GitHub Repository:**
   - Repository: `tuanhqv123/data_review_ggmaps`
   - Branch: `main`
3. **Cấu hình như sau:**
   ```
   Name: google-maps-crawler
   Environment: Python 3
   Region: Singapore (cùng region với database)
   Plan: Starter ($7/month)
   Build Command: pip install -r requirements.txt && playwright install chromium
   Start Command: python main.py
   ```
4. **Click "Create Web Service"**

## 📋 Bước 3: Cấu hình Environment Variables

1. **Vào Web Service settings**
2. **Tab "Environment"**
3. **Thêm các biến sau:**
   ```
   DB_HOST = [host từ PostgreSQL service]
   DB_PORT = 5432
   DB_NAME = ggmaps
   DB_USER = ggmaps
   DB_PASSWORD = [password từ PostgreSQL service]
   PYTHONUNBUFFERED = 1
   ```
4. **Click "Save Changes"**

## 📋 Bước 4: Deploy và Monitor

1. **Click "Deploy"**
2. **Monitor logs để xem tiến trình:**
   - Database connection
   - Table creation
   - Checkpoint initialization
   - URL processing

## 🔍 Sử dụng Render CLI để Monitor:

```bash
# Xem tất cả services
render services

# Xem logs của web service
render logs --service google-maps-crawler

# Kết nối database
render psql --database ggmaps-db

# Kiểm tra tables
\dt

# Đếm records
SELECT COUNT(*) FROM place;
SELECT COUNT(*) FROM review;
```

## 📊 Kết quả mong đợi:

### 🏪 Places Data (194 records):
- Tên quán, địa chỉ, rating
- Giờ mở cửa, website, phone
- Accessibility, amenities, etc.

### 💬 Reviews Data (hàng nghìn records):
- Rating, text, thời gian
- Reviewer name, profile URL
- Photos URLs

### ⏱️ Thời gian:
- **~2-3 giờ** để crawl hết 194 URLs
- **Checkpoint system** đảm bảo không mất dữ liệu

## 🛡️ Checkpoint System Features:

### ✅ Tự động Resume:
- Nếu service bị timeout → restart sẽ tiếp tục từ URL cuối cùng
- Progress được lưu trong `crawl_checkpoint.json`
- Không crawl lại URLs đã xử lý

### 📊 Progress Tracking:
```
📊 Total URLs: 194
📊 Remaining URLs: 150
📊 Progress: 22.68%
✅ Successfully processed: 44
❌ Failed URLs: 0
```

## ⚠️ Troubleshooting:

### Nếu service bị timeout:
1. Service sẽ tự động restart
2. Checkpoint system sẽ resume từ URL cuối cùng
3. Không cần can thiệp thủ công

### Nếu có lỗi database:
1. Kiểm tra environment variables
2. Kiểm tra database connection
3. Xem logs để debug

### Nếu crawl chậm:
1. Đây là bình thường (194 URLs × 30s = ~1.5 giờ minimum)
2. Render có thể chậm hơn local environment
3. Monitor progress qua logs

## 🎉 Kết quả cuối cùng:

Sau khi deploy thành công, bạn sẽ có:
- **Database PostgreSQL** với dữ liệu đầy đủ
- **194 places** từ Quận 1 & Quận 2
- **Hàng nghìn reviews** chi tiết
- **Remote access** để query dữ liệu từ bất kỳ đâu
- **Checkpoint system** đảm bảo không mất dữ liệu

---

**💡 Tip**: Deploy vào giờ ít traffic (đêm/mờ sáng) để tránh rate limiting từ Google Maps.
