#!/bin/bash

echo "============================================"
echo "Task 3: Inverted Index and Boolean Search"
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
echo "Running Task 3 indexer..."
echo ""
python task3_indexer.py

deactivate

echo ""
echo "============================================"
echo "Task 3 Complete!"
echo "============================================"
echo ""
echo "Output:"
echo "  - Inverted index: index_output/inverted_index.txt"
echo "  - Index JSON: index_output/inverted_index.json"
echo ""
