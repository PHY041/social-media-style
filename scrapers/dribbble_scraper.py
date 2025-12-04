"""Dribbble Scraper - High-quality design shots
Website: https://dribbble.com
"""
import asyncio, hashlib, json, random
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "dribbble_dataset.json"
LOG_FILE = OUTPUT_DIR / "dribbble_scraper.log"
MASTER_CSV = OUTPUT_DIR / "master_dataset.csv"

# Load all categories from config
import sys, csv
sys.path.insert(0, str(Path(__file__).parent.parent))
import config
SEARCH_QUERIES = [cat["search"] for cat in config.CATEGORIES.values()]  # All 124 categories!

# Dribbble 分类页面 (扩展到更多)
DRIBBBLE_CATEGORIES = [
    # Popular 分类
    ("popular", "https://dribbble.com/shots/popular"),
    ("recent", "https://dribbble.com/shots/recent"),
    ("animation", "https://dribbble.com/shots/popular/animation"),
    ("branding", "https://dribbble.com/shots/popular/branding"),
    ("illustration", "https://dribbble.com/shots/popular/illustration"),
    ("mobile", "https://dribbble.com/shots/popular/mobile"),
    ("print", "https://dribbble.com/shots/popular/print"),
    ("product_design", "https://dribbble.com/shots/popular/product-design"),
    ("typography", "https://dribbble.com/shots/popular/typography"),
    ("web_design", "https://dribbble.com/shots/popular/web-design"),
    # Recent 分类 (更多新内容)
    ("recent_animation", "https://dribbble.com/shots/recent/animation"),
    ("recent_branding", "https://dribbble.com/shots/recent/branding"),
    ("recent_illustration", "https://dribbble.com/shots/recent/illustration"),
    ("recent_mobile", "https://dribbble.com/shots/recent/mobile"),
    ("recent_print", "https://dribbble.com/shots/recent/print"),
    ("recent_product", "https://dribbble.com/shots/recent/product-design"),
    ("recent_typography", "https://dribbble.com/shots/recent/typography"),
    ("recent_web", "https://dribbble.com/shots/recent/web-design"),
    # 搜索热门关键词 - 设计类
    ("search_luxury", "https://dribbble.com/search/shots/popular?q=luxury"),
    ("search_minimal", "https://dribbble.com/search/shots/popular?q=minimal"),
    ("search_3d", "https://dribbble.com/search/shots/popular?q=3d"),
    ("search_logo", "https://dribbble.com/search/shots/popular?q=logo"),
    ("search_app", "https://dribbble.com/search/shots/popular?q=app+design"),
    ("search_packaging", "https://dribbble.com/search/shots/popular?q=packaging"),
    ("search_poster", "https://dribbble.com/search/shots/popular?q=poster"),
    ("search_brand_identity", "https://dribbble.com/search/shots/popular?q=brand+identity"),
    ("search_website", "https://dribbble.com/search/shots/popular?q=website"),
    ("search_icon", "https://dribbble.com/search/shots/popular?q=icon"),
    ("search_fashion", "https://dribbble.com/search/shots/popular?q=fashion"),
    ("search_advertising", "https://dribbble.com/search/shots/popular?q=advertising"),
    # 搜索 - 艺术风格
    ("search_surreal", "https://dribbble.com/search/shots/popular?q=surreal"),
    ("search_minimalist", "https://dribbble.com/search/shots/popular?q=minimalist"),
    ("search_abstract", "https://dribbble.com/search/shots/popular?q=abstract"),
    ("search_retro", "https://dribbble.com/search/shots/popular?q=retro"),
    ("search_futuristic", "https://dribbble.com/search/shots/popular?q=futuristic"),
    ("search_vintage", "https://dribbble.com/search/shots/popular?q=vintage"),
    ("search_geometric", "https://dribbble.com/search/shots/popular?q=geometric"),
    ("search_organic", "https://dribbble.com/search/shots/popular?q=organic"),
    # 搜索 - 商业类
    ("search_product_shot", "https://dribbble.com/search/shots/popular?q=product+shot"),
    ("search_commercial", "https://dribbble.com/search/shots/popular?q=commercial"),
    ("search_editorial", "https://dribbble.com/search/shots/popular?q=editorial"),
    ("search_campaign", "https://dribbble.com/search/shots/popular?q=campaign"),
    ("search_beauty", "https://dribbble.com/search/shots/popular?q=beauty"),
    ("search_cosmetics", "https://dribbble.com/search/shots/popular?q=cosmetics"),
    ("search_food", "https://dribbble.com/search/shots/popular?q=food"),
    ("search_drink", "https://dribbble.com/search/shots/popular?q=drink"),
    ("search_automotive", "https://dribbble.com/search/shots/popular?q=automotive"),
    ("search_tech", "https://dribbble.com/search/shots/popular?q=tech"),
    # 搜索 - 视觉技法
    ("search_gradient", "https://dribbble.com/search/shots/popular?q=gradient"),
    ("search_neon", "https://dribbble.com/search/shots/popular?q=neon"),
    ("search_glassmorphism", "https://dribbble.com/search/shots/popular?q=glassmorphism"),
    ("search_neumorphism", "https://dribbble.com/search/shots/popular?q=neumorphism"),
    ("search_dark_mode", "https://dribbble.com/search/shots/popular?q=dark+mode"),
    ("search_colorful", "https://dribbble.com/search/shots/popular?q=colorful"),
    ("search_monochrome", "https://dribbble.com/search/shots/popular?q=monochrome"),
]

def load_existing_hashes() -> set:
    """Load existing content hashes to avoid duplicates"""
    hashes = set()
    if MASTER_CSV.exists():
        try:
            with open(MASTER_CSV, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row.get("content_hash"): hashes.add(row["content_hash"])
        except: pass
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE) as f:
                for item in json.load(f):
                    if item.get("content_hash"): hashes.add(item["content_hash"])
        except: pass
    return hashes

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG_FILE, "a") as f: f.write(f"[{ts}] {msg}\n")

def content_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

async def scrape_dribbble(queries: list[str] = None, max_pages: int = 5, headless: bool = False):
    """Scrape shots from Dribbble"""
    queries = queries or SEARCH_QUERIES
    existing_hashes = load_existing_hashes()
    log(f"🚀 Starting Dribbble scraper with {len(queries)} queries...")
    log(f"   📊 Already have {len(existing_hashes)} images (will skip duplicates)")
    
    all_shots = []
    skipped = 0
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=headless)  # Firefox works better headless
        context = await browser.new_context(viewport={"width": 1920, "height": 1080}, user_agent=USER_AGENT)
        page = await context.new_page()
        
        for query in queries:
            log(f"🔍 Searching: {query}")
            
            for page_num in range(1, max_pages + 1):
                search_url = f"https://dribbble.com/search/shots/popular?q={query.replace(' ', '%20')}&page={page_num}"
                
                try:
                    await page.goto(search_url, wait_until="networkidle", timeout=30000)
                    await asyncio.sleep(2)
                    
                    # Extract shot cards
                    shots = await page.locator("[class*='shot-thumbnail'], .shot-thumbnail, [data-testid='shot']").all()
                    log(f"   Page {page_num}: Found {len(shots)} shots")
                    
                    if len(shots) == 0:
                        break
                    
                    for shot in shots:
                        try:
                            # Get image
                            img = await shot.locator("img").first.get_attribute("src")
                            if not img or "placeholder" in img or "avatar" in img:
                                continue
                            
                            # Get higher res version
                            if "_teaser" in img:
                                img = img.replace("_teaser", "")
                            if "_1x" in img:
                                img = img.replace("_1x", "_2x")
                            
                            # Get title
                            title_el = shot.locator("[class*='title'], img").first
                            title = await title_el.get_attribute("alt") or ""
                            
                            # Get link
                            link = await shot.locator("a").first.get_attribute("href")
                            if link and not link.startswith("http"):
                                link = f"https://dribbble.com{link}"
                            
                            h = content_hash(img)
                            if h in existing_hashes:
                                skipped += 1
                                continue
                            existing_hashes.add(h)
                            all_shots.append({
                                "url": img,
                                "title": title.strip() if title else "",
                                "page_url": link,
                                "search_term": query,
                                "source": "dribbble",
                                "category_type": "design",
                                "content_hash": h,
                                "collected_at": datetime.now().isoformat()
                            })
                        except:
                            continue
                    
                except Exception as e:
                    log(f"   ⚠️ Error: {e}")
                    continue
                
                await asyncio.sleep(random.uniform(1, 2))
            
            await asyncio.sleep(random.uniform(2, 4))
        
        await browser.close()
    
    # Load existing and append
    existing_data = []
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE) as f: existing_data = json.load(f)
        except: pass
    
    all_data = existing_data + all_shots
    seen = set()
    unique = []
    for shot in all_data:
        if shot["content_hash"] not in seen:
            seen.add(shot["content_hash"])
            unique.append(shot)
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(unique, f, indent=2)
    
    log(f"✅ Total: {len(unique)} shots (+{len(all_shots)} new, {skipped} skipped duplicates)")
    return unique

async def scrape_dribbble_categories(max_loads: int = 10):
    """Scrape Dribbble category pages using Chrome 2 (port 9223)"""
    existing_hashes = load_existing_hashes()
    log(f"🚀 Scraping {len(DRIBBBLE_CATEGORIES)} Dribbble categories...")
    log(f"   📊 Already have {len(existing_hashes)} images")
    
    all_shots, skipped = [], 0
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9223")
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = context.pages[0] if context.pages else await context.new_page()
            log("   ✅ Connected to Chrome 2")
        except Exception as e:
            log(f"   ❌ Chrome connection failed: {e}")
            return []
        
        for cat_name, cat_url in DRIBBBLE_CATEGORIES:
            log(f"\n📂 {cat_name}")
            try:
                await page.goto(cat_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)
                
                # Dribbble uses infinite scroll (limited)
                prev_count = 0
                for scroll_idx in range(max_loads):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(random.uniform(1.2, 2.0))
                    
                    # Check if more images loaded
                    curr_count = await page.locator("img[src*='cdn.dribbble.com']").count()
                    if curr_count == prev_count:
                        break  # No more loading
                    prev_count = curr_count
                
                imgs = await page.locator("img[src*='cdn.dribbble.com']").all()
                log(f"   Found {len(imgs)} images")
                
                new_count = 0
                for img_el in imgs:
                    try:
                        img = await img_el.get_attribute("src")
                        if not img or "avatar" in img or "profile" in img: continue
                        # Get higher res
                        img = img.replace("_teaser", "").replace("_1x", "_2x")
                        h = content_hash(img)
                        if h in existing_hashes: skipped += 1; continue
                        existing_hashes.add(h)
                        title = await img_el.get_attribute("alt") or ""
                        all_shots.append({"url": img, "title": title.strip(), "page_url": cat_url, "search_term": cat_name, "source": "dribbble", "category_type": "dribbble_category", "content_hash": h, "collected_at": datetime.now().isoformat()})
                        new_count += 1
                    except: continue
                log(f"   ✅ +{new_count} new")
            except Exception as e:
                log(f"   ⚠️ Error: {e}")
            await asyncio.sleep(random.uniform(2, 4))
    
    # Save
    existing_data = []
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE) as f: existing_data = json.load(f)
        except: pass
    all_data = existing_data + all_shots
    seen = set()
    unique = [d for d in all_data if d["content_hash"] not in seen and not seen.add(d["content_hash"])]
    with open(OUTPUT_FILE, "w") as f: json.dump(unique, f, indent=2)
    log(f"\n✅ Total: {len(unique)} shots (+{len(all_shots)} new, {skipped} skipped)")
    return unique

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Dribbble scraper")
    parser.add_argument("--pages", type=int, default=5, help="Pages per query")
    parser.add_argument("--scrolls", type=int, default=15, help="Load more clicks per category")
    parser.add_argument("--headless", action="store_true", help="Run headless Firefox")
    parser.add_argument("--categories", action="store_true", help="Scrape category pages with Chrome 2")
    args = parser.parse_args()
    if args.categories: await scrape_dribbble_categories(max_loads=args.scrolls)
    else: await scrape_dribbble(max_pages=args.pages, headless=args.headless)

if __name__ == "__main__":
    asyncio.run(main())

