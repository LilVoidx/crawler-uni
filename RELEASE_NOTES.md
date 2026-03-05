# Release Notes

**Authors:** Aboelmakarem Youssef, Ahmed Maryam
**Group:** 11-200

## Version 1.0 - Task 1 (March 5, 2026)

### What's Implemented

**Web Crawler**
- Downloads 100+ web pages from Wikipedia
- Saves pages with HTML markup
- Creates index file mapping page numbers to URLs
- Filters out non-HTML content (images, CSS, JS, PDFs)
- All pages in English

**Files Generated**
- `page_XXXX.html` - Downloaded pages
- `index.txt` - Page number and URL mapping
- `urls_list.txt` - List of all URLs

### How to Use

```bash
./run_task1.sh
```

### Technical Details

- Language: Python 3
- Libraries: requests, BeautifulSoup4, lxml
- Crawl delay: 0.5 seconds between requests
- Timeout: 10 seconds per request
- Minimum text length: 200 characters

### Known Issues

- Only works with Wikipedia currently
- No resume capability if interrupted
- Downloads pages sequentially (not parallel)

### Tested On

- macOS
- Python 3.7+

### Future Tasks

- Task 2: Text processing
- Task 3: Indexing
- Task 4: Search
- Task 5: Ranking

---

## Changelog

### [1.0] - 2026-03-05
- Initial release
- Web crawler implementation
- Index generation
- Documentation
