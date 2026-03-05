#!/usr/bin/env python3
"""
Vector Search Engine
Implements vector-based search using TF-IDF and cosine similarity.
"""

import os
import math
import re
from collections import defaultdict, Counter
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

try:
    import pymorphy2
    RUSSIAN_SUPPORT = True
except ImportError:
    RUSSIAN_SUPPORT = False


class VectorSearchEngine:
    """Vector-based search engine using TF-IDF and cosine similarity."""

    def __init__(self, tokens_dir="tokens_output/tokens", index_file="crawl_output/index.txt"):
        self.tokens_dir = tokens_dir
        self.index_file = index_file

        # Document collection
        self.doc_vectors = {}
        self.doc_urls = {}
        self.idf = {}
        self.all_terms = set()

        # NLP tools for query processing
        try:
            self.en_stop_words = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords', quiet=True)
            self.en_stop_words = set(stopwords.words('english'))

        try:
            self.en_lemmatizer = WordNetLemmatizer()
            self.en_lemmatizer.lemmatize("test")
        except LookupError:
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
            self.en_lemmatizer = WordNetLemmatizer()

        self.ru_morph = pymorphy2.MorphAnalyzer() if RUSSIAN_SUPPORT else None

    def is_english_word(self, word):
        """Check if word contains only English letters."""
        return bool(re.match(r'^[a-z]+$', word))

    def is_russian_word(self, word):
        """Check if word contains only Russian letters."""
        return bool(re.match(r'^[а-яё]+$', word))

    def is_valid_token(self, token):
        """Check if token should be included."""
        if len(token) < 2:
            return False
        if token.isdigit():
            return False
        if token in self.en_stop_words:
            return False
        if not (self.is_english_word(token) or self.is_russian_word(token)):
            return False
        return True

    def lemmatize_token(self, token):
        """Lemmatize a single token."""
        if self.is_english_word(token):
            lemma = self.en_lemmatizer.lemmatize(token, pos='n')
            lemma = self.en_lemmatizer.lemmatize(lemma, pos='v')
            lemma = self.en_lemmatizer.lemmatize(lemma, pos='a')
            return lemma
        elif self.is_russian_word(token) and self.ru_morph:
            parsed = self.ru_morph.parse(token)[0]
            return parsed.normal_form
        return token

    def process_query(self, query):
        """Process query text into lemmatized tokens."""
        tokens = re.findall(r'[a-zA-Zа-яА-ЯёЁ]+', query.lower())

        valid_tokens = []
        for token in tokens:
            if self.is_valid_token(token):
                lemma = self.lemmatize_token(token)
                valid_tokens.append(lemma)

        return valid_tokens

    def load_index(self):
        """Load document URLs from index file."""
        if not os.path.exists(self.index_file):
            print(f"Error: Index file not found: {self.index_file}")
            return False

        with open(self.index_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    doc_id = int(parts[0])
                    url = parts[1]
                    self.doc_urls[doc_id] = url

        print(f"Loaded {len(self.doc_urls)} document URLs")
        return True

    def build_document_vectors(self):
        """Build TF-IDF vectors for all documents."""
        if not os.path.exists(self.tokens_dir):
            print(f"Error: Tokens directory not found: {self.tokens_dir}")
            return False

        # Get all token files
        files = sorted([f for f in os.listdir(self.tokens_dir) if f.endswith('_tokens.txt')])
        if not files:
            print(f"Error: No token files found in {self.tokens_dir}")
            return False

        print(f"Building vectors for {len(files)} documents...")

        # Read all documents and compute document frequency
        doc_terms = {}  # doc_id -> list of terms
        df = defaultdict(int)  # document frequency

        for file_name in files:
            # Extract document ID from filename
            doc_id = int(file_name.split('_')[1])

            file_path = os.path.join(self.tokens_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                terms = [line.strip() for line in f if line.strip()]

            doc_terms[doc_id] = terms
            self.all_terms.update(terms)

            # Count document frequency
            for term in set(terms):
                df[term] += 1

        # Compute IDF
        N = len(doc_terms)
        for term in self.all_terms:
            if df[term] > 0:
                self.idf[term] = math.log(N / df[term])
            else:
                self.idf[term] = 0

        # Build TF-IDF vectors for each document
        for doc_id, terms in doc_terms.items():
            tf = Counter(terms)
            tfidf_vector = {}

            for term, tf_value in tf.items():
                tfidf_vector[term] = tf_value * self.idf[term]

            self.doc_vectors[doc_id] = tfidf_vector

        print(f"Built vectors with {len(self.all_terms)} unique terms")
        return True

    def compute_query_vector(self, query_terms):
        """Compute TF-IDF vector for query."""
        tf = Counter(query_terms)
        query_vector = {}

        for term, tf_value in tf.items():
            if term in self.idf:
                query_vector[term] = tf_value * self.idf[term]

        return query_vector

    def cosine_similarity(self, vec1, vec2):
        """Compute cosine similarity between two sparse vectors."""
        # dot product
        dot_product = 0.0
        for term in vec1:
            if term in vec2:
                dot_product += vec1[term] * vec2[term]

        # Compute magnitudes
        mag1 = math.sqrt(sum(val**2 for val in vec1.values()))
        mag2 = math.sqrt(sum(val**2 for val in vec2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def search(self, query, top_k=10):
        """Search for documents matching the query."""
        # Process query
        query_terms = self.process_query(query)
        if not query_terms:
            print("No valid terms in query")
            return []

        print(f"Query terms: {query_terms}")

        # Compute query vector
        query_vector = self.compute_query_vector(query_terms)
        if not query_vector:
            print("Query terms not found in corpus")
            return []

        # Compute similarity with all documents
        similarities = []
        for doc_id, doc_vector in self.doc_vectors.items():
            similarity = self.cosine_similarity(query_vector, doc_vector)
            if similarity > 0:
                similarities.append((doc_id, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top K results
        return similarities[:top_k]

    def run_interactive(self):
        """Run interactive search interface."""
        print("=" * 60)
        print("Task 5: Vector Search Engine")
        print("=" * 60)
        print()

        # Load index and build vectors
        if not self.load_index():
            return

        if not self.build_document_vectors():
            return

        print()
        print("=" * 60)
        print("Search engine ready!")
        print("=" * 60)
        print()
        print("Enter your search query (or 'exit' to quit)")
        print()

        while True:
            query = input("Query: ").strip()

            if query.lower() in ['exit', 'quit', 'q']:
                break

            if not query:
                continue

            print()
            results = self.search(query, top_k=10)

            if not results:
                print("No results found.")
            else:
                print(f"Found {len(results)} results:")
                print()
                for rank, (doc_id, score) in enumerate(results, 1):
                    url = self.doc_urls.get(doc_id, "Unknown")
                    print(f"{rank}. [Score: {score:.4f}] Page {doc_id}")
                    print(f"   {url}")

            print()


def main():
    engine = VectorSearchEngine()
    engine.run_interactive()


if __name__ == "__main__":
    main()
