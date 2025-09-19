import asyncio
import json
import re
import random
import psycopg2
import csv
import os
import glob
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from playwright.async_api import async_playwright, Playwright
from datetime import datetime, timedelta


# Database connection parameters - sử dụng environment variables
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_config():
    """Lấy cấu hình database từ environment variables"""
    # Ưu tiên DATABASE_URL từ Render
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return {'connection_string': database_url}
    
    # Fallback cho local development
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'ggmaps'),
        'user': os.getenv('DB_USER', 'ggmaps'),
        'password': os.getenv('DB_PASSWORD', 'ggmaps')
    }

DB_CONFIG = get_db_config()


def connect_to_db():
    """Connect to PostgreSQL database"""
    try:
        # Sử dụng connection string hoặc individual parameters
        if 'connection_string' in DB_CONFIG:
            conn = psycopg2.connect(DB_CONFIG['connection_string'])
        else:
            conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def insert_place(conn, place_data: dict) -> int:
    """Insert place data and return place_id"""
    cursor = conn.cursor()
    
    try:
        # Insert place data
        place_query = """
        INSERT INTO place (
            url, name, rating, review_count, address, website, phone,
            business_hours, accessibility, service_options, highlights,
            popular_for, offerings, dining_options, amenities, atmosphere,
            crowd, planning, payments, children, parking
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id;
        """
        
        cursor.execute(place_query, (
            place_data.get('url'),
            place_data.get('name'),
            place_data.get('rating'),
            place_data.get('review_count'),
            place_data.get('address'),
            place_data.get('website'),
            place_data.get('phone'),
            json.dumps(place_data.get('business_hours', {})),
            place_data.get('accessibility', []),
            place_data.get('service_options', []),
            place_data.get('highlights', []),
            place_data.get('popular_for', []),
            place_data.get('offerings', []),
            place_data.get('dining_options', []),
            place_data.get('amenities', []),
            place_data.get('atmosphere', []),
            place_data.get('crowd', []),
            place_data.get('planning', []),
            place_data.get('payments', []),
            place_data.get('children', []),
            place_data.get('parking', [])
        ))
        
        place_id = cursor.fetchone()[0]
        conn.commit()
        return place_id
        
    except Exception as e:
        print(f"Error inserting place: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()


def insert_reviews(conn, place_id: int, reviews: list):
    """Insert reviews for a place"""
    cursor = conn.cursor()
    
    try:
        review_query = """
        INSERT INTO review (
            place_id, review_id, reviewer_name, reviewer_profile_url,
            rating, time, time_datetime, text, owner_response, review_details, photos
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON CONFLICT (review_id) DO NOTHING;
        """
        
        for review in reviews:
            cursor.execute(review_query, (
                place_id,
                review.get('review_id'),
                review.get('reviewer_name'),
                review.get('reviewer_profile_url'),
                review.get('rating'),
                review.get('time'),
                review.get('time_datetime'),
                review.get('text'),
                review.get('owner_response'),
                json.dumps(review.get('review_details', {})),
                review.get('photos', [])
            ))
        
        conn.commit()
        print(f"Inserted {len(reviews)} reviews for place_id {place_id}")
        
    except Exception as e:
        print(f"Error inserting reviews: {e}")
        conn.rollback()
    finally:
        cursor.close()


def save_to_database(place_data: dict):
    """Save place data to PostgreSQL database"""
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        # Insert place
        place_id = insert_place(conn, place_data)
        if not place_id:
            print(f"Failed to insert place: {place_data.get('name')}")
            return False
        
        # Insert reviews
        reviews = place_data.get('reviews', [])
        if reviews:
            insert_reviews(conn, place_id, reviews)
        
        print(f"Successfully saved place to database: {place_data.get('name')}")
        return True
        
    except Exception as e:
        print(f"Error saving to database: {e}")
        return False
    finally:
        conn.close()


async def _get_text(page, selectors: list[str]) -> str:
    for sel in selectors:
        locator = page.locator(sel).first
        try:
            if await locator.count() > 0:
                text = await locator.text_content()
                if text:
                    return text.strip()
        except Exception:
            continue
    return ""


async def _get_attr(page, selectors: list[str], attr_name: str) -> str:
    for sel in selectors:
        locator = page.locator(sel).first
        try:
            if await locator.count() > 0:
                val = await locator.get_attribute(attr_name)
                if val:
                    return val.strip()
        except Exception:
            continue
    return ""


def _parse_float(text: str) -> float | None:
    if not text:
        return None
    match = re.search(r"\d+(?:[\.,]\d+)?", text)
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def _parse_reviews_count(text: str) -> int | None:
    if not text:
        return None
    match = re.search(r"\d{1,3}(?:[.,]\d{3})*|\d+", text)
    if not match:
        return None
    return int(match.group(0).replace(".", "").replace(",", ""))


def _parse_relative_time(time_text: str) -> datetime | None:
    """
    Chuyển đổi thời gian tương đối thành datetime thực tế
    Ví dụ: "2 tháng trước" -> datetime object
    """
    if not time_text:
        return None
    
    # Làm sạch text
    time_text = time_text.strip().lower()
    
    # Loại bỏ "Thời gian chỉnh sửa:" nếu có
    if "thời gian chỉnh sửa:" in time_text:
        time_text = time_text.replace("thời gian chỉnh sửa:", "").strip()
    
    now = datetime.now()
    
    # Mapping tiếng Việt
    time_mapping = {
        'giây': 'second',
        'phút': 'minute', 
        'giờ': 'hour',
        'ngày': 'day',
        'tuần': 'week',
        'tháng': 'month',
        'năm': 'year'
    }
    
    # Regex patterns
    patterns = [
        # "2 tháng trước", "3 ngày trước"
        (r'(\d+)\s+(giây|phút|giờ|ngày|tuần|tháng|năm)\s+trước', 1),
        # "một tuần trước", "một năm trước"
        (r'một\s+(giây|phút|giờ|ngày|tuần|tháng|năm)\s+trước', 2),
    ]
    
    for pattern, group_num in patterns:
        match = re.search(pattern, time_text)
        if match:
            if group_num == 1:
                # Pattern có số
                try:
                    number = int(match.group(1))
                except:
                    number = 1
                unit = match.group(2)
            else:
                # Pattern "một"
                number = 1
                unit = match.group(1)
            
            # Chuyển đổi unit
            if unit in time_mapping:
                unit = time_mapping[unit]
            else:
                continue
            
            # Tính toán datetime
            if unit == 'second':
                return now - timedelta(seconds=number)
            elif unit == 'minute':
                return now - timedelta(minutes=number)
            elif unit == 'hour':
                return now - timedelta(hours=number)
            elif unit == 'day':
                return now - timedelta(days=number)
            elif unit == 'week':
                return now - timedelta(weeks=number)
            elif unit == 'month':
                # Xấp xỉ 30 ngày cho 1 tháng
                return now - timedelta(days=number * 30)
            elif unit == 'year':
                # Xấp xỉ 365 ngày cho 1 năm
                return now - timedelta(days=number * 365)
    
    # Nếu không match được pattern nào
    return None


async def _extract_business_hours(page) -> dict[str, str]:
    # Try to expand weekly open hours if the toggle exists
    toggle_selectors = [
        'button[aria-label*="Show open hours"]',
        'span.puWIL.hKrmvd.google-symbols.OazX1c[aria-label*="Show open hours"]',
        'span[role="img"][aria-label*="Show open hours"]',
        'button[aria-label*="Giờ mở cửa"]',
        'span[role="img"][aria-label*="Giờ mở cửa"]',
    ]

    for sel in toggle_selectors:
        try:
            loc = page.locator(sel).first
            if await loc.count() > 0:
                await loc.click()
                await page.wait_for_timeout(500)
                break
        except Exception:
            continue

    # Wait for the hours table to be present (if available)
    try:
        await page.wait_for_selector('table.eK4R0e', timeout=3000)
    except Exception:
        pass

    hours: dict[str, str] = {}
    rows = page.locator('table.eK4R0e tr.y0skZc')
    try:
        count = await rows.count()
    except Exception:
        count = 0

    for i in range(count):
        # Day name
        day_text = await _get_text(
            page,
            [
                f'table.eK4R0e tr.y0skZc:nth-child({i+1}) td.ylH6lf div',
                f'table.eK4R0e tr.y0skZc:nth-child({i+1}) td.ylH6lf',
            ],
        )
        day = day_text or f'Day_{i+1}'

        # Hours string: prefer aria-label on the hours cell
        cell_selector = f'table.eK4R0e tr.y0skZc:nth-child({i+1}) td.mxowUb'
        aria = await _get_attr(page, [cell_selector], 'aria-label')
        if not aria:
            aria = await _get_text(
                page,
                [
                    f'{cell_selector} li.G8aQO',
                    cell_selector,
                ],
            )

        hours[day] = aria.strip() if aria else ""

    return hours


async def _go_to_about_tab(page) -> None:
    # Try clicking the About tab by aria-label or visible text
    selectors = [
        'button[role="tab"][aria-label^="Giới thiệu "]',
        'button[role="tab"]:has-text("Giới thiệu")',
        'div.Gpq6kf:has-text("Giới thiệu")',
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if await loc.count() > 0:
                await loc.click()
                await page.wait_for_timeout(300)  # Reduced from 500
                break
        except Exception:
            continue


async def _extract_about_list(page, heading_text: str) -> list[str]:
    # Find the section by heading
    section_locator = page.locator(f'div.iP2t7d:has(h2.iL3Qke:has-text("{heading_text}"))')
    try:
        if await section_locator.count() == 0:
            return []
    except Exception:
        return []

    items_locator = section_locator.locator('ul.ZQ6we li.hpLkke')
    items: list[str] = []
    try:
        count = await items_locator.count()
    except Exception:
        count = 0

    for i in range(count):
        # Prefer aria-label within span after icon
        label = await _get_attr(page, [f'div.iP2t7d:has(h2.iL3Qke:has-text("{heading_text}")) ul.ZQ6we li.hpLkke:nth-child({i+1}) span[aria-label]'], 'aria-label')
        if not label:
            label = await _get_text(page, [f'div.iP2t7d:has(h2.iL3Qke:has-text("{heading_text}")) ul.ZQ6we li.hpLkke:nth-child({i+1})'])
        if label:
            items.append(label)
    return items


async def _go_to_reviews_tab(page) -> None:
    selectors = [
        'button[role="tab"][aria-label^="Bài đánh giá "]',
        'button[role="tab"]:has-text("Bài đánh giá")',
        'div.Gpq6kf:has-text("Bài đánh giá")',
        'button[role="tab"][aria-label^="Reviews "]',
        'button[role="tab"]:has-text("Reviews")',
        'div.Gpq6kf:has-text("Reviews")',
    ]
    found_tab = False
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if await loc.count() > 0:
                await loc.click()
                print(f"Clicked on reviews tab with selector: {sel}")
                await page.wait_for_timeout(2000)  # Increased wait time
                found_tab = True
                break
        except Exception as e:
            print(f"Error clicking tab with selector {sel}: {e}")
            continue
    
    if not found_tab:
        print("Could not find reviews tab, trying alternative approach")
        # Try to find any tab-like element that might be the reviews tab
        try:
            tab_elements = page.locator('button[role="tab"]')
            tab_count = await tab_elements.count()
            print(f"Found {tab_count} tab elements")
            # Try clicking the last tab, which is often the reviews tab
            if tab_count > 0:
                await tab_elements.last.click()
                print("Clicked on last tab element")
                await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Error with alternative tab approach: {e}")


async def _extract_reviews(page, max_reviews: int = 5) -> list[dict]:
    reviews: list[dict] = []
    print("Starting review extraction...")
    
    # Wait for review elements to load
    try:
        await page.wait_for_selector('div.jftiEf', timeout=10000)
        print("Review containers loaded")
    except Exception as e:
        print(f"Timeout waiting for review containers: {e}")
        return reviews
    
    # Try to find all review containers directly
    review_containers = page.locator('div.jftiEf')
    try:
        total_count = await review_containers.count()
        print(f"Found {total_count} review containers")
    except Exception as e:
        print(f"Error counting review containers: {e}")
        return reviews
    
    actual_count = min(total_count, max_reviews)
    print(f"Will extract {actual_count} reviews")
    
    for i in range(actual_count):
        try:
            print(f"Processing review {i+1}/{actual_count}")
            container = review_containers.nth(i)
            
            # Get review ID
            review_id = await container.get_attribute('data-review-id')
            if not review_id:
                print(f"No review ID found for review {i+1}")
                continue
                
            print(f"Review ID: {review_id}")
            
            # Get reviewer name
            try:
                name_element = container.locator('div.d4r55')
                if await name_element.count() > 0:
                    name = await name_element.first.text_content()
                    name = name.strip() if name else ""
                else:
                    name = ""
            except Exception as e:
                print(f"Error getting reviewer name: {e}")
                name = ""
            
            # Get rating
            try:
                rating_element = container.locator('span.kvMYJc[aria-label]')
                if await rating_element.count() > 0:
                    rating_label = await rating_element.first.get_attribute('aria-label')
                    rating_value = _parse_float(rating_label or '')
                else:
                    rating_value = None
            except Exception as e:
                print(f"Error getting rating: {e}")
                rating_value = None
            
            # Get time
            try:
                time_element = container.locator('span.rsqaWe')
                if await time_element.count() > 0:
                    time_text = await time_element.first.text_content()
                    time_text = time_text.strip() if time_text else ""
                else:
                    time_text = ""
            except Exception as e:
                print(f"Error getting time: {e}")
                time_text = ""
            
            # Convert relative time to datetime
            review_datetime = _parse_relative_time(time_text)
            
            # Click "More" button if it exists
            try:
                more_button = container.locator('button.w8nwRe.kyuRq')
                if await more_button.count() > 0:
                    print(f"Clicking 'More' button for review {review_id}")
                    await more_button.first.click(timeout=1000)
                    await page.wait_for_timeout(500)  # Increased wait time
            except Exception as e:
                print(f"Could not click 'More' button: {e}")
            
            # Get review text
            try:
                text_element = container.locator('div.MyEned')
                if await text_element.count() > 0:
                    review_text = await text_element.first.text_content()
                    review_text = review_text.strip() if review_text else ""
                else:
                    review_text = ""
            except Exception as e:
                print(f"Error getting review text: {e}")
                review_text = ""

            # Extract structured detail chips and clean the review text
            try:
                review_details, removal_snippets = await _extract_review_details(container)
                review_text = _strip_detail_snippets_from_text(review_text, removal_snippets)
            except Exception as e:
                print(f"Error extracting review details: {e}")
                review_details = {}
            
            # Try to get profile URL
            try:
                profile_link = container.locator('button.al6Kxe')
                if await profile_link.count() > 0:
                    profile_url = await profile_link.first.get_attribute('data-href')
                else:
                    profile_url = ""
            except Exception as e:
                print(f"Error getting profile URL: {e}")
                profile_url = ""
            
            # Extract photos
            try:
                photos = await _extract_review_photos(container)
            except Exception as e:
                print(f"Error extracting photos for review {review_id}: {e}")
                photos = []

            # Create review object
            review_obj = {
                'review_id': review_id,
                'reviewer_name': name,
                'reviewer_profile_url': profile_url,
                'rating': rating_value,
                'time': time_text,  # Giữ nguyên text gốc
                'time_datetime': review_datetime,  # Thêm datetime đã chuyển đổi
                'text': review_text,
                'owner_response': "",
                'review_details': review_details,
                'photos': photos
            }
            
            reviews.append(review_obj)
            print(f"Successfully extracted review {i+1}")
            
        except Exception as e:
            print(f"Error processing review {i+1}: {e}")
            continue
    
    print(f"Finished extracting reviews. Total: {len(reviews)}")
    return reviews


async def _extract_review_details(container) -> tuple[dict[str, str], list[str]]:
    """Extract structured review detail chips (e.g., Đồ ăn, Dịch vụ, Bầu không khí, Độ ồn, ...)
    from a single review container. Also returns a list of text snippets that can be
    removed from the free-form review text.

    The DOM often looks like groups `div.PBK6be`, each containing two rows: a bold label
    and a value row; sometimes it's a single row like "Đồ ăn: 4".
    """
    details: dict[str, str] = {}
    removal_snippets: list[str] = []

    try:
        blocks = container.locator('div.PBK6be')
        block_count = await blocks.count()
    except Exception:
        block_count = 0

    for i in range(block_count):
        block = blocks.nth(i)
        # Try to read label/value spans
        try:
            spans = block.locator('span.RfDO5c')
            span_count = await spans.count()
        except Exception:
            span_count = 0

        texts: list[str] = []
        for j in range(span_count):
            try:
                t = await spans.nth(j).text_content()
                if t:
                    texts.append(t.strip())
            except Exception:
                continue

        if not texts:
            # Fallback: take the whole block text
            try:
                t = await block.text_content()
                if t:
                    texts = [t.strip()]
            except Exception:
                pass

        if not texts:
            continue

        label = ""
        value = ""
        if len(texts) >= 2:
            label = texts[0].rstrip(":").strip()
            value = texts[1].strip()
        else:
            # Single line form: "Đồ ăn: 4" or just a label
            m = re.match(r"^([^:]+):\s*(.+)$", texts[0])
            if m:
                label = m.group(1).strip()
                value = m.group(2).strip()
            else:
                label = texts[0].strip()
                value = ""

        if label:
            details[label] = value
            if value:
                removal_snippets.append(f"{label}{value}")
                removal_snippets.append(f"{label}: {value}")
            else:
                removal_snippets.append(label)

    return details, removal_snippets


def _strip_detail_snippets_from_text(text: str, snippets: list[str]) -> str:
    """Remove known detail substrings from the free-form review text and tidy spaces."""
    if not text:
        return text
    cleaned = text
    for s in snippets:
        if s:
            cleaned = cleaned.replace(s, " ")

    # Extra safety: remove common Vietnamese headings if left hanging
    common_labels = [
        "Đồ ăn",
        "Dịch vụ",
        "Bầu không khí",
        "Độ ồn",
        "Quy mô nhóm",
        "Những món ăn đề xuất",
        "Loại hình bữa ăn",
        "Giá mỗi người",
    ]
    for k in common_labels:
        cleaned = re.sub(rf"{re.escape(k)}\s*", " ", cleaned)

    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned


async def _extract_review_photos(container) -> list[str]:
    """Extract photo URLs from a review container.
    Photos are typically in buttons with class 'Tya61d' inside a div 'KtCyie'.
    The URLs are in the background-image style attribute.
    """
    photos: list[str] = []
    
    try:
        # Look for the photos container
        photos_container = container.locator('div.KtCyie')
        if await photos_container.count() == 0:
            return photos
        
        # Find all photo buttons
        photo_buttons = photos_container.locator('button.Tya61d')
        button_count = await photo_buttons.count()
        
        for i in range(button_count):
            try:
                button = photo_buttons.nth(i)
                # Get the background-image URL from style attribute
                style_attr = await button.get_attribute('style')
                if style_attr:
                    # Extract URL from background-image: url("...")
                    url_match = re.search(r'background-image:\s*url\("([^"]+)"\)', style_attr)
                    if url_match:
                        photo_url = url_match.group(1)
                        photos.append(photo_url)
            except Exception as e:
                print(f"Error extracting photo {i+1}: {e}")
                continue
                
    except Exception as e:
        print(f"Error extracting photos: {e}")
    
    return photos


async def _scroll_reviews_to_end(page) -> None:
    """Scroll through the reviews container until it can't scroll anymore.
    This ensures we load all available reviews before extraction.
    """
    print("Starting to scroll reviews to load all content...")
    
    # Try to find the reviews container
    container_selectors = [
        'div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde',
        'div[aria-label="Reviews"]',
        'div.m6QErb.DxyBCb.kA9KIf.dS8AEf',
    ]
    
    container = None
    for sel in container_selectors:
        try:
            loc = page.locator(sel).first
            if await loc.count() > 0:
                container = loc
                print(f"Found reviews container with selector: {sel}")
                break
        except Exception:
            continue
    
    if not container:
        print("Could not find reviews container, using page scroll")
        # Fallback to page scroll if container not found
        await _scroll_page_until_end(page)
        return
    
    # Scroll the reviews container until we can't scroll anymore
    previous_height = 0
    scroll_attempts = 0
    max_attempts = 50  # Prevent infinite scrolling
    
    while scroll_attempts < max_attempts:
        try:
            # Get current scroll height
            current_height = await container.evaluate('el => el.scrollHeight')
            
            if current_height == previous_height:
                # No more content to load
                print(f"Reached end of reviews (height: {current_height})")
                break
            
            # Scroll to bottom of container
            await container.evaluate('el => el.scrollTo(0, el.scrollHeight)')
            print(f"Scrolled reviews container (attempt {scroll_attempts + 1}, height: {current_height})")
            
            # Wait for new content to load with random delay (0.5 to 1 second)
            random_delay = random.uniform(0.5, 1.0)
            await page.wait_for_timeout(int(random_delay * 1000))
            
            previous_height = current_height
            scroll_attempts += 1
            
        except Exception as e:
            print(f"Error scrolling reviews container: {e}")
            # Try alternative scroll method
            try:
                await container.evaluate('el => el.scrollBy(0, 500)')
                random_delay = random.uniform(0.5, 1.0)
                await page.wait_for_timeout(int(random_delay * 1000))
            except Exception:
                break
            scroll_attempts += 1
    
    print(f"Finished scrolling reviews after {scroll_attempts} attempts")


async def _scroll_page_until_end(page) -> None:
    """Fallback: scroll the entire page until we can't scroll anymore."""
    print("Using page scroll fallback...")
    
    previous_height = 0
    scroll_attempts = 0
    max_attempts = 30
    
    while scroll_attempts < max_attempts:
        try:
            # Get current page height
            current_height = await page.evaluate('document.body.scrollHeight')
            
            if current_height == previous_height:
                print(f"Reached end of page (height: {current_height})")
                break
            
            # Scroll down
            await page.evaluate('window.scrollBy(0, 800)')
            print(f"Scrolled page (attempt {scroll_attempts + 1}, height: {current_height})")
            
            # Wait for content to load with random delay (0.5 to 1 second)
            random_delay = random.uniform(0.5, 1.0)
            await page.wait_for_timeout(int(random_delay * 1000))
            
            previous_height = current_height
            scroll_attempts += 1
            
        except Exception as e:
            print(f"Error scrolling page: {e}")
            break
    
    print(f"Finished page scrolling after {scroll_attempts} attempts")


def _force_vi_lang(url: str) -> str:
    try:
        parsed = urlparse(url)
        query_pairs = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query_pairs["hl"] = "vi"
        new_query = urlencode(query_pairs)
        netloc = parsed.netloc
        if netloc.startswith("www.google.com"):
            netloc = "www.google.com.vn"
        rebuilt = parsed._replace(netloc=netloc, query=new_query)
        return urlunparse(rebuilt)
    except Exception:
        return url


def load_urls_from_specific_files() -> list[str]:
    """
    Load URLs from specific CSV files: Quận 1 and Quận 2
    """
    urls = []
    
    # Specific files to crawl
    csv_files = [
        "urls/urls_nhà_hang_quán_an_Quận_1.csv",
        "urls/urls_nhà_hang_quán_an_Quận_2.csv"
    ]
    
    print(f"Loading URLs from 2 specific CSV files")
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            print(f"Reading URLs from: {os.path.basename(csv_file)}")
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    file_urls = [row['url'] for row in reader if row.get('url')]
                    urls.extend(file_urls)
                    print(f"  - Loaded {len(file_urls)} URLs from {os.path.basename(csv_file)}")
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
                continue
        else:
            print(f"File not found: {csv_file}")
    
    print(f"Total URLs loaded: {len(urls)}")
    return urls


async def open_place_pages_with_checkpoint(playwright: Playwright, urls: list[str]) -> list[dict]:
    """Version với checkpoint system để tránh timeout và có thể resume"""
    from checkpoint_system import checkpoint
    
    browser = await playwright.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    context = await browser.new_context(
        viewport={"width": 1366, "height": 900},
        timezone_id="Asia/Ho_Chi_Minh",
        locale="vi-VN",
        extra_http_headers={
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.4",
        },
    )
    page = await context.new_page()

    results: list[dict] = []
    for idx, url in enumerate(urls, start=1):
        try:
            print(f"\n{'='*60}")
            print(f"Processing URL {idx}/{len(urls)}: {url}")
            print(f"{'='*60}")
            
            target_url = _force_vi_lang(url)
            await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)

            # Ensure title appears
            await page.wait_for_selector("h1.DUwDvf.lfPIob", timeout=15000)
            await page.wait_for_timeout(10)

            name = await _get_text(page, ["h1.DUwDvf.lfPIob"])
            
            if not name:
                print(f"❌ Could not extract name for URL: {url}")
                checkpoint.mark_url_processed(url, "", success=False)
                continue

            rating_text = await _get_text(page, ['div.F7nice span[aria-hidden="true"]'])
            rating = _parse_float(rating_text)

            reviews_label = await _get_attr(page, [
                'div.F7nice span[aria-label*="bài đánh giá"]',
                'div.F7nice span[aria-label*="review"]',
            ], attr_name="aria-label")
            if not reviews_label:
                reviews_label = await _get_text(page, ['div.F7nice span[aria-label*="bài đánh giá"]', 'div.F7nice span[aria-label*="review"]'])
            review_count = _parse_reviews_count(reviews_label)

            address = await _get_text(page, [
                'button[data-item-id="address"] div.Io6YTe',
                'button[data-item-id="address"]',
            ])

            website_url = await _get_attr(page, [
                'a[data-item-id="authority"]',
                'a.CsEnBe[data-item-id="authority"]',
                'a[aria-label^="Website:"]',
                'a[aria-label*="Website"]',
            ], attr_name="href")

            tel_href = await _get_attr(page, ['a[href^="tel:"]'], 'href')
            if tel_href:
                phone = tel_href.replace('tel:', '').strip()
            else:
                phone = await _get_text(page, [
                    'button[data-item-id^="phone"] div.Io6YTe',
                    'a[data-item-id^="phone"] div.Io6YTe',
                    'button[aria-label*="Phone"] div.Io6YTe',
                    'a[aria-label*="Phone"] div.Io6YTe',
                ])

            business_hours = await _extract_business_hours(page)
            await _go_to_about_tab(page)
            await asyncio.sleep(5)

            accessibility = await _extract_about_list(page, "Phù hợp cho người khuyết tật")
            service_options = await _extract_about_list(page, "Các tùy chọn dịch vụ")
            highlights = await _extract_about_list(page, "Điểm nổi bật")
            popular_for = await _extract_about_list(page, "Nổi tiếng về")
            offerings = await _extract_about_list(page, "Dịch vụ")
            dining_options = await _extract_about_list(page, "Lựa chọn ăn uống")
            amenities = await _extract_about_list(page, "Tiện nghi")
            atmosphere = await _extract_about_list(page, "Bầu không khí")
            crowd = await _extract_about_list(page, "Khách hàng")
            planning = await _extract_about_list(page, "Lên kế hoạch")
            payments = await _extract_about_list(page, "Thanh toán")
            children = await _extract_about_list(page, "Trẻ em")
            parking = await _extract_about_list(page, "Bãi đỗ xe")

            await _go_to_reviews_tab(page)
            print("Navigated to Reviews tab")
            await page.wait_for_timeout(3000)
            await _scroll_reviews_to_end(page)

            reviews = await _extract_reviews(page, max_reviews=review_count)
            print(f"Extracted {len(reviews)} reviews")
            
            result = {
                "url": url,
                "name": name,
                "rating": rating,
                "review_count": review_count,
                "address": address,
                "website": website_url,
                "phone": phone,
                "business_hours": business_hours,
                "accessibility": accessibility,
                "service_options": service_options,
                "highlights": highlights,
                "popular_for": popular_for,
                "offerings": offerings,
                "dining_options": dining_options,
                "amenities": amenities,
                "atmosphere": atmosphere,
                "crowd": crowd,
                "planning": planning,
                "payments": payments,
                "children": children,
                "parking": parking,
                "reviews": reviews,
            }
            
            # Save to database
            try:
                success = save_to_database(result)
                if success:
                    checkpoint.mark_url_processed(url, name, success=True)
                    print(f"✅ Data saved to database for place {idx}: {name}")
                else:
                    checkpoint.mark_url_processed(url, name, success=False)
                    print(f"❌ Failed to save data to database for place {idx}: {name}")
            except Exception as e:
                checkpoint.mark_url_processed(url, name, success=False)
                print(f"❌ Could not save data to database: {e}")
            
            results.append(result)
            print(f"✅ Captured [{idx}/{len(urls)}]: {name}")
            
            # Add delay before next URL (except for the last one)
            if idx < len(urls):
                print(f"⏳ Waiting 30 seconds before next URL...")
                await asyncio.sleep(30)  # Reduced delay for Render
                
        except Exception as e:
            print(f"Failed to open URL #{idx}: {url} -> {e}")
            checkpoint.mark_url_processed(url, "", success=False)
            error_result = {
                "url": url,
                "error": str(e),
            }
            results.append(error_result)

    await context.close()
    await browser.close()
    return results

async def open_place_pages(playwright: Playwright, urls: list[str]) -> list[dict]:
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

    results: list[dict] = []
    for idx, url in enumerate(urls, start=1):
        try:
            print(f"\n{'='*60}")
            print(f"Processing URL {idx}/{len(urls)}: {url}")
            print(f"{'='*60}")
            
            target_url = _force_vi_lang(url)
            await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)  # Added explicit timeout
            # Give the page a brief moment to stabilize
            await page.wait_for_timeout(2000)  # Reduced from 3000

            # Ensure title appears
            await page.wait_for_selector("h1.DUwDvf.lfPIob", timeout=15000)  # Reduced from 30000

            await page.wait_for_timeout(10)

            name = await _get_text(
                page,
                [
                    "h1.DUwDvf.lfPIob",
                ],
            )

            rating_text = await _get_text(
                page,
                [
                    'div.F7nice span[aria-hidden="true"]',
                ],
            )
            rating = _parse_float(rating_text)

            reviews_label = await _get_attr(
                page,
                [
                    'div.F7nice span[aria-label*="bài đánh giá"]',
                    'div.F7nice span[aria-label*="review"]',
                ],
                attr_name="aria-label",
            )
            if not reviews_label:
                # Fallback to text content if aria-label not available
                reviews_label = await _get_text(page, ['div.F7nice span[aria-label*="bài đánh giá"]', 'div.F7nice span[aria-label*="review"]'])
            review_count = _parse_reviews_count(reviews_label)

            address = await _get_text(
                page,
                [
                    'button[data-item-id="address"] div.Io6YTe',
                    'button[data-item-id="address"]',
                ],
            )

            # Website URL (link quán)
            website_url = await _get_attr(
                page,
                [
                    'a[data-item-id="authority"]',
                    'a.CsEnBe[data-item-id="authority"]',
                    'a[aria-label^="Website:"]',
                    'a[aria-label*="Website"]',
                ],
                attr_name="href",
            )

            # Phone number
            tel_href = await _get_attr(page, ['a[href^="tel:"]'], 'href')
            if tel_href:
                phone = tel_href.replace('tel:', '').strip()
            else:
                phone = await _get_text(
                    page,
                    [
                        'button[data-item-id^="phone"] div.Io6YTe',
                        'a[data-item-id^="phone"] div.Io6YTe',
                        'button[aria-label*="Phone"] div.Io6YTe',
                        'a[aria-label*="Phone"] div.Io6YTe',
                    ],
                )

            business_hours = await _extract_business_hours(page)

            # Navigate to About tab to extract additional attributes
            await _go_to_about_tab(page)

            await asyncio.sleep(5)

            accessibility = await _extract_about_list(page, "Phù hợp cho người khuyết tật")
            service_options = await _extract_about_list(page, "Các tùy chọn dịch vụ")
            highlights = await _extract_about_list(page, "Điểm nổi bật")
            popular_for = await _extract_about_list(page, "Nổi tiếng về")
            offerings = await _extract_about_list(page, "Dịch vụ")
            dining_options = await _extract_about_list(page, "Lựa chọn ăn uống")
            amenities = await _extract_about_list(page, "Tiện nghi")
            atmosphere = await _extract_about_list(page, "Bầu không khí")
            crowd = await _extract_about_list(page, "Khách hàng")
            planning = await _extract_about_list(page, "Lên kế hoạch")
            payments = await _extract_about_list(page, "Thanh toán")
            children = await _extract_about_list(page, "Trẻ em")
            parking = await _extract_about_list(page, "Bãi đỗ xe")

            # Go to Reviews tab and extract reviews
            await _go_to_reviews_tab(page)
            print("Navigated to Reviews tab")
            
            # Wait for reviews to load
            await page.wait_for_timeout(3000)
            
            # Scroll through all reviews to load all content
            await _scroll_reviews_to_end(page)
            
            # Debug: Check if review containers exist
            try:
                review_check = page.locator('div.jftiEf')
                review_count_check = await review_check.count()
                print(f"DEBUG: Found {review_count_check} review containers before extraction")
            except Exception as e:
                print(f"DEBUG: Error checking review containers: {e}")
            
            print("Starting to extract reviews...")
            reviews = await _extract_reviews(page, max_reviews=review_count)
            print(f"Extracted {len(reviews)} reviews")
            
            # Create result object before continuing
            result = {
                "url": url,
                "name": name,
                "rating": rating,
                "review_count": review_count,
                "address": address,
                "website": website_url,
                "phone": phone,
                "business_hours": business_hours,
                "accessibility": accessibility,
                "service_options": service_options,
                "highlights": highlights,
                "popular_for": popular_for,
                "offerings": offerings,
                "dining_options": dining_options,
                "amenities": amenities,
                "atmosphere": atmosphere,
                "crowd": crowd,
                "planning": planning,
                "payments": payments,
                "children": children,
                "parking": parking,
                "reviews": reviews,
            }
            
            # Save to database instead of JSON
            try:
                success = save_to_database(result)
                if success:
                    print(f"✅ Data saved to database for place {idx}: {name}")
                else:
                    print(f"❌ Failed to save data to database for place {idx}: {name}")
            except Exception as e:
                print(f"❌ Could not save data to database: {e}")
            
            # Save result and continue
            results.append(result)
            print(f"✅ Captured [{idx}/{len(urls)}]: {name}")
            
            # Add 1 minute delay before next URL (except for the last one)
            if idx < len(urls):
                print(f"⏳ Waiting 1 minute before next URL...")
                await asyncio.sleep(60)  # 1 minute delay
        except Exception as e:
            print(f"Failed to open URL #{idx}: {url} -> {e}")
            error_result = {
                "url": url,
                "error": str(e),
            }
            results.append(error_result)

            # Log error but don't save to database
            print(f"Error processing place {idx}: {str(e)}")
            results.append(
                {
                    "url": url,
                    "error": str(e),
                }
            )

    await context.close()
    await browser.close()
    return results


async def main() -> None:
    # Load URLs from specific files (Quận 1 and Quận 2)
    print("🚀 Starting Google Maps Places Crawler")
    print("📍 Target: Quận 1 & Quận 2 only")
    print("=" * 60)
    
    urls = load_urls_from_specific_files()
    
    if not urls:
        print("❌ No URLs found in the specified files!")
        return
    
    print(f"📊 Total URLs to process: {len(urls)}")
    print(f"⏱️  Estimated time: {len(urls)} minutes (1 minute per URL)")
    print("=" * 60)
    
    # Ask for confirmation
    try:
        confirm = input("Do you want to continue? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Operation cancelled by user")
            return
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return

    async with async_playwright() as playwright:
        data = await open_place_pages(playwright, urls)

    # Data is already saved to database during processing
    print("\n" + "=" * 60)
    print("🎉 Processing completed!")
    print("=" * 60)
    print(f"📊 Total places processed: {len(data)}")
    
    # Count successful vs error records
    successful = len([r for r in data if 'error' not in r])
    errors = len([r for r in data if 'error' in r])
    print(f"✅ Successfully processed: {successful}")
    print(f"❌ Errors: {errors}")
    
    if successful > 0:
        print(f"💾 All data has been saved to PostgreSQL database")
        print(f"🔗 Database: localhost:5432/ggmaps")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())