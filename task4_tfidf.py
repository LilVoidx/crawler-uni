#!/usr/bin/env python3
"""
TF-IDF Calculator
Computes TF-IDF for terms and lemmas from Task 2.
"""

import os
import re
import math
import zipfile
from pathlib import Path
from bs4 import BeautifulSoup


class TFIDFCalculator:
    """Calculates TF-IDF for terms and lemmas."""

    def __init__(self,
                 crawl_dir="crawl_output",
                 tokens_vocab="tokens_output/tokens.txt",
                 lemmas_vocab="tokens_output/lemmas.txt",
                 output_dir="tfidf_output"):
        self.crawl_dir = crawl_dir
        self.tokens_vocab_path = tokens_vocab
        self.lemmas_vocab_path = lemmas_vocab
        self.output_dir = output_dir

    # Vocabulary loading

    def load_all_tokens(self):
        """Read global token list from tokens_output/tokens.txt."""
        with open(self.tokens_vocab_path, 'r', encoding='utf-8') as f:
            tokens = [line.strip() for line in f if line.strip()]
        return tokens

    def load_lemmas_dict(self):
        """
        Read global lemmas from tokens_output/lemmas.txt.
        Format: "lemma: form1 form2 ..."
        Returns {lemma: [form1, form2, ...]}
        """
        lemmas = {}
        with open(self.lemmas_vocab_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Split on the colon
                colon_idx = line.index(':')
                lemma = line[:colon_idx].strip()
                forms_str = line[colon_idx + 1:].strip()
                forms = forms_str.split() if forms_str else []
                lemmas[lemma] = forms
        return lemmas

    # Text extraction (same logic as Task 2)

    def extract_words_from_html(self, html_file):
        """
        Extract all [a-zA-Z]+ words from an HTML page
        (after removing script/style/meta/noscript tags).
        Returns a list of lowercased words (with repetitions for TF counting).
        """
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        for element in soup(["script", "style", "meta", "noscript"]):
            element.decompose()

        text = soup.get_text(separator=' ')
        words = re.findall(r'[a-zA-Z]+', text)
        return [w.lower() for w in words]

    # IDF

    def compute_idf(self, all_terms, doc_words_list):
        """
        IDF(t) = log(N / df(t))
        N = number of documents, df(t) = docs containing term t.
        """
        N = len(doc_words_list)
        df = {}
        for term in all_terms:
            df[term] = sum(1 for words in doc_words_list if term in words)

        idf = {}
        for term in all_terms:
            idf[term] = math.log(N / df[term]) if df[term] > 0 else 0.0
        return idf

    # ------------------------------------------------------------------
    # Main processing
    # ------------------------------------------------------------------

    def run(self):
        """Compute TF-IDF for terms and lemmas, write output files."""
        print("=" * 50)
        print("Task 4: TF-IDF Calculator")
        print("=" * 50)

        # Load vocabulary
        if not os.path.exists(self.tokens_vocab_path):
            print(f"Error: {self.tokens_vocab_path} not found. Run Task 2 first.")
            return
        if not os.path.exists(self.lemmas_vocab_path):
            print(f"Error: {self.lemmas_vocab_path} not found. Run Task 2 first.")
            return

        print("\nLoading vocabulary...")
        all_tokens = self.load_all_tokens()
        lemmas_dict = self.load_lemmas_dict()
        print(f"  Tokens: {len(all_tokens)}, Lemmas: {len(lemmas_dict)}")

        # Collect HTML files sorted, map to 0-indexed output filenames
        html_files = sorted(Path(self.crawl_dir).glob("page_*.html"))
        if not html_files:
            print(f"No HTML files found in {self.crawl_dir}")
            return
        print(f"\nFound {len(html_files)} HTML files")

        # Create output directories
        terms_out_dir = os.path.join(self.output_dir, "tf_idf_terms")
        lemmas_out_dir = os.path.join(self.output_dir, "tf_idf_lemmas")
        os.makedirs(terms_out_dir, exist_ok=True)
        os.makedirs(lemmas_out_dir, exist_ok=True)

        # Extract words from each document (with repetitions for TF)
        print("\nExtracting words from HTML files...")
        doc_words = []        # list of word lists
        doc_word_sets = []    # list of sets (for IDF df computation)
        for html_file in html_files:
            words = self.extract_words_from_html(html_file)
            doc_words.append(words)
            doc_word_sets.append(set(words))

        # ---- TERMS ----
        print("\n1. Computing TF-IDF for terms...")
        idf_terms = self.compute_idf(all_tokens, doc_word_sets)

        for idx, (html_file, words) in enumerate(zip(html_files, doc_words)):
            total = len(words)
            out_name = f"{idx}.txt"
            out_path = os.path.join(terms_out_dir, out_name)

            with open(out_path, 'w', encoding='utf-8') as f:
                for term in sorted(all_tokens):
                    count = words.count(term)
                    if count == 0:
                        continue
                    tf = count / total if total > 0 else 0.0
                    tfidf = tf * idf_terms[term]
                    f.write(f"{term} {idf_terms[term]:.6f} {tfidf:.6f}\n")

        print(f"  Written {len(html_files)} files to {terms_out_dir}")

        # ---- LEMMAS ----
        print("\n2. Computing TF-IDF for lemmas...")
        all_lemmas = list(lemmas_dict.keys())
        idf_lemmas = self.compute_idf(all_lemmas, doc_word_sets)

        for idx, (html_file, words) in enumerate(zip(html_files, doc_words)):
            total = len(words)
            out_name = f"{idx}.txt"
            out_path = os.path.join(lemmas_out_dir, out_name)

            with open(out_path, 'w', encoding='utf-8') as f:
                for lemma in sorted(all_lemmas):
                    variants = lemmas_dict[lemma]
                    count = sum(words.count(v) for v in variants)
                    if count == 0:
                        continue
                    tf = count / total if total > 0 else 0.0
                    tfidf = tf * idf_lemmas[lemma]
                    f.write(f"{lemma} {idf_lemmas[lemma]:.6f} {tfidf:.6f}\n")

        print(f"  Written {len(html_files)} files to {lemmas_out_dir}")

        # ---- ARCHIVE ----
        print("\nCreating archive...")
        archive_path = os.path.join(self.output_dir, "Archive.zip")
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for folder, subdir in [(terms_out_dir, "tf_idf_terms"),
                                   (lemmas_out_dir, "tf_idf_lemmas")]:
                for file in sorted(Path(folder).glob("*.txt")):
                    zf.write(file, arcname=f"{subdir}/{file.name}")
        print(f"Archive: {archive_path}")

        print()
        print("=" * 50)
        print("TF-IDF calculation complete!")
        print("=" * 50)
        print(f"\nOutput:")
        print(f"  Terms:  {terms_out_dir}")
        print(f"  Lemmas: {lemmas_out_dir}")
        print(f"  Zip:    {archive_path}")


def main():
    calculator = TFIDFCalculator()
    calculator.run()


if __name__ == "__main__":
    main()
