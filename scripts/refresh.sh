#!/bin/bash
# Refresh MindStream: Scrape new videos to SQLite
# Run: ./scripts/refresh.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔄 MindStream Refresh"
echo "====================="

# Trigger OpenClaw to scrape with 2 queries per person
echo ""
echo "1️⃣ Triggering scrape..."
openclaw system event --mode now --text "SCRAPE TASK: Update MindStream with latest AI videos.

Use youtube-search-scraper skill to scrape video data from YouTube, for below People and keywords:
1. Sam Altman: 'interview', 'podcast'
2. Andrej Karpathy: 'tutorial', 'interview'
3. Dario Amodei: 'interview', 'podcast'
4. Demis Hassabis: 'talk', 'interview'

After ALL searches complete:
- Use youtube-save-to-sqlite skill to save ALL videos to DB
- DB path: /Users/alexsmini/.openclaw/workspace/mindstream-static/mindstream.db
- Map: Sam Altman → yt-sam-altman, Andrej Karpathy → yt-andrej-karpathy, Dario Amodei → yt-search-dario-amodei, Demis Hassabis → yt-demis-hassabis
- IMPORTANT: Deduplicate by URL and Title before inserting!
- After done, send Telegram message to 8468925147: 'Done! X videos saved. Run ./scripts/deploy.sh to update the site!'
- Close all remaining tabs (keep 0 tabs)"

echo "✅ Scrape triggered!"
