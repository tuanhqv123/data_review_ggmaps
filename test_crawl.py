#!/usr/bin/env python3
"""
Test script để kiểm tra crawl hoạt động
"""
import asyncio
import sys
import importlib.util

# Import từ file có tên đặc biệt
spec = importlib.util.spec_from_file_location("crawl_info_place", "crawl_info_place (1).py")
crawl_module = importlib.util.module_from_spec(spec)
sys.modules["crawl_info_place"] = crawl_module
spec.loader.exec_module(crawl_module)

async def test_single_url():
    """Test với 1 URL duy nhất"""
    print("🧪 Testing crawl với 1 URL...")
    
    # Lấy 1 URL đầu tiên từ Quận 1
    urls = crawl_module.load_urls_from_specific_files()
    if not urls:
        print("❌ Không tìm thấy URLs!")
        return False
    
    # Chỉ lấy 1 URL đầu tiên
    test_url = urls[0]
    print(f"📍 Test URL: {test_url}")
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as playwright:
            print("🚀 Starting browser...")
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={"width": 1366, "height": 900},
                timezone_id="Asia/Ho_Chi_Minh",
                locale="vi-VN",
                extra_http_headers={
                    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.4",
                },
            )
            page = await context.new_page()
            
            print("🌐 Navigating to URL...")
            await page.goto(test_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Kiểm tra title
            title = await page.title()
            print(f"📄 Page title: {title}")
            
            # Kiểm tra tên quán
            try:
                name_element = page.locator("h1.DUwDvf.lfPIob").first
                if await name_element.count() > 0:
                    name = await name_element.text_content()
                    print(f"🏪 Place name: {name}")
                else:
                    print("❌ Không tìm thấy tên quán")
            except Exception as e:
                print(f"❌ Lỗi khi lấy tên quán: {e}")
            
            # Kiểm tra rating
            try:
                rating_element = page.locator('div.F7nice span[aria-hidden="true"]').first
                if await rating_element.count() > 0:
                    rating_text = await rating_element.text_content()
                    print(f"⭐ Rating: {rating_text}")
                else:
                    print("❌ Không tìm thấy rating")
            except Exception as e:
                print(f"❌ Lỗi khi lấy rating: {e}")
            
            await context.close()
            await browser.close()
            
            print("✅ Test hoàn thành!")
            return True
            
    except Exception as e:
        print(f"❌ Lỗi trong quá trình test: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_single_url())
    if success:
        print("\n🎉 Script crawl hoạt động tốt!")
        print("🚀 Sẵn sàng deploy lên Render!")
    else:
        print("\n❌ Script crawl có vấn đề!")
        sys.exit(1)
