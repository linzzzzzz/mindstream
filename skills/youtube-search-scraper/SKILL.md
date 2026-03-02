---
name: youtube-search-scraper
description: Scrape YouTube search results using browser automation. Searches YouTube for a query and extracts video results. Use when: (1) YouTube API quota is exhausted, (2) Need unlimited searches, (3) Want real-time results.
---

# YouTube Search Scraper Skill

Use OpenClaw's browser automation to search YouTube and scrape video results.

This skill performs multiple searches (one per person + keyword combination) and combines results into a single JSON file.

## Paths

- **Data directory**: `/Users/alexsmini/.openclaw/workspace/mindstream/data`
- **Database**: `/Users/alexsmini/.openclaw/workspace/mindstream/mindstream.db`

## Search Configuration

The caller provides a list of people and keywords to search for. Example:

```
People and keywords:
1. Sam Altman: 'interview', 'podcast'
2. Andrej Karpathy: 'tutorial', 'interview'
3. Dario Amodei: 'interview', 'podcast'
4. Demis Hassabis: 'talk', 'interview'

For EACH person + keyword combination:
1. Navigate to YouTube search: 'NAME KEYWORD after:2026-01-01 duration:long'
2. Extract top 3-5 video results
3. Filter out shorts (videos under 5 minutes)
4. Move to next search (in same tab or new tab)
5. Close tab after each search

After ALL searches complete:
- Combine all videos into ONE JSON file
- Deduplicate by URL before saving
```

## When to Use

- YouTube API quota exhausted
- Need unlimited searches
- Want to search without API key


## Workflow

This skill runs **multiple searches** in sequence. Each search goes through steps 1-5, then step 6 consolidates everything.

**Before starting**: Generate a single run timestamp (e.g., `2026-03-02T14-30-00`) to use consistently across all intermediate and combined files for this run.

```
For each (person, keyword) pair (steps 1-5):
  1. Navigate to YouTube with search query
  2. Wait for results
  3. Extract video data
  4. Filter by duration
  5. Save intermediate JSON file (with run timestamp)

After ALL searches (step 6):
  6. Combine all results into one final JSON file (with same run timestamp)
```

### Step 1: Navigate to YouTube Search

Open a new tab and navigate to:
```
https://www.youtube.com/results?search_query={QUERY}
```

Replace `{QUERY}` with your search term. You can use operators like:
- `duration:long` for 20+ minute videos
- `after:YYYY-MM-DD` for videos after a specific date

Example URL with dynamic date:
```
https://www.youtube.com/results?search_query=Sam+Altman+interview+duration:long+after:2026-01-24
```

### Step 2: Wait for Results

Wait 3-5 seconds for the page to fully load before extracting data.

### Step 3: Extract Video Data

Get a snapshot of the page and parse (for THIS search only):

- **Title**: From video link elements
- **URL**: `https://www.youtube.com/watch?v={videoId}`
- **Thumbnail**: `https://img.youtube.com/vi/{videoId}/maxresdefault.jpg`
- **Channel**: Channel name text
- **Views**: View count text
- **Date**: Upload date text (e.g., "2 days ago", "1 year ago")
- **Duration**: Video length (e.g., "12:34", "1:30:00")


### Step 4: Filter by Duration (IMPORTANT)

**Only keep videos that are 5 minutes or longer** (300+ seconds).

Videos shorter than 5 minutes are likely Shorts/clips, not full talks.

Convert duration to seconds:
- `12:34` → 754 seconds ✅ (keep)
- `4:30` → 270 seconds ❌ (skip)
- `1:30:00` → 5400 seconds ✅ (keep)

Discard any video where `durationSeconds < 300`.

### Step 5: Save Intermediate JSON File

After extracting and filtering data for this search, use your **file write tool** to save:

- **Path**: `/Users/alexsmini/.openclaw/workspace/mindstream/data/scrape-{thoughtLeader}-{keyword}-{timestamp}.json`
  (e.g., `scrape-Sam-Altman-interview-2026-03-02T14-30-00.json` — replace spaces with hyphens, use the run timestamp from the start)
- **Content**:

```json
{
  "thoughtLeader": "Sam Altman",
  "keyword": "interview",
  "query": "Sam Altman interview after:2026-01-01 duration:long",
  "videos": [
    {
      "title": "...",
      "url": "https://www.youtube.com/watch?v=xxx",
      "thumbnail": "https://img.youtube.com/vi/xxx/maxresdefault.jpg",
      "channel": "...",
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

**Key points:**
- After each individual search → save `scrape-Sam-Altman-interview-{timestamp}.json` (same timestamp for all files in this run)
- After ALL 8 searches → save combined `scrape-{timestamp}.json` as final output
- Each video tagged with `thoughtLeader`

> **Repeat steps 1-5** for each person + keyword combination. Once ALL searches are complete, proceed to **Step 6**.


### Step 6: Combine All Results (After ALL Searches)

After all searches are done, use your **file write tool** to save one final combined file:

- **Path**: `/Users/alexsmini/.openclaw/workspace/mindstream/data/scrape-{timestamp}.json`
  (e.g., `scrape-2026-03-02T12-00-00.json` — use current datetime, replacing `:` and `.` with `-`)
- **Content**: Merge all videos from all intermediate files, deduplicate by URL:

```json
{
  "scrapedAt": "<current ISO timestamp>",
  "searchCount": 8,
  "totalVideos": 24,
  "searches": [
    { "thoughtLeader": "Sam Altman", "keyword": "interview", "query": "...", "videoCount": 3 },
    { "thoughtLeader": "Sam Altman", "keyword": "podcast", "query": "...", "videoCount": 3 }
  ],
  "videos": [
    { "...all videos from all searches, each with thoughtLeader field..." }
  ]
}
```

### Video Object Structure

Each video in the `videos` array must have these fields:

```json
{
  "title": "Sam Altman Unfiltered: ChatGPT, AI Risks & What's Coming Next",
  "url": "https://www.youtube.com/watch?v=qH7thwrCluM",
  "thumbnail": "https://img.youtube.com/vi/qH7thwrCluM/maxresdefault.jpg",
  "channel": "OpenAI",
  "views": "338K views",
  "viewCount": 338000,
  "date": "3 days ago",
  "duration": "59:56",
  "durationSeconds": 3596,
  "thoughtLeader": "Sam Altman"
}
```

## Search Query Examples

### Basic Queries

| Person | Query |
|--------|-------|
| Sam Altman | `Sam Altman AI interview` |
| Andrej Karpathy | `Andrej Karpathy tutorial` |
| Dario Amodei | `Dario Amodei AI` |
| Demis Hassabis | `Demis Hassabis DeepMind` |

### Advanced Queries (Recommended)

Use these operators to get better results:

| Person | Advanced Query |
|--------|----------------|
| Sam Altman | `Sam Altman interview after:2025-01-01 duration:long` |
| Andrej Karpathy | `Andrej Karpathy tutorial after:2025-01-01 duration:long` |
| Dario Amodei | `Dario Amodei interview after:2025-01-01` |
| Demis Hassabis | `Demis Hassabis talk after:2025-01-01` |

### YouTube Search Operators Reference

| Operator | Example | Description |
|----------|---------|-------------|
| `after:YYYY-MM-DD` | `Sam Altman after:2025-01-01` | Videos after date |
| `before:YYYY-MM-DD` | `before:2025-12-31` | Videos before date |
| `duration:long` | `AI tutorial duration:long` | Videos 20+ minutes |
| `duration:medium` | `duration:medium` | Videos 4-20 minutes |
| `intitle:` | `intitle:interview` | Keyword in title |
| `"exact phrase"` | `"Sam Altman"` | Exact match |

## Important Notes

- YouTube may show different layouts - adapt selectors accordingly
- Add 2-3 second delays between searches to avoid rate limiting
- Click "Videos" filter if you only want full videos (not Shorts)
- Sort by upload date for latest content
- **ALWAYS filter out videos shorter than 5 minutes (300 seconds)** - these are likely Shorts/clips, not full talks
- After EACH search: save intermediate JSON file using your file write tool
- After ALL searches: save ONE final combined JSON file using your file write tool

## Quick Reference

```
URL: https://www.youtube.com/results?search_query={QUERY}
Wait: 2-3 seconds
Extract: title, url, thumbnail, channel, views, date, duration
Filter: durationSeconds >= 300
Save each search to: /Users/alexsmini/.openclaw/workspace/mindstream/data/scrape-{Name}-{keyword}-{timestamp}.json
Save combined to:    /Users/alexsmini/.openclaw/workspace/mindstream/data/scrape-{timestamp}.json
Close tabs: When finished
```