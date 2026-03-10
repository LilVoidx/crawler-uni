#!/usr/bin/env python3
"""
Tokenization and Lemmatization
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

try:
    import pymorphy2
    PYMORPHY2_AVAILABLE = True
except ImportError:
    PYMORPHY2_AVAILABLE = False
    print("Warning: pymorphy2 not installed. Russian lemmatization will be limited.")


class TokenProcessor:
    def __init__(self, input_dir="crawl_output", output_dir="tokens_output"):
        self.input_dir = input_dir
        self.output_dir = output_dir

        # Create output directories
        Path(self.output_dir).mkdir(exist_ok=True)
        Path(os.path.join(self.output_dir, "tokens")).mkdir(exist_ok=True)
        Path(os.path.join(self.output_dir, "lemmas")).mkdir(exist_ok=True)

        self._download_nltk_data()

        # Initialize lemmatizers
        self.en_lemmatizer = WordNetLemmatizer()
        self.en_stop_words = set(stopwords.words('english'))

        # Initialize Russian lemmatizer
        if PYMORPHY2_AVAILABLE:
            self.ru_morph = pymorphy2.MorphAnalyzer()
            try:
                self.ru_stop_words = set(stopwords.words('russian'))
            except:
                self.ru_stop_words = set()
        else:
            self.ru_morph = None
            self.ru_stop_words = set()

    def _download_nltk_data(self):
        """Download required NLTK resources"""
        resources = ['punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'omw-1.4']
        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}')
            except LookupError:
                print(f"Downloading {resource}...")
                nltk.download(resource, quiet=True)

    def extract_text_from_html(self, html_file):
        """Extract clean text from HTML file"""
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script, style, and navigation elements
        for element in soup(["script", "style", "nav", "header", "footer"]):
            element.decompose()

        # Get text with separator to prevent word concatenation
        text = soup.get_text(separator=' ', strip=True)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)

        return text

    def is_english_word(self, token):
        """Check if token contains only English letters"""
        return bool(re.match(r'^[a-zA-Z]+$', token))

    def is_russian_word(self, token):
        """Check if token contains only Russian letters"""
        return bool(re.match(r'^[а-яА-ЯёЁ]+$', token))

    def is_valid_token(self, token):
        """Check if token is valid (English or Russian)"""
        # Must be at least 2 characters
        if len(token) < 2:
            return False

        # Filter out unreasonably long words
        if len(token) > 30:
            return False

        # Must be either English or Russian
        is_en = self.is_english_word(token)
        is_ru = self.is_russian_word(token)

        if not (is_en or is_ru):
            return False

        # Check stop words
        token_lower = token.lower()
        if is_en and token_lower in self.en_stop_words:
            return False
        if is_ru and token_lower in self.ru_stop_words:
            return False

        return True

    def process_text(self, text):
        """Tokenize and filter text"""
        tokens = re.findall(r'[a-zA-Zа-яА-ЯёЁ]+', text.lower())

        # Filter and collect valid tokens
        valid_tokens = []
        for token in tokens:
            if self.is_valid_token(token):
                valid_tokens.append(token)

        return valid_tokens

    def lemmatize_token(self, token):
        """Get lemma for a single token (English or Russian)"""
        if self.is_english_word(token):
            # English lemmatization
            lemma = self.en_lemmatizer.lemmatize(token, pos='n')
            lemma = self.en_lemmatizer.lemmatize(lemma, pos='v')
            lemma = self.en_lemmatizer.lemmatize(lemma, pos='a')
            return lemma
        elif self.is_russian_word(token) and self.ru_morph:
            # Russian lemmatization using pymorphy2
            parsed = self.ru_morph.parse(token)[0]
            return parsed.normal_form
        else:
            return token

    def lemmatize_tokens(self, tokens):
        """Group tokens by their lemmas"""
        lemma_groups = defaultdict(set)

        for token in tokens:
            lemma = self.lemmatize_token(token)
            lemma_groups[lemma].add(token)

        return lemma_groups

    def process_single_file(self, html_file):
        """Process a single HTML file and create tokens/lemmas files"""
        page_num = html_file.stem.replace('page_', '')

        print(f"Processing {html_file.name}...")

        # Extract text
        text = self.extract_text_from_html(html_file)

        # Tokenize and filter
        tokens = self.process_text(text)

        if not tokens:
            print(f"  No valid tokens found")
            return

        # Get unique tokens
        unique_tokens = sorted(set(tokens))

        # Lemmatize
        lemma_groups = self.lemmatize_tokens(unique_tokens)

        # Save tokens file
        tokens_file = os.path.join(self.output_dir, "tokens", f"page_{page_num}_tokens.txt")
        with open(tokens_file, 'w', encoding='utf-8') as f:
            for token in unique_tokens:
                f.write(f"{token}\n")

        # Save lemmas file
        lemmas_file = os.path.join(self.output_dir, "lemmas", f"page_{page_num}_lemmas.txt")
        with open(lemmas_file, 'w', encoding='utf-8') as f:
            for lemma, tokens_set in sorted(lemma_groups.items()):
                tokens_str = ' '.join(sorted(tokens_set))
                f.write(f"{lemma} {tokens_str}\n")

        print(f"  Tokens: {len(unique_tokens)}, Lemmas: {len(lemma_groups)}")

    def process_all_files(self):
        """Process all HTML files from Task 1"""
        html_files = sorted(Path(self.input_dir).glob("page_*.html"))

        if not html_files:
            print(f"No HTML files found in {self.input_dir}")
            print("Please run Task 1 first to download pages.")
            return

        print(f"Processing {len(html_files)} HTML files...\n")

        for html_file in html_files:
            self.process_single_file(html_file)

        print(f"\n{'='*60}")
        print("All files processed!")
        print(f"Tokens files: {self.output_dir}/tokens/")
        print(f"Lemmas files: {self.output_dir}/lemmas/")

    def create_archives(self):
        """Create archives for submission"""
        import zipfile

        print("\nCreating archives...")

        # Archive tokens
        tokens_archive = os.path.join(self.output_dir, "tokens_archive.zip")
        with zipfile.ZipFile(tokens_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
            tokens_dir = os.path.join(self.output_dir, "tokens")
            for file in Path(tokens_dir).glob("*.txt"):
                zipf.write(file, arcname=f"tokens/{file.name}")
        print(f"Tokens archive: {tokens_archive}")

        # Archive lemmas
        lemmas_archive = os.path.join(self.output_dir, "lemmas_archive.zip")
        with zipfile.ZipFile(lemmas_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
            lemmas_dir = os.path.join(self.output_dir, "lemmas")
            for file in Path(lemmas_dir).glob("*.txt"):
                zipf.write(file, arcname=f"lemmas/{file.name}")
        print(f"Lemmas archive: {lemmas_archive}")


def main():
    print("=" * 60)
    print("Task 2: Tokenization and Lemmatization")
    print("English and Russian support")
    print("=" * 60)

    processor = TokenProcessor(input_dir="crawl_output", output_dir="tokens_output")

    processor.process_all_files()

    processor.create_archives()

    print("\n" + "=" * 60)
    print("Task 2 complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
