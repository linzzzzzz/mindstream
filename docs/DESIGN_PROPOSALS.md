# MindStream Design Proposals

## Current Problem
Videos are harder to describe in a few words than news headlines. Users need more context to decide whether to click.

---

## Proposal 1: Card Grid with Thumbnails (Recommended)

**Layout:** Grid of cards (2-3 columns)

```
┌─────────────────────────────────────────────────────────────┐
│  🧠 MindStream                              [🔍 Search]   │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  ┌─────────┐ │  │  ┌─────────┐ │  │  ┌─────────┐ │
│  │ ▶ 12:34 │ │  │  │ ▶ 45:21 │ │  │  │ ▶ 8:15  │ │
│  │ [thumb] │ │  │  │ [thumb] │ │  │  │ [thumb] │ │
│  └─────────┘ │  │  └─────────┘ │  │  └─────────┘ │
│              │  │              │  │              │
│  Sam Altman  │  │ Andrej K.   │  │ Dario A.    │
│  Title here  │  │ Title here  │  │ Title here  │
│  1.2M views  │  │ 850K views  │  │ 2.1M views  │
└──────────────┘  └──────────────┘  └──────────────┘
```

**Each card shows:**
- Thumbnail image with duration badge
- Video title (max 2 lines)
- Thought leader name
- Views + date

**Pros:** Visual-first, easy to scan, YouTube-like

---

## Proposal 2: List with Small Thumbnails

**Layout:** Vertical list

```
┌─────────────────────────────────────────────────────────────┐
│  🧠 MindStream                              [🔍 Search]   │
└─────────────────────────────────────────────────────────────┘

🔥 热门推荐
┌──────────────────────────────────────────────────────────┐
│ ┌────────┐  Sam Altman  •  2.2M views  •  3天前        │
│ │ thumb  │  Video title goes here with some description │
│ └────────┘                                              │
└──────────────────────────────────────────────────────────┘

📺 最新更新
┌──────────────────────────────────────────────────────────┐
│ ┌────────┐  Video title line one                        │
│ │ thumb  │  Video title line two                        │
│ └────────┘  850K views •  5天前              [Sam A.]  │
└──────────────────────────────────────────────────────────┘
│ ┌────────┐  Another video title here                    │
│ │ thumb  │  Description line here                       │
│ └────────┘  1.1M views •  1周前            [Andrej]   │
└──────────────────────────────────────────────────────────┘
```

**Each row shows:**
- Small thumbnail (left)
- Title + description
- Leader name as tag

**Pros:** Compact but visual, shows description

---

## Proposal 3: Tabs by Thought Leader

**Layout:** Tab bar at top

```
┌─────────────────────────────────────────────────────────────┐
│  🧠 MindStream                              [🔍 Search]   │
└─────────────────────────────────────────────────────────────┘

[ All ] [ Sam Altman ] [ Andrej ] [ Dario ] [ Demis ]

┌──────────────────────────────────────────────────────────┐
│ ┌────────┐  Video title here                            │
│ │ thumb  │  Description line here                      │
│ └────────┘  2.2M views •  3天前            ▶ Play    │
└──────────────────────────────────────────────────────────┘
│ ┌────────┐  Another video title                        │
│ │ thumb  │  More description                           │
│ └────────┘  1.5M views •  5天前            ▶ Play    │
└──────────────────────────────────────────────────────────┘
```

**Tabs:** All | Sam Altman | Andrej | Dario | Demis

**Pros:** Focused, less overwhelming

---

## Proposal 4: Timeline/Masonry

**Layout:** Staggered grid

```
┌────────┐   ┌────────────────┐   ┌────────┐
│        │   │                │   │        │
│ thumb  │   │    thumb       │   │ thumb  │
│        │   │                │   │        │
└────────┘   │   Title here   └────────┘
  Title      │   longer than   ───────────
  ─────      │   others here   Author
             └────────────────┘

    ┌────────┐   ┌────────────────┐
    │ thumb  │   │    thumb      │
    │        │   │                │
    └────────┘   └────────────────┘
```

**Pros:** Modern, visually interesting

---

## Proposal 5: Two-Column with Preview

**Layout:** Left list + Right player

```
┌─────────────────────────────┬───────────────────────────┐
│  🧠 MindStream              │                           │
├─────────────────────────────┤    ┌─────────────────┐    │
│  [All] [Leaders ▼]         │    │                 │    │
├─────────────────────────────┤    │   ▶ VIDEO       │    │
│ ┌────────┐ Video title  ▶  │    │   PREVIEW      │    │
│ │ thumb  │ 1.2M • 3d      │    │   PLAYER       │    │
│ └────────┘                 │    │                 │    │
│ ┌────────┐ Video title  ▶  │    │                 │    │
│ │ thumb  │ 850K • 5d       │    └─────────────────┘    │
│ └────────┘                 │                           │
│ ┌────────┐ Video title  ▶  │    Title of selected    │
│ │ thumb  │ 2.1M • 1w      │    Author • 1.2M views   │
│ └────────┘                 │    Description here...    │
└─────────────────────────────┴───────────────────────────┘
```

**Pros:** Browse + watch simultaneously

---

## Comparison Summary

| # | Design | Best For | Complexity |
|---|--------|---------|------------|
| 1 | Card Grid | Visual scanning | Easy |
| 2 | List + Thumb | Context-rich | Easy |
| 3 | Tabs | Leader-focused | Medium |
| 4 | Masonry | Discovery | Medium |
| 5 | Preview | Watch while browsing | Harder |

---

## Recommendation

**Best for MVP:** Proposal 1 or 2

- **Proposal 1** if we want visual appeal
- **Proposal 2** if we want to show more context

Both are simple to implement and work well for video content.

---

## Next Steps

1. Choose a proposal
2. I'll implement it
3. Iterate based on feedback
