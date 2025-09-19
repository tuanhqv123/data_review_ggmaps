# 🚀 Hướng dẫn Deploy lên Render

## ✅ Hệ thống đã sẵn sàng!

Bạn đã có đầy đủ các file cần thiết để deploy lên Render:

### 📁 Files đã tạo:

- ✅ `main.py` - Entry point cho Render
- ✅ `crawl_info_place (1).py` - Script crawl chính (đã test OK)
- ✅ `create_tables.sql` - Database schema
- ✅ `requirements.txt` - Dependencies (đã loại bỏ undetected-playwright)
- ✅ `render.yaml` - Cấu hình Render deployment
- ✅ `env.example` - Environment variables template
- ✅ `test_connection.py` - Test kết nối database
- ✅ `README.md` - Hướng dẫn chi tiết

## 🌐 Các bước Deploy:

### 1. Push code lên GitHub/GitLab

```bash
git init
git add .
git commit -m "Initial commit - Google Maps Crawler for Render"
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. Tạo Render Account

- Đăng ký tại [render.com](https://render.com)
- Kết nối GitHub/GitLab account

### 3. Deploy từ Repository

- Chọn "New" → "Blueprint"
- Connect repository của bạn
- Render sẽ tự động detect `render.yaml`
- Click "Apply" để deploy

### 4. Render sẽ tự động:

- ✅ Tạo PostgreSQL database service
- ✅ Tạo web service cho crawler
- ✅ Cài đặt dependencies từ `requirements.txt`
- ✅ Cài đặt Playwright browsers
- ✅ Set environment variables từ `render.yaml`
- ✅ Chạy `main.py` để tự động tạo tables và crawl

## 🔧 Cấu hình Render:

### PostgreSQL Service:

- **Name**: ggmaps-database
- **Plan**: Starter (free tier)
- **Database**: ggmaps
- **User**: ggmaps
- **Password**: Auto-generated

### Web Service:

- **Name**: ggmaps-crawler
- **Plan**: Starter (free tier)
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  playwright install chromium
  playwright install-deps
  ```
- **Start Command**: `python main.py`

## 📊 Sau khi Deploy:

### 1. Kiểm tra Logs

- Vào Render Dashboard
- Click vào web service
- Xem logs để theo dõi quá trình crawl

### 2. Kết nối Database từ xa

- Vào PostgreSQL service
- Copy connection string
- Sử dụng để kết nối từ tools như pgAdmin, DBeaver

### 3. Monitor Progress

- Crawler sẽ tự động crawl 194 URLs (Quận 1 & Quận 2)
- Mỗi URL mất khoảng 1 phút
- Tổng thời gian: ~3 giờ

## 🎯 Kết quả mong đợi:

- ✅ **194 places** được crawl từ Google Maps
- ✅ **Hàng nghìn reviews** được lưu vào database
- ✅ **Database** có thể truy cập từ xa
- ✅ **Dữ liệu** sẵn sàng để phân tích

## 🚨 Lưu ý quan trọng:

1. **Free Tier Limits**: Render free tier có giới hạn về thời gian chạy
2. **Rate Limiting**: Google Maps có thể chặn requests nếu quá nhiều
3. **Timeout**: Script có timeout 30 phút, có thể cần tăng nếu crawl lâu
4. **Monitoring**: Theo dõi logs để đảm bảo không có lỗi

## 🔗 Kết nối Database sau khi Deploy:

### Connection String:

```
postgresql://ggmaps:password@host:port/ggmaps
```

### Python Connection:

```python
import psycopg2

conn = psycopg2.connect(
    host="your-render-host",
    port=5432,
    database="ggmaps",
    user="ggmaps",
    password="your-password"
)
```

---

## 🎉 Chúc mừng!

Hệ thống của bạn đã sẵn sàng để deploy lên Render và tự động crawl dữ liệu Google Maps!

**Next Steps:**

1. Push code lên GitHub/GitLab
2. Deploy trên Render
3. Monitor quá trình crawl
4. Kết nối database từ xa để kiểm tra dữ liệu
