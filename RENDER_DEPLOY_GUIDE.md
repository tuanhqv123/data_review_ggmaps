# 🚀 Hướng dẫn Deploy Google Maps Crawler lên Render

## ✅ Đã chuẩn bị sẵn sàng:
- ✅ **GitHub Repository**: [https://github.com/tuanhqv123/data_review_ggmaps.git](https://github.com/tuanhqv123/data_review_ggmaps.git)
- ✅ **Checkpoint System**: Tự động lưu tiến độ và có thể resume từ điểm dừng
- ✅ **Timeout Prevention**: Giảm delay giữa các URL (30s thay vì 60s)
- ✅ **Headless Mode**: Tối ưu cho Render environment

## 📋 Bước 1: Tạo PostgreSQL Database

1. Vào [Render Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"PostgreSQL"**
3. Cấu hình:
   - **Name**: `ggmaps-db`
   - **Database**: `ggmaps`
   - **User**: `ggmaps`
   - **Password**: Tạo password mạnh (lưu lại!)
   - **Plan**: Starter ($7/month)
   - **Region**: Singapore (gần Việt Nam)

## 📋 Bước 2: Tạo Web Service

1. Click **"New"** → **"Web Service"**
2. Connect GitHub repository: `tuanhqv123/data_review_ggmaps`
3. Cấu hình:
   - **Name**: `google-maps-crawler`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium`
   - **Start Command**: `python main.py`
   - **Plan**: Starter ($7/month)
   - **Region**: Singapore (cùng region với database)

## 📋 Bước 3: Cấu hình Environment Variables

Trong Web Service settings, thêm các biến môi trường:

```
DB_HOST=<database-host-from-step-1>
DB_PORT=5432
DB_NAME=ggmaps
DB_USER=ggmaps
DB_PASSWORD=<password-from-step-1>
PYTHONUNBUFFERED=1
```

**Lưu ý**: Lấy `DB_HOST` từ PostgreSQL service đã tạo ở bước 1.

## 📋 Bước 4: Deploy và Monitor

1. Click **"Deploy"**
2. Monitor logs để xem quá trình:
   - Database connection
   - Table creation
   - Checkpoint system initialization
   - URL processing progress

## 🔄 Checkpoint System Features:

### ✅ Tự động Resume:
- Nếu service bị timeout → restart sẽ tiếp tục từ URL cuối cùng đã xử lý
- Không mất dữ liệu đã crawl
- Progress được lưu trong `crawl_checkpoint.json`

### 📊 Progress Tracking:
```
📊 Total URLs: 194
📊 Remaining URLs: 150
📊 Progress: 22.68%
```

### 🛡️ Error Handling:
- Failed URLs được ghi lại riêng
- Có thể retry failed URLs sau
- Database integrity được đảm bảo

## 📊 Kết quả mong đợi:

### 🏪 Places Data:
- **194 places** từ Quận 1 & Quận 2
- Thông tin chi tiết: tên, địa chỉ, rating, giờ mở cửa, etc.

### 💬 Reviews Data:
- **Hàng nghìn reviews** với rating, text, thời gian
- **Reviewer information**: tên, profile URL
- **Photos**: URLs của ảnh trong reviews

### ⏱️ Thời gian:
- **~2-3 giờ** để crawl hết 194 URLs
- **30 giây delay** giữa mỗi URL (tối ưu cho Render)

## 🔍 Kiểm tra kết quả:

### Sử dụng Render CLI:
```bash
# Xem logs
render logs --service google-maps-crawler

# Kết nối database
render psql --database ggmaps-db

# Kiểm tra tables
\dt

# Đếm số records
SELECT COUNT(*) FROM place;
SELECT COUNT(*) FROM review;
```

### Truy vấn dữ liệu:
```sql
-- Top 10 places có rating cao nhất
SELECT name, rating, review_count, address 
FROM place 
ORDER BY rating DESC 
LIMIT 10;

-- Reviews mới nhất
SELECT p.name, r.rating, r.text, r.time_datetime
FROM review r
JOIN place p ON r.place_id = p.id
ORDER BY r.time_datetime DESC
LIMIT 10;
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
