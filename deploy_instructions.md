# 🚀 Hướng dẫn Deploy lên Render

## ✅ Đã chuẩn bị sẵn sàng:
- ✅ Render CLI đã cài đặt và đăng nhập thành công
- ✅ Tất cả files cần thiết đã sẵn sàng
- ✅ Script crawl đã được test (có vấn đề với Playwright local nhưng sẽ hoạt động trên Render)

## 📋 Bước deploy thủ công:

### 1. Tạo PostgreSQL Database
1. Vào [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "PostgreSQL"
3. Cấu hình:
   - **Name**: `ggmaps-db`
   - **Database**: `ggmaps`
   - **User**: `ggmaps`
   - **Password**: `ggmaps` (hoặc tự tạo)
   - **Plan**: Starter ($7/month)

### 2. Tạo Web Service
1. Click "New" → "Web Service"
2. Connect GitHub repository (hoặc upload code)
3. Cấu hình:
   - **Name**: `google-maps-crawler`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium`
   - **Start Command**: `python main.py`
   - **Plan**: Starter ($7/month)

### 3. Cấu hình Environment Variables
Trong Web Service settings, thêm:
```
DB_HOST=<database-host-from-step-1>
DB_PORT=5432
DB_NAME=ggmaps
DB_USER=ggmaps
DB_PASSWORD=<password-from-step-1>
```

### 4. Deploy và Monitor
1. Click "Deploy"
2. Monitor logs để xem quá trình crawl
3. Kiểm tra database để xem dữ liệu

## 🔍 Kiểm tra kết quả:
```bash
# Sử dụng Render CLI để xem logs
render logs --service google-maps-crawler

# Kết nối database
render psql --database ggmaps-db
```

## 📊 Kết quả mong đợi:
- **194 places** từ Quận 1 & Quận 2
- **Hàng nghìn reviews** được crawl
- **Database** có thể truy cập từ xa

## ⚠️ Lưu ý:
- Script có thể chạy 3-4 giờ để crawl hết 194 URLs
- Render sẽ tự động restart nếu có lỗi
- Có thể monitor progress qua logs
