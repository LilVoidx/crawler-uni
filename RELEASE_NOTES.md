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

## Version 1.2 - Task 3 (March 5, 2026)

### Added
- Inverted index construction
- Boolean search engine with AND, OR, NOT operators
- Support for complex queries with parentheses
- Shunting Yard algorithm for query parsing
- Interactive search interface
- Index export in TXT and JSON formats

### Technical Details
- Inverted index: term ->set of document IDs
- Query parsing using infix to postfix conversion
- Set operations for Boolean logic
- Interactive command-line search

### Files
- `task3_indexer.py` - Inverted index and Boolean search
- `run_task3.sh` - Run script for Task 3
- Output: `inverted_index.txt`, `inverted_index.json`

---

## Version 1.3 - Task 4 (March 5, 2026)

### Added
- TF-IDF (Term Frequency-Inverse Document Frequency) calculator
- Per-document TF-IDF computation for tokens and lemmas
- TF (term frequency) calculation per document
- IDF (inverse document frequency) calculation across corpus
- TF-IDF = TF × IDF scoring

### Technical Details
- TF: count of term in document
- IDF: log(N / df(t)) where N = total docs, df(t) = docs containing term
- Per-document output files with format: `<term> <idf> <tf-idf>`
- Separate processing for tokens and lemmas
- Sorted output by term name

### Files
- `task4_tfidf.py` - TF-IDF calculation implementation
- `run_task4.sh` - Run script for Task 4
- Output: `tfidf_output/tokens/*.txt` and `tfidf_output/lemmas/*.txt`

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
