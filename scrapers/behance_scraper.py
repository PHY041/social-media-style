"""Behance Scraper - High-quality design and advertising work
Website: https://www.behance.net
"""
import asyncio, hashlib, json, random
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "behance_dataset.json"
LOG_FILE = OUTPUT_DIR / "behance_scraper.log"
MASTER_CSV = OUTPUT_DIR / "master_dataset.csv"

# Load all categories from config
import sys, csv
sys.path.insert(0, str(Path(__file__).parent.parent))
import config
SEARCH_QUERIES = [cat["search"] for cat in config.CATEGORIES.values()]  # All 124 categories!

# Behance 全部分类 (39个，包括滑动栏所有内容)
BEHANCE_CATEGORIES = [
    # 主分类
    ("for_you", "https://www.behance.net/for_you"),
    ("best_of_behance", "https://www.behance.net/galleries/best-of-behance"),
    ("graphic_design", "https://www.behance.net/galleries/graphic-design"),
    ("photography", "https://www.behance.net/galleries/photography"),
    ("illustration", "https://www.behance.net/galleries/illustration"),
    ("3d_art", "https://www.behance.net/galleries/3d-art"),
    ("ui_ux", "https://www.behance.net/galleries/ui-ux"),
    ("motion", "https://www.behance.net/galleries/motion"),
    ("advertising", "https://www.behance.net/galleries/advertising"),
    ("fashion", "https://www.behance.net/galleries/fashion"),
    ("product_design", "https://www.behance.net/galleries/product-design"),
    ("architecture", "https://www.behance.net/galleries/architecture"),
    ("fine_arts", "https://www.behance.net/galleries/fine-arts"),
    ("crafts", "https://www.behance.net/galleries/crafts"),
    ("game_design", "https://www.behance.net/galleries/game-design"),
    ("sound", "https://www.behance.net/galleries/sound"),
    # 子分类
    ("branding", "https://www.behance.net/galleries/graphic-design/branding"),
    ("packaging", "https://www.behance.net/galleries/graphic-design/packaging"),
    ("typography", "https://www.behance.net/galleries/graphic-design/typography"),
    # Adobe 工具分类
    ("photoshop", "https://www.behance.net/galleries/photoshop"),
    ("illustrator", "https://www.behance.net/galleries/illustrator"),
    ("after_effects", "https://www.behance.net/galleries/after-effects"),
    ("premiere_pro", "https://www.behance.net/galleries/premiere-pro"),
    ("indesign", "https://www.behance.net/galleries/indesign"),
    ("lightroom", "https://www.behance.net/galleries/lightroom"),
    ("fresco", "https://www.behance.net/galleries/fresco"),
    ("capture", "https://www.behance.net/galleries/capture"),
    ("substance_3d", "https://www.behance.net/galleries/substance-3d-designer"),
]

def load_existing_hashes() -> set:
    """Load existing content hashes from master CSV to avoid duplicates"""
    hashes = set()
    if MASTER_CSV.exists():
        try:
            with open(MASTER_CSV, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if "content_hash" in row and row["content_hash"]:
                        hashes.add(row["content_hash"])
        except: pass
    # Also load from existing JSON
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE) as f:
                data = json.load(f)
                for item in data:
                    if "content_hash" in item:
                        hashes.add(item["content_hash"])
        except: pass
    return hashes

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG_FILE, "a") as f: f.write(f"[{ts}] {msg}\n")

def content_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

async def scrape_behance(queries: list[str] = None, max_scrolls: int = 10, headless: bool = False, use_chrome: bool = False):
    """Scrape images from Behance. use_chrome=True to use logged-in Chrome session"""
    queries = queries or SEARCH_QUERIES
    existing_hashes = load_existing_hashes()
    log(f"🚀 Starting Behance scraper with {len(queries)} queries...")
    log(f"   📊 Already have {len(existing_hashes)} images (will skip duplicates)")
    
    all_images = []
    skipped = 0
    
    async with async_playwright() as p:
        if use_chrome:
            # Connect to Chrome 2 on port 9223 (separate from Pinterest's 9222)
            try:
                browser = await p.chromium.connect_over_cdp("http://localhost:9223")
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                log("   ✅ Connected to Chrome 2 (port 9223)")
            except Exception as e:
                log(f"   ❌ Chrome connection failed: {e}")
                log("   💡 Start Chrome 2: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9223 --user-data-dir=/tmp/chrome-behance")
                return []
        else:
            browser = await p.firefox.launch(headless=headless)  # Firefox works better headless
            context = await browser.new_context(viewport={"width": 1920, "height": 1080}, user_agent=USER_AGENT)
        page = await context.new_page()
        
        for query in queries:
            log(f"🔍 Searching: {query}")
            search_url = f"https://www.behance.net/search/projects?search={query.replace(' ', '%20')}"
            
            try:
                await page.goto(search_url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
                
                # Scroll to load more content
                for scroll in range(max_scrolls):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(random.uniform(1, 2))
                
                # Extract project images directly
                imgs = await page.locator("img[src*='mir-s3-cdn-cf.behance.net/projects']").all()
                log(f"   Found {len(imgs)} project images")
                
                for img_el in imgs[:50]:  # Limit per query
                    try:
                        img = await img_el.get_attribute("src")
                        if not img or "avatar" in img:
                            continue
                        
                        # Get high-res version (replace 404 with max1200)
                        img = img.replace("/projects/404/", "/projects/max1200/")
                        
                        # Get alt as title
                        title = await img_el.get_attribute("alt") or ""
                        
                        h = content_hash(img)
                        if h in existing_hashes:
                            skipped += 1
                            continue
                        existing_hashes.add(h)  # Mark as seen
                        all_images.append({
                            "url": img,
                            "title": title.strip(),
                            "page_url": "",
                            "search_term": query,
                            "source": "behance",
                            "category_type": "design",
                            "content_hash": h,
                            "collected_at": datetime.now().isoformat()
                        })
                    except:
                        continue
                
            except Exception as e:
                log(f"   ⚠️ Error: {e}")
                continue
            
            await asyncio.sleep(random.uniform(2, 4))
        
        await browser.close()
    
    # Load existing JSON and append new images
    existing_data = []
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE) as f:
                existing_data = json.load(f)
        except: pass
    
    # Merge and dedupe
    all_data = existing_data + all_images
    seen = set()
    unique = []
    for img in all_data:
        if img["content_hash"] not in seen:
            seen.add(img["content_hash"])
            unique.append(img)
    
    # Save (append mode)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(unique, f, indent=2)
    
    log(f"✅ Total: {len(unique)} images (+{len(all_images)} new, {skipped} skipped duplicates)")
    return unique

async def scrape_behance_categories(max_scrolls: int = 20):
    """Scrape all Behance category pages using Chrome (port 9223)"""
    existing_hashes = load_existing_hashes()
    log(f"🚀 Scraping {len(BEHANCE_CATEGORIES)} Behance categories...")
    log(f"   📊 Already have {len(existing_hashes)} images")
    
    all_images, skipped = [], 0
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9223")
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = context.pages[0] if context.pages else await context.new_page()
            log("   ✅ Connected to Chrome 2")
        except Exception as e:
            log(f"   ❌ Chrome connection failed: {e}")
            return []
        
        for cat_name, cat_url in BEHANCE_CATEGORIES:
            log(f"\n📂 {cat_name}")
            try:
                await page.goto(cat_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)
                for _ in range(max_scrolls):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(random.uniform(0.8, 1.2))
                
                imgs = await page.locator("img[src*='mir-s3-cdn-cf.behance.net/projects']").all()
                log(f"   Found {len(imgs)} images")
                
                new_count = 0
                for img_el in imgs:
                    try:
                        img = await img_el.get_attribute("src")
                        if not img or "avatar" in img: continue
                        img = img.replace("/projects/404/", "/projects/max1200/").replace("/projects/202/", "/projects/max1200/")
                        h = content_hash(img)
                        if h in existing_hashes: skipped += 1; continue
                        existing_hashes.add(h)
                        title = await img_el.get_attribute("alt") or ""
                        all_images.append({"url": img, "title": title.strip(), "page_url": cat_url, "search_term": cat_name, "source": "behance", "category_type": "behance_gallery", "content_hash": h, "collected_at": datetime.now().isoformat()})
                        new_count += 1
                    except: continue
                log(f"   ✅ +{new_count} new")
            except Exception as e:
                log(f"   ⚠️ Error: {e}")
            await asyncio.sleep(random.uniform(2, 4))
    
    existing_data = []
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE) as f: existing_data = json.load(f)
        except: pass
    all_data = existing_data + all_images
    seen = set()
    unique = [d for d in all_data if d["content_hash"] not in seen and not seen.add(d["content_hash"])]
    with open(OUTPUT_FILE, "w") as f: json.dump(unique, f, indent=2)
    log(f"\n✅ Total: {len(unique)} images (+{len(all_images)} new, {skipped} skipped)")
    return unique

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Behance scraper")
    parser.add_argument("--scrolls", type=int, default=10, help="Scrolls per query/category")
    parser.add_argument("--headless", action="store_true", help="Run headless Firefox")
    parser.add_argument("--chrome", action="store_true", help="Use Chrome (port 9223)")
    parser.add_argument("--categories", action="store_true", help="Scrape 28 category pages")
    args = parser.parse_args()
    if args.categories: await scrape_behance_categories(max_scrolls=args.scrolls)
    else: await scrape_behance(max_scrolls=args.scrolls, headless=args.headless, use_chrome=args.chrome)

if __name__ == "__main__":
    asyncio.run(main())

