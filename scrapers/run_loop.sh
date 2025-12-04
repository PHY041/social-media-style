#!/bin/bash
# 循环运行 scrapers - 并行执行！
cd /Users/haoyangpang/Desktop/Canlah+Marketing/social-media-style
source venv/bin/activate

ROUND=1

while true; do
    echo ""
    echo "========================================"
    echo "🔄 ROUND $ROUND - $(date)"
    echo "========================================"
    
    # 并行启动所有 scrapers！
    echo "🚀 启动 3 个 scrapers 并行..."
    
    python scrapers/behance_scraper.py --scrolls $((5 + ROUND * 2)) --headless &
    PID_B=$!
    echo "   🎨 Behance PID: $PID_B"
    
    python scrapers/dribbble_scraper.py --pages $((3 + ROUND)) --headless &
    PID_D=$!
    echo "   🏀 Dribbble PID: $PID_D"
    
    python scrapers/adsoftheworld_scraper.py --pages $((5 + ROUND)) --headless &
    PID_A=$!
    echo "   📺 AdsOfWorld PID: $PID_A"
    
    # 等待全部完成
    echo ""
    echo "⏳ 等待 3 个 scrapers 完成..."
    wait $PID_B $PID_D $PID_A
    echo "✅ Round $ROUND 全部完成！"
    
    # Stats
    echo ""
    echo "📊 当前数据量:"
    for f in behance_dataset.json dribbble_dataset.json adsoftheworld_dataset.json; do
        if [ -f "output/$f" ]; then
            count=$(python -c "import json; print(len(json.load(open('output/$f'))))" 2>/dev/null || echo "0")
            echo "   $f: $count 张"
        fi
    done
    echo "   master_dataset.csv: $(wc -l < output/master_dataset.csv) 行"
    
    ROUND=$((ROUND + 1))
    
    echo ""
    echo "⏳ 休息 10 秒后开始 Round $ROUND..."
    sleep 10
done

