#!/bin/bash
# 快速状态检查脚本 - 运行: ./check_status.sh

cd /Users/haoyangpang/Desktop/Canlah+Marketing/social-media-style
source venv/bin/activate 2>/dev/null

echo "╔══════════════════════════════════════════════════════╗"
echo "║           Style Universe 状态检查                    ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

echo "📊 数据统计:"
echo "  Master CSV: $(wc -l < output/master_dataset.csv 2>/dev/null || echo 0) 行"
if [ -f "output/qalign_scores.json" ]; then
    scored=$(python3 -c "import json; print(len(json.load(open('output/qalign_scores.json'))))" 2>/dev/null || echo 0)
    echo "  Q-Align 已评分: $scored 张"
fi

echo ""
echo "🔄 进程状态:"
if ps aux | grep -q "[e]mbed_pipeline"; then
    echo "  ✅ Embedding: 运行中"
    tail -1 output/embed_new.log 2>/dev/null | grep -oE "Batches:[ ]+[0-9]+%"
else
    echo "  ⏹️ Embedding: 未运行"
fi

if ps aux | grep -q "[q]align_scorer"; then
    echo "  ✅ Q-Align: 运行中"
else
    echo "  ⏹️ Q-Align: 未运行"
fi

echo ""
echo "💾 Supabase 嵌入数量:"
python3 -c "
from vector_db.supabase_client import get_client
try:
    result = get_client().table('image_embeddings').select('content_hash', count='exact').limit(1).execute()
    print(f'  已嵌入: {result.count} 条')
except Exception as e:
    print(f'  检查失败: {e}')
" 2>/dev/null

echo ""
echo "⏰ 最后更新时间:"
ls -lh output/master_dataset.csv 2>/dev/null | awk '{print "  Master CSV: " $6, $7, $8}'
ls -lh output/qalign_scores.json 2>/dev/null | awk '{print "  Q-Align: " $6, $7, $8}'

echo ""
echo "════════════════════════════════════════════════════════"

