#!/usr/bin/env python3
"""
Upload mindstream highlight clips to Bilibili.

Run from the mindstream directory:
  cd /path/to/mindstream
  uv run python scripts/upload_to_bilibili.py

Options:
  --video-id ID   Process a specific video (default: all clips_generated)
  --limit N       Max videos to process (default: 5)
  --tid N         Bilibili category ID (default: 208 = 科学科普)
  --cred FILE     Path to credentials JSON (default: .bilibili_creds.json)
  --dry-run       Print upload plan without calling the API

Credentials:
  Either provide a .bilibili_creds.json file (copy from .bilibili_creds.json.example)
  or set env vars: BILIBILI_SESSDATA, BILIBILI_BILI_JCT, BILIBILI_BUVID3
"""

import sys
import os
import re
import json
import zlib
import struct
import asyncio
import logging
import argparse
import tempfile
import sqlite3
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
MINDSTREAM_DIR = Path(__file__).parent.parent
DB_PATH        = MINDSTREAM_DIR / "mindstream.db"
OUTPUT_DIR     = MINDSTREAM_DIR / "data" / "processed_videos"
DEFAULT_CREDS  = MINDSTREAM_DIR / ".bilibili_creds.json"

# ---------------------------------------------------------------------------
# Bootstrap bilibili-api: prefer local clone, fall back to installed package
# ---------------------------------------------------------------------------
BILIBILI_API_DIR = Path(os.environ.get(
    "BILIBILI_API_DIR",
    str(Path(__file__).parent.parent.parent / "bilibili-api"),
))
if BILIBILI_API_DIR.exists():
    sys.path.insert(0, str(BILIBILI_API_DIR))

try:
    from bilibili_api import Credential
    from bilibili_api.utils.picture import Picture
    from bilibili_api.video_uploader import (
        VideoUploader,
        VideoUploaderPage,
        VideoMeta,
        Lines,
    )
except ImportError as e:
    print(
        f"bilibili-api not found: {e}\n"
        f"Install it:  uv add bilibili-api-python\n"
        f"Or clone it: git clone https://github.com/nemo2011/bilibili-api.git "
        f"alongside this repo and set BILIBILI_API_DIR."
    )
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(levelname)-8s %(message)s"
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Credential helpers
# ---------------------------------------------------------------------------

def load_credential(cred_path: Path) -> Credential:
    sessdata = os.environ.get("BILIBILI_SESSDATA")
    bili_jct = os.environ.get("BILIBILI_BILI_JCT")
    buvid3   = os.environ.get("BILIBILI_BUVID3")
    buvid4   = os.environ.get("BILIBILI_BUVID4")

    if not (sessdata and bili_jct):
        if not cred_path.exists():
            raise FileNotFoundError(
                f"No credentials found.\n"
                f"  Option A: Create {cred_path} "
                f"(copy from .bilibili_creds.json.example and fill in values)\n"
                f"  Option B: Set env vars BILIBILI_SESSDATA + BILIBILI_BILI_JCT\n\n"
                f"How to get cookies: log into bilibili.com → F12 → "
                f"Application → Cookies → bilibili.com"
            )
        data     = json.loads(cred_path.read_text())
        sessdata = data["sessdata"]
        bili_jct = data["bili_jct"]
        buvid3   = data.get("buvid3", "")
        buvid4   = data.get("buvid4", "")

    return Credential(
        sessdata=sessdata,
        bili_jct=bili_jct,
        buvid3=buvid3 or "",
        buvid4=buvid4 or "",
    )


# ---------------------------------------------------------------------------
# DB helpers (same pattern as process_insights.py)
# ---------------------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_clips_generated_videos(conn: sqlite3.Connection, limit: int) -> list:
    return conn.execute(
        """
        SELECT ci.id, ci.title, ci.url, ci.thumbnail_url, ci.topics,
               ci.published_at, tl.name AS leader_name
        FROM content_items ci
        JOIN thought_leaders tl ON ci.thought_leader_id = tl.id
        WHERE ci.processing_status = 'clips_generated'
          AND ci.platform = 'youtube'
        ORDER BY ci.published_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


def get_video_by_id(conn: sqlite3.Connection, video_id: str) -> sqlite3.Row | None:
    return conn.execute(
        """
        SELECT ci.id, ci.title, ci.url, ci.thumbnail_url, ci.topics,
               ci.published_at, tl.name AS leader_name
        FROM content_items ci
        JOIN thought_leaders tl ON ci.thought_leader_id = tl.id
        WHERE ci.id = ?
        """,
        (video_id,),
    ).fetchone()


def get_insights_for_video(conn: sqlite3.Connection, video_id: str) -> list:
    return conn.execute(
        """
        SELECT id, order_index, claim, quote, topic, clip_url, clip_filename
        FROM insights
        WHERE content_item_id = ?
        ORDER BY order_index
        """,
        (video_id,),
    ).fetchall()


def update_clip_url(conn: sqlite3.Connection, insight_id: str, clip_url: str) -> None:
    conn.execute(
        "UPDATE insights SET clip_url = ?, updated_at = ? WHERE id = ?",
        (clip_url, datetime.now().isoformat(), insight_id),
    )
    conn.commit()


def update_status(conn: sqlite3.Connection, video_id: str, status: str) -> None:
    conn.execute(
        "UPDATE content_items SET processing_status = ?, updated_at = ? WHERE id = ?",
        (status, datetime.now().isoformat(), video_id),
    )
    conn.commit()


def migrate_db(conn: sqlite3.Connection) -> None:
    """Add concat columns if they don't exist yet."""
    for sql in [
        "ALTER TABLE content_items ADD COLUMN concat_clip_url TEXT",
        "ALTER TABLE insights ADD COLUMN concat_start_seconds INTEGER",
    ]:
        try:
            conn.execute(sql)
            conn.commit()
        except sqlite3.OperationalError:
            pass  # column already exists


def update_concat_result(
    conn: sqlite3.Connection,
    video_id: str,
    concat_clip_url: str,
    start_map: dict,  # {insight_id: concat_start_seconds}
) -> None:
    """Write concat_clip_url to content_items and concat_start_seconds to each insight."""
    now = datetime.now().isoformat()
    conn.execute(
        "UPDATE content_items SET concat_clip_url = ?, updated_at = ? WHERE id = ?",
        (concat_clip_url, now, video_id),
    )
    for insight_id, start_sec in start_map.items():
        conn.execute(
            "UPDATE insights SET concat_start_seconds = ?, updated_at = ? WHERE id = ?",
            (start_sec, now, insight_id),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# Upload helpers
# ---------------------------------------------------------------------------

def _blank_cover_picture() -> Picture:
    """Return a 1×1 white PNG Picture (no external deps) for use when no thumbnail."""
    def chunk(name: bytes, data: bytes) -> bytes:
        c = struct.pack(">I", len(data)) + name + data
        return c + struct.pack(">I", zlib.crc32(c[4:]) & 0xFFFFFFFF)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff"))
        + chunk(b"IEND", b"")
    )
    return Picture.from_content(png, "png")


def find_clip_file(clips_dir: Path, order_index: int, clip_filename: str | None = None) -> Path | None:
    """Return the post-processed MP4 for this insight.

    Prefers the explicit clip_filename stored in the DB; falls back to
    globbing rank_NN_*.mp4 (for insights processed before this column existed).
    """
    if clip_filename:
        explicit = clips_dir / clip_filename
        if explicit.exists():
            return explicit
        # File missing — fall through to glob so we still find something
    prefix = f"rank_{order_index + 1:02d}_"
    matches = sorted(clips_dir.glob(f"{prefix}*.mp4"))
    return matches[0] if matches else None


def download_thumbnail(url: str) -> str | None:
    """Download YouTube thumbnail to a temp file. Returns path or None."""
    if not url:
        return None
    try:
        suffix = ".jpg" if ".jpg" in url.lower() else ".png"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            tmp_path = f.name
        urllib.request.urlretrieve(url, tmp_path)
        return tmp_path
    except Exception as exc:
        logger.warning(f"Could not download thumbnail: {exc}")
        return None


def build_tags(insight: sqlite3.Row, video_row: sqlite3.Row) -> list[str]:
    tags: list[str] = []

    if insight["topic"]:
        tags.append(insight["topic"][:20])

    # Add last name of the thought leader
    leader_last = video_row["leader_name"].split()[-1]
    tags.append(leader_last)

    # Add video-level topics (stored as JSON array)
    try:
        video_topics = json.loads(video_row["topics"] or "[]")
        tags.extend(str(t)[:20] for t in video_topics[:5])
    except Exception:
        pass

    tags.append("AI")

    # Deduplicate while preserving order, max 10
    seen: set[str] = set()
    deduped: list[str] = []
    for t in tags:
        if t and t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped[:10]


def build_meta(
    insight: sqlite3.Row,
    video_row: sqlite3.Row,
    tid: int,
    cover_path: str | None = None,
) -> VideoMeta:
    title_raw = f"{video_row['leader_name']}: {insight['claim']}"
    if len(title_raw) <= 80:
        title = title_raw
    else:
        # Truncate at last word boundary before the limit
        cut = title_raw[:79].rsplit(" ", 1)[0]
        title = cut + "…"

    quote = insight["quote"] or ""
    desc = f"{quote}\n\n原视频: {video_row['url']}"[:2000]

    tags = build_tags(insight, video_row)

    cover_pic = (
        Picture.from_file(cover_path) if cover_path else _blank_cover_picture()
    )

    return VideoMeta(
        tid=tid,
        title=title,
        desc=desc,
        tags=tags,
        cover=cover_pic,
        original=False,
        source=video_row["url"],
    )


def get_video_duration(mp4_path: Path) -> float:
    """Return video duration in seconds via ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(mp4_path),
        ],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def _get_video_info(mp4_path: Path) -> dict:
    """Return width, height, fps string (e.g. '30/1') of a video."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate",
            "-of", "json", str(mp4_path),
        ],
        capture_output=True, text=True, check=True,
    )
    s = json.loads(result.stdout)["streams"][0]
    return {"width": s["width"], "height": s["height"], "fps": s["r_frame_rate"]}


def _escape_drawtext(text: str) -> str:
    """Escape a string for use as an ffmpeg drawtext filter value."""
    return (
        text.replace("\\", "\\\\")
            .replace("'", "\u2019")   # replace straight quote with curly to avoid shell issues
            .replace(":", "\\:")
            .replace(",", "\\,")
            .replace("[", "\\[")
            .replace("]", "\\]")
    )


def _make_transition_clip(
    output_path: Path,
    width: int,
    height: int,
    fps: str,
    duration: float,
    clip_num: int,    # 1-based index of the NEXT clip
    total_clips: int,
    next_claim: str,
) -> None:
    """Generate a black title card to show between two clips."""
    label = _escape_drawtext(f"Insight {clip_num} / {total_clips}")
    # Split claim into two lines (~52 chars each) so it fits comfortably
    line1 = _escape_drawtext(next_claim[:52])
    line2_raw = next_claim[52:104] + ("…" if len(next_claim) > 104 else "")
    line2 = _escape_drawtext(line2_raw) if len(next_claim) > 52 else ""

    fade_dur = min(0.5, duration / 4)  # fade in + fade out each up to 0.5s
    fade_out_start = duration - fade_dur

    # Claim is the hero; label is a small caption above it
    vf = (
        f"drawtext=text='{label}'"
        f":fontsize=50:fontcolor=0x888888"
        f":x=(w-text_w)/2:y=(h-text_h)/2-90,"
        f"drawtext=text='{line1}'"
        f":fontsize=50:fontcolor=white"
        f":x=(w-text_w)/2:y=(h-text_h)/2-20"
    )
    if line2:
        vf += (
            f",drawtext=text='{line2}'"
            f":fontsize=50:fontcolor=white"
            f":x=(w-text_w)/2:y=(h-text_h)/2+40"
        )
    vf += (
        f",fade=t=in:st=0:d={fade_dur}"
        f",fade=t=out:st={fade_out_start}:d={fade_dur}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=black:size={width}x{height}:rate={fps}",
        "-f", "lavfi", "-i", "aevalsrc=0:c=stereo:s=44100",
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def concat_clips_with_transitions(
    clips: list[Path],
    output_path: Path,
    transition_duration: float = 3.0,
    claims: list[str] | None = None,
) -> list[int]:
    """
    Concatenate MP4 clips with a titled black card between each pair.

    Returns concat_start_seconds (int) for each clip — the position within
    the concatenated video where that clip begins.
    """
    import shutil

    n = len(clips)
    if n == 0:
        return []
    if n == 1:
        shutil.copy2(str(clips[0]), str(output_path))
        return [0]

    durations = [get_video_duration(p) for p in clips]
    info = _get_video_info(clips[0])

    # Compute start seconds
    starts: list[int] = []
    t = 0.0
    for i, dur in enumerate(durations):
        starts.append(round(t))
        t += dur + (transition_duration if i < n - 1 else 0)

    tmpdir = output_path.parent / "_concat_tmp"
    tmpdir.mkdir(parents=True, exist_ok=True)
    try:
        # Interleave: clip0, trans0→1, clip1, trans1→2, ..., clip(n-1)
        items: list[Path] = []
        for i, clip in enumerate(clips):
            items.append(clip)
            if i < n - 1:
                trans_path = tmpdir / f"trans_{i}_{i + 1}.mp4"
                next_claim = claims[i + 1] if (claims and i + 1 < len(claims)) else ""
                logger.info(f"    Generating transition card {i + 1}→{i + 2} ...")
                _make_transition_clip(
                    trans_path,
                    width=info["width"],
                    height=info["height"],
                    fps=info["fps"],
                    duration=transition_duration,
                    clip_num=i + 2,
                    total_clips=n,
                    next_claim=next_claim,
                )
                items.append(trans_path)

        # Write concat list
        list_path = tmpdir / "list.txt"
        list_path.write_text(
            "\n".join(f"file '{p}'" for p in items) + "\n"
        )

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac",
            "-movflags", "+faststart",
            str(output_path),
        ]
        logger.info(f"  Running ffmpeg concat ({n} clips → {output_path.name}) ...")
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"  Concat complete: {output_path}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return starts


def build_concat_meta(
    video_row: sqlite3.Row,
    insights: list,
    tid: int,
    cover_path: str | None = None,
) -> "VideoMeta":
    """Build VideoMeta for a concatenated highlights video."""
    leader = video_row["leader_name"]
    pub = datetime.fromisoformat(video_row["published_at"][:10])
    month_year = pub.strftime("%b %Y")  # e.g. "Feb 2026"
    raw_title = f"{leader} {month_year} Podcast: Key Insights"
    title = raw_title if len(raw_title) <= 80 else raw_title[:79] + "…"

    # Description: numbered list of claims + source
    claims = "\n".join(
        f"{i + 1}. {ins['claim']}"
        for i, ins in enumerate(insights)
        if ins["claim"]
    )
    desc = f"{claims}\n\n原视频: {video_row['url']}"[:2000]

    # Tags: leader last name + video topics + "AI" + "精华"
    tags: list[str] = []
    tags.append(leader.split()[-1])
    try:
        video_topics = json.loads(video_row["topics"] or "[]")
        tags.extend(str(t)[:20] for t in video_topics[:5])
    except Exception:
        pass
    tags += ["AI", "精华"]
    seen: set[str] = set()
    deduped: list[str] = []
    for t in tags:
        if t and t not in seen:
            seen.add(t)
            deduped.append(t)

    cover_pic = (
        Picture.from_file(cover_path) if cover_path else _blank_cover_picture()
    )

    return VideoMeta(
        tid=tid,
        title=title,
        desc=desc,
        tags=deduped[:10],
        cover=cover_pic,
        original=False,
        source=video_row["url"],
    )


async def upload_clip(
    mp4_path: Path,
    insight: sqlite3.Row,
    video_row: sqlite3.Row,
    cred: Credential,
    cover_path: str | None,
    tid: int,
) -> str | None:
    """Upload one clip. Returns bvid on success, None on failure."""
    meta = build_meta(insight, video_row, tid, cover_path)
    page = VideoUploaderPage(path=str(mp4_path), title=meta.title)

    uploader = VideoUploader(
        pages=[page],
        meta=meta,
        credential=cred,
        line=Lines.BDA2,
    )

    result_bvid: str | None = None

    @uploader.on("COMPLETE")
    async def on_complete(data: dict) -> None:
        nonlocal result_bvid
        result_bvid = data.get("bvid")
        logger.info(f"    ✓ Uploaded: {result_bvid}")

    @uploader.on("FAILED")
    async def on_fail(data: dict) -> None:
        logger.error(f"    ✗ Upload failed: {data}")

    await uploader.start()
    return result_bvid


async def upload_video(
    mp4_path: Path,
    meta: "VideoMeta",
    cred: Credential,
) -> str | None:
    """Upload a single MP4 with pre-built meta. Returns bvid on success, None on failure."""
    page = VideoUploaderPage(path=str(mp4_path), title=meta.title)
    uploader = VideoUploader(
        pages=[page],
        meta=meta,
        credential=cred,
        line=Lines.BDA2,
    )

    result_bvid: str | None = None

    @uploader.on("COMPLETE")
    async def on_complete(data: dict) -> None:
        nonlocal result_bvid
        result_bvid = data.get("bvid")
        logger.info(f"    ✓ Uploaded: {result_bvid}")

    @uploader.on("FAILED")
    async def on_fail(data: dict) -> None:
        logger.error(f"    ✗ Upload failed: {data}")

    await uploader.start()
    return result_bvid


# ---------------------------------------------------------------------------
# Per-video processing
# ---------------------------------------------------------------------------

async def process_video(
    video_row: sqlite3.Row,
    conn: sqlite3.Connection,
    cred: "Credential | None",
    tid: int,
    dry_run: bool,
    delay: int = 0,
    max_clips: int = 0,
    concat: bool = False,
    transition_duration: float = 1.0,
    no_upload: bool = False,
) -> None:
    video_id = video_row["id"]
    title    = video_row["title"]

    # Reconstruct the safe directory name (matches VideoOrchestrator's logic)
    safe_title = re.sub(r'[^\w\s-]', '', title)
    safe_title = re.sub(r'[\s\-]+', '_', safe_title)
    safe_title = re.sub(r'_+', '_', safe_title).strip('_')
    clips_dir = OUTPUT_DIR / safe_title / "clips_post_processed"

    if not clips_dir.exists():
        logger.warning(f"clips_post_processed not found for '{title}' (looked in {clips_dir}), skipping")
        return

    insights = get_insights_for_video(conn, video_id)
    if not insights:
        logger.warning(f"No insights found for video {video_id}")
        return

    cover_path = download_thumbnail(video_row["thumbnail_url"])

    try:
        if concat:
            await _process_concat(
                video_row, conn, cred, tid, dry_run,
                insights, clips_dir, cover_path,
                max_clips=max_clips, transition_duration=transition_duration,
                no_upload=no_upload,
            )
        else:
            await _process_per_clip(
                video_row, conn, cred, tid, dry_run,
                insights, clips_dir, cover_path,
                delay=delay, max_clips=max_clips,
            )
    finally:
        if cover_path:
            Path(cover_path).unlink(missing_ok=True)


async def _process_per_clip(
    video_row: sqlite3.Row,
    conn: sqlite3.Connection,
    cred: "Credential | None",
    tid: int,
    dry_run: bool,
    insights: list,
    clips_dir: Path,
    cover_path: str | None,
    delay: int = 0,
    max_clips: int = 0,
) -> None:
    video_id = video_row["id"]
    title = video_row["title"]
    uploaded = skipped = failed = 0
    uploaded_files: set[str] = set()

    for insight in insights:
        rank = insight["order_index"] + 1

        if insight["clip_url"]:
            logger.info(f"  rank_{rank:02d}: already uploaded, skipping")
            mp4_done = find_clip_file(clips_dir, insight["order_index"], insight["clip_filename"])
            if mp4_done:
                uploaded_files.add(mp4_done.name)
            skipped += 1
            continue

        mp4 = find_clip_file(clips_dir, insight["order_index"], insight["clip_filename"])
        if not mp4:
            logger.warning(f"  rank_{rank:02d}: MP4 not found in {clips_dir}, skipping")
            failed += 1
            continue

        if mp4.name in uploaded_files:
            skipped += 1
            continue

        _ct = f"{video_row['leader_name']}: {insight['claim']}"
        clip_title = _ct if len(_ct) <= 80 else _ct[:79].rsplit(" ", 1)[0] + "…"

        if dry_run:
            logger.info(f"  [DRY RUN] rank_{rank:02d}: {mp4.name}")
            logger.info(f"            title: {clip_title}")
            logger.info(f"            tags:  {build_tags(insight, video_row)}")
            uploaded_files.add(mp4.name)
            uploaded += 1
            if max_clips and uploaded >= max_clips:
                logger.info(f"  Reached --max-clips {max_clips}, stopping.")
                break
            continue

        logger.info(f"  Uploading rank_{rank:02d}: {mp4.name}")
        bvid = await upload_clip(mp4, insight, video_row, cred, cover_path, tid)

        if bvid:
            clip_url = f"https://player.bilibili.com/player.html?bvid={bvid}"
            update_clip_url(conn, insight["id"], clip_url)
            uploaded_files.add(mp4.name)
            uploaded += 1
            if max_clips and uploaded >= max_clips:
                logger.info(f"  Reached --max-clips {max_clips}, stopping.")
                break
            if delay:
                logger.info(f"  Waiting {delay}s before next upload...")
                await asyncio.sleep(delay)
        else:
            failed += 1

    if uploaded > 0 and not dry_run:
        update_status(conn, video_id, "published")

    logger.info(
        f"  '{title[:60]}': "
        f"{uploaded} uploaded, {skipped} skipped, {failed} failed"
    )


async def _process_concat(
    video_row: sqlite3.Row,
    conn: sqlite3.Connection,
    cred: "Credential | None",
    tid: int,
    dry_run: bool,
    insights: list,
    clips_dir: Path,
    cover_path: str | None,
    max_clips: int = 0,
    transition_duration: float = 1.0,
    no_upload: bool = False,
) -> None:
    """Concatenate all clips for a video and upload as one."""
    video_id = video_row["id"]
    title = video_row["title"]

    # Idempotency: skip if concat already uploaded
    row = conn.execute(
        "SELECT concat_clip_url FROM content_items WHERE id = ?", (video_id,)
    ).fetchone()
    if row and row["concat_clip_url"]:
        logger.info(f"  Concat already uploaded: {row['concat_clip_url']}, skipping")
        return

    # Collect ordered clips
    ordered_clips: list[tuple[sqlite3.Row, Path]] = []
    seen_files: set[str] = set()
    for insight in insights:
        mp4 = find_clip_file(clips_dir, insight["order_index"], insight["clip_filename"])
        if not mp4:
            logger.warning(f"  rank_{insight['order_index'] + 1:02d}: MP4 not found, skipping from concat")
            continue
        if mp4.name in seen_files:
            continue  # deduplicate
        seen_files.add(mp4.name)
        ordered_clips.append((insight, mp4))
        if max_clips and len(ordered_clips) >= max_clips:
            break

    if not ordered_clips:
        logger.warning("  No clip files found — nothing to concatenate")
        return

    clip_paths = [mp4 for _, mp4 in ordered_clips]
    clip_insights = [ins for ins, _ in ordered_clips]

    if dry_run:
        logger.info(f"  [DRY RUN] Would concatenate {len(clip_paths)} clips:")
        cumulative = 0.0
        for i, (ins, mp4) in enumerate(ordered_clips):
            try:
                dur = get_video_duration(mp4)
            except Exception:
                dur = 0.0
            start_s = round(cumulative)
            logger.info(
                f"    [{i + 1}] rank_{ins['order_index'] + 1:02d} @ {start_s}s "
                f"(dur {dur:.1f}s): {mp4.name}"
            )
            logger.info(f"         claim: {ins['claim'][:80]}")
            cumulative += dur + (transition_duration if i < len(ordered_clips) - 1 else 0)
        total_dur = cumulative
        meta = build_concat_meta(video_row, clip_insights, tid, cover_path)
        logger.info(f"  [DRY RUN] Concat video title: {meta.title}")
        logger.info(f"  [DRY RUN] Concat video tags:  {meta.tags}")
        logger.info(f"  [DRY RUN] Total duration: {total_dur:.1f}s")
        return

    # Concatenate
    upload_dir = clips_dir.parent / "upload"
    upload_dir.mkdir(exist_ok=True)
    concat_output = upload_dir / "concat_highlights.mp4"
    claims = [ins["claim"] for ins in clip_insights]
    try:
        start_seconds = concat_clips_with_transitions(
            clip_paths, concat_output,
            transition_duration=transition_duration,
            claims=claims,
        )
    except subprocess.CalledProcessError as exc:
        logger.error(f"  ffmpeg concat failed: {exc.stderr.decode(errors='replace')}")
        return

    logger.info(f"  Concat start times: {start_seconds}")
    logger.info(f"  Saved to: {concat_output}")

    if no_upload:
        logger.info("  --no-upload set: skipping Bilibili upload")
        return

    # Upload
    meta = build_concat_meta(video_row, clip_insights, tid, cover_path)
    logger.info(f"  Uploading concat video: {concat_output.name}")
    bvid = await upload_video(concat_output, meta, cred)

    if not bvid:
        logger.error("  Concat upload failed")
        return

    concat_clip_url = f"https://player.bilibili.com/player.html?bvid={bvid}"
    start_map = {
        ins["id"]: sec
        for ins, sec in zip(clip_insights, start_seconds)
    }
    update_concat_result(conn, video_id, concat_clip_url, start_map)
    update_status(conn, video_id, "published")

    logger.info(f"  '{title[:60]}': concat uploaded → {bvid}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload mindstream highlight clips to Bilibili"
    )
    parser.add_argument("--video-id", help="Process a specific video ID")
    parser.add_argument(
        "--limit", type=int, default=5,
        help="Max videos to process when no --video-id given (default: 5)"
    )
    parser.add_argument(
        "--tid", type=int, default=208,
        help="Bilibili category ID (default: 208 = 科学科普)"
    )
    parser.add_argument(
        "--cred", default=str(DEFAULT_CREDS),
        help=f"Path to credentials JSON (default: {DEFAULT_CREDS})"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print upload plan without calling the Bilibili API"
    )
    parser.add_argument(
        "--delay", type=int, default=0,
        help="Seconds to wait between clip uploads (default: 0)"
    )
    parser.add_argument(
        "--max-clips", type=int, default=0,
        help="Stop after uploading N clips total; 0 = no limit (default: 0)"
    )
    parser.add_argument(
        "--concat", action="store_true",
        help="Concatenate all clips into one video and upload it once"
    )
    parser.add_argument(
        "--transition", type=float, default=3.0,
        help="Transition card duration in seconds between clips when using --concat (default: 3.0)"
    )
    parser.add_argument(
        "--no-upload", action="store_true",
        help="With --concat: run ffmpeg and save the file but skip the Bilibili upload"
    )
    args = parser.parse_args()

    cred = None if (args.dry_run or args.no_upload) else load_credential(Path(args.cred))
    conn = get_db()
    migrate_db(conn)

    if args.video_id:
        row = get_video_by_id(conn, args.video_id)
        rows = [row] if row else []
        if not rows:
            logger.error(f"Video ID '{args.video_id}' not found in database")
            return
    else:
        rows = get_clips_generated_videos(conn, args.limit)

    if not rows:
        logger.info("No videos with clips_generated status found.")
        return

    logger.info(f"Processing {len(rows)} video(s)...")
    for row in rows:
        logger.info(f"\n{'='*60}")
        logger.info(f"Video: {row['title']}")
        await process_video(
            row, conn, cred, args.tid, args.dry_run,
            delay=args.delay, max_clips=args.max_clips,
            concat=args.concat, transition_duration=args.transition,
            no_upload=args.no_upload,
        )


if __name__ == "__main__":
    asyncio.run(main())
