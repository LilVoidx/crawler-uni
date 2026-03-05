#!/bin/bash

echo "============================================"
echo "Task 5: Vector Search Engine - Web Interface"
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
echo "Starting web server..."
echo ""
python task5_web.py

deactivate

echo ""
echo "============================================"
echo "Server stopped"
echo "============================================"
echo ""
