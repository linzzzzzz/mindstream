# Research Document: AI Thought Leader Video Aggregator

**Project:** Cross-platform video aggregator for YouTube & Bilibili AI thought leader content with notifications  
**Date:** 2026-02-22  
**Prepared for:** User

---

## 1. Executive Summary

After comprehensive research, **no direct competitor exists** that combines YouTube + Bilibili video aggregation with push notifications specifically for AI thought leaders. The closest solutions are RSS-based feed aggregators, but they have significant limitations:

- **No solution combines both platforms** in one unified interface
- **No dedicated AI thought leader curation** exists
- **Push notifications for new videos** are not a core feature of most aggregators

This represents a clear **market opportunity**.

---

## 2. Existing Solutions Analysis

### 2.1 RSS Feed Readers (Closest Category)

| Product | Platform | YouTube | Bilibili | Notifications | AI Focus |
|---------|----------|---------|----------|---------------|----------|
| **Feedly** | Web, iOS, Android | ✅ Via RSS | ❌ | ❌ (email only, paid) | ❌ |
| **Inoreader** | Web, iOS, Android | ✅ (best integration) | ❌ | ❌ | ❌ |
| **NewsBlur** | Web, iOS, Android | ✅ Via RSS | ❌ | ❌ | ❌ |
| **Feedbro** | Browser Extension | ✅ Via RSS | ❌ | ❌ | ❌ |
| **Reeder** | iOS/macOS | ✅ Via RSS | ❌ | ❌ | ❌ |
| **NetNewsWire** | iOS/macOS | ✅ Via RSS | ❌ | ❌ | ❌ |
| **Miniflux** | Self-hosted | ✅ Via RSS | ❌ | ✅ (via plugins) | ❌ |
| **FreshRSS** | Self-hosted | ✅ Via RSS | ❌ | ✅ (via extensions) | ❌ |

**Key Finding:** RSS readers can aggregate YouTube via channel RSS feeds, but:
- Require manual RSS feed setup per channel
- No native Bilibili support (requires RSSHub or similar workarounds)
- No push notifications for new videos (most require paid plans or email)
- No AI thought leader curation or categorization

### 2.2 RSSHub & Custom Feed Solutions

| Product | Type | YouTube | Bilibili | Notes |
|---------|------|---------|----------|-------|
| **RSSHub** | Open Source | ✅ (via routes) | ✅ (robust) | Best for generating custom feeds, requires self-hosting |
| **RSS Bridge** | Open Source | ✅ | ✅ | Simpler than RSSHub |
| **OpenRSS.org** | Service | ✅ | ❌ | Free, no Bilibili support |

**Key Finding:** RSSHub is the technical backbone for many custom feed solutions. It supports Bilibili but requires:
- Self-hosting or using public instances
- Technical knowledge to set up routes
- No notifications or app experience

### 2.3 Video Downloaders (Partial Solution)

| Product | YouTube | Bilibili | Notifications | Notes |
|---------|---------|----------|---------------|-------|
| **4K Video Downloader** | ✅ | ✅ | ❌ | Desktop app, download only |
| **JDownloader** | ✅ | ✅ | ❌ | Requires plugins |
| **YTDL** | ✅ | ❌ | ❌ | YouTube only |

### 2.4 AI Content Curators (Newsletter Style)

| Product | Type | YouTube | Bilibili | Notes |
|---------|------|---------|----------|-------|
| **Import AI** | Newsletter | ❌ | ❌ | Text-only AI news summary |
| **The Neuron** | Newsletter | ❌ | ❌ | AI news, no video |
| **Morning Brew** | Newsletter | ❌ | ❌ | Tech news, no video |
| **DeepLearning.AI** | YouTube | N/A | N/A | Single creator, no aggregation |

**Key Finding:** Existing AI "curation" is text-based newsletters, not video aggregation.

### 2.5 Chinese Market Tools

| Product | Type | Notes |
|---------|------|-------|
| **BiUdder** | Bilibili tool | Bilibili only, Chinese-focused |
| **Bilibili RSS** | Various | Fragmented, no YouTube integration |
| **WeChat video accounts** | WeChat | China-only, no YouTube |

---

## 3. Gap Analysis

### What's Missing:

1. **Unified YouTube + Bilibili aggregation** - No app combines both
2. **AI thought leader curation** - No pre-curated list of AI creators
3. **Push notifications for new videos** - Not a core feature anywhere
4. **Cross-platform discovery** - Can't find same creator on both platforms
5. **Bilingual interface** - No English/Chinese hybrid for this niche
6. **Content filtering** - No filtering by topic, length, or recency

### User Pain Points:

- Manually checking multiple YouTube channels
- No way to follow Bilibili creators from the same creators
- No notifications when new AI talks/podcasts drop
- Language barrier between English (YouTube) and Chinese (Bilibili) content

---

## 4. Technical Approaches to Consider

### Option A: Official APIs
- **YouTube Data API v3** - Free tier available, requires OAuth for some features
- **Bilibili API** - More limited, requires registration

### Option B: RSS + RSSHub
- Use RSSHub to generate feeds for both platforms
- Combine with RSS reader app
- Requires hosting

### Option C: Web Scraping
- More flexible but potentially against ToS
- Requires ongoing maintenance

### Option D: Hybrid
- Official APIs for core functionality
- RSSHub for additional sources
- Custom notification system

---

## 5. Recommendations

### For MVP:
1. **Start with YouTube only** - Official API is reliable
2. **Curate 20-50 top AI thought leader channels** - Lex Fridman, Andrej Karpathy, Sam Altman, etc.
3. **Build simple notification system** - Push via Telegram/Discord/email
4. **Add Bilibili later** - Via RSSHub or API

### Differentiation:
- Focus on **AI thought leaders specifically** (not general video aggregator)
- **Bilingual support** (English + Chinese)
- **Push notifications** as core feature
- **Clean, modern UI** focused on content discovery

---

## 6. Potential Competitors to Monitor

- Feedly (if they add video notifications)
- Inoreader (if they add Bilibili)
- NewTube / Libretube (YouTube clients, no Bilibili)
- Any new AI video aggregator startups

---

## 7. Next Steps

If you want to proceed, I can help with:

1. **Technical architecture** - Stack selection, API integration plan
2. **Channel list** - Curated list of top AI thought leaders on both platforms
3. **MVP feature list** - Minimum viable product scope
4. **Competitive analysis deeper dive** - Any specific competitor you'd like me to research further

---

*Document generated based on web research as of 2026-02-22*
