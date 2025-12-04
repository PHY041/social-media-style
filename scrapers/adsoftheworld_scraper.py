"""Ads of the World Scraper - High-quality advertising visuals
Website: https://www.adsoftheworld.com
Focus: Static Images, OOH, Print Ads, KV Compositions
Special handling for dropdown filters
"""
import asyncio, hashlib, json, random
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, Page

OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "adsoftheworld_dataset.json"
LOG_FILE = OUTPUT_DIR / "aotw_scraper.log"
MASTER_CSV = OUTPUT_DIR / "master_dataset.csv"

def load_existing_hashes() -> set:
    """Load existing content hashes to avoid duplicates"""
    import csv
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

# Medium types to scrape (dropdown values)
MEDIUM_TYPES = ["Static Images", "Print", "OOH Outdoor"]

# Industries to scrape (dropdown values) - ALL of them!
INDUSTRIES = [
    "Automotive and Personal Transportation", "Beauty", "Fashion", 
    "Food", "Drinks (Non Alcoholic)", "Alcoholic Drinks",
    "Electronics, Technology", "Jewelry", "Luxury",
    "Retail, E-commerce", "Travel, Destinations", "Health, Wellness",
    "Financial Services", "Entertainment, Sports", "Home, Living"
]

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG_FILE, "a") as f: f.write(f"[{ts}] {msg}\n")

def content_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]

async def select_dropdown(page: Page, dropdown_label: str, option_text: str) -> bool:
    """Click a dropdown and select an option"""
    try:
        # Find and click the dropdown trigger
        dropdown = page.locator(f"[class*='select']:has-text('{dropdown_label}')").first
        await dropdown.click()
        await asyncio.sleep(0.5)
        
        # Click the option
        option = page.locator(f"[class*='option']:has-text('{option_text}'), li:has-text('{option_text}')").first
        await option.click()
        await asyncio.sleep(0.5)
        return True
    except Exception as e:
        log(f"   ⚠️ Dropdown selection failed for {dropdown_label}/{option_text}: {e}")
        return False

async def scrape_campaign_page(page: Page, url: str) -> list[dict]:
    """Scrape individual campaign page for all images"""
    images = []
    try:
        await page.goto(url, wait_until="networkidle", timeout=15000)
        await asyncio.sleep(1)
        
        # Get all images on the page
        img_elements = await page.locator("img[src*='adsoftheworld'], img[src*='cdn']").all()
        
        for img_el in img_elements:
            try:
                src = await img_el.get_attribute("src")
                if src and "avatar" not in src and "logo" not in src:
                    # Try to get higher resolution
                    if "/thumbnail/" in src:
                        src = src.replace("/thumbnail/", "/original/")
                    images.append(src)
            except:
                continue
    except:
        pass
    
    return list(set(images))  # Dedupe

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Medium type IDs (from AdsOfWorld URL structure)
MEDIUM_IDS = {
    "Print": 1, "Outdoor": 2, "Digital": 3, "Film": 4, 
    "Audio": 5, "Experiential": 6, "Direct": 7, "PR": 8
}

# Industry IDs (from AdsOfWorld)
INDUSTRY_IDS = {
    "Automotive": 1, "Beauty": 2, "Fashion": 3, "Food": 4,
    "Beverages": 5, "Technology": 6, "Finance": 7, "Travel": 8,
    "Health": 9, "Retail": 10, "Entertainment": 11, "Home": 12
}

async def scrape_adsoftheworld(medium_types: list = None, industries: list = None, 
                                max_pages: int = 10, scrape_detail: bool = True,
                                headless: bool = False):
    """Scrape ads from adsoftheworld.com using URL parameters"""
    
    existing_hashes = load_existing_hashes()
    log(f"🚀 Starting Ads of the World scraper (URL-based)")
    log(f"   📊 Already have {len(existing_hashes)} images (will skip duplicates)")
    
    all_ads = []
    skipped = 0
    
    # Direct URL patterns - ONLY image-based ads (Print, Outdoor, Direct)
    # Using page parameter for pagination
    CATEGORY_URLS = [
        # Print ads (平面广告) - 图片为主
        ("print_ads", "https://www.adsoftheworld.com/campaigns?medium_type_ids%5B%5D=1"),
        # Outdoor/OOH (户外广告) - 图片为主  
        ("outdoor_ads", "https://www.adsoftheworld.com/campaigns?medium_type_ids%5B%5D=2"),
        # Direct (直邮广告) - 图片为主
        ("direct_ads", "https://www.adsoftheworld.com/campaigns?medium_type_ids%5B%5D=7"),
        # All campaigns (所有类型)
        ("all_campaigns", "https://www.adsoftheworld.com/campaigns"),
    ]
    
    async with async_playwright() as p:
        # Try Chrome 2 first, fallback to Firefox
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9223")
            context = browser.contexts[0]
            page = context.pages[0]
            log("   ✅ Connected to Chrome 2")
            use_chrome = True
        except:
            browser = await p.firefox.launch(headless=headless)
            context = await browser.new_context(viewport={"width": 1920, "height": 1080}, user_agent=USER_AGENT)
            page = await context.new_page()
            log("   🦊 Using Firefox (headless)")
            use_chrome = False
        
        for cat_name, cat_url in CATEGORY_URLS:
            log(f"\n🔍 Scraping: {cat_name}")
            
            # Navigate to category page - use "commit" to avoid timeout
            try:
                await page.goto(cat_url, wait_until="commit", timeout=30000)
                await asyncio.sleep(8)  # Wait for content to load
            except Exception as e:
                log(f"   ⚠️ Failed to load {cat_name}: {e}")
                continue
            
            # Scrape pages using URL pagination
            for page_num in range(1, max_pages + 1):
                # Build paginated URL
                if page_num == 1:
                    page_url = cat_url
                else:
                    # Add page parameter
                    separator = "&" if "?" in cat_url else "?"
                    page_url = f"{cat_url}{separator}page={page_num}"
                
                log(f"   📃 Page {page_num}...")
                
                try:
                    await page.goto(page_url, wait_until="commit", timeout=30000)
                    await asyncio.sleep(5)
                except Exception as e:
                    log(f"      ⚠️ Page load failed: {e}")
                    break
                
                # Find campaign cards - correct selector
                cards = await page.locator("a[href*='/campaigns/']").all()
                log(f"      Found {len(cards)} campaigns")
                
                if len(cards) == 0:
                    log(f"      No more campaigns, moving to next category")
                    break
                
                seen_on_page = set()  # Avoid duplicates on same page
                for card in cards[:50]:  # Limit per page
                    try:
                        # Get campaign link
                        link = await card.get_attribute("href")
                        if not link or link in seen_on_page:
                            continue
                        seen_on_page.add(link)
                        
                        if not link.startswith("http"):
                            link = f"https://www.adsoftheworld.com{link}"
                        
                        # Get thumbnail - check inside the link
                        img_el = card.locator("img").first
                        thumb = None
                        if await img_el.count() > 0:
                            thumb = await img_el.get_attribute("src")
                            # Get higher resolution if possible
                            if thumb and "adsoftheworld.com" in thumb:
                                thumb = thumb.replace("/thumbnail/", "/original/").replace("_thumb", "")
                        
                        if not thumb:
                            continue  # Skip if no image
                        
                        # Get title from aria-label or text
                        title = await card.get_attribute("aria-label") or await card.get_attribute("title") or ""
                        if not title:
                            title = link.split("/campaigns/")[-1].replace("-", " ").title()
                        
                        h = content_hash(thumb)
                        if h in existing_hashes:
                            skipped += 1
                            continue
                        existing_hashes.add(h)
                        
                        ad_data = {
                            "url": thumb,
                            "title": title.strip(),
                            "page_url": link,
                            "category": cat_name,
                            "source": "adsoftheworld",
                            "category_type": "advertising",
                            "content_hash": h,
                            "collected_at": datetime.now().isoformat()
                        }
                        
                        # Optionally scrape detail page for more images
                        if scrape_detail and thumb:
                            detail_images = await scrape_campaign_page(page, link)
                            if detail_images:
                                ad_data["all_images"] = detail_images
                                ad_data["url"] = detail_images[0]  # Use first as main
                            await page.go_back()
                            await asyncio.sleep(1)
                        
                        all_ads.append(ad_data)
                        
                    except Exception as e:
                        continue
                
                # Small delay between pages
                await asyncio.sleep(random.uniform(1, 2))
            
            await asyncio.sleep(random.uniform(1, 2))
        
        if not use_chrome:  # Don't close Chrome CDP connection
            await browser.close()
    
    # Load existing and append
    existing_data = []
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE) as f: existing_data = json.load(f)
        except: pass
    
    all_data = existing_data + all_ads
    seen = set()
    unique = []
    for ad in all_data:
        if ad["content_hash"] not in seen:
            seen.add(ad["content_hash"])
            unique.append(ad)
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(unique, f, indent=2)
    
    log(f"\n✅ Total: {len(unique)} ads (+{len(all_ads)} new, {skipped} skipped duplicates)")
    return unique

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Ads of the World scraper")
    parser.add_argument("--pages", type=int, default=5, help="Pages per filter combination")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    parser.add_argument("--no-detail", action="store_true", help="Skip detail page scraping")
    args = parser.parse_args()
    
    await scrape_adsoftheworld(
        max_pages=args.pages, 
        scrape_detail=not args.no_detail,
        headless=args.headless
    )

if __name__ == "__main__":
    asyncio.run(main())

