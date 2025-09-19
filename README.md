# Google Maps Places Crawler

Crawler tự động thu thập dữ liệu nhà hàng và reviews từ Google Maps, được tối ưu cho deployment trên Render.

## 🚀 Deploy trên Render

### Cách 1: Sử dụng Render Blueprint (Khuyến nghị)

1. **Fork repository này**
2. **Vào [Render Dashboard](https://dashboard.render.com)**
3. **Click "New" → "Blueprint"**
4. **Connect GitHub repository**
5. **Click "Apply"**

Render sẽ tự động tạo:
- PostgreSQL database (`ggmaps-db`)
- Web service (`google-maps-crawler`)
- Cấu hình environment variables

### Cách 2: Deploy thủ công

1. **Tạo PostgreSQL Database:**
   - Name: `ggmaps-db`
   - Plan: Starter ($7/month)

2. **Tạo Web Service:**
   - Repository: `tuanhqv123/data_review_ggmaps`
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt && playwright install chromium`
   - Start Command: `python main.py`
   - Plan: Starter ($7/month)

3. **Cấu hình Environment Variables:**
   ```
   DATABASE_URL = <connection-string-from-database>
   PYTHONUNBUFFERED = 1
   ```

## 📊 Dữ liệu thu thập

- **194 places** từ Quận 1 & Quận 2 (TP.HCM)
- **Thông tin chi tiết**: tên, địa chỉ, rating, giờ mở cửa, website, phone
- **Reviews**: rating, text, thời gian, reviewer info, photos

## 🔄 Checkpoint System

- Tự động lưu tiến độ crawl
- Resume từ URL cuối cùng nếu bị timeout
- Không mất dữ liệu đã crawl

## 📋 Files chính

- `main.py` - Entry point cho Render
- `crawl_info_place (1).py` - Core crawler logic
- `checkpoint_system.py` - Progress tracking
- `create_tables.sql` - Database schema
- `render.yaml` - Render Blueprint configuration

## 🔍 Monitor Deployment

```bash
# Xem logs
render logs --service google-maps-crawler

# Kết nối database
render psql --database ggmaps-db

# Kiểm tra dữ liệu
SELECT COUNT(*) FROM place;
SELECT COUNT(*) FROM review;
```

## ⏱️ Thời gian crawl

- **~2-3 giờ** để crawl hết 194 URLs
- **30 giây delay** giữa mỗi URL
- **Checkpoint system** đảm bảo không mất dữ liệu

---

**💡 Tip**: Deploy vào giờ ít traffic để tránh rate limiting từ Google Maps.