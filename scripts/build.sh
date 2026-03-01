#!/bin/bash
# Build script for MindStream static site
# Run: ./scripts/build.sh

set -e

echo "📦 Building MindStream Static Site"
echo "===================================="

cd "$(dirname "$0")/.."

# 1. Export data from original DB
echo ""
echo "1️⃣ Exporting videos from database..."
npx tsx scripts/export-json.ts

# 2. Build static site
echo ""
echo "2️⃣ Building static site..."
npm run build

# 3. Done
echo ""
echo "✅ Done! Static site output:"
echo "   $(pwd)/out/"
echo ""
echo "To deploy:"
echo "   npx wrangler pages deploy out/ --project-name=mindstream"
