'use client';

import { useState, useEffect } from 'react';
import videosData from '@/../public/videos.json';
import './globals.css';

interface FeedItem {
  id: string | null;
  title: string;
  title_zh: string;
  description: string;
  description_zh: string;
  thumbnailUrl: string;
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

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  
  if (hours < 1) return '刚刚';
  if (hours < 24) return `${hours}小时前`;
  if (days === 1) return '昨天';
  if (days < 7) return `${days}天前`;
  return date.toLocaleDateString('zh-CN');
}

function getYouTubeId(url: string): string | null {
  const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&]+)/);
  return match ? match[1] : null;
}

export default function Home() {
  const feed = videosData.videos as FeedItem[];
  const [selectedVideo, setSelectedVideo] = useState<FeedItem | null>(feed[0] || null);
  const [selectedLeaders, setSelectedLeaders] = useState<string[]>([]); // Multi-select
  const [filterOpen, setFilterOpen] = useState(false);
  const [lang, setLang] = useState<'en' | 'zh'>('en');
  const [showPreview, setShowPreview] = useState<boolean>(true);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= 768);
    checkMobile();
    if (window.innerWidth <= 768) {
      setShowPreview(false);
    }
    window.addEventListener('resize', checkMobile);
    
    // Close filter dropdown when clicking outside
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.filterWrapper')) {
        setFilterOpen(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    
    return () => {
      window.removeEventListener('resize', checkMobile);
      document.removeEventListener('click', handleClickOutside);
    };
  }, []);

  const handleVideoSelect = (item: FeedItem) => {
    setSelectedVideo(item);
    if (showPreview === false) {
      setShowPreview(true);
    }
  };

  const handleClosePreview = () => {
    setShowPreview(false);
  };

  // Toggle leader filter
  const toggleLeader = (leader: string) => {
    setSelectedLeaders(prev => 
      prev.includes(leader) 
        ? prev.filter(l => l !== leader)
        : [...prev, leader]
    );
  };

  const clearFilters = () => {
    setSelectedLeaders([]);
  };

  const shouldShowPreview = !isMobile || showPreview;

  const t = {
    filter: lang === 'en' ? 'Filter' : '筛选',
    all: lang === 'en' ? 'All' : '全部',
    videos: lang === 'en' ? 'videos' : '个视频',
    selectVideo: lang === 'en' ? 'Select a video' : '选择一个视频',
    clear: lang === 'en' ? 'Clear' : '清除',
  };

  // Filter videos - show all if no leaders selected, otherwise match any selected
  const filteredVideos = selectedLeaders.length === 0
    ? feed
    : feed.filter(v => selectedLeaders.includes(v.thoughtLeader?.name || ''));

  const leaders = Array.from(new Set(feed.map(v => v.thoughtLeader?.name).filter(Boolean)));

  const selectedVideoId = selectedVideo ? getYouTubeId(selectedVideo.url) : null;

  const getVideoKey = (item: FeedItem | null) => item?.id || item?.url || '';

  return (
    <div className="container">
      <header className="header">
        <h1 className="title">🧠 MindStream</h1>
        <div className="header-right">
          <button 
            className="langToggle"
            onClick={() => setLang(lang === 'en' ? 'zh' : 'en')}
          >
            {lang === 'en' ? '中文' : 'EN'}
          </button>
        </div>
      </header>

      <main className="main">
        <div className="layout">
          {/* Left Column - Video List */}
          <div className="leftColumn">
            {/* Filter Dropdown - Multi-select */}
            <div className="filterBar">
              <div className="filterWrapper">
                <button 
                  className="filterButton"
                  onClick={() => setFilterOpen(!filterOpen)}
                >
                  <span>👤</span>
                  <span>{selectedLeaders.length === 0 ? t.filter : `${selectedLeaders.length} selected`}</span>
                  <span className="filterArrow">{filterOpen ? '▲' : '▼'}</span>
                </button>
                {filterOpen && (
                  <div className="filterDropdown">
                    <div 
                      className={selectedLeaders.length === 0 ? 'filterOptionActive' : 'filterOption'}
                      onClick={clearFilters}
                    >
                      {t.all}
                    </div>
                    {leaders.map(leader => (
                      <div 
                        key={leader}
                        className={selectedLeaders.includes(leader || '') ? 'filterOptionActive' : 'filterOption'}
                        onClick={() => toggleLeader(leader || '')}
                      >
                        {leader} {selectedLeaders.includes(leader || '') ? '✓' : ''}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {selectedLeaders.length > 0 && (
                <button className="clearButton" onClick={clearFilters}>
                  {t.clear}
                </button>
              )}
              <span className="videoCount">
                {filteredVideos.length} {t.videos}
              </span>
            </div>

            {/* Video List */}
            <div className="videoList">
              {filteredVideos.map((item) => (
                <div 
                  key={getVideoKey(item)}
                  className={getVideoKey(selectedVideo!) === getVideoKey(item) ? 'videoItemSelected' : 'videoItem'}
                  onClick={() => handleVideoSelect(item)}
                >
                  <div className="videoThumbnail">
                    <img 
                      src={item.thumbnailUrl} 
                      alt={item.title}
                      className="thumbnailImg"
                    />
                    <span className="duration">{item.duration}</span>
                    {getVideoKey(selectedVideo!) === getVideoKey(item) && (
                      <div className="playOverlay">
                        <span className="playIcon">▶</span>
                      </div>
                    )}
                  </div>
                  <div className="videoInfo">
                    <h4 className="videoTitle">{lang === 'zh' && item.title_zh ? item.title_zh : item.title}</h4>
                    <div className="videoMeta">
                      <span className="leaderTag">{item.thoughtLeader?.name}</span>
                      <span className="metaDot">•</span>
                      <span>{formatDate(item.publishedAt)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column - Preview */}
          <div className={`rightColumn ${!shouldShowPreview ? 'hidden' : ''}`}>
            {selectedVideo ? (
              <div className="preview">
                {/* Close button for mobile */}
                <button className="goBackButton" onClick={handleClosePreview}>
                  ← Go Back
                </button>
                <div className="videoPlayer">
                  {selectedVideoId ? (
                    <iframe
                      width="100%"
                      height="100%"
                      src={`https://www.youtube.com/embed/${selectedVideoId}`}
                      title={selectedVideo.title}
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      className="iframe"
                    />
                  ) : (
                    <div className="noPreview">无法播放</div>
                  )}
                </div>
                <div className="previewInfo">
                  <h3 className="previewTitle">{lang === 'zh' && selectedVideo.title_zh ? selectedVideo.title_zh : selectedVideo.title}</h3>
                  <div className="previewMeta">
                    <span className="previewLeader">{selectedVideo.thoughtLeader?.name}</span>
                    <span className="metaDot">•</span>
                    <span>{formatDate(selectedVideo.publishedAt)}</span>
                  </div>
                  <p className="previewDesc">{lang === 'zh' && selectedVideo.description_zh ? selectedVideo.description_zh : selectedVideo.description}</p>
                </div>
              </div>
            ) : (
              <div className="noVideo">{t.selectVideo}</div>
            )}
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>MindStream - AI Thought Leader Content Aggregator</p>
      </footer>
    </div>
  );
}
