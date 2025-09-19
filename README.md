# Google Maps Places Crawler - Render Deployment

Hệ thống tự động crawl dữ liệu nhà hàng/quán ăn từ Google Maps và lưu vào PostgreSQL database trên Render.

## 🚀 Tính năng

- ✅ Tự động tạo database tables
- ✅ Crawl dữ liệu từ Google Maps (Quận 1 & Quận 2)
- ✅ Lưu trữ vào PostgreSQL database
- ✅ Deploy tự động trên Render
- ✅ Kết nối từ xa để kiểm tra dữ liệu

## 📁 Cấu trúc Project

```
├── main.py                    # Entry point cho Render
├── crawl_info_place (1).py    # Script crawl chính (đã test OK)
├── create_tables.sql          # SQL schema cho database
├── requirements.txt           # Python dependencies
├── render.yaml               # Cấu hình Render deployment
├── env.example               # Environment variables template
├── test_connection.py        # Test kết nối database
├── urls/                    # CSV files chứa URLs
│   ├── urls_nhà_hang_quán_an_Quận_1.csv
│   └── urls_nhà_hang_quán_an_Quận_2.csv
└── README.md                # Hướng dẫn này
```

## 🛠️ Cài đặt Local Development

### 1. Clone repository

```bash
git clone <your-repo-url>
cd data_review_ggmaps
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Thiết lập database (PostgreSQL)

```bash
# Sử dụng Docker Compose
docker-compose up -d

# Hoặc cài đặt PostgreSQL local
# Tạo database: ggmaps
# User: ggmaps, Password: ggmaps
```

### 4. Cấu hình environment variables

```bash
cp env.example .env
# Chỉnh sửa .env với thông tin database của bạn
```

### 5. Test kết nối database

```bash
python test_connection.py
```

### 6. Chạy crawler

```bash
python main.py
```

## 🌐 Deploy lên Render

### 1. Chuẩn bị Repository

- Push code lên GitHub/GitLab
- Đảm bảo có file `render.yaml`

### 2. Tạo Render Account

- Đăng ký tại [render.com](https://render.com)
- Kết nối GitHub/GitLab account

### 3. Deploy từ Repository

- Chọn "New" → "Blueprint"
- Connect repository
- Render sẽ tự động detect `render.yaml`
- Click "Apply" để deploy

### 4. Cấu hình Environment Variables

Render sẽ tự động set các biến môi trường từ `render.yaml`:

- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

## 📊 Database Schema

### Bảng `place`

- `id`: Primary key
- `url`: URL Google Maps
- `name`: Tên địa điểm
- `rating`: Đánh giá (1-5)
- `review_count`: Số lượng đánh giá
- `address`: Địa chỉ
- `website`: Website
- `phone`: Số điện thoại
- `business_hours`: Giờ mở cửa (JSON)
- `accessibility`, `service_options`, `highlights`, etc.: Các thuộc tính khác (Array)

### Bảng `review`

- `id`: Primary key
- `place_id`: Foreign key đến bảng place
- `review_id`: ID đánh giá từ Google Maps
- `reviewer_name`: Tên người đánh giá
- `rating`: Điểm đánh giá
- `time`: Thời gian đánh giá (text)
- `time_datetime`: Thời gian đánh giá (datetime)
- `text`: Nội dung đánh giá
- `photos`: Ảnh đánh giá (Array)

## 🔗 Kết nối Database từ xa

### 1. Lấy thông tin kết nối từ Render Dashboard

- Vào PostgreSQL service trên Render
- Copy connection string hoặc thông tin kết nối

### 2. Kết nối bằng psql

```bash
psql "postgresql://username:password@host:port/database"
```

### 3. Kết nối bằng Python

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

### 4. Kết nối bằng GUI tools

- **pgAdmin**: Import connection string
- **DBeaver**: Tạo PostgreSQL connection
- **TablePlus**: Nhập thông tin kết nối

## 📈 Monitoring & Logs

### Render Dashboard

- Xem logs real-time
- Monitor resource usage
- Check deployment status

### Database Monitoring

```sql
-- Kiểm tra số lượng records
SELECT COUNT(*) FROM place;
SELECT COUNT(*) FROM review;

-- Xem dữ liệu mới nhất
SELECT * FROM place ORDER BY created_at DESC LIMIT 10;
SELECT * FROM review ORDER BY created_at DESC LIMIT 10;
```

## 🚨 Troubleshooting

### Lỗi kết nối database

- Kiểm tra environment variables
- Đảm bảo PostgreSQL service đang chạy
- Check firewall/network settings

### Lỗi Playwright

- Đảm bảo đã install chromium: `playwright install chromium`
- Check browser dependencies

### Lỗi crawl

- Kiểm tra URLs trong CSV files
- Verify Google Maps selectors
- Check rate limiting

## 📞 Support

Nếu gặp vấn đề:

1. Check logs trên Render Dashboard
2. Kiểm tra database connection
3. Verify environment variables
4. Test local development trước khi deploy

## 🎯 Next Steps

Sau khi deploy thành công:

1. Monitor crawler progress
2. Check data quality
3. Set up automated scheduling (nếu cần)
4. Implement data analysis/visualization
5. Add more districts/quận nếu cần

---

**Happy Crawling! 🕷️**
