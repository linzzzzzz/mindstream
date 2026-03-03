#!/usr/bin/env python3
"""
Mindstream Insight Pipeline

Processes pending YouTube videos through the full pipeline:
  download → transcript → speaker diarization → insight extraction → clip generation

Run from the openclip directory so its dependencies are available:
  cd /path/to/openclip && uv run python /path/to/mindstream/scripts/process_insights.py

Environment variables:
  OPENCLIP_DIR   Path to openclip project (default: sibling directory ../openclip)
  QWEN_API_KEY   API key for Qwen LLM
"""

import sys
import os
import sqlite3
import json
import asyncio
import logging
import uuid
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Bootstrap: add openclip to Python path
# ---------------------------------------------------------------------------
OPENCLIP_DIR = Path(os.environ.get("OPENCLIP_DIR", str(Path(__file__).parent.parent.parent / "openclip")))
if not OPENCLIP_DIR.exists():
    raise RuntimeError(f"openclip not found at {OPENCLIP_DIR}. Set OPENCLIP_DIR env var.")
sys.path.insert(0, str(OPENCLIP_DIR))

from video_orchestrator import VideoOrchestrator

try:
    from core.transcript_generation_whisperx import TranscriptProcessorWhisperX
    WHISPERX_AVAILABLE = True
except ImportError:
    WHISPERX_AVAILABLE = False

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
MINDSTREAM_DIR = Path(__file__).parent.parent
DB_PATH = MINDSTREAM_DIR / "mindstream.db"
SPEAKER_REFS_DIR = MINDSTREAM_DIR / "data" / "speaker_references"
OUTPUT_DIR = MINDSTREAM_DIR / "data" / "processed_videos"

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_pending_videos(conn: sqlite3.Connection, limit: int = 5) -> list:
    return conn.execute(
        """
        SELECT ci.id, ci.title, ci.url, ci.duration_seconds, ci.published_at,
               tl.name AS leader_name
        FROM content_items ci
        JOIN thought_leaders tl ON ci.thought_leader_id = tl.id
        WHERE ci.processing_status = 'pending'
          AND ci.platform = 'youtube'
        ORDER BY ci.published_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


def update_status(conn: sqlite3.Connection, video_id: str, status: str) -> None:
    conn.execute(
        "UPDATE content_items SET processing_status = ?, updated_at = ? WHERE id = ?",
        (status, datetime.now().isoformat(), video_id),
    )
    conn.commit()


def save_transcript(
    conn: sqlite3.Connection,
    video_id: str,
    srt_path: str,
    language: str = "en",
    had_speaker_diarization: bool = False,
) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO transcripts
          (id, content_item_id, srt_path, language, had_speaker_diarization, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            video_id,
            srt_path,
            language,
            1 if had_speaker_diarization else 0,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()


def save_insights(conn: sqlite3.Connection, video_id: str, insights: list) -> None:
    now = datetime.now().isoformat()
    for i, insight in enumerate(insights):
        conn.execute(
            """
            INSERT INTO insights
              (id, content_item_id, order_index, claim, quote,
               start_seconds, end_seconds, topic, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                video_id,
                i,
                insight.get("claim", ""),
                insight.get("quote", ""),
                insight.get("start_seconds"),
                insight.get("end_seconds"),
                insight.get("topic", ""),
                now,
                now,
            ),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def time_str_to_seconds(time_str: str) -> int:
    """Convert HH:MM:SS or MM:SS to integer seconds."""
    parts = time_str.strip().split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(float(parts[2]))
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(float(parts[1]))
    except (ValueError, IndexError):
        pass
    return 0


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

async def process_video(video: dict, conn: sqlite3.Connection, skip_download: bool = False) -> bool:
    video_id = video["id"]
    video_url = video["url"]
    leader_name = video["leader_name"]
    title = video["title"]

    logger.info(f"── {title} ({leader_name})")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        update_status(conn, video_id, "downloading")

        ref_audio = SPEAKER_REFS_DIR / f"{leader_name}.wav"
        enable_diarization = WHISPERX_AVAILABLE and ref_audio.exists()
        if enable_diarization:
            logger.info(f"  Speaker diarization enabled ({leader_name})")
        else:
            reason = "WhisperX not installed" if not WHISPERX_AVAILABLE else f"no reference audio for {leader_name}"
            logger.info(f"  Speaker diarization disabled ({reason})")

        orchestrator = VideoOrchestrator(
            output_dir=str(OUTPUT_DIR),
            api_key=os.environ.get("QWEN_API_KEY"),
            llm_provider="qwen",
            language="en",
            mode="insights",
            enable_diarization=enable_diarization,
            speaker_references_dir=str(SPEAKER_REFS_DIR) if enable_diarization else None,
            generate_clips=True,
            add_titles=False,
            generate_cover=False,
        )

        result = await orchestrator.process_video(video_url, skip_download=skip_download)

        if not result.success:
            raise RuntimeError(result.error_message or "VideoOrchestrator failed")

        # ------------------------------------------------------------------
        # Save transcript path to DB
        # ------------------------------------------------------------------
        update_status(conn, video_id, "transcript_fetched")

        transcript_path = None
        if result.transcript_parts:
            transcript_path = result.transcript_parts[0]
        elif result.transcript_path:
            transcript_path = result.transcript_path

        if transcript_path:
            save_transcript(conn, video_id, transcript_path, had_speaker_diarization=enable_diarization)
            logger.info(f"  Transcript: {Path(transcript_path).name}")
        else:
            logger.warning("  No transcript path found in result")

        # ------------------------------------------------------------------
        # Save insights to DB
        # ------------------------------------------------------------------
        update_status(conn, video_id, "extracting_insights")

        engaging_result = result.engaging_moments_analysis or {}
        insights = engaging_result.get("insights", [])

        if not insights:
            logger.warning("  No insights extracted")
            update_status(conn, video_id, "insights_extracted")
            return True

        logger.info(f"  {len(insights)} insights extracted")

        # Convert timestamps to seconds for DB storage
        for insight in insights:
            insight["start_seconds"] = time_str_to_seconds(insight.get("start_time", ""))
            insight["end_seconds"] = time_str_to_seconds(insight.get("end_time", ""))

        save_insights(conn, video_id, insights)
        update_status(conn, video_id, "insights_extracted")

        # ------------------------------------------------------------------
        # Report clip generation
        # ------------------------------------------------------------------
        generated = 0
        if result.clip_generation:
            generated = result.clip_generation.get("successful_clips", 0)
        logger.info(f"  {generated}/{len(insights)} clips generated")
        update_status(conn, video_id, "clips_generated")

        return True

    except Exception as e:
        logger.error(f"  Failed: {e}", exc_info=True)
        update_status(conn, video_id, "failed")
        return False


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Mindstream insight pipeline")
    parser.add_argument("--limit", type=int, default=5, help="Max videos to process (default: 5)")
    parser.add_argument("--video-id", help="Process a specific video ID regardless of status")
    parser.add_argument("--skip-download", action="store_true", help="Skip download, use existing video")
    args = parser.parse_args()

    conn = get_db()

    if args.video_id:
        rows = conn.execute(
            """
            SELECT ci.id, ci.title, ci.url, ci.duration_seconds, ci.published_at,
                   tl.name AS leader_name
            FROM content_items ci
            JOIN thought_leaders tl ON ci.thought_leader_id = tl.id
            WHERE ci.id = ?
            """,
            (args.video_id,),
        ).fetchall()
    else:
        rows = get_pending_videos(conn, limit=args.limit)

    if not rows:
        logger.info("No videos to process")
        conn.close()
        return

    logger.info(f"Processing {len(rows)} video(s)...\n")
    results = []
    for row in rows:
        ok = await process_video(dict(row), conn, skip_download=args.skip_download)
        results.append(ok)

    logger.info(f"\nDone: {sum(results)}/{len(rows)} succeeded")
    conn.close()


if __name__ == "__main__":
    asyncio.run(main())