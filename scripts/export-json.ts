/**
 * Export script: Reads from the original mindstream DB and exports to videos.json
 * Run: npx tsx scripts/export-json.ts
 */

import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';

const DB_PATH = path.join(__dirname, '../mindstream.db');
const OUTPUT_PATH = path.join(__dirname, '../public/videos.json');

interface Video {
  id: string;
  title: string;
  title_zh: string;
  description: string;
  description_zh: string;
  thumbnailUrl: string;
  channel: string;
  publishedAt: string;
  duration: string;
  durationSeconds: number;
  viewCount: number;
  platform: string;
  thoughtLeader: {
    id: string;
    name: string;
    avatarUrl: string | null;
    verified: boolean;
  };
  url: string;
}

interface ExportData {
  generatedAt: string;
  videos: Video[];
}

function formatDuration(seconds: number | null): string {
  if (!seconds) return '0:00';
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function main() {
  console.log('📦 Exporting videos from database...');
  console.log(`   DB path: ${DB_PATH}`);
  console.log(`   Output: ${OUTPUT_PATH}`);

  // Check if DB exists
  if (!fs.existsSync(DB_PATH)) {
    console.error('❌ Database not found!');
    process.exit(1);
  }

  const db = new Database(DB_PATH);

  // Query videos with thought leader info
  const rows = db.prepare(`
    SELECT
      ci.id,
      ci.title as title_en,
      ci.title_zh,
      ci.description as description_en,
      ci.description_zh,
      ci.thumbnail_url,
      ci.channel,
      ci.published_at,
      ci.duration_seconds,
      ci.view_count,
      ci.url,
      tl.id as leader_id,
      tl.name as leader_name,
      tl.verified
    FROM content_items ci
    JOIN thought_leaders tl ON ci.thought_leader_id = tl.id
    ORDER BY ci.published_at DESC
  `).all() as any[];

  const videos: Video[] = rows.map((row) => ({
    id: row.id,
    title: row.title_en,
    title_zh: row.title_zh || row.title_en,
    description: row.description_en || '',
    description_zh: row.description_zh || row.description_en || '',
    thumbnailUrl: row.thumbnail_url || '',
    channel: row.channel || '',
    publishedAt: row.published_at,
    duration: formatDuration(row.duration_seconds),
    durationSeconds: row.duration_seconds || 0,
    viewCount: row.view_count || 0,
    platform: 'youtube',
    thoughtLeader: {
      id: row.leader_id,
      name: row.leader_name,
      avatarUrl: null,
      verified: !!row.verified,
    },
    url: row.url,
  }));

  const exportData: ExportData = {
    generatedAt: new Date().toISOString(),
    videos,
  };

  // Ensure output directory exists
  const outputDir = path.dirname(OUTPUT_PATH);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Write JSON
  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(exportData, null, 2));

  db.close();

  console.log(`✅ Exported ${videos.length} videos`);
  console.log(`   Generated at: ${exportData.generatedAt}`);
}

main();
