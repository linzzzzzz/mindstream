-- MindStream Database Schema (PostgreSQL)
-- Version: 1.0
-- For: MVP Phase 1

-- ============================================================
-- TABLE: thought_leaders
-- The core entity: AI thought leaders (people)
-- ============================================================
CREATE TABLE thought_leaders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    display_name    VARCHAR(255),  -- How it shows publicly (may differ from name)
    bio             TEXT,
    avatar_url      VARCHAR(512),
    language        VARCHAR(20) DEFAULT 'english',  -- 'english', 'chinese', 'bilingual'
    topics          VARCHAR(255)[], -- Array: ['LLMs', 'AI Safety', 'AGI']
    verified        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for search
CREATE INDEX idx_thought_leaders_name ON thought_leaders USING gin(to_tsvector('english', name));

-- ============================================================
-- TABLE: content_sources
-- Platforms where thought leaders publish content
-- One person can have multiple sources (YouTube, Bilibili, Twitter, etc.)
-- ============================================================
CREATE TABLE content_sources (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thought_leader_id   UUID NOT NULL REFERENCES thought_leaders(id) ON DELETE CASCADE,
    
    platform            VARCHAR(50) NOT NULL,  -- 'youtube', 'bilibili', 'podcast', 'twitter', 'conference'
    source_id           VARCHAR(255) NOT NULL, -- Platform-specific ID (e.g., YouTube channel ID)
    source_handle       VARCHAR(255),           -- @username or handle
    source_url          VARCHAR(512) NOT NULL,  -- Link to the source
    
    subscriber_count    INTEGER DEFAULT 0,
    last_fetched_at     TIMESTAMP,
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(platform, source_id)  -- Prevent duplicate sources
);

-- Index for lookups
CREATE INDEX idx_content_sources_leader ON content_sources(thought_leader_id);
CREATE INDEX idx_content_sources_platform ON content_sources(platform);

-- ============================================================
-- TABLE: content_items
-- Individual pieces of content (videos, podcasts, tweets)
-- ============================================================
CREATE TABLE content_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_source_id   UUID NOT NULL REFERENCES content_sources(id) ON DELETE CASCADE,
    
    title               VARCHAR(500) NOT NULL,
    description         TEXT,
    url                 VARCHAR(512) NOT NULL,
    thumbnail_url       VARCHAR(512),
    
    duration_seconds    INTEGER,    -- For videos/podcasts
    published_at        TIMESTAMP NOT NULL,
    
    content_type        VARCHAR(50) DEFAULT 'video',  -- 'video', 'podcast_episode', 'interview', 'conference_talk', 'tweet'
    topics              VARCHAR(255)[], -- Auto-detected or assigned tags
    
    -- Metadata
    view_count          INTEGER DEFAULT 0,
    like_count          INTEGER DEFAULT 0,
    
    -- Tracking
    fetched_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(content_source_id, url)  -- Prevent duplicates
);

-- Indexes for feed/querying
CREATE INDEX idx_content_items_source ON content_items(content_source_id);
CREATE INDEX idx_content_items_published ON content_items(published_at DESC);
CREATE INDEX idx_content_items_type ON content_items(content_type);

-- Full-text search index
CREATE INDEX idx_content_items_search ON content_items USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- ============================================================
-- TABLE: topics
-- Curation of topics for filtering
-- ============================================================
CREATE TABLE topics (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL UNIQUE,
    slug            VARCHAR(100) NOT NULL UNIQUE,  -- URL-friendly: 'large-language-models'
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- SAMPLE DATA: Initial Thought Leaders (MVP)
-- ============================================================
INSERT INTO thought_leaders (name, display_name, bio, language, topics, verified) VALUES
('Sam Altman', 'Sam Altman', 'CEO of OpenAI, leading AI company focused on artificial general intelligence', 'english', ARRAY['LLMs', 'AI Policy', 'Startups', 'AGI'], TRUE),
('Andrej Karpathy', 'Andrej Karpathy', 'Former Tesla AI Director, educator atkarpathy.io, focused on LLMs and AI education', 'english', ARRAY['LLMs', 'AI Education', 'Self-Driving', 'Neural Networks'], TRUE),
('Dario Amodei', 'Dario Amodei', 'CEO of Anthropic, leading AI safety and alignment research', 'english', ARRAY['AI Safety', 'LLMs', 'AI Ethics', 'Alignment'], TRUE),
('Demis Hassabis', 'Demis Hassabis', 'CEO of Google DeepMind, leading AGI research and AlphaFold', 'english', ARRAY['AGI', 'Neuroscience', 'AlphaFold', 'Robotics'], TRUE);

-- ============================================================
-- SAMPLE DATA: Topics
-- ============================================================
INSERT INTO topics (name, slug, description) VALUES
('Large Language Models', 'large-language-models', 'LLMs, GPT, language AI'),
('AI Safety', 'ai-safety', 'AI alignment, safety, ethics'),
('AGI', 'agi', 'Artificial General Intelligence'),
('AI Education', 'ai-education', 'Learning AI, tutorials, courses'),
('Computer Vision', 'computer-vision', 'Image recognition, CV, visual AI'),
('Robotics', 'robotics', 'Physical AI, robots, automation'),
('AI Ethics', 'ai-ethics', 'AI policy, ethics, societal impact'),
('Neural Networks', 'neural-networks', 'Deep learning fundamentals'),
('AI Research', 'ai-research', 'Papers, academia, research');

-- ============================================================
-- VIEW: Unified Feed
-- All content ordered by date
-- ============================================================
CREATE OR REPLACE VIEW unified_feed AS
SELECT 
    ci.id,
    ci.title,
    ci.description,
    ci.url,
    ci.thumbnail_url,
    ci.duration_seconds,
    ci.published_at,
    ci.content_type,
    ci.topics,
    ci.view_count,
    tl.name AS thought_leader_name,
    tl.display_name AS thought_leader_display_name,
    tl.avatar_url AS thought_leader_avatar,
    cs.platform,
    cs.source_url AS thought_leader_source_url
FROM content_items ci
JOIN content_sources cs ON ci.content_source_id = cs.id
JOIN thought_leaders tl ON cs.thought_leader_id = tl.id
ORDER BY ci.published_at DESC;

-- ============================================================
-- FUNCTION: Refresh thought leader content count
-- ============================================================
CREATE OR REPLACE FUNCTION update_content_count()
RETURNS TRIGGER AS $$
BEGIN
    -- This could be used to maintain a cached content count per thought leader
    -- For MVP, we'll query directly
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
