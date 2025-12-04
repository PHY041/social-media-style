#!/bin/bash
# 持续同步 Q-Align 分数到 Supabase
cd /Users/haoyangpang/Desktop/Canlah+Marketing/social-media-style
source venv/bin/activate

while true; do
    echo "$(date): Syncing scores..."
    python -m vlm.sync_scores_to_db --sync
    echo "$(date): Waiting 5 minutes..."
    sleep 300
done
