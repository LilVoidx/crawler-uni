#!/bin/bash

echo "============================================"
echo "Task 2: Tokenization and Lemmatization"
echo "============================================"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing requirements..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "Running Task 2 tokenizer..."
echo ""
python task2_tokenizer.py

deactivate

echo ""
echo "============================================"
echo "Task 2 Complete!"
echo "============================================"
echo ""
echo "Output:"
echo "  - Tokens: tokens_output/tokens.txt"
echo "  - Lemmas: tokens_output/lemmas.txt"
echo ""
