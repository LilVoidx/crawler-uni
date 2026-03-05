#!/bin/bash

echo "============================================"
echo "Task 4: TF-IDF Calculator"
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
echo "Running Task 4 TF-IDF calculator..."
echo ""
python task4_tfidf.py

deactivate

echo ""
echo "============================================"
echo "Task 4 Complete!"
echo "============================================"
echo ""
echo "Output:"
echo "  - Token TF-IDF: tfidf_output/tokens/"
echo "  - Lemma TF-IDF: tfidf_output/lemmas/"
echo ""
