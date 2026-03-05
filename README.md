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

**Run:**
```bash
./run_task1.sh
```

## Task 2: Tokenization and Lemmatization

Extracts tokens from each HTML page and groups them by lemmas. Creates per-page files.

**Features:**
- Extracts clean text from HTML
- Tokenizes text into individual words
- Filters out stop words, numbers, and non-English/Russian words
- Proper lemmatization: WordNet for English, pymorphy2 for Russian
- Groups tokens by their lemmas
- Creates separate files for each page
- Generates archives for submission

**Run:**
```bash
./run_task2.sh
```

(Note: Run Task 1 first to download pages)

## Requirements

- Python 3.7+
- Internet connection

Dependencies are installed automatically by the run script.

## Project Structure

```
crawler-uni/
├── task1_crawler.py      # Task 1: Crawler
├── task2_tokenizer.py    # Task 2: Tokenization
├── run_task1.sh          # Run Task 1
├── run_task2.sh          # Run Task 2
├── requirements.txt      # Python packages
├── README.md             # This file
├── DEPLOYMENT.md         # Setup instructions
├── crawl_output/         # Task 1 output
│   ├── page_XXXX.html
│   └── index.txt
└── tokens_output/        # Task 2 output
    ├── tokens/
    │   ├── page_0001_tokens.txt
    │   └── ...
    ├── lemmas/
    │   ├── page_0001_lemmas.txt
    │   └── ...
    ├── tokens_archive.zip
    └── lemmas_archive.zip
```

## Output Files

**Task 1:**
- `crawl_output/page_XXXX.html` - Downloaded pages
- `crawl_output/index.txt` - Page numbers and URLs

**Task 2:**
- `tokens_output/tokens/page_XXXX_tokens.txt` - Tokens per page
- `tokens_output/lemmas/page_XXXX_lemmas.txt` - Lemmas per page
- `tokens_output/tokens_archive.zip` - Archive for submission
- `tokens_output/lemmas_archive.zip` - Archive for submission

## Technologies

- Python 3
- requests (HTTP library)
- BeautifulSoup4 (HTML parsing)
- NLTK (Natural Language Processing - English)
- pymorphy2 (Russian morphological analyzer)
