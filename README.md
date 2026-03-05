# Web Crawler Project

**Authors:** 
Aboelmakarem Youssef Magdi Anwar Abdelfattah,
Ahmed Maryam Kareem Ahmed Ibrahim
**Group:** 11-200

## Description

This project implements a web crawler for information retrieval tasks. The crawler downloads web pages, processes them, and creates indexes for searching.

## Task 1: Web Crawler

Downloads 100+ web pages from Wikipedia and saves them with HTML markup.

**Features:**
- Downloads HTML pages with full markup
- Creates index file (page number → URL)
- All pages in English
- Filters out non-HTML content (images, CSS, JS, etc.)

## How to Run

```bash
chmod +x run_task1.sh
./run_task1.sh
```

## Requirements

- Python 3.7+
- Internet connection

Dependencies are installed automatically by the run script.

## Project Structure

```
crawler-uni/
├── task1_crawler.py      # Main crawler code
├── run_task1.sh          # Run script
├── requirements.txt      # Python packages
├── README.md             # This file
├── DEPLOYMENT.md         # Setup instructions
└── crawl_output/         # Downloaded pages (created when run)
    ├── page_0001.html
    ├── page_0002.html
    ├── ...
    └── index.txt
```

## Output Files

- **HTML pages:** `crawl_output/page_XXXX.html`
- **Index file:** `crawl_output/index.txt` (page numbers and URLs)
- **URLs list:** `crawl_output/urls_list.txt`

## Technologies

- Python 3
- requests (HTTP library)
- BeautifulSoup4 (HTML parsing)
