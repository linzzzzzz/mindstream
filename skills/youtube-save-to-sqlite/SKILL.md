---
name: youtube-save-to-sqlite
description: Save scraped YouTube video data to SQLite database and optionally send Telegram notification. Use after: (1) Running youtube-search-scraper skill, (2) Having intermediate JSON file from scrape.
---

# YouTube Save to SQLite Skill

Save scraped YouTube video data to SQLite database and optionally notify via Telegram.

## Paths

- **Data directory**: `/Users/alexsmini/.openclaw/workspace/mindstream/data`
- **Database**: `/Users/alexsmini/.openclaw/workspace/mindstream/mindstream.db`

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
  id TEXT PRIMARY KEY,                     -- Use YouTube video ID (e.g., 'dQw4w9WgXcQ')
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
  platform TEXT DEFAULT 'youtube',         -- 'youtube' or 'bilibili'
  fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(thought_leader_id, url),
  FOREIGN KEY (thought_leader_id) REFERENCES thought_leaders(id) ON DELETE CASCADE
);

CREATE INDEX idx_content_items_leader ON content_items(thought_leader_id);
CREATE INDEX idx_content_items_published ON content_items(published_at DESC);
CREATE INDEX idx_content_items_platform ON content_items(platform);
```

## Intermediate JSON Format

The search scraper saves:

1. **Individual files** after each search (e.g., `scrape-Sam-Altman-interview-2026-02-25T12-00-00.json`) - for debugging
2. **Combined file** after all searches (e.g., `scrape-2026-02-25T12-00-00.json`) - **this is the skill's input**

This skill reads the **combined file** (timestamp only in filename, no person/keyword prefix).

```json
{
  "scrapedAt": "2026-02-25T12:00:00.000Z",
  "searchCount": 8,
  "totalVideos": 24,
  "searches": [
    { "thoughtLeader": "Sam Altman", "keyword": "interview", "query": "...", "videoCount": 5 },
    { "thoughtLeader": "Sam Altman", "keyword": "podcast", "query": "...", "videoCount": 4 }
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

Use your **file read tool** to load the most recent scrape file:

1. List files in `/Users/alexsmini/.openclaw/workspace/mindstream/data/`
2. Find the **combined** file — it matches `scrape-YYYY-*.json` with **no person/keyword prefix** (e.g., `scrape-2026-03-02T14-30-00.json`). Individual search files have names like `scrape-Sam-Altman-interview-{timestamp}.json` — ignore those.
3. Pick the most recent combined file
4. Read and parse it as JSON

If no combined file exists, stop and report the issue.

### 2. Process Videos by Thought Leader

For each video in `scrapeData.videos`:

1. Get the `thoughtLeader` name (e.g., `"Sam Altman"`)
2. Look up their database ID using bash:
   ```bash
   sqlite3 /Users/alexsmini/.openclaw/workspace/mindstream/mindstream.db \
     "SELECT id FROM thought_leaders WHERE name = 'Sam Altman';"
   ```
3. If no match found, skip that person's videos and log a warning
4. Group all videos under their matching `thought_leader_id`

### 3. Prepare Video Data

For each video, extract from the JSON:
- `title` — video title
- `url` — YouTube watch URL
- `thumbnail` — thumbnail URL (or construct from video ID)
- `channel` — channel name
- `viewCount` — number of views (integer)
- `date` — upload date string (e.g., "2 days ago")
- `durationSeconds` — duration in seconds (integer)

**ID Convention:** Extract the YouTube video ID from the URL `v` parameter and use it as the `id` field.
- URL: `https://youtube.com/watch?v=dQw4w9WgXcQ` → ID: `dQw4w9WgXcQ`

**Date parsing:** Convert relative dates ("2 days ago", "1 year ago") to ISO format (e.g., `2026-02-28`).

### 4. Map to Thought Leader

Use the `thought_leader_id` found in Step 2 for each video's `thought_leader_id` field.

### 5. Translate Title and Description to Chinese

For each video, translate using your own language capability:
- `title` → `title_zh` (Chinese translation)
- `description` → `description_zh` (Chinese translation, first 500 chars max)

**Important:**
- If description is empty/null, set `description_zh` to empty string
- Keep the original English `title` and `description` as-is
- The translations are for the bilingual display feature

### 6. Insert into SQLite (with Deduplication)

Use bash to run sqlite3 with a transaction. Insert all videos for all thought leaders:

```bash
sqlite3 /Users/alexsmini/.openclaw/workspace/mindstream/mindstream.db "
BEGIN TRANSACTION;

-- Repeat this block for each video, substituting real values:
INSERT INTO content_items
(id, thought_leader_id, title, title_zh, description, description_zh, url, thumbnail_url, channel, duration_seconds, published_at, content_type, view_count, platform)
SELECT
  'VIDEO_ID',
  'THOUGHT_LEADER_ID',
  'Video Title',
  '中文标题',
  '',
  '',
  'https://youtube.com/watch?v=VIDEO_ID',
  'https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg',
  'Channel Name',
  754,
  '2026-01-15',
  'video',
  1200000,
  'youtube'
WHERE NOT EXISTS (
  SELECT 1 FROM content_items
  WHERE thought_leader_id = 'THOUGHT_LEADER_ID'
    AND (url = 'https://youtube.com/watch?v=VIDEO_ID'
         OR title = 'Video Title')
);

-- ... repeat for every video ...

COMMIT;"
```

**Key points:**
- Use `WHERE NOT EXISTS` on each insert for deduplication
- Use the YouTube video ID (from URL `v` parameter) as the `id` field
- Include `view_count` from the scraped data
- Set `platform = 'youtube'`

### 7. (Optional) Send Telegram Notification

Use OpenClaw message tool:

```
action: "send"
channel: "telegram"
target: "8468925147"
message: "Done! X videos saved. Refresh the page!"
```

## Important Notes

- Always close browser tabs after scraping
- **DEDUPLICATION IS MANDATORY** — Check both `url` AND `title` per thought leader; the same video is often re-uploaded to different channels with the same title but a different URL
- Parse YouTube dates ("2 days ago", "1 year ago") to ISO format
- Convert duration ("12:34") to seconds (754)
- Use transactions for bulk inserts for better performance
- **Include view_count and channel** from the scraped data
- Read the **combined** JSON file (the one with timestamp in filename)
- Group videos by `thoughtLeader` and look up each person's ID from the database
- Set `platform = 'youtube'`

## Quick Reference

```
Data directory: /Users/alexsmini/.openclaw/workspace/mindstream/data
Scrape files:   /Users/alexsmini/.openclaw/workspace/mindstream/data/scrape-{timestamp}.json
Database:       /Users/alexsmini/.openclaw/workspace/mindstream/mindstream.db
Table:          content_items
Fields:         id (YouTube video ID), thought_leader_id, title, title_zh, description, description_zh, url, thumbnail_url, channel, duration_seconds, published_at, content_type, view_count, platform
Telegram:       message tool with action: "send", channel: "telegram", target: "<chat_id>"
Close tabs:     Always close new tabs when finished
```