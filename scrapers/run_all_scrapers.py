#!/usr/bin/env python3
"""Run all scrapers in parallel (headless mode)
Tests: 1. No keyboard/mouse needed 2. Anti-scraping avoidance 3. Unified output format
"""
import asyncio, json, csv, sys
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
import subprocess

OUTPUT_DIR = Path(__file__).parent.parent / "output"
LOG_FILE = OUTPUT_DIR / "scraper_master.log"

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG_FILE, "a") as f: f.write(f"[{ts}] {msg}\n")

def convert_to_csv_format(json_file: Path, source: str) -> list[dict]:
    """Convert scraper JSON output to master_dataset.csv compatible format"""
    if not json_file.exists():
        return []
    
    with open(json_file) as f:
        data = json.load(f)
    
    rows = []
    for item in data:
        row = {
            "url": item.get("url", ""),
            "category": item.get("category", item.get("search_term", "unknown")),
            "category_type": item.get("category_type", source),
            "search_term": item.get("search_term", ""),
            "title": item.get("title", ""),
            "alt_text": item.get("alt_text", ""),
            "content_hash": item.get("content_hash", ""),
            "source": source,
            "page_url": item.get("page_url", ""),
            "collected_at": item.get("collected_at", datetime.now().isoformat())
        }
        if row["url"]:
            rows.append(row)
    
    return rows

def merge_to_master_csv(new_rows: list[dict]):
    """Merge new rows into master_dataset.csv, avoiding duplicates"""
    master_csv = OUTPUT_DIR / "master_dataset.csv"
    
    # Load existing hashes
    existing_hashes = set()
    if master_csv.exists():
        with open(master_csv, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "content_hash" in row:
                    existing_hashes.add(row["content_hash"])
    
    # Filter new rows
    truly_new = [r for r in new_rows if r["content_hash"] not in existing_hashes]
    
    if not truly_new:
        log("   No new unique rows to add")
        return 0
    
    # Append to CSV
    write_header = not master_csv.exists()
    with open(master_csv, "a", newline="") as f:
        fieldnames = ["url", "category", "category_type", "search_term", "title", "alt_text", "content_hash", "source", "page_url", "collected_at"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(truly_new)
    
    log(f"   ✅ Added {len(truly_new)} new rows to master_dataset.csv")
    return len(truly_new)

async def run_scraper_async(name: str, cmd: list[str]) -> tuple[str, bool, str]:
    """Run a scraper as subprocess"""
    log(f"🚀 Starting {name}...")
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=600)  # 10 min timeout
        success = proc.returncode == 0
        output = stdout.decode() + stderr.decode()
        log(f"{'✅' if success else '❌'} {name} finished (exit: {proc.returncode})")
        return (name, success, output)
    except asyncio.TimeoutError:
        log(f"⏰ {name} timed out")
        return (name, False, "Timeout")
    except Exception as e:
        log(f"❌ {name} error: {e}")
        return (name, False, str(e))

async def test_scrapers_sequential(quick: bool = True):
    """Test each scraper one by one (safer for anti-bot)"""
    scrapers = [
        ("Behance", ["python", "scrapers/behance_scraper.py", "--scrolls", "3" if quick else "10", "--headless"]),
        ("Dribbble", ["python", "scrapers/dribbble_scraper.py", "--pages", "2" if quick else "5", "--headless"]),
        ("AdsOfTheWorld", ["python", "scrapers/adsoftheworld_scraper.py", "--pages", "2" if quick else "5", "--headless", "--no-detail"]),
    ]
    
    log("=" * 50)
    log("🧪 Testing scrapers SEQUENTIALLY (anti-bot safe)")
    log("=" * 50)
    
    results = {}
    for name, cmd in scrapers:
        result = await run_scraper_async(name, cmd)
        results[name] = result
        await asyncio.sleep(5)  # Cool down between scrapers
    
    return results

async def test_scrapers_parallel():
    """Test all scrapers in parallel (faster but riskier)"""
    scrapers = [
        ("Behance", ["python", "scrapers/behance_scraper.py", "--scrolls", "3", "--headless"]),
        ("Dribbble", ["python", "scrapers/dribbble_scraper.py", "--pages", "2", "--headless"]),
        ("AdsOfTheWorld", ["python", "scrapers/adsoftheworld_scraper.py", "--pages", "2", "--headless", "--no-detail"]),
    ]
    
    log("=" * 50)
    log("🧪 Testing scrapers IN PARALLEL")
    log("=" * 50)
    
    tasks = [run_scraper_async(name, cmd) for name, cmd in scrapers]
    results = await asyncio.gather(*tasks)
    
    return {r[0]: r for r in results}

def collect_and_merge():
    """Collect all scraper outputs and merge to master CSV"""
    log("\n📦 Collecting scraper outputs...")
    
    sources = [
        (OUTPUT_DIR / "behance_dataset.json", "behance"),
        (OUTPUT_DIR / "dribbble_dataset.json", "dribbble"),
        (OUTPUT_DIR / "adsoftheworld_dataset.json", "adsoftheworld"),
    ]
    
    total_new = 0
    for json_file, source in sources:
        if json_file.exists():
            rows = convert_to_csv_format(json_file, source)
            log(f"   {source}: {len(rows)} rows")
            added = merge_to_master_csv(rows)
            total_new += added
        else:
            log(f"   {source}: no data file found")
    
    log(f"\n📊 Total new rows added: {total_new}")
    return total_new

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run all scrapers")
    parser.add_argument("--parallel", action="store_true", help="Run in parallel (faster but riskier)")
    parser.add_argument("--quick", action="store_true", help="Quick test with fewer pages")
    parser.add_argument("--collect-only", action="store_true", help="Only collect existing outputs")
    args = parser.parse_args()
    
    import os
    os.chdir(Path(__file__).parent.parent)  # Ensure we're in project root
    
    if args.collect_only:
        collect_and_merge()
        return
    
    if args.parallel:
        results = await test_scrapers_parallel()
    else:
        results = await test_scrapers_sequential(quick=args.quick)
    
    # Summary
    log("\n" + "=" * 50)
    log("📊 RESULTS SUMMARY")
    log("=" * 50)
    for name, (_, success, _) in results.items():
        log(f"   {name}: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Collect and merge
    collect_and_merge()

if __name__ == "__main__":
    asyncio.run(main())



