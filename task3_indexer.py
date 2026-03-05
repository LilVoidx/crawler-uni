#!/usr/bin/env python3
"""
Inverted Index and Boolean Search
Creates an inverted index and implements Boolean search with AND, OR, NOT operators.
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict


class InvertedIndex:
    def __init__(self, tokens_dir="tokens_output/tokens"):
        self.tokens_dir = tokens_dir
        self.index = defaultdict(set)
        self.doc_count = 0

    def build_index(self):
        """Build inverted index from token files"""
        print("Building inverted index...")

        token_files = sorted(Path(self.tokens_dir).glob("page_*_tokens.txt"))

        if not token_files:
            print(f"No token files found in {self.tokens_dir}")
            print("Please run Task 2 first.")
            return False

        for token_file in token_files:
            # Extract document ID from filename
            doc_id = token_file.stem.replace('page_', '').replace('_tokens', '')

            # Read tokens from file
            with open(token_file, 'r', encoding='utf-8') as f:
                tokens = [line.strip() for line in f if line.strip()]

            # Add to inverted index
            for token in tokens:
                self.index[token].add(doc_id)

            self.doc_count += 1

        print(f"Index built: {len(self.index)} unique terms, {self.doc_count} documents")
        return True

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
    def __init__(self, index):
        self.index = index

    def search_term(self, term):
        """Search for a single term"""
        term = term.lower().strip()
        return self.index.get(term, set())

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
    print("=" * 60)

    # Build inverted index
    indexer = InvertedIndex(tokens_dir="tokens_output/tokens")

    if not indexer.build_index():
        return

    # Save index
    print("\nSaving index...")
    indexer.save_index("index_output/inverted_index.txt")
    indexer.save_index_json("index_output/inverted_index.json")

    # Initialize Boolean search
    searcher = BooleanSearch(indexer.index)

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
