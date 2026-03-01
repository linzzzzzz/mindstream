# MindStream Static Site - Option 2 (Non-Destructive)

## Goal

Create a fully static version of MindStream **without modifying any existing files**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Workspace                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  mindstream/                              mindstream-static/│
│  ├── src/ (original app)                   ├── src/ (new)  │
│  │   ├── app/                               │   ├── app/    │
│  │   ├── lib/                               │   └── ...     │
│  │   └── mindstream.db                      ├── public/    │
│  │                                           │   └── videos.json
│  │                                           └── package.json
│  │                                                            │
│  └── (unchanged!)                            (brand new)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                     Static site output
```

---

## What to Create

### 1. `mindstream-static/`

New folder with its own `package.json` and Next.js setup.

```
mindstream-static/
├── src/
│   ├── app/
│   │   ├── page.tsx      # Simplified, reads from JSON
│   │   └── layout.tsx    # Copy from original
│   └── components/       # Copy relevant components
├── public/
│   ├── videos.json       # (generated - copy from src/public)
│   └── images/           # Copy any static assets
├── scripts/
│   └── export-json.ts    # Export from main DB to JSON
├── package.json
├── next.config.ts
└── tsconfig.json
```

### 2. Workflow

```bash
# Option A: Full build (export + build)
cd mindstream-static
./scripts/build.sh

# Option B: Step by step
cd mindstream-static
npx tsx scripts/export-json.ts   # Export DB → JSON
npm run build                      # Build static site

# Output in: mindstream-static/out/
```

### 3. Serve Locally

```bash
cd mindstream-static
npx serve out/
# Or use any static server
```

### 4. Deploy

Deploy the `out/` folder to:
- GitHub Pages
- Cloudflare Pages
- Netlify
- Vercel (static output)
- Or host locally on your Mac

---

## Files Created

| File | Status |
|------|--------|
| `mindstream-static/package.json` | ✅ Created |
| `mindstream-static/tsconfig.json` | ✅ Created |
| `mindstream-static/next.config.mjs` | ✅ Created |
| `mindstream-static/scripts/export-json.ts` | ✅ Created |
| `mindstream-static/scripts/build.sh` | ✅ Created |
| `mindstream-static/src/app/page.tsx` | ✅ Created |
| `mindstream-static/src/app/layout.tsx` | ✅ Created |
| `mindstream-static/src/app/globals.css` | ✅ Created |
| `mindstream-static/public/videos.json` | ✅ Generated |

---

## Scraping Button

**Option A:** Keep using the original app
- Scrape via original app's button
- Then run export + build

**Option B:** Separate scraping script
- Run `npx tsx scripts/scrape.ts` 
- Updates the shared DB
- Then export + build

**Recommendation:** Option A (least change)

---

## Effort Estimate

| Task | Time |
|------|------|
| Set up new Next.js project | 15 min |
| Export script | 30 min |
| Copy & adapt frontend | 30 min |
| Build config | 10 min |
| Test | 15 min |

**Total: ~1.5 hours**

---

## What Stays the Same

- Original `mindstream/` app works exactly as before
- Database stays where it is
- No risk of breaking existing functionality

---

## What Changes

- New `mindstream-static/` folder for the static version
- Workflow: scrape → export → build → deploy
