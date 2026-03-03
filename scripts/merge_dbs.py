#!/usr/bin/env python3
"""
Merge worker SQLite DBs into a single canonical DB.

Use after distributed processing where each worker machine handled a
non-overlapping set of video IDs. Workers start from a copy of the
canonical DB; this script folds their results back in.

Usage:
  python scripts/merge_dbs.py mindstream.db machine_a.db machine_b.db ...

Prerequisites:
  - Sync output files from each worker before running:
      rsync -av machine-a:~/mindstream/data/processed_videos/ data/processed_videos/
      rsync -av machine-b:~/mindstream/data/processed_videos/ data/processed_videos/
  - If transcript paths in the worker DBs are machine-local, fix them after:
      UPDATE transcripts SET srt_path = REPLACE(srt_path, '/home/machine-a', '/canonical/path');
"""

import sys
import sqlite3


def merge(canonical_path: str, worker_paths: list[str]) -> None:
    conn = sqlite3.connect(canonical_path)

    for worker_path in worker_paths:
        print(f"Merging {worker_path}...")
        conn.execute("ATTACH DATABASE ? AS w", (worker_path,))

        # Update processing_status for videos this worker handled.
        # Rows already exist in the canonical DB (copied from base); we just
        # overwrite the status for videos the worker actually processed.
        conn.execute("""
            UPDATE content_items
            SET processing_status = w.processing_status,
                updated_at        = w.updated_at
            FROM (SELECT id, processing_status, updated_at FROM w.content_items) AS w
            WHERE content_items.id = w.id
              AND w.processing_status != 'pending'
        """)

        # Copy transcripts and insights — these only exist in the worker DB.
        # OR IGNORE is a safety net if merge is run twice (UUID IDs won't collide).
        conn.execute("INSERT OR IGNORE INTO transcripts SELECT * FROM w.transcripts")
        conn.execute("INSERT OR IGNORE INTO insights    SELECT * FROM w.insights")

        conn.execute("DETACH DATABASE w")
        conn.commit()
        print(f"  done")

    conn.close()
    print("Merge complete.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/merge_dbs.py canonical.db worker1.db worker2.db ...")
        sys.exit(1)
    merge(sys.argv[1], sys.argv[2:])