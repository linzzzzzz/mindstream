# Product Requirements Document (PRD)

## MindStream - AI Thought Leader Content Aggregator

**Version:** 1.0  
**Date:** 2026-02-22  
**Status:** Draft  
**Author:** [User]  

---

## 1. Executive Summary

### Product Name
**MindStream** ✅ (confirmed)

**Potential Domain:** mindstream.ai, mindstream.io (TBD)

### Product Vision
MindStream is a person-centric AI content aggregator that consolidates videos, podcasts, and talks from AI thought leaders across YouTube, Bilibili, and other platforms into a searchable, unified feed.

### Problem Statement
AI enthusiasts and professionals currently face significant friction in staying updated with AI content:
- Manually checking multiple YouTube channels is time-consuming
- Bilibili hosts valuable Chinese AI content but has no integration with English platforms
- No existing solution provides push notifications for new AI talks/podcasts
- Language barriers prevent discovery of relevant content across platforms

### Target Users
1. **AI Researchers & Engineers** - Stay current with latest AI talks, papers explained, technical deep-dives
2. **AI Enthusiasts** - Follow prominent AI thought leaders and podcasts
3. **Tech Professionals** - Keep up with AI trends for career/professional development
4. **Students** - Learn from top AI educators and researchers
5. **Content Creators** - Monitor competitors and gather research material

---

## 2. Market Opportunity

### Market Gap
- **No unified solution** exists that combines YouTube + Bilibili video aggregation
- **No dedicated AI thought leader curator** exists in the market
- **Push notifications for new videos** are not a core feature anywhere
- Existing RSS readers require manual setup and lack platform integration

### Competitive Advantage
| Feature | Existing Solutions | Our Product |
|---------|-------------------|-------------|
| YouTube + Bilibili | ❌ | ✅ |
| AI-focused curation | ❌ | ✅ |
| Push notifications | ❌ | ✅ |
| Bilingual (EN/CN) | ❌ | ✅ |
| Pre-curated channels | ❌ | ✅ |

---

## 3. User Personas

### Persona 1: Alex - AI Researcher
- **Age:** 28-35
- **Background:** PhD student or industry researcher
- **Goals:** Stay current with AI papers, talks from top researchers (Lex Fridman, Andrej Karpathy, Ilya Sutskever)
- **Pain Points:** Misses videos, manually checks 10+ channels
- **Tech Level:** High - comfortable with APIs, self-hosting options

### Persona 2: Wei - Bilingual AI Professional
- **Age:** 25-35
- **Background:** Works in AI industry, reads both English and Chinese content
- **Goals:** Follow both Western and Chinese AI thought leaders
- **Pain Points:** Hard to find Chinese AI content in English platforms
- **Tech Level:** Medium - wants plug-and-play solution

### Persona 3: Jordan - AI Enthusiast
- **Age:** 20-30
- **Background:** Software developer learning AI/ML
- **Goals:** Discover quality AI content, learn from experts
- **Pain Points:** Overwhelmed by content volume, doesn't know who to follow
- **Tech Level:** Low - wants curated recommendations

---

## 4. Functional Requirements

### 4.1 Two Deployment Options

MindStream can be deployed in two modes:

#### Option A: Static Site (Current Implementation)
- **Hosting:** Cloudflare Pages, GitHub Pages, Netlify, or any static host
- **Data:** Pre-built JSON file (regenerated on each update)
- **Pros:** Free hosting, fast, no server required, highly scalable
- **Cons:** Requires rebuild to update content, no real-time features

#### Option B: Dynamic Site (Future)
- **Hosting:** Vercel, Railway, Fly.io, or self-hosted server
- **Data:** SQLite database (real-time updates)
- **Pros:** Real-time data, search, notifications, user accounts
- **Cons:** Requires server, more complex deployment

---

### 4.2 Core Features - Thought Leader Aggregation

#### F1: Thought Leader Aggregation (Person-Centric)
- **F1.1** ✅ System aggregates content from pre-curated AI thought leaders
- **F1.2** Content sources include: YouTube channels, Bilibili channels, podcast appearances
- **F1.3** Each thought leader can have multiple content sources (multi-platform)
- **F1.4** ✅ Initial database includes 4 thought leaders (expandable)
- **F1.5** System tracks appearances - guest appearances, interviews

#### F2: Unified Feed (Public, No Login Required)
- **F2.1** ✅ Display all content in a single chronological feed (newest first)
- **F2.2** ✅ Show content metadata: title, thought leader, source, duration, date
- **F2.3** ✅ Display thumbnails from source platform
- **F2.4** Support filtering by platform (YouTube only, Bilibili only, All) — *Static: N/A*
- **F2.5** ✅ Support filtering by thought leader (multi-select)
- **F2.6** Support filtering by topic/category — *Static: N/A*

#### F3: Video Playback & Preview (Two-Column Layout)
- **F3.1** ✅ Two-column layout: video list on left (450px), embedded player on right
- **F3.2** ✅ Click video to preview in embedded player (no autoplay by default)
- **F3.3** ✅ Embed videos directly in the app (YouTube player)
- **F3.4** ✅ Deep link to source platform as fallback
- **F3.5** Track watched/not watched status per user — *Dynamic only*

#### F3B: Search (MVP - Core Feature!)
- **F3B.1** Full-text search — *Dynamic only*
- **F3B.2** Search by thought leader name — *Dynamic only*
- **F3B.3** Search by topic/category — *Dynamic only*
- **F3B.4** Search results ranked by relevance and recency*
- **F3B.5** Auto-complete suggestions — *Dynamic only — *Dynamic only*

*Note: Search requires server-side processing. Static site uses client-side filtering by thought leader only.*

#### F4: Notifications (Optional - No Auth Required)
- **F4.1** Telegram bot notifications — *Dynamic only*
- **F4.2** No email/push notifications in MVP (requires auth) — *Dynamic only*
- **F4.3** ✅ Public feed available without login

#### F4B: AI-Powered Video Clips (Key MVP Feature!)
- **F4B.1** Integrate with OpenClip project to generate short clips — *Future*
- **F4B.2** Extract most engaging moments from videos using AI — *Future*
- **F4B.3** Generate clips in multiple languages (EN/CN) — *Future*
- **F4B.4** Upload clips to Bilibili automatically — *Future*
- **F4B.5** Push clip links to users via Telegram — *Future*

*Note: This is a key differentiator for the app. Requires: (1) OpenClip integration, (2) Bilibili upload automation*

#### F5: Thought Leader Directory
- **F5.1** Browse all curated thought leaders in a directory — *Future*
- **F5.2** View thought leader profile: bio, topics, all content sources — *Future*
- **F5.3** Filter by topic/category — *Future*
- **F5.4** Filter by platform — *Future*
- **F5.5** Show total content count per thought leader — *Future*
- **F5.6** Community can suggest new thought leaders — *Future*

#### F6: Mobile Support
- **F6.1** ✅ Responsive design for mobile devices
- **F6.2** ✅ Mobile: List view with tap-to-preview
- **F6.3** ✅ Mobile: Full-screen video player with "Go Back" button
- **F6.4** ✅ Mobile: Multi-select thought leader filter

#### F7: Data Refresh Workflow
- **F7.1** ✅ Trigger scrape via CLI script
- **F7.2** ✅ Export database to JSON
- **F7.3** ✅ Build static site
- **F7.4** ✅ Deploy to static hosting
- **F7.5** Telegram notification when scrape complete — *Dynamic only*

### 4.2 Enhanced Features (Post-MVP)

#### F6 (Phase 2): User Accounts & Personalization
- **F6.1** Email/password authentication
- **F6.2** OAuth sign-in (Google, GitHub)
- **F6.3** Personalized feed based on subscriptions
- **F6.4** Watch history tracking
- **F6.5** "Watch Later" playlists

#### F7: Advanced Search & Discovery
- **F7.1** Filter by topic tags (LLMs, Computer Vision, Robotics, Ethics, etc.)
- **F7.2** Recommend similar content based on watch history
- **F7.3** "Related thought leaders" suggestions based on similar topics
- **F7.4** Trending thought leaders section (growing fastest)
- **F7.5** Community submissions: users can suggest new thought leaders
- **F7.6** Platform cross-reference: show if same creator exists on YouTube + Bilibili
- **F7.7** Thought leader verification badge (official/verified accounts)

#### F8: Bilingual Support (Implemented in MVP)
- **F8.1** Full UI in English and Chinese (Simplified)
- **F8.2** Auto-translate video titles/descriptions
- **F8.3** Show both original and translated titles

#### F9: Playlist/Collections
- **F9.1** Allow users to create custom playlists
- **F9.2** Share playlists with other users
- **F9.3** "Watch Later" default playlist

#### F10: Analytics Dashboard
- **F10.1** Show watch time statistics
- **F10.2** Display most-watched channels/categories
- **F10.3** Weekly/monthly activity reports

---

## 5. Non-Functional Requirements

### 5.1 Performance
- **NFR1** Feed shall load within 2 seconds on stable internet
- **NFR2** New video detection shall occur within 15 minutes of publication
- **NFR3** Support 10,000+ concurrent users for MVP

### 5.2 Scalability
- **NFR4** Architecture shall support horizontal scaling
- **NFR5** Database design shall handle 100,000+ videos and growing

### 5.3 Reliability
- **NFR6** System uptime shall be 99.5% (excluding scheduled maintenance)
- **NFR7** Automatic retry for failed API calls (YouTube/Bilibili)
- **NFR8** Rate limiting compliance with platform APIs

### 5.4 Security
- **NFR9** All API keys stored securely (environment variables, secrets manager)
- **NFR10** User passwords hashed with bcrypt (min 12 rounds)
- **NFR11** HTTPS for all production traffic

### 5.5 Privacy
- **NFR12** GDPR compliant data handling
- **NFR13** Users can delete their account and all associated data
- **NFR14** No tracking pixels or third-party analytics without consent

---

## 6. Technical Architecture

### 6.1 Technology Stack (Recommended)

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Frontend** | Next.js + React | SEO-friendly, great developer experience |
| **Mobile** | React Native | Share code with web, cross-platform |
| **Backend** | Node.js / Python | Strong API ecosystem |
| **Database** | SQLite (libsql/better-sqlite3) | Local-first, open-source friendly |
| **Video Index** | YouTube Data API v3, Bilibili API | Official APIs for reliability |
| **Notifications** | Telegram Bot API, SendGrid | Reliable, free tier available |
| **Hosting** | Vercel (FE) + Railway/Render (BE) | Easy scaling, reasonable cost |
| **Monitoring** | Sentry + LogRocket | Error tracking + session replay |

> **Note:** SQLite is chosen for local-first, open-source friendliness. Optional cloud deployment via Supabase can be added later for production.

### 6.1.1 Local-First Deployment (Recommended for Open-Source)

MindStream is designed to run locally on user's machines, giving them full control and customization ability.

#### Prerequisites
| Requirement | Installation |
|-------------|--------------|
| Node.js 18+ | nodejs.org or `brew install node` |
| Google Chrome | google.com/chrome |
| OpenClaw CLI | `npm install -g openclaw` |

#### Running Locally
```bash
# Terminal 1: Start OpenClaw Gateway
openclaw gateway

# Terminal 2: Start MindStream
cd mindstream/src
npm run dev

# Open http://localhost:3000
```

#### Architecture When Running Locally
```
User's Machine:
┌─────────────┐    ┌─────────────┐    ┌─────────┐
│  Browser   │───▶│  Next.js   │───▶│ SQLite  │
│  (website) │    │  :3000     │    │  DB     │
└─────────────┘    └──────┬──────┘    └─────────┘
                         │
                  ┌──────▼──────┐
                  │  OpenClaw  │
                  │  Gateway   │
                  │  :18789    │
                  └─────────────┘
```

#### Setup Guide
See `SETUP.md` for detailed installation and troubleshooting instructions.

### 6.2 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Web/Mobile)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway / Auth                     │
│                   (Next.js API Routes)                      │
└─────────────────────────────────────────────────────────────┘
          │                    │                    │           │
          ▼                    ▼                    ▼           │
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  Video Indexer  │  │  User Service   │  │ Thought Leader  │ │
│  (YouTube API) │  │  (Auth, prefs)  │  │ Discovery Svc   │ │
│  (Bilibili API)│  │                 │  │ (Search, Browse)│ │
└─────────────────┘  └─────────────────┘  └─────────────────┘ │
          │                    │                    │           │
          ▼                    ▼                    ▼           │
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Notification   │  │  SQLite         │  │  SQLite         │
│  Service        │  │  (local file)  │  │ (thought_leaders│
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 6.3 API Integrations

#### YouTube Data API v3
- **Quota:** 10,000 units/day (free) - sufficient for MVP
- **Endpoints needed:**
  - `search.list` - discover new videos
  - `channels.list` - get channel info
  - `playlistItems.list` - get channel uploads

#### Bilibili API
- **Registration:** Required (free)
- **Endpoints needed:**
  - `x/v2/web/video/info` - get video details
  - `x/v3/channel/list` - get channel info
  - `x/feed/list` - get feed

### 6.4 Video Scraping Mechanism (OpenClaw Agent)

The app uses **OpenClaw Agent** to scrape YouTube videos via browser automation.

#### Browser Profile
- **Default:** `openclaw` (managed browser)
- **Config:** Set in `~/.openclaw/openclaw.json` as `"browser": { "defaultProfile": "openclaw" }`

#### How It Works

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  User       │────▶│  /api/trigger-  │────▶│  OpenClaw       │
│  clicks     │     │  agent          │     │  system event   │
│  🤖 button  │     │  (POST)         │     │  (TASK)        │
└─────────────┘     └──────────────────┘     └────────┬────────┘
                                                    │
                                                    ▼
                                          ┌─────────────────────┐
                                          │  Agent (me)         │
                                          │  receives task      │
                                          └─────────┬───────────┘
                                                    │
                    ┌───────────────────────────────┼───────────────────────────────┐
                    │                               │                               │
                    ▼                               ▼                               ▼
                                  ┌───────────────────┐           ┌───────────────────┐
                                  │ youtube-search-   │           │ youtube-save-to   │
                                  │ scraper skill    │           │ sqlite skill     │
                                  │ (browse & extract)│           │ (save to DB)     │
                                  └───────────────────┘           └───────────────────┘
                                                    │
                                                    ▼
                                          ┌─────────────────────┐
                                          │  Send Telegram      │
                                          │  notification       │
                                          │  (Done! X videos)  │
                                          └─────────────────────┘
```

#### Skills Used

The scraping uses two modular skills:

1. **youtube-search-scraper** (`skills/youtube-search-scraper/SKILL.md`)
   - Uses browser tool to search YouTube
   - Extracts video data: title, URL, thumbnail, channel, views, date, duration
   - Returns JSON array of videos

2. **youtube-save-to-sqlite** (`skills/youtube-save-to-sqlite/SKILL.md`)
   - Maps videos to `content_source_id`
   - Inserts into SQLite database
   - Sends Telegram notification on completion

#### Task Definition

The scraping task is defined in `/api/trigger-agent/route.ts`:

```typescript
const TASK = `SCRAPE TASK: Update MindStream with latest AI videos.

Follow these skills:
1. youtube-search-scraper: Scrape YouTube for latest videos
2. youtube-save-to-sqlite: Save results to database

## Steps:
### Step 1: Scrape YouTube
For each leader, search YouTube and get latest videos:
- Sam Altman: Sam Altman AI interview
- Andrej Karpathy: Andrej Karpathy tutorial
- Dario Amodei: Dario Amodei AI interview
- Demis Hassabis: Demis Hassabis DeepMind talk

### Step 2: Save to Database
- Database: /path/to/mindstream.db
- Map each leader to their content_source_id

### Step 3: Notify User
- Send Telegram message to chat ID: 8468925147

### Step 4: Cleanup
- Close all new tabs opened during scraping
- Keep only 1 tab attached
```

#### API Endpoint

- **POST** `/api/trigger-agent`
- Triggers OpenClaw system event with the task
- Returns: `{ success: true, message: "Agent triggered!" }`

#### Telegram Notification

After scraping completes, the agent sends a Telegram message:
```
Done! X videos saved. Refresh the page!
```

---

### 6.5 AI Clip Generation & Bilibili Upload

The app will integrate with **OpenClip** to generate AI-powered video clips.

#### How It Works

```
New Video Scraped
       │
       ▼
┌──────────────────┐
│  OpenClip AI    │ ──▶ Generate short clips (highlights)
│  Integration    │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Bilibili API   │ ──▶ Upload clips automatically
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Telegram       │ ──▶ Push clip URL to users
│  Notification   │
└──────────────────┘
```

#### OpenClip Integration

- **Purpose:** Generate short, engaging clips from full videos
- **Project:** Reuse existing OpenClip project for clip extraction
- **Input:** YouTube video URL
- **Output:** Short video clips (30-90 seconds)

#### Bilibili Upload

- **Purpose:** Host AI-generated clips
- **Platform:** Bilibili (more clip-friendly than YouTube)
- **API:** Bilibili creator upload API
- **Authentication:** Requires Bilibili account credentials

#### Clip Generation Workflow

```
1. After scraping new videos:
   ├── Select videos with high engagement potential
   └── Queue for clip generation

2. OpenClip processes videos:
   ├── Analyze video content
   ├── Identify highlight moments
   └── Generate 1-3 short clips

3. Upload to Bilibili:
   ├── Auto-generate title & description
   ├── Add relevant tags
   └── Publish to account

4. Push to Telegram:
   ├── Send to subscribed users
   └── Include: Clip title + Bilibili URL + Summary
```

#### MVP Scope for Clips

- **Phase 1 (MVP):** Generate and upload clips for selected top videos
- **Manual trigger:** Button to generate clips for specific videos
- **Test with few leaders first:** Start with Sam Altman + Andrej Karpathy

#### Requirements

| Component | Status | Notes |
|-----------|--------|-------|
| OpenClip integration | 🔄 Explore | Need to integrate with existing project |
| Bilibili API access | 🔄 Explore | Need account + API credentials |
| Auto-upload workflow | 🔄 Explore | Requires authentication handling |
| Telegram push | 🔄 Explore | Send clip links to users |

---

## 7. Initial Channel List (Curated AI Thought Leaders)

### 7.1 Thought Leader Database Schema (Person-Centric)

The core entity is the **Thought Leader (Person)**, not the channel.

#### Table: thought_leaders
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `name` | String | Display name |
| `display_name` | String | Public display name (may differ) |
| `bio` | Text | Short biography |
| `avatar_url` | String | Profile image URL |
| `language` | Enum | English, Chinese, Bilingual |
| `topics` | Array | Topic tags [LLMs, CV, Robotics, etc.] |
| `verified` | Boolean | Official/verified account |
| `created_at` | Timestamp | Date added to curation |

#### Table: content_sources
Each thought leader can have multiple sources (YouTube channel, Bilibili channel, podcast, conference series):
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `thought_leader_id` | UUID | FK to thought_leaders |
| `platform` | Enum | youtube, bilibili, podcast, conference, twitter |
| `source_id` | String | Platform-specific ID (e.g., UC channel ID) |
| `source_handle` | String | Handle/username |
| `source_url` | String | Link to source |
| `subscriber_count` | Integer | Current subscriber count |
| `last_fetched_at` | Timestamp | Last sync time |

#### Table: content_items
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `content_source_id` | UUID | FK to content_sources |
| `title` | String | Content title |
| `description` | Text | Content description |
| `url` | String | Link to content |
| `thumbnail_url` | String | Preview image |
| `duration_seconds` | Integer | Video length |
| `published_at` | Timestamp | Publication date |
| `content_type` | Enum | video, podcast_episode, interview, conference_talk |
| `topics` | Array | Auto-detected or assigned tags |

### 7.2 Initial Curated Thought Leaders (MVP Starting Point)

*MVP Phase: Start with 4 key AI leaders*

| # | Name | Role | Primary Topics | Why Include |
|---|------|------|----------------|-------------|
| 1 | **Sam Altman** | OpenAI CEO | LLMs, AI Policy, Startups | Leading voice in AI |
| 2 | **Andrej Karpathy** | Former Tesla AI Director | LLMs, AI Education, Self-Driving | Excellent AI tutorials, technical depth |
| 3 | **Dario Amodei** | Anthropic CEO | AI Safety, LLMs, Ethics | Leading AI safety researcher |
| 4 | **Demis Hassabis** | Google DeepMind CEO | AGI, AlphaFold, Neuroscience | Head of leading AI research lab |

*Note: This list will expand after MVP based on user demand*

### 7.3 Topic Categories

| Category | Description | Example Leaders |
|----------|-------------|----------------|
| **LLMs** | Large Language Models | Andrej Karpathy, Sam Altman, Jay Alammar |
| **Computer Vision** | Image/Video AI | Yann LeCun, 3Blue1Brown |
| **Robotics** | Physical AI, Robots | Lex Fridman, Sentdex |
| **AI Research** | Papers, Academia | Yannic Kilcher, Two Minute Papers |
| **AI Ethics** | AI safety, policy | Lex Fridman (episodes) |
| **AI Education** | Teaching AI | 3Blue1Brown, 跟李沐学AI |
| **Tech News** | Industry news | 科技老高 |

*Note: This list will be expanded based on user demand and community suggestions*

---

## 8. User Flows (MVP - No Auth Required)

### Flow 1: New User (MVP)
```
1. User lands on homepage → sees two-column layout
2. Left column: Video list with thumbnails + filter dropdown
3. Right column: Video preview player
4. User clicks filter → selects thought leader to filter videos
5. User clicks video → preview plays in right column
6. User clicks again → deep links to YouTube/Bilibili
7. User searches using search box in header
```

### Flow 2: Search & Discovery (MVP)
```
1. User types in search box in header
2. Auto-suggestions appear (thought leaders, topics) — *Not yet implemented*
3. User selects suggestion or presses Enter
4. Results filter the video list
5. User clicks video → preview plays in right column
```

### Flow 3: Browse by Topic (MVP)
```
1. User clicks filter dropdown
2. User selects thought leader from dropdown
3. Video list filters to show only that leader's videos
4. User clicks video → preview plays in right column
5. User clicks content → deep links to platform
```

### Flow 4: Thought Leader Profile (MVP)
```
1. User clicks on thought leader name/avatar
2. User sees thought leader profile:
   - Bio, topics, verified badge
   - All content sources (YouTube, Bilibili)
   - All their videos in chronological order
3. User clicks video → deep links to platform
```

### Flow 5: Telegram Notifications (Phase 2 - Post-Auth)
```
1. User signs up / logs in
2. User connects Telegram account
3. User selects thought leaders to follow
4. System sends notifications for new content
5. User clicks notification → opens app directly to video
```

---

## 9. Current UI Layout

The current implementation uses a **two-column layout with video preview**:

```
┌─────────────────────────────────────────────────────────────────────┐
│  🧠 MindStream                                    [🔍 Search]    │
├─────────────────────────────────────────────────────────────────────┤
│  [🤖 Scrape Videos]                                                │
├──────────────────────────┬──────────────────────────────────────────┤
│  👤 筛选 ▼   26个视频  │                                          │
├──────────────────────────┤    ┌────────────────────────────────┐    │
│  ┌──────────────────┐   │    │                                │    │
│  │  [Thumbnail]     │   │    │     YouTube Embed              │    │
│  │  ▶ 12:34        │   │    │     (Click to play)           │    │
│  └──────────────────┘   │    │                                │    │
│  Title here             │    └────────────────────────────────┘    │
│  Sam Altman • 1.2M • 3d│                                          │
│  ┌──────────────────┐   │    Title of Selected Video          │
│  │  [Thumbnail]     │   │    Sam Altman • 1.2M views • 3天前   │
│  │  ▶ 45:21        │   │                                      │
│  └──────────────────┘   │    Description text here...          │
│  Another title          │                                      │
│  Andrej K. • 850K • 5d │                                      │
│  ...                   │                                      │
└──────────────────────────┴──────────────────────────────────────────┘
```

### UI Components

| Component | Description |
|-----------|-------------|
| Header | Logo + Search box + Language toggle (EN/中文) |
| Controls | Scrape button to trigger OpenClaw agent |
| Left Column (450px) | Filter dropdown + video list with thumbnails + date |
| Right Column | Embedded YouTube player (max 711x400) + video details + description |
| Filter Dropdown | Filter by thought leader (All / Sam Altman / Andrej / etc.) |
| Language Toggle | Button to switch between English and Chinese |

### Video Filtering

- **Duration filter:** Only videos 5+ minutes (300+ seconds) are shown - filters out Shorts/clips
- **Date filter:** Uses YouTube `duration:long` and `after:YYYY-MM-DD` operators during scraping

### Bilingual Support (Implemented)

The app supports **English and Chinese** (Simplified):

| English | Chinese |
|---------|---------|
| Loading... | 加载中... |
| Filter | 筛选 |
| All | 全部 |
| X videos | X 个视频 |
| Select a video | 选择一个视频 |
| 中文 button | EN button |

Users can toggle language by clicking the **中文 / EN** button in the header.

### Current Features
- ✅ Two-column layout with preview player
- ✅ Filter by thought leader (dropdown)
- ✅ YouTube embedded player (click to play, max 711x400)
- ✅ Video count display
- ✅ Search box in header
- ✅ Video description below preview (scrollable)
- ✅ Duration filter (5+ minutes only)
- ✅ Bilingual support (EN/中文)
- ✅ Telegram notifications after scraping
- ✅ OpenClaw browser automation (openclaw profile)

---

## 10. MVP Success Metrics

### Engagement Metrics
- **DAU/MAU Ratio:** Target 40%+
- **Average Session Duration:** Target 5+ minutes
- **Videos Watched per User per Week:** Target 10+

### Growth Metrics
- **Month 1 Target:** 1,000 registered users
- **Month 3 Target:** 10,000 registered users
- **Month 6 Target:** 50,000 registered users

### Technical Metrics
- **Page Load Time:** < 2 seconds (P95)
- **API Response Time:** < 500ms (P95)
- **Notification Delivery Rate:** > 95%
- **System Uptime:** > 99.5%

---

## 11. Monetization (Post-MVP)

### Option A: Freemium
- **Free:** 5 channel subscriptions, daily notifications, web access
- **Pro ($5/month):** Unlimited subscriptions, real-time notifications, mobile app, no ads

### Option B: Subscription
- **$9.99/month:** Full access, priority notifications, offline mode, exclusive features

### Option C: B2B
- **Enterprise:** Custom channel lists, team features, API access
- **Pricing:** Custom (contact sales)

---

## 12. Roadmap

### Phase 1: MVP (Months 1-2) - No Auth, Search-First + AI Clips
- [ ] **Thought Leader Database** - Build curated DB of 30-50 AI thought leaders
- [ ] **Multi-Source Content Aggregation** - YouTube + Bilibili (per thought leader)
- [ ] **Public Feed** - No login required, chronological feed
- [ ] **Search** - Full-text search (thought leaders, topics, content)
- [ ] **Thought Leader Directory** - Browse by name, topic, platform
- [ ] **Deep Links** - Click to open in YouTube/Bilibili app
- [ ] **Basic Analytics** - Track popular content, top thought leaders
- [ ] **AI Clip Generation** - Explore OpenClip integration for clip creation
- [ ] **Bilibili Upload** - Explore automatic clip upload to Bilibili

### Phase 2: User Accounts & Notifications (Months 3-4)
- [ ] User authentication (email + OAuth)
- [ ] Personalized feed (follow specific thought leaders)
- [ ] Telegram bot notifications (with AI clip links)
- [ ] Watch history tracking
- [ ] "Watch Later" playlists
- [ ] Community suggestions for new thought leaders

### Phase 3: AI Clips + Mobile (Months 5-6)
- [ ] Full Bilibili integration
- [ ] **Auto-generate and upload AI clips** - Integrate OpenClip + Bilibili upload
- [ ] Mobile app (React Native)
- [ ] Email notifications
- [ ] Recommendations engine

### Phase 4: Growth & Monetization (Months 7-12)
- [x] Bilingual UI (EN/CN)
- [ ] Monetization (freemium model)
- [ ] API for third-party integrations
- [ ] Enterprise features (custom channel lists)

---

## 13. Open Questions

- [ ] **Q1:** Should we prioritize YouTube first, or build both from day 1?
- [ ] **Q2:** What is the preferred notification channel? (Telegram vs Email vs In-app)
- [ ] **Q3:** Should we open-source the backend for community contributions?
- [ ] **Q4:** What is the branding/product name?
- [ ] **Q5:** Should we target iOS first or Android first for mobile?
- [ ] **Q6:** How aggressive should we be with content licensing/ToS compliance?

---

## 14. Appendix

### A. Reference Documents
- Research Document: `research-ai-video-aggregator.md`
- YouTube Data API Documentation: https://developers.google.com/youtube/v3
- Bilibili API Documentation: https://open.home.xiaomi.com/

### B. Glossary
- **Aggregator:** Software that collects content from multiple sources
- **Deep Link:** URL that links directly to specific content in an app
- **OAuth:** Standard for authorization, allows "Sign in with Google/GitHub"
- **P95:** 95th percentile - 95% of requests are faster than this
- **RSS:** Really Simple Syndication - web feed format
- **ToS:** Terms of Service

### C. Similar Products to Study
- Feedly (https://feedly.com)
- Inoreader (https://inoreader.com)
- RSSHub (https://github.com/DIYgod/RSSHub)
- NewPipe (YouTube client, open source)

---

## 15. Deployment Options

### Option A: Static Site (Current)

**Live at:** https://mindstream-42g.pages.dev

| Aspect | Details |
|--------|---------|
| Hosting | Cloudflare Pages (free) |
| Data | Pre-built JSON from SQLite |
| Update Flow | Scrape → Export JSON → Build → Deploy |
| Scripts | `refresh.sh`, `build.sh`, `deploy.sh` |
| Pros | Free, fast, no server, CDN |
| Cons | Requires rebuild to update |

**Files:**
- `mindstream-static/` - Complete static site project
- `mindstream.db` - SQLite database with video data
- `public/videos.json` - Exported data (generated)

### Option B: Dynamic Site (Future)

For full features like search, notifications, user accounts:

| Aspect | Details |
|--------|---------|
| Hosting | Vercel, Railway, or self-hosted |
| Data | SQLite (runtime queries) |
| Features | Search, notifications, user accounts |
| Pros | Real-time, full features |
| Cons | Requires server, more complex |

**Migration Path:**
1. Keep using current static site for viewing
2. Add dynamic API routes when needed
3. Deploy to Vercel for full functionality

---

*End of PRD*
