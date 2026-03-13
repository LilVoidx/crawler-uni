#!/usr/bin/env python3
"""
Tokenization and Lemmatization
"""

import os
import re
import zipfile
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


class TokenProcessor:
    def __init__(self, input_dir="crawl_output", output_dir="tokens_output"):
        self.input_dir = input_dir
        self.output_dir = output_dir

        # Create output directories
        Path(self.output_dir).mkdir(exist_ok=True)
        Path(os.path.join(self.output_dir, "tokens")).mkdir(exist_ok=True)
        Path(os.path.join(self.output_dir, "lemmas")).mkdir(exist_ok=True)

        self._download_nltk_data()

        # Initialize lemmatizer
        self.en_lemmatizer = WordNetLemmatizer()
        self.en_stop_words = set(stopwords.words('english'))

        # Global accumulators (across all docs)
        self.all_tokens = set()
        self.global_lemma_groups = defaultdict(set)  # lemma -> set of forms

    def _download_nltk_data(self):
        """Download required NLTK resources"""
        resources = [
            ('tokenizers/punkt_tab', 'punkt_tab'),
            ('corpora/stopwords', 'stopwords'),
            ('corpora/wordnet', 'wordnet'),
            ('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng'),
            ('corpora/omw-1.4', 'omw-1.4'),
        ]
        for find_path, download_name in resources:
            try:
                nltk.data.find(find_path)
            except LookupError:
                print(f"Downloading {download_name}...")
                nltk.download(download_name, quiet=True)

    def extract_text_from_html(self, html_file):
        """Extract clean text from full HTML page (excluding script/style/meta/noscript)."""
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove non-content tags
        for element in soup(["script", "style", "meta", "noscript"]):
            element.decompose()

        text = soup.get_text(separator=' ')
        return text

    def _wordnet_pos(self, treebank_tag):
        """Map Penn Treebank POS tag to WordNet POS."""
        if treebank_tag.startswith('J'):
            return 'a'
        elif treebank_tag.startswith('V'):
            return 'v'
        elif treebank_tag.startswith('R'):
            return 'r'
        else:
            return 'n'

    def process_text(self, text):
        """
        Tokenize text: extract [a-zA-Z]+ words, apply length/stopword filters,
        then POS-filter using Penn Treebank tags.
        Returns a list of unique valid tokens (lowercased).
        """
        # Extract raw English words
        raw_words = re.findall(r'[a-zA-Z]+', text)
        words_lower = [w.lower() for w in raw_words]

        # Length and stopword filter
        candidates = [
            w for w in words_lower
            if 2 <= len(w) <= 30 and w not in self.en_stop_words
        ]

        if not candidates:
            return []

        # POS-tag in batches to exclude function-word tags
        EXCLUDED_TAGS = {'IN', 'CC', 'RP', 'TO', 'UH'}
        BATCH_SIZE = 1000
        kept = []
        for i in range(0, len(candidates), BATCH_SIZE):
            batch = candidates[i:i + BATCH_SIZE]
            tagged = nltk.pos_tag(batch)
            for word, tag in tagged:
                if tag not in EXCLUDED_TAGS:
                    kept.append(word)

        # Deduplicate preserving sorted order
        unique_tokens = sorted(set(kept))
        return unique_tokens

    def lemmatize_tokens(self, tokens):
        """
        Lemmatize tokens using POS-aware WordNet lemmatizer.
        Returns lemma_groups: {lemma: set_of_forms}.
        """
        # Build a pos lookup from tagging all tokens
        if not tokens:
            return {}

        tagged = nltk.pos_tag(tokens)
        lemma_groups = defaultdict(set)
        for word, tag in tagged:
            wn_pos = self._wordnet_pos(tag)
            lemma = self.en_lemmatizer.lemmatize(word, pos=wn_pos)
            lemma_groups[lemma].add(word)

        return lemma_groups

    def process_single_file(self, html_file):
        """Process a single HTML file and create tokens/lemmas files."""
        page_num = html_file.stem.replace('page_', '')

        print(f"Processing {html_file.name}...")

        # Extract text
        text = self.extract_text_from_html(html_file)

        # Tokenize and filter (returns unique sorted tokens)
        unique_tokens = self.process_text(text)

        if not unique_tokens:
            print(f"  No valid tokens found")
            return

        # Lemmatize
        lemma_groups = self.lemmatize_tokens(unique_tokens)

        # --- Per-page token file (one word per line) ---
        tokens_file = os.path.join(self.output_dir, "tokens", f"page_{page_num}_tokens.txt")
        with open(tokens_file, 'w', encoding='utf-8') as f:
            for token in unique_tokens:
                f.write(f"{token}\n")

        # --- Per-page lemma file (no colon: "lemma form1 form2\n") ---
        lemmas_file = os.path.join(self.output_dir, "lemmas", f"page_{page_num}_lemmas.txt")
        with open(lemmas_file, 'w', encoding='utf-8') as f:
            for lemma, forms in sorted(lemma_groups.items()):
                forms_str = ' '.join(sorted(forms))
                f.write(f"{lemma} {forms_str}\n")

        # Accumulate globals
        self.all_tokens.update(unique_tokens)
        for lemma, forms in lemma_groups.items():
            self.global_lemma_groups[lemma].update(forms)

        print(f"  Tokens: {len(unique_tokens)}, Lemmas: {len(lemma_groups)}")

    def process_all_files(self):
        """Process all HTML files and write global vocab files."""
        html_files = sorted(Path(self.input_dir).glob("page_*.html"))

        if not html_files:
            print(f"No HTML files found in {self.input_dir}")
            print("Please run Task 1 first to download pages.")
            return

        print(f"Processing {len(html_files)} HTML files...\n")

        for html_file in html_files:
            self.process_single_file(html_file)

        # --- Global tokens.txt: all unique tokens, one per line, sorted ---
        global_tokens_file = os.path.join(self.output_dir, "tokens.txt")
        with open(global_tokens_file, 'w', encoding='utf-8') as f:
            for token in sorted(self.all_tokens):
                f.write(f"{token}\n")

        # --- Global lemmas.txt: "lemma: form1 form2\n", sorted by lemma ---
        global_lemmas_file = os.path.join(self.output_dir, "lemmas.txt")
        with open(global_lemmas_file, 'w', encoding='utf-8') as f:
            for lemma, forms in sorted(self.global_lemma_groups.items()):
                forms_str = ' '.join(sorted(forms))
                f.write(f"{lemma}: {forms_str}\n")

        print(f"\n{'='*60}")
        print("All files processed!")
        print(f"Per-page tokens: {self.output_dir}/tokens/")
        print(f"Per-page lemmas: {self.output_dir}/lemmas/")
        print(f"Global tokens:   {global_tokens_file}  ({len(self.all_tokens)} entries)")
        print(f"Global lemmas:   {global_lemmas_file}  ({len(self.global_lemma_groups)} entries)")

    def create_archives(self):
        """Create archives for submission."""
        print("\nCreating archives...")

        # Archive tokens
        tokens_archive = os.path.join(self.output_dir, "tokens_archive.zip")
        with zipfile.ZipFile(tokens_archive, 'w', zipfile.ZIP_DEFLATED) as zf:
            tokens_dir = os.path.join(self.output_dir, "tokens")
            for file in sorted(Path(tokens_dir).glob("*.txt")):
                zf.write(file, arcname=f"tokens/{file.name}")
        print(f"Tokens archive: {tokens_archive}")

        # Archive lemmas
        lemmas_archive = os.path.join(self.output_dir, "lemmas_archive.zip")
        with zipfile.ZipFile(lemmas_archive, 'w', zipfile.ZIP_DEFLATED) as zf:
            lemmas_dir = os.path.join(self.output_dir, "lemmas")
            for file in sorted(Path(lemmas_dir).glob("*.txt")):
                zf.write(file, arcname=f"lemmas/{file.name}")
        print(f"Lemmas archive: {lemmas_archive}")


def main():
    print("=" * 60)
    print("Task 2: Tokenization and Lemmatization")
    print("English support with POS-aware lemmatization")
    print("=" * 60)

    processor = TokenProcessor(input_dir="crawl_output", output_dir="tokens_output")

    processor.process_all_files()

    processor.create_archives()

    print("\n" + "=" * 60)
    print("Task 2 complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
