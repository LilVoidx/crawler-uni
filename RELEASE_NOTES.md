# Release Notes

**Authors:** Aboelmakarem Youssef, Ahmed Maryam
**Group:** 11-200

---

## Version 1.1 - Task 2 (March 5, 2026)

### Added
- Per-page tokenization and lemmatization
- Text extraction from HTML files
- Token filtering (removes stop words, numbers, non-English words)
- Proper lemmatization using WordNet (noun, verb, adjective forms)
- Separate token/lemma files for each page
- Automatic archive creation for submission

### Technical Details
- NLTK integration for English NLP processing
- WordNet Lemmatizer with POS tagging for English
- pymorphy2 for Russian lemmatization
- English and Russian support (filters out other languages)
- Per-page processing (100 token files + 100 lemma files)
- ZIP archives for easy submission

### Files
- `task2_tokenizer.py` - Tokenization implementation
- `run_task2.sh` - Run script for Task 2
- Output: `tokens_output/tokens/*.txt` and `tokens_output/lemmas/*.txt`
- Archives: `tokens_archive.zip`, `lemmas_archive.zip`

---

## Version 1.0 - Task 1 (March 5, 2026)

### Added
- Web crawler implementation
- Downloads 100+ web pages from Wikipedia
- HTML markup preservation
- Index file generation
- URL list generation
- Content filtering (removes non-HTML files)

### Technical Details
- requests library for HTTP
- BeautifulSoup4 for HTML parsing
- 0.5 second delay between requests
- 10 second timeout per request

### Files
- `task1_crawler.py` - Crawler implementation
- `run_task1.sh` - Run script for Task 1
- `README.md` - Project documentation
- `DEPLOYMENT.md` - Setup instructions

### Known Issues
- Only works with Wikipedia
- No resume capability
- Sequential downloads only

---

## Planned

### Task 3 - Indexing
- Build inverted index
- Term frequency analysis

### Task 4 - Search
- Query processing
- Search functionality

### Task 5 - Ranking
- Ranking algorithms
- Results optimization
