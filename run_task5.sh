#!/bin/bash

echo "============================================"
echo "Task 5: Vector Search Engine"
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
echo "Starting search engine..."
echo ""
python task5_search.py

deactivate

echo ""
echo "============================================"
echo "Search session ended"
echo "============================================"
echo ""
