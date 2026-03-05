#!/usr/bin/env python3
"""
TF-IDF Calculator
Computes TF-IDF for terms and lemmas from Task 2.
"""

import os
import math
from collections import defaultdict, Counter


class TFIDFCalculator:
    """Calculates TF-IDF for terms and lemmas."""

    def __init__(self, tokens_dir="tokens_output/tokens", lemmas_dir="tokens_output/lemmas",
                 output_dir="tfidf_output"):
        self.tokens_dir = tokens_dir
        self.lemmas_dir = lemmas_dir
        self.output_dir = output_dir

    def read_file_terms(self, file_path):
        """Read terms from a token or lemma file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by whitespace and filter empty strings
        terms = [term.strip() for term in content.split() if term.strip()]
        return terms

    def compute_tf(self, terms):
        """Compute term frequency for each term in a document."""
        return Counter(terms)

    def compute_idf(self, doc_terms_list, all_terms):
        """
        Compute IDF for all terms across all documents.
        IDF(t) = log(N / df(t))
        where N = total number of documents, df(t) = number of documents containing term t
        """
        N = len(doc_terms_list)
        df = defaultdict(int) 

        # Count how many documents contain each term
        for terms in doc_terms_list:
            unique_terms = set(terms)
            for term in unique_terms:
                df[term] += 1

        # Compute IDF
        idf = {}
        for term in all_terms:
            if df[term] > 0:
                idf[term] = math.log(N / df[term])
            else:
                idf[term] = 0

        return idf

    def process_directory(self, input_dir, output_subdir, file_suffix):
        """Process all files in a directory and compute TF-IDF."""
        print(f"Processing {input_dir}...")

        # Get all input files
        files = sorted([f for f in os.listdir(input_dir) if f.endswith(file_suffix)])
        if not files:
            print(f"No files found in {input_dir}")
            return

        print(f"Found {len(files)} files")

        # Read all documents
        doc_terms = {}  # doc_id -> list of terms
        all_terms = set()

        for file_name in files:
            file_path = os.path.join(input_dir, file_name)
            terms = self.read_file_terms(file_path)
            doc_terms[file_name] = terms
            all_terms.update(terms)

        print(f"Total unique terms: {len(all_terms)}")

        # Compute IDF for all terms
        doc_terms_list = list(doc_terms.values())
        idf = self.compute_idf(doc_terms_list, all_terms)

        # Create output directory
        output_dir = os.path.join(self.output_dir, output_subdir)
        os.makedirs(output_dir, exist_ok=True)

        # Compute TF-IDF for each document
        for file_name, terms in doc_terms.items():
            # Compute TF
            tf = self.compute_tf(terms)

            # Compute TF-IDF
            tfidf = {}
            for term, tf_value in tf.items():
                tfidf[term] = tf_value * idf[term]

            # Sort by term name for consistent output
            sorted_terms = sorted(tfidf.keys())

            # Write output file
            output_file = file_name.replace(file_suffix, '_tfidf.txt')
            output_path = os.path.join(output_dir, output_file)

            with open(output_path, 'w', encoding='utf-8') as f:
                for term in sorted_terms:
                    f.write(f"{term} {idf[term]:.6f} {tfidf[term]:.6f}\n")

        print(f"✓ Created {len(doc_terms)} TF-IDF files in {output_dir}")

    def run(self):
        """Process both tokens and lemmas."""
        print("=" * 50)
        print("Task 4: TF-IDF Calculator")
        print("=" * 50)
        print()

        # Check input directories exist
        if not os.path.exists(self.tokens_dir):
            print(f"Error: Tokens directory not found: {self.tokens_dir}")
            print("Please run Task 2 first.")
            return

        if not os.path.exists(self.lemmas_dir):
            print(f"Error: Lemmas directory not found: {self.lemmas_dir}")
            print("Please run Task 2 first.")
            return

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Process tokens
        print("\n1. Processing tokens...")
        self.process_directory(self.tokens_dir, "tokens", "_tokens.txt")

        # Process lemmas
        print("\n2. Processing lemmas...")
        self.process_directory(self.lemmas_dir, "lemmas", "_lemmas.txt")

        print()
        print("=" * 50)
        print("TF-IDF calculation complete!")
        print("=" * 50)
        print()
        print("Output files:")
        print(f"  - Token TF-IDF: {self.output_dir}/tokens/")
        print(f"  - Lemma TF-IDF: {self.output_dir}/lemmas/")
        print()


def main():
    calculator = TFIDFCalculator()
    calculator.run()


if __name__ == "__main__":
    main()
