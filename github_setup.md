# 📋 Hướng dẫn tạo GitHub Repository

## Bước 1: Tạo Repository trên GitHub

1. Vào [github.com](https://github.com) và đăng nhập
2. Click "New repository" (nút + ở góc phải)
3. Điền thông tin:
   - **Repository name**: `data_review_ggmaps`
   - **Description**: `Google Maps Places Crawler for Restaurant Reviews`
   - **Visibility**: Public
   - **Initialize**: Không check (vì đã có code local)

## Bước 2: Push code lên GitHub

Sau khi tạo repository, GitHub sẽ hiển thị commands. Chạy:

```bash
git remote add origin https://github.com/YOUR_USERNAME/data_review_ggmaps.git
git branch -M main
git push -u origin main
```

## Bước 3: Deploy trên Render

1. Vào [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect GitHub repository `data_review_ggmaps`
4. Cấu hình theo `deploy_instructions.md`

## ✅ Kết quả:

- Code đã được push lên GitHub
- Sẵn sàng deploy trên Render
- Script sẽ tự động crawl 194 URLs và lưu vào database

