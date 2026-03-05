#!/usr/bin/env python3
"""
Vector Search Engine - Web Interface
Web-based search using TF-IDF and cosine similarity.
"""

import os
import math
import re
from collections import defaultdict, Counter
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from flask import Flask, render_template, request, jsonify

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

        # NLP tools
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
        return bool(re.match(r'^[a-z]+$', word))

    def is_russian_word(self, word):
        return bool(re.match(r'^[а-яё]+$', word))

    def is_valid_token(self, token):
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
        tokens = re.findall(r'[a-zA-Zа-яА-ЯёЁ]+', query.lower())
        valid_tokens = []
        for token in tokens:
            if self.is_valid_token(token):
                lemma = self.lemmatize_token(token)
                valid_tokens.append(lemma)
        return valid_tokens

    def load_index(self):
        if not os.path.exists(self.index_file):
            return False
        with open(self.index_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    doc_id = int(parts[0])
                    url = parts[1]
                    self.doc_urls[doc_id] = url
        return True

    def build_document_vectors(self):
        if not os.path.exists(self.tokens_dir):
            return False

        files = sorted([f for f in os.listdir(self.tokens_dir) if f.endswith('_tokens.txt')])
        if not files:
            return False

        doc_terms = {}
        df = defaultdict(int)

        for file_name in files:
            doc_id = int(file_name.split('_')[1])
            file_path = os.path.join(self.tokens_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                terms = [line.strip() for line in f if line.strip()]
            doc_terms[doc_id] = terms
            self.all_terms.update(terms)
            for term in set(terms):
                df[term] += 1

        N = len(doc_terms)
        for term in self.all_terms:
            if df[term] > 0:
                self.idf[term] = math.log(N / df[term])
            else:
                self.idf[term] = 0

        for doc_id, terms in doc_terms.items():
            tf = Counter(terms)
            tfidf_vector = {}
            for term, tf_value in tf.items():
                tfidf_vector[term] = tf_value * self.idf[term]
            self.doc_vectors[doc_id] = tfidf_vector

        return True

    def compute_query_vector(self, query_terms):
        tf = Counter(query_terms)
        query_vector = {}
        for term, tf_value in tf.items():
            if term in self.idf:
                query_vector[term] = tf_value * self.idf[term]
        return query_vector

    def cosine_similarity(self, vec1, vec2):
        dot_product = 0.0
        for term in vec1:
            if term in vec2:
                dot_product += vec1[term] * vec2[term]

        mag1 = math.sqrt(sum(val**2 for val in vec1.values()))
        mag2 = math.sqrt(sum(val**2 for val in vec2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot_product / (mag1 * mag2)

    def search(self, query, top_k=10):
        query_terms = self.process_query(query)
        if not query_terms:
            return [], []

        query_vector = self.compute_query_vector(query_terms)
        if not query_vector:
            return [], query_terms

        similarities = []
        for doc_id, doc_vector in self.doc_vectors.items():
            similarity = self.cosine_similarity(query_vector, doc_vector)
            if similarity > 0:
                similarities.append((doc_id, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k], query_terms


# Initialize Flask app
app = Flask(__name__)
search_engine = VectorSearchEngine()


@app.route('/')
def index():
    return render_template('search.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '').strip()

    if not query:
        return jsonify({'error': 'Empty query', 'results': []})

    results, query_terms = search_engine.search(query, top_k=10)

    response = {
        'query': query,
        'query_terms': query_terms,
        'total_results': len(results),
        'results': []
    }

    for rank, (doc_id, score) in enumerate(results, 1):
        url = search_engine.doc_urls.get(doc_id, "Unknown")
        response['results'].append({
            'rank': rank,
            'doc_id': doc_id,
            'score': round(score, 4),
            'url': url
        })

    return jsonify(response)


@app.route('/stats')
def stats():
    return jsonify({
        'total_documents': len(search_engine.doc_vectors),
        'total_terms': len(search_engine.all_terms),
        'indexed': len(search_engine.doc_vectors) > 0
    })


def main():
    print("=" * 60)
    print("Task 5: Vector Search Engine - Web Interface")
    print("=" * 60)
    print()
    print("Loading search index...")

    if not search_engine.load_index():
        print("Error: Could not load document index")
        print("Please run Task 1 first.")
        return

    if not search_engine.build_document_vectors():
        print("Error: Could not build document vectors")
        print("Please run Task 2 first.")
        return

    print(f"Loaded {len(search_engine.doc_vectors)} documents")
    print(f"Indexed {len(search_engine.all_terms)} unique terms")
    print()
    print("=" * 60)
    print("Starting web server...")
    print("=" * 60)
    print()
    print("Open your browser and go to:")
    print("  http://127.0.0.1:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print()

    app.run(host='127.0.0.1', port=5000, debug=False)


if __name__ == "__main__":
    main()
