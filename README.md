# MindStream

AI Thought Leader Content Aggregator. Collects YouTube interviews, podcasts, and speeches from AI thought leaders, extracts key intellectual insights, and presents them as browsable insight cards with short video clips.

## Architecture

```
YouTube videos
      ↓
 process_insights.py (Python pipeline)
      ↓
mindstream.db (SQLite)
  ├── thought_leaders
  ├── content_items      ← scraped video metadata
  ├── transcripts        ← path to downloaded .srt files
  └── insights           ← extracted claim + quote + timestamps + topic
      ↓
Next.js frontend
```

The pipeline depends on [openclip](../openclip) for downloading, transcript processing, speaker diarization, and clip generation.

---

## Setup

### 1. Prerequisites

- Node.js (for the frontend)
- [openclip](../openclip) cloned as a sibling directory, with its dependencies installed (`uv sync` inside openclip)
- `QWEN_API_KEY` environment variable set (for insight extraction)

### 2. Install frontend dependencies

```bash
npm install
```

### 3. Speaker reference audio

To enable speaker identification in transcripts, add reference audio files (10–30s WAV clips) for each thought leader:

```
data/speaker_references/
├── Sam Altman.wav
├── Andrej Karpathy.wav
├── Dario Amodei.wav
└── Demis Hassabis.wav
```

Filenames must match the `name` field in the `thought_leaders` table exactly. Files are optional — if missing, the pipeline falls back to generic `SPEAKER_00` / `SPEAKER_01` labels.

---

## Running the insight pipeline

The pipeline processes pending videos end-to-end: download → transcript → speaker diarization → insight extraction → clip generation.

**Run from the openclip directory** so its Python dependencies are available:

```bash
cd /path/to/openclip

# Process up to 5 pending videos (default)
uv run python /path/to/mindstream/scripts/process_insights.py

# Process a specific number of videos
uv run python /path/to/mindstream/scripts/process_insights.py --limit 10

# Process a specific video by ID (regardless of status)
uv run python /path/to/mindstream/scripts/process_insights.py --video-id qH7thwrCluM

# Skip re-downloading if the video is already on disk
uv run python /path/to/mindstream/scripts/process_insights.py --skip-download --video-id qH7thwrCluM
```

If openclip is not in the default sibling location, set the `OPENCLIP_DIR` environment variable:

```bash
OPENCLIP_DIR=/custom/path/to/openclip uv run python .../process_insights.py
```

### Pipeline steps

| Step | Status written to DB | What happens |
|------|----------------------|--------------|
| 1 | `downloading` | Downloads video + YouTube captions via yt-dlp (skipped if `--skip-download` and video exists) |
| 2 | — | Speaker diarization via WhisperX (only if WhisperX installed AND reference audio exists; fails hard on error) |
| 3 | `transcript_fetched` | Saves SRT file path to `transcripts` table |
| 4 | `extracting_insights` → `insights_extracted` | Sends transcript to LLM, extracts insight cards into `insights` table |
| 5 | `clips_generated` | Generates MP4 clips for each insight |

### Processing status values

| Status | Meaning |
|--------|---------|
| `pending` | Not yet processed |
| `downloading` | Download in progress |
| `transcript_fetched` | Transcript available |
| `extracting_insights` | LLM analysis in progress |
| `insights_extracted` | Insights saved to DB, clips not yet generated |
| `clips_generated` | Clips on disk, ready for Bilibili upload |
| `published` | `clip_url` populated, visible on site |
| `failed` | Pipeline error — check logs |

### Output files

VideoOrchestrator organises output by video title directly under `processed_videos/`:

```
data/processed_videos/{safe_video_title}/
├── downloads/
│   ├── {title}.mp4               ← full video
│   └── {title}.srt               ← transcript
├── splits/
│   ├── {title}_part01.mp4        ← video part (single video → always part01)
│   ├── {title}_part01.srt        ← transcript part (with speaker labels if diarization ran)
│   ├── insights_part01.json      ← per-part raw insights
│   ├── all_insights.json         ← merged insights (mindstream format)
│   └── top_engaging_moments.json ← ClipGenerator-compatible format
└── clips/
    ├── rank_01_{claim}.mp4       ← insight clip
    ├── rank_02_{claim}.mp4
    └── ...
```

---

## Running the frontend

```bash
npm run dev     # development
npm run build   # production build
npm run start   # production server
```

---

## Database

SQLite database at `mindstream.db`. Key tables:

- **`thought_leaders`** — Sam Altman, Andrej Karpathy, etc.
- **`content_items`** — scraped video metadata + `processing_status`
- **`transcripts`** — path to SRT file per video
- **`insights`** — extracted insight cards: `claim`, `quote`, `start_seconds`, `end_seconds`, `topic`, `clip_url`
- **`topics`** — topic taxonomy

To inspect:

```bash
sqlite3 mindstream.db
sqlite> SELECT title, processing_status FROM content_items ORDER BY published_at DESC LIMIT 10;
sqlite> SELECT claim, topic FROM insights WHERE content_item_id = 'VIDEO_ID';
```

---

## Uploading clips to Bilibili

After clips are generated (`clips_generated` status), upload each clip to Bilibili and store the embed URL back in the database:

```sql
UPDATE insights SET clip_url = 'https://player.bilibili.com/player.html?bvid=BV...'
WHERE id = 'INSIGHT_ID';

UPDATE content_items SET processing_status = 'published'
WHERE id = 'VIDEO_ID';
```

See [docs/BILIBILI_UPLOAD_RESEARCH.md](docs/BILIBILI_UPLOAD_RESEARCH.md) for upload research and notes.