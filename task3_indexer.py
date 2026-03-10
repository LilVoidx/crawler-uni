#!/usr/bin/env python3
"""
Inverted Index and Boolean Search
Creates an inverted index from lemmas and implements Boolean search with AND, OR, NOT operators.
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict
import nltk
from nltk.stem import WordNetLemmatizer

try:
    import pymorphy2
    PYMORPHY2_AVAILABLE = True
except ImportError:
    PYMORPHY2_AVAILABLE = False


class InvertedIndex:
    def __init__(self, lemmas_dir="tokens_output/lemmas"):
        self.lemmas_dir = lemmas_dir
        self.index = defaultdict(set)
        self.doc_count = 0

        # Initialize lemmatizers for query processing
        self._download_nltk_data()
        self.en_lemmatizer = WordNetLemmatizer()
        if PYMORPHY2_AVAILABLE:
            self.ru_morph = pymorphy2.MorphAnalyzer()
        else:
            self.ru_morph = None

    def _download_nltk_data(self):
        """Download required NLTK resources"""
        resources = ['wordnet', 'averaged_perceptron_tagger', 'omw-1.4']
        for resource in resources:
            try:
                nltk.data.find(f'corpora/{resource}' if resource in ['wordnet', 'omw-1.4'] else f'taggers/{resource}')
            except LookupError:
                nltk.download(resource, quiet=True)

    def build_index(self):
        """Build inverted index from lemma files"""
        print("Building inverted index from lemmas...")

        lemma_files = sorted(Path(self.lemmas_dir).glob("page_*_lemmas.txt"))

        if not lemma_files:
            print(f"No lemma files found in {self.lemmas_dir}")
            print("Please run Task 2 first.")
            return False

        for lemma_file in lemma_files:
            # Extract document ID from filename
            doc_id = lemma_file.stem.replace('page_', '').replace('_lemmas', '')

            # Read lemmas from file
            with open(lemma_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if parts:
                            lemma = parts[0]
                            self.index[lemma].add(doc_id)

            self.doc_count += 1

        print(f"Index built: {len(self.index)} unique lemmas, {self.doc_count} documents")
        return True

    def lemmatize_word(self, word):
        """Lemmatize a single word"""
        if re.match(r'^[a-zA-Z]+$', word):
            # English lemmatization
            lemma = self.en_lemmatizer.lemmatize(word, pos='n')
            lemma = self.en_lemmatizer.lemmatize(lemma, pos='v')
            lemma = self.en_lemmatizer.lemmatize(lemma, pos='a')
            return lemma
        elif re.match(r'^[а-яА-ЯёЁ]+$', word) and self.ru_morph:
            # Russian lemmatization
            parsed = self.ru_morph.parse(word)[0]
            return parsed.normal_form
        else:
            return word

    def save_index(self, output_file="index_output/inverted_index.txt"):
        """Save inverted index to file"""
        Path(output_file).parent.mkdir(exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            for term in sorted(self.index.keys()):
                doc_ids = sorted(self.index[term])
                f.write(f"{term}: {', '.join(doc_ids)}\n")

        print(f"Index saved to: {output_file}")

    def save_index_json(self, output_file="index_output/inverted_index.json"):
        """Save inverted index as JSON"""
        Path(output_file).parent.mkdir(exist_ok=True)

        # Convert sets to sorted lists for JSON serialization
        json_index = {term: sorted(list(docs)) for term, docs in self.index.items()}

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_index, f, indent=2, ensure_ascii=False)

        print(f"Index JSON saved to: {output_file}")


class BooleanSearch:
    def __init__(self, index, lemmatizer):
        self.index = index
        self.lemmatizer = lemmatizer

    def search_term(self, term):
        """Search for a single term (lemmatized)"""
        term = term.lower().strip()
        # Lemmatize the search term
        lemma = self.lemmatizer.lemmatize_word(term)
        return self.index.get(lemma, set())

    def search_and(self, results1, results2):
        """AND operation: intersection"""
        return results1 & results2

    def search_or(self, results1, results2):
        """OR operation: union"""
        return results1 | results2

    def search_not(self, results, all_docs):
        """NOT operation: complement"""
        return all_docs - results

    def parse_query(self, query):
        """Parse and execute Boolean query"""
        query = query.strip()

        # Get all document IDs
        all_docs = set()
        for docs in self.index.values():
            all_docs.update(docs)

        # Tokenize query (handle parentheses, operators, terms)
        tokens = re.findall(r'\(|\)|AND|OR|NOT|[a-zA-Zа-яА-ЯёЁ]+', query)

        # Convert infix to postfix (Shunting Yard algorithm)
        postfix = self._infix_to_postfix(tokens)

        # Evaluate postfix expression
        result = self._evaluate_postfix(postfix, all_docs)

        return result

    def _infix_to_postfix(self, tokens):
        """Convert infix notation to postfix using Shunting Yard algorithm"""
        precedence = {'NOT': 3, 'AND': 2, 'OR': 1}
        output = []
        stack = []

        for token in tokens:
            if token in ['AND', 'OR', 'NOT']:
                # Operator
                while (stack and stack[-1] != '(' and
                       stack[-1] in precedence and
                       precedence[stack[-1]] >= precedence[token]):
                    output.append(stack.pop())
                stack.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if stack:
                    stack.pop()
            else:
                # Term
                output.append(token)

        while stack:
            output.append(stack.pop())

        return output

    def _evaluate_postfix(self, postfix, all_docs):
        """Evaluate postfix expression"""
        stack = []

        for token in postfix:
            if token == 'AND':
                right = stack.pop()
                left = stack.pop()
                stack.append(self.search_and(left, right))
            elif token == 'OR':
                right = stack.pop()
                left = stack.pop()
                stack.append(self.search_or(left, right))
            elif token == 'NOT':
                operand = stack.pop()
                stack.append(self.search_not(operand, all_docs))
            else:
                stack.append(self.search_term(token))

        return stack[0] if stack else set()

    def search(self, query):
        """Execute Boolean search query"""
        print(f"\nQuery: {query}")

        try:
            results = self.parse_query(query)
            sorted_results = sorted(results)

            print(f"Results: {len(sorted_results)} documents")
            if sorted_results:
                print(f"Document IDs: {', '.join(sorted_results)}")
            else:
                print("No documents found")

            return sorted_results

        except Exception as e:
            print(f"Error executing query: {e}")
            return []


def main():
    print("=" * 60)
    print("Task 3: Inverted Index and Boolean Search")
    print("(Using lemmas with query lemmatization)")
    print("=" * 60)

    # Build inverted index
    indexer = InvertedIndex(lemmas_dir="tokens_output/lemmas")

    if not indexer.build_index():
        return

    # Save index
    print("\nSaving index...")
    indexer.save_index("index_output/inverted_index.txt")
    indexer.save_index_json("index_output/inverted_index.json")

    # Initialize Boolean search
    searcher = BooleanSearch(indexer.index, indexer)

    # Interactive search
    print("\n" + "=" * 60)
    print("Boolean Search Engine")
    print("=" * 60)
    print("Operators: AND, OR, NOT")
    print("Example: (algorithm AND machine) OR learning")
    print("Type 'exit' to quit")
    print("=" * 60)

    while True:
        query = input("\nEnter query: ").strip()

        if query.lower() in ['exit', 'quit', 'q']:
            break

        if not query:
            continue

        searcher.search(query)

    print("\n" + "=" * 60)
    print("Task 3 complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
