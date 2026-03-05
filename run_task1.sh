#!/bin/bash

echo "============================================"
echo "Task 1: Web Crawler Setup and Execution"
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
echo "Running Task 1 crawler..."
echo ""
python task1_crawler.py

deactivate

echo ""
echo "============================================"
echo "Task 1 Complete!"
echo "============================================"
echo ""
echo "Output:"
echo "  - Downloaded pages: crawl_output/"
echo "  - Index file: crawl_output/index.txt"
echo ""
