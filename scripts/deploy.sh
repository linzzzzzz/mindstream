#!/bin/bash
# Deploy MindStream: Export → Build → Deploy
# Run after scraping is done (after you get "Done!" message)
# Run: ./scripts/deploy.sh

set -e

echo "🚀 Deploying MindStream Static Site"
echo "===================================="

cd "$(dirname "$0")/.."

# 1. Export data from original DB
echo ""
echo "1️⃣ Exporting videos..."
npx tsx scripts/export-json.ts

# 2. Build static site
echo ""
echo "2️⃣ Building..."
npm run build

# 3. Deploy to Cloudflare
echo ""
echo "3️⃣ Deploying to Cloudflare..."
npx wrangler pages deploy out/ --project-name=mindstream

echo ""
echo "✅ Done! https://mindstream-42g.pages.dev"
