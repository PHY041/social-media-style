import csv, time, random, sys # Master Pinterest scraper with pin exploration
from datetime import datetime
from pathlib import Path
import config
from pin_explorer import PinExplorer, connect_browser

class MasterScraper:
    def __init__(self):
        self.existing_urls = set()
        self.existing_hashes = set()
        self._load_existing()
    
    def _load_existing(self): # Load existing URLs to avoid duplicates
        if config.MASTER_CSV.exists():
            try:
                with open(config.MASTER_CSV, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'url' in row: self.existing_urls.add(row['url'])
                        if 'content_hash' in row: self.existing_hashes.add(row['content_hash'])
                print(f"📂 Loaded {len(self.existing_urls)} existing URLs")
            except Exception as e: print(f"⚠️ Could not load existing data: {e}")
    
    def _save_batch(self, results): # Append new results to master CSV
        if not results: return 0
        new_results = [r for r in results if r['url'] not in self.existing_urls and r['content_hash'] not in self.existing_hashes]
        if not new_results: return 0
        
        file_exists = config.MASTER_CSV.exists()
        with open(config.MASTER_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=config.CSV_COLUMNS, quoting=csv.QUOTE_ALL)
            if not file_exists: writer.writeheader()
            for r in new_results:
                writer.writerow(r)
                self.existing_urls.add(r['url'])
                self.existing_hashes.add(r['content_hash'])
        return len(new_results)
    
    def run(self, categories=None, start_from=None): # Main run loop
        config.OUTPUT_DIR.mkdir(exist_ok=True)
        cats = categories or config.CATEGORY_ORDER
        if start_from and start_from in cats: cats = cats[cats.index(start_from):]
        
        print("\n" + "="*70)
        print("🚀 PINTEREST MASTER SCRAPER - EXPLORATION MODE")
        print("="*70)
        print(f"📊 Categories to process: {len(cats)}")
        print(f"📌 Initial pins per category: {config.PINS_PER_SEARCH}")
        print(f"🔗 Max URLs per pin: {config.MAX_URLS_PER_PIN}")
        print(f"🔄 Explore discovered pins: YES")
        print(f"💾 Output: {config.MASTER_CSV}")
        print("="*70 + "\n")
        
        pw, browser, ctx = connect_browser() # Connect to Chrome
        if not ctx:
            print("❌ Cannot continue without browser connection")
            return
        
        explorer = PinExplorer(ctx)
        total_new, total_dup, pins_processed = 0, 0, 0
        
        try:
            for cat_idx, cat_key in enumerate(cats):
                cat_info = config.CATEGORIES[cat_key]
                search_term = cat_info["search"]
                cat_type = cat_info["type"]
                
                print(f"\n{'='*70}")
                print(f"📦 CATEGORY {cat_idx+1}/{len(cats)}: {cat_key}")
                print(f"   Search: '{search_term}'")
                print("="*70)
                
                pin_queue = explorer.search_for_pins(search_term, config.PINS_PER_SEARCH) # Initial pins from search
                if not pin_queue:
                    print(f"   ⚠️ No pins found, skipping category")
                    continue
                
                processed_in_cat = set()
                cat_new, cat_dup = 0, 0
                max_pins_per_cat = 100 # Explore up to 100 pins per category
                
                while pin_queue and len(processed_in_cat) < max_pins_per_cat:
                    pin_url = pin_queue.pop(0)
                    if pin_url in processed_in_cat: continue
                    processed_in_cat.add(pin_url)
                    
                    print(f"\n   📌 Pin {len(processed_in_cat)}/{max_pins_per_cat} (queue: {len(pin_queue)})")
                    results, new_pins = explorer.scrape_pin(pin_url, cat_key, cat_type, search_term)
                    
                    new_count = self._save_batch(results)
                    dup_count = len(results) - new_count
                    
                    cat_new += new_count
                    cat_dup += dup_count
                    total_new += new_count
                    total_dup += dup_count
                    pins_processed += 1
                    
                    print(f"      💾 Saved: {new_count} new, {dup_count} dups | Total: {len(self.existing_urls)}")
                    
                    for np in new_pins[:10]: # Add discovered pins to queue (limit to prevent explosion)
                        if np not in processed_in_cat and np not in pin_queue:
                            pin_queue.append(np)
                    
                    if pins_processed % config.COOLDOWN_EVERY_N_PINS == 0: # Cooldown
                        cooldown = random.uniform(*config.COOLDOWN_DURATION)
                        print(f"\n   ⏸️ Cooldown {cooldown:.0f}s...")
                        time.sleep(cooldown)
                    
                    dup_rate = cat_dup / (cat_new + cat_dup) if (cat_new + cat_dup) > 0 else 0 # Check duplicate rate
                    if cat_new > 500 and dup_rate >= config.DUPLICATE_STOP_THRESHOLD:
                        print(f"\n   ⚠️ High dup rate ({dup_rate:.1%}) - moving to next category")
                        break
                
                print(f"\n   📊 Category done: {cat_new} new images from {len(processed_in_cat)} pins")
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            pw.stop() if pw else None
            
            print("\n" + "="*70)
            print("📊 FINAL SUMMARY")
            print("="*70)
            print(f"✅ Total URLs collected: {len(self.existing_urls)}")
            print(f"🆕 New this session: {total_new}")
            print(f"🔄 Duplicates skipped: {total_dup}")
            print(f"📌 Pins processed: {pins_processed}")
            print(f"💾 Saved to: {config.MASTER_CSV}")
            print("="*70 + "\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Pinterest Master Scraper")
    parser.add_argument("--original", action="store_true", help="Run original 48 categories")
    parser.add_argument("--expanded", action="store_true", help="Run new 76 taxonomy categories (default)")
    parser.add_argument("--all", action="store_true", help="Run all 124 categories")
    parser.add_argument("--start", type=str, help="Start from specific category")
    args = parser.parse_args()
    
    if args.original:
        cats = config.ORIGINAL_ORDER
        print("📦 Running ORIGINAL 48 categories")
    elif args.all:
        cats = config.ORIGINAL_ORDER + config.EXPANDED_ORDER
        print("📦 Running ALL 124 categories")
    else:  # Default: expanded
        cats = config.EXPANDED_ORDER
        print("📦 Running EXPANDED 76 taxonomy categories")
    
    scraper = MasterScraper()
    scraper.run(categories=cats, start_from=args.start)
