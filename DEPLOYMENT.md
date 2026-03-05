# Deployment Manual

**Authors:** Aboelmakarem Youssef, Ahmed Maryam
**Group:** 11-200

## Requirements

- Python 3.7+
- pip
- Internet connection

## Installation

### Step 1: Clone Repository

```bash
git clone <repo-url>
cd crawler-uni
```

### Step 2: Run Task 1

```bash
chmod +x run_task1.sh
./run_task1.sh
```

The script will:
1. Create virtual environment
2. Install dependencies
3. Run the crawler
4. Save results to `crawl_output/`

## Manual Installation (if script doesn't work)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run crawler
python task1_crawler.py

# Deactivate
deactivate
```

## Configuration

To change number of pages, edit `task1_crawler.py` line 163:

```python
crawler = WebCrawler(output_dir="crawl_output", max_pages=100)
```

## Output

**Task 1 Output** (`crawl_output/`):
- `page_XXXX.html` - Downloaded pages
- `index.txt` - Page numbers and URLs mapping
- `urls_list.txt` - List of all URLs

**Task 2 Output** (`tokens_output/`):
- `tokens/page_XXXX_tokens.txt` - Tokens per page (one per line)
- `lemmas/page_XXXX_lemmas.txt` - Lemmas per page (lemma + tokens)
- `tokens_archive.zip` - Archive with all token files
- `lemmas_archive.zip` - Archive with all lemma files

**Task 3 Output** (`index_output/`):
- `inverted_index.txt` - Inverted index (term: doc IDs)
- `inverted_index.json` - Inverted index (JSON format)

**Task 4 Output** (`tfidf_output/`):
- `tokens/page_XXXX_tfidf.txt` - TF-IDF scores for tokens
- `lemmas/page_XXXX_tfidf.txt` - TF-IDF scores for lemmas

## Common Issues

**"Module not found"**
→ Run: `pip install -r requirements.txt`

**"Permission denied"**
→ Run: `chmod +x run_task1.sh`

**Too few pages downloaded**
→ Check internet connection and try again