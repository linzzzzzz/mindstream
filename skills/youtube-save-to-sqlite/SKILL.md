---
name: youtube-save-to-sqlite
description: Save scraped YouTube video data to SQLite database and optionally send Telegram notification. Use after: (1) Running youtube-search-scraper skill, (2) Having intermediate JSON file from scrape.
---

# YouTube Save to SQLite Skill

Save scraped YouTube video data to SQLite database and optionally notify via Telegram.

## When to Use

- After running youtube-search-scraper skill
- When you have an intermediate JSON file from scraping
- When you want to notify users of completion

## Prerequisites

- SQLite database must exist with `content_items` table
- Database path must be known
- For Telegram: Telegram chat ID must be known

## Database Schema

```sql
CREATE TABLE thought_leaders (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  display_name TEXT,
  bio TEXT,
  avatar_url TEXT,
  language TEXT DEFAULT 'english',
  topics TEXT,
  verified INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE content_items (
  id TEXT PRIMARY KEY,
  thought_leader_id TEXT NOT NULL,
  title TEXT NOT NULL,
  title_zh TEXT,
  description TEXT,
  description_zh TEXT,
  url TEXT NOT NULL,
  thumbnail_url TEXT,
  channel TEXT,
  duration_seconds INTEGER,
  published_at TEXT NOT NULL,
  content_type TEXT DEFAULT 'video',
  topics TEXT,
  view_count INTEGER DEFAULT 0,
  like_count INTEGER DEFAULT 0,
  fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(thought_leader_id, url),
  FOREIGN KEY (thought_leader_id) REFERENCES thought_leaders(id) ON DELETE CASCADE
);

CREATE INDEX idx_content_items_leader ON content_items(thought_leader_id);
CREATE INDEX idx_content_items_published ON content_items(published_at DESC);
```

## Intermediate JSON Format

The search scraper saves:

1. **Individual files** after each search (e.g., `scrape-Sam-Altman-interview.json`) - for debugging
2. **Combined file** after all searches (e.g., `scrape-2026-02-25T12-00-00.json`) - **this is the skill's output**

This skill reads the **combined file** (the one with timestamp in filename).

```json
{
  "scrapedAt": "2026-02-25T12:00:00.000Z",
  "searchCount": 8,
  "totalVideos": 24,
  "searches": [
    { "thoughtLeader": "Sam Altman", "keyword": "interview", "query": "...", "videoCount": 5 },
    { "thoughtLeader": "Sam Altman", "keyword": "podcast", "query": "...", "videoCount": 4 },
    ...
  ],
  "videos": [
    {
      "title": "Video Title",
      "url": "https://www.youtube.com/watch?v=xxxxxxxx",
      "thumbnail": "https://img.youtube.com/vi/xxxxxxxx/maxresdefault.jpg",
      "channel": "Lex Fridman",
      "views": "1.2M views",
      "viewCount": 1200000,
      "date": "2 days ago",
      "duration": "12:34",
      "durationSeconds": 754,
      "thoughtLeader": "Sam Altman"
    }
  ]
}
```

**Note:** Each video has a `thoughtLeader` field (person's name). This skill looks up the corresponding `id` from the `thought_leaders` table.

## Workflow

### 1. Read Combined JSON File

Find and read the single scrape file:

```typescript
import fs from 'fs';
import path from 'path';
const dataDir = '/Users/alexsmini/.openclaw/workspace/mindstream-static/data';

// Find the most recent scrape file
const files = fs.readdirSync(dataDir)
  .filter(f => f.startsWith('scrape-') && f.endsWith('.json'))
  .sort()
  .reverse();

if (files.length === 0) {
  throw new Error('No scrape files found!');
}

const latestFile = path.join(dataDir, files[0]);
const scrapeData = JSON.parse(fs.readFileSync(latestFile, 'utf-8'));

console.log(`📂 Loaded ${scrapeData.totalVideos} videos from ${files[0]}`);
console.log(`   Searches: ${scrapeData.searchCount}`);

### 2. Process Videos by Thought Leader

Group videos by `thoughtLeader` and insert:

```typescript
// Group videos by thought leader
const videosByLeader: Record<string, typeof scrapeData.videos> = {};

for (const video of scrapeData.videos) {
  const leaderName = video.thoughtLeader;
  if (!videosByLeader[leaderName]) {
    videosByLeader[leaderName] = [];
  }
  videosByLeader[leaderName].push(video);
}

// Process each group
let totalSaved = 0;

for (const [leaderName, videos] of Object.entries(videosByLeader)) {
  // Look up thought_leader_id
  const leaderRow = db.prepare('SELECT id FROM thought_leaders WHERE name = ?').get(leaderName) as { id: string } | undefined;
  const thoughtLeaderId = leaderRow?.id;
  
  if (!thoughtLeaderId) {
    console.warn(`⚠️ Unknown thought leader: ${leaderName}, skipping ${videos.length} videos...`);
    continue;
  }
  
  console.log(`\n📄 ${leaderName} (${thoughtLeaderId}): ${videos.length} videos`);
  
  // Insert videos (with translation, deduplication, etc.)
  const savedCount = await insertVideos(videos, thoughtLeaderId);
  totalSaved += savedCount;
  console.log(`   ✅ Saved ${savedCount} videos`);
}

console.log(`\n🎉 Total: ${totalSaved} videos saved to database`);
```

### 2. Prepare Video Data

Collect video data from youtube-search-scraper with fields from the JSON file:
- `title`
- `url` (YouTube watch URL)
- `thumbnail` (or construct from video ID)
- `channel` (e.g., "Lex Fridman", "TED")
- `viewCount` (number of views)
- `date` (published date)
- `duration` (if available)

### 3. Map to Thought Leader

Look up the `thought_leader_id` from the `thoughtLeader` name in the JSON. (See Step 1 code example - it queries the database to find the ID.)

### 4. Translate Title and Description to Chinese

For each video, use the LLM's own translation capability to translate:
- `title` → `title_zh` (Chinese translation)
- `description` → `description_zh` (Chinese translation, first 500 chars max)

**Important:** 
- If description is empty/null, set `description_zh` to empty string
- Keep the original English `title` and `description` as-is
- The translations are for the bilingual display feature

### 4. Insert into SQLite (with Deduplication - Bulk)

**IMPORTANT:** Always check for duplicates before inserting. The database uses:
- `UNIQUE(content_source_id, url)` - deduplicates by source + URL combination

Use **transactions** for efficient bulk inserts:

```bash
# Bulk insert with transaction (recommended)
# Note: Use thought_leader_id from the JSON metadata
sqlite3 /Users/alexsmini/.openclaw/workspace/mindstream-static/mindstream.db "
BEGIN TRANSACTION;

-- Video 1
INSERT INTO content_items 
(id, thought_leader_id, title, title_zh, description, description_zh, url, thumbnail_url, channel, duration_seconds, published_at, content_type, view_count)
SELECT 
  'vid-' || lower(hex(randomblob(4))),
  'sam-altman', 
  'Video Title 1', 
  '视频标题1（中文）', 
  'Description 1', 
  '描述1（中文）',
  'https://youtube.com/watch?v=xxx1', 
  'https://img.youtube.com/vi/xxx1/maxresdefault.jpg', 
  'Lex Fridman',
  3600, 
  '2025-01-01', 
  'video',
  1200000
WHERE NOT EXISTS (
  SELECT 1 FROM content_items 
  WHERE thought_leader_id = 'sam-altman' 
    AND url = 'https://youtube.com/watch?v=xxx1'
);

-- Video 2
INSERT INTO content_items 
(id, thought_leader_id, title, title_zh, description, description_zh, url, thumbnail_url, channel, duration_seconds, published_at, content_type, view_count)
SELECT 
  'vid-' || lower(hex(randomblob(4))),
  'sam-altman', 
  'Video Title 2', 
  '视频标题2（中文）', 
  'Description 2', 
  '描述2（中文）',
  'https://youtube.com/watch?v=xxx2', 
  'https://img.youtube.com/vi/xxx2/maxresdefault.jpg', 
  'TED',
  2400, 
  '2025-01-02', 
  'video',
  500000
WHERE NOT EXISTS (
  SELECT 1 FROM content_items 
  WHERE thought_leader_id = 'sam-altman' 
    AND url = 'https://youtube.com/watch?v=xxx2'
);

-- Add more videos as needed...

COMMIT;"
```

**Key points:**
- Use `content_source_id` from the JSON metadata
- Include `view_count` from the scraped data
- Deduplication checks `content_source_id + url` combination

### 5. (Optional) Send Telegram Notification

Use OpenClaw message tool:

```typescript
{
  action: "send",
  channel: "telegram",
  target: "8468925147",  // Chat ID
  message: "Done! X videos saved. Refresh the page!"
}
```

## Example: Full Pipeline

```typescript
// Step 1: Run youtube-search-scraper skill (saves to data/scrape-{timestamp}.json)

// Step 2: Run youtube-save-to-sqlite skill
// It reads from the latest scrape JSON file and saves to DB
import fs from 'fs';
import path from 'path';

const dataDir = '/Users/alexsmini/.openclaw/workspace/mindstream-static/data';
const dbPath = '/Users/alexsmini/.openclaw/workspace/mindstream-static/mindstream.db';

// Find latest scrape file
const files = fs.readdirSync(dataDir)
  .filter(f => f.startsWith('scrape-') && f.endsWith('.json'))
  .sort()
  .reverse();
const scrapeData = JSON.parse(fs.readFileSync(path.join(dataDir, files[0]), 'utf-8'));

// Process each video (with translation, deduplication, view_count)
for (const video of scrapeData.videos) {
  // Translate to Chinese, parse date/duration, check duplicates
  // Insert with view_count from video.viewCount
}

// Step 3: Notify via Telegram
await sendTelegramMessage("Done! X videos saved. Refresh the page!");
```

## Important Notes

- Always close browser tabs after scraping
- **DEDUPLICATION IS MANDATORY** - The database uses `UNIQUE(thought_leader_id, url)`, so duplicates will fail silently
- Parse YouTube dates ("2 days ago", "1 year ago") to ISO format
- Convert duration ("12:34") to seconds (754)
- Use transactions for bulk inserts for better performance
- **Include view_count and channel** from the scraped data
- Read the **combined** JSON file (the one with timestamp in filename)
- Group videos by `thoughtLeader` and look up each person's ID from the database

## Quick Reference

```
Data directory: /Users/alexsmini/.openclaw/workspace/mindstream-static/data/
Scrape files: data/scrape-{timestamp}.json
Database: /Users/alexsmini/.openclaw/workspace/mindstream-static/mindstream.db
Table: content_items
Fields: id, thought_leader_id, title, title_zh, description, description_zh, url, thumbnail_url, channel, duration_seconds, published_at, view_count
Telegram: message tool with channel: "telegram", target: "<chat_id>"
Close tabs: Always close new tabs when finished
```
