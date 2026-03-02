SCRAPE TASK: Update MindStream with latest AI videos

For EACH person below, do 2 searches on YouTube:
  - Search 1: [name] + first keyword
  - Search 2: [name] + second keyword

People and keywords:
  1. Sam Altman: 'interview', 'podcast'
  2. Demis Hassabis: 'talk', 'interview'

For EACH search:
  1. Use youtube-search-scraper skill at mindstream workspace to search and extract video data
  2. Close that tab immediately after extracting (use browser action=close)
  3. Open next search in a new tab
  4. Use query format: 'NAME KEYWORD after:2026-01-01 duration:long'
  5. Get top 3-5 results per search
  6. Filter out shorts (videos under 5 minutes)

After ALL searches complete:
  1. Use youtube-save-to-sqlite skill at mindstream workspace to save all scraped videos to SQLite (do NOT send Telegram from within the skill — we'll do that here)
  2. Send Telegram to 8468925147: 'Done! X videos saved. Run ./scripts/deploy.sh to update!' (replace X with the count of newly inserted videos reported by the skill)
  3. Close all remaining tabs (keep 0 tabs)