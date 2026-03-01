# MindStream Static Migration Plan

## Overview

Transform MindStream from a dynamic Next.js app (requiring server + SQLite) into a fully static site that can be hosted anywhere.

---

## Current Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Client        │ ──► │   Next.js API   │ ──► │   SQLite DB     │
│   (React)       │     │   (/api/feed)   │     │   (mindstream.db)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Target Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Client        │ ──► │   Static JSON   │
│   (React)       │     │   (videos.json) │
└─────────────────┘     └─────────────────┘
        │
        ▼
┌─────────────────┐
│   Video URLs    │
│   (YouTube)     │
└─────────────────┘
```

---

## Migration Steps

### Step 1: Export Script

Create `scripts/export-json.ts` that:
1. Reads from SQLite database (`mindstream.db`)
2. Queries all videos with thought leader info (JOINs content_items, content_sources, thought_leaders)
3. Outputs to `public/videos.json`

**Output format:**
```json
{
  "generatedAt": "2026-02-24T12:00:00Z",
  "videos": [
    {
      "id": "abc123",
      "title": "AI and the Future",
      "description": "...",
      "thumbnailUrl": "https://...",
      "publishedAt": "2026-02-20T10:00:00Z",
      "duration": "10:32",
      "durationSeconds": 632,
      "viewCount": 150000,
      "platform": "youtube",
      "thoughtLeader": {
        "id": "andrej-karpathy",
        "name": "Andrej Karpathy",
        "avatarUrl": null,
        "verified": true
      },
      "url": "https://www.youtube.com/watch?v=abc123"
    }
  ]
}
```

### Step 2: Update Frontend

**File: `src/app/page.tsx`**

Change from:
```typescript
const res = await fetch('/api/feed?page=1&limit=50', { cache: 'no-store' });
const json: FeedResponse = await res.json();
setFeed(json.data || []);
```

To:
```typescript
import videosData from '@/../public/videos.json';

const feed = videosData.videos as FeedItem[];
setFeed(feed);
```

Also remove:
- `useEffect` that calls `fetchFeed()`
- Loading states for initial data
- The `/api/feed` dependency

### Step 3: Build Configuration

**File: `next.config.ts`**

Add:
```typescript
const nextConfig: NextConfig = {
  output: 'export',
  // Optional: disable image optimization for static export
  images: {
    unoptimized: true,
  },
};
```

### Step 4: Remove Unused Code (Optional)

Delete or ignore:
- `src/app/api/` directory (all routes)
- `src/lib/db.ts` (database)
- `src/lib/cache.ts` (caching logic)
- `src/mindstream.db` (runtime DB not needed)

### Step 5: Build & Deploy

```bash
npm run build
# Output in: src/out/ (or src/.next/static/chunks/pages/)
```

Serve the `out/` folder with any static host (nginx, GitHub Pages, Cloudflare Pages, etc.)

---

## Data Flow (Option A - Recommended)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  YouTube API    │ ──► │   SQLite DB     │ ──► │   JSON Export   │
│  (scraper)      │     │  (source truth) │     │  (build artifact)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Static Site   │
                                               │   (HTML/JS)     │
                                               └─────────────────┘
```

### Workflow

1. **Daily (or on demand):** Run scraper → updates SQLite
2. **Build time:** Export script reads SQLite → outputs JSON
3. **Deploy:** Static files go to hosting

### Keeping SQLite

- The DB remains your **source of truth**
- Run scraper the same way you do now
- Export script is a new step before `npm run build`
- Same maintainability you're used to

---

## Data Refresh Strategy

Since it's static, you need to regenerate when content changes:

| Approach | How | When |
|----------|-----|------|
| Manual | Run scraper → export script → build → deploy | When you add new videos |
| CI/CD | GitHub Action runs scraper + export + deploy | Daily/weekly |
| Cron | OpenClaw cron job triggers export + build | On a schedule |

---

## What Breaks

These features won't work in static mode:

1. **"Refresh from YouTube" button** — No server to call APIs (would need to rebuild)
2. **Pagination** — Could do client-side if needed
3. **Real-time updates** — Stale until next rebuild

**Still works:**
- Search/filtering — Load all videos from JSON, filter client-side (fine for <500 videos)
- Video selection — React state works the same

---

## Files to Modify

| File | Action |
|------|--------|
| `scripts/export-json.ts` | Create (new) - reads DB, writes JSON |
| `src/app/page.tsx` | Modify (replace fetch with import) |
| `src/app/api/` | Delete (no longer needed at runtime) |
| `src/lib/cache.ts` | Delete (optional - was for runtime caching) |
| `next.config.ts` | Modify (add output: 'export') |

**Keep:**
- SQLite DB (`mindstream.db`) — your source of truth
- `src/lib/db.ts` — still needed by export script

---

## Estimated Effort

- Export script: ~30 min
- Frontend changes: ~15 min
- Build config: ~10 min
- Testing: ~15 min

**Total: ~1-1.5 hours**
