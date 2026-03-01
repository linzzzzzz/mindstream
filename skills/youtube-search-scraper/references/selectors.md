# YouTube Search Results Page Selectors

## Page Structure

YouTube search results page URL:
```
https://www.youtube.com/results?search_query={QUERY}
```

## Video Results (Current Layout)

When you search, videos appear in a grid/list. Current selectors:

### Video Item Container
```css
ytd-video-renderer    # Main video element
#video-title         # Title link
#thumbnail          # Thumbnail container
ytd-channel-name    # Channel name
ytd-video-meta-info # Metadata (views, date)
```

### Extracting Data

| Field | Selector | Example |
|-------|----------|---------|
| Title | `#video-title` | "Sam Altman: The Future of AI" |
| URL | `#video-title a[href]` | /watch?v=xxx |
| Channel | `ytd-channel-name` | "Lex Fridman Podcast" |
| Views/Date | `ytd-video-meta-info` | "1.2M views • 2 days ago" |
| Thumbnail | `#thumbnail img` | i.ytimg.com/vi/xxx |

## Alternative Layout (Grid)

Sometimes YouTube shows a grid view:

```css
ytd-grid-video-renderer  # Grid item
#title                  # Title
#thumbnail             # Thumbnail
```

## Tips

1. **Filter by Videos**: Add `&sp=CAI%253D` to URL for videos only
2. **Sort by Date**: Add `&sp=CAI%253D` (recent) 
3. **Scroll** to load more results
4. **Wait** 3-5 seconds for dynamic content

## Example URL

```
# Search for Sam Altman AI, videos only, sorted by date
https://www.youtube.com/results?search_query=Sam+Altman+AI&sp=CAI%253D
```

## Parsing Tips

- Views often include "views" keyword: "1.2M views"
- Date often includes "ago": "2 days ago"
- Extract video ID from URL: `/watch?v=VIDEO_ID`
- Construct thumbnail: `https://i.ytimg.com/vi/{VIDEO_ID}/hqdefault.jpg`
