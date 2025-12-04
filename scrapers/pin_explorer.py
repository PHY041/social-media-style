import time, random, hashlib, re # Pinterest pin explorer - single tab mode (no focus stealing)
from datetime import datetime
from playwright.sync_api import sync_playwright
import config

class PinExplorer:
    def __init__(self, browser_context):
        self.ctx = browser_context
        self.page = self.ctx.pages[0] if self.ctx.pages else self.ctx.new_page() # Reuse existing tab
        self.discovered_pins = set()
    
    def _delay(self, delay_range): time.sleep(random.uniform(*delay_range))
    
    def _hash(self, url): return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def _scroll_page(self, times, amount=3000): # JS scroll - no focus steal
        for i in range(times):
            self.page.evaluate(f"window.scrollBy(0, {amount})")
            self._delay((0.2, 0.4))
    
    def _navigate(self, url): # Navigate without creating new tab
        try:
            self.page.goto(url, timeout=30000, wait_until="domcontentloaded")
            self._delay((1, 2))
            return True
        except Exception as e:
            print(f"      ⚠️ Nav failed: {e}")
            return False
    
    def search_for_pins(self, search_term, max_pins=25):
        pin_urls = []
        search_url = f"https://www.pinterest.com/search/pins/?q={search_term.replace(' ', '%20')}"
        print(f"   🔍 Searching: {search_term}")
        
        if not self._navigate(search_url): return pin_urls
        self._scroll_page(20, 3000)
        self._delay((1, 2))
        
        links = self.page.query_selector_all("a[href*='/pin/']")
        seen = set()
        for link in links:
            href = link.get_attribute("href")
            if href and "/pin/" in href:
                pin_match = re.search(r'/pin/(\d+)', href)
                if pin_match:
                    clean_url = f"https://www.pinterest.com/pin/{pin_match.group(1)}/"
                    if clean_url not in seen:
                        seen.add(clean_url)
                        pin_urls.append(clean_url)
                        if len(pin_urls) >= max_pins: break
        print(f"   ✅ Found {len(pin_urls)} pins")
        return pin_urls
    
    def scrape_pin(self, pin_url, category, category_type, search_term):
        results, new_pins = [], []
        print(f"      📌 {pin_url[:55]}...")
        
        if not self._navigate(pin_url): return results, new_pins
        
        pin_title, pin_saves, pin_comments = "", "0", "0"
        try:
            title_el = self.page.query_selector("h1")
            if title_el: pin_title = title_el.inner_text().strip()[:200]
        except: pass
        try:
            saves_el = self.page.query_selector("[data-test-id='pin-save-count']")
            if saves_el: pin_saves = re.sub(r'[^\d]', '', saves_el.inner_text()) or "0"
        except: pass
        
        self._scroll_page(config.SCROLLS_PER_PIN, 4000) # Scroll for "More like this"
        self._delay((1, 2))
        
        images = self.page.query_selector_all("img[src*='pinimg.com']")
        seen_urls = set()
        for img in images:
            if len(results) >= config.MAX_URLS_PER_PIN: break
            try:
                src = img.get_attribute("src")
                alt = img.get_attribute("alt") or ""
                if src and "pinimg.com" in src and "75x75" not in src:
                    high_res = src.replace("/236x/", "/originals/").replace("/474x/", "/originals/").replace("/736x/", "/originals/")
                    if high_res not in seen_urls:
                        seen_urls.add(high_res)
                        engagement = (int(pin_saves) * 2) if pin_saves.isdigit() else 0
                        results.append({
                            "url": high_res, "pin_url": pin_url, "category": category,
                            "category_type": category_type, "search_term": search_term,
                            "title": pin_title.replace(",", ";").replace("\n", " ")[:200],
                            "alt_text": alt.replace(",", ";").replace("\n", " ")[:200],
                            "saves": pin_saves, "comments": pin_comments,
                            "engagement_score": engagement, "content_hash": self._hash(high_res),
                            "collected_at": datetime.now().isoformat()
                        })
            except: pass
        
        links = self.page.query_selector_all("a[href*='/pin/']") # Discover more pins
        for link in links:
            try:
                href = link.get_attribute("href")
                if href and "/pin/" in href:
                    pin_match = re.search(r'/pin/(\d+)', href)
                    if pin_match:
                        new_pin = f"https://www.pinterest.com/pin/{pin_match.group(1)}/"
                        if new_pin not in self.discovered_pins and new_pin != pin_url:
                            self.discovered_pins.add(new_pin)
                            new_pins.append(new_pin)
            except: pass
        
        print(f"      ✅ {len(results)} imgs, {len(new_pins)} new pins")
        return results, new_pins

def connect_browser():
    pw = sync_playwright().start()
    try:
        browser = pw.chromium.connect_over_cdp(f"http://localhost:{config.CHROME_DEBUG_PORT}")
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        print(f"✅ Connected to Chrome (single-tab mode)")
        return pw, browser, ctx
    except Exception as e:
        print(f"❌ Failed: {e}\n💡 Start Chrome: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port={config.CHROME_DEBUG_PORT}")
        pw.stop()
        return None, None, None
