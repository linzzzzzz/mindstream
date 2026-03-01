# Browser Scraper Integration

## Overview

MindStream uses two methods to fetch YouTube data:

| Method | Source | Quota | Status |
|--------|--------|-------|--------|
| YouTube Search API | Google API | Limited (10k/day) | ✅ Implemented |
| Browser Scraper | Puppeteer | Unlimited | ✅ Implemented |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MindStream App                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌──────────────┐                     │
│  │  API Route   │     │   Puppeteer  │                     │
│  │/api/scrape   │────▶│   Browser    │                     │
│  └──────────────┘     └──────┬───────┘                     │
│                               │                              │
│                         Scrapes                             │
│                         YouTube                             │
│                               │                              │
│                               ▼                              │
│                        ┌──────────┐                         │
│                        │ SQLite   │◀── Save results        │
│                        │  DB      │                        │
│                        └──────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Implementation

| Component | File | Description |
|-----------|------|-------------|
| Scraper Script | `src/app/api/scrape-browser/route.ts` | Puppeteer-based scraper |
| YouTube Library | `src/lib/youtube-search.ts` | YouTube API client |
| Skills | `skills/youtube-search-scraper/` | OpenClaw skill docs |

## Why Puppeteer Instead of OpenClaw Browser?

| Factor | Puppeteer | OpenClaw Browser |
|--------|-----------|------------------|
| Works in API | ✅ Yes | ❌ No (needs session) |
| No quota | ✅ Yes | ✅ Yes |
| Self-contained | ✅ Yes | ❌ Needs gateway |

The Puppeteer approach works directly in the Next.js API without needing the OpenClaw gateway.

## How It Works

### 1. User Clicks "Refresh (Browser)"

```javascript
// Frontend calls scrape API
const res = await fetch('/api/scrape-browser', { method: 'POST' });
```

### 2. API Triggers OpenClaw

The API endpoint calls the OpenClaw gateway to spawn a scraping task:

```javascript
// POST /api/scrape-browser
// Calls OpenClaw sessions_spawn with the scraping task
```

### 3. OpenClaw Agent Scrapes

The sub-agent uses the `youtube-search-scraper` skill:
- Navigates to YouTube search results page
- Extracts video titles, URLs, channels, dates
- Returns structured JSON

### 4. Results Saved to SQLite

The scraped data is saved to the database, same as API method.

## Files

| File | Purpose |
|------|---------|
| `skills/youtube-search-scraper/SKILL.md` | Skill definition |
| `skills/youtube-search-scraper/references/selectors.md` | CSS selectors |
| `src/lib/youtube-browser-scraper.ts` | Scraper library |
| `src/app/api/scrape-browser/route.ts` | API endpoint (TODO) |

## Implementation Status

- [x] YouTube Search API integration ✅
- [ ] Browser scraper skill ✅
- [ ] Browser scraper API integration 🔄
- [ ] Automatic fallback logic 🔄

## Usage

### Current (API)

```bash
# Uses YouTube API
curl -X POST http://localhost:3000/api/refresh
```

### After Integration (Browser)

```bash
# Uses browser scraper (no quota)
curl -X POST http://localhost:3000/api/scrape-browser
```

## Requirements

For browser scraping to work:

1. **OpenClaw Gateway must be running**
   ```bash
   openclaw gateway
   ```

2. **Chrome with extension must be running**
   - Extension loaded in Chrome
   - Browser connected to OpenClaw

3. **User must be in an OpenClaw session**
   - For sub-agent spawning to work

## Troubleshooting

### "Browser not connected"

Make sure:
1. OpenClaw gateway is running
2. Chrome extension is loaded
3. Click extension icon to attach

### "Session not found"

Sub-agents need an active parent session. The API must be called from within an OpenClaw session context.

## Future Improvements

1. Combine both buttons into one (auto-fallback)
2. Cache results from both methods
3. Show which source was used
