#!/bin/bash

echo "========================================"
echo "AI-Driven Dynamic Pricing E-commerce"
echo "========================================"
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python found!"
echo

echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

echo
echo "Activating virtual environment..."
source venv/bin/activate

echo
echo "Installing dependencies..."
pip install -r requirements.txt

echo
echo "Setting up database..."
python add_sample_data.py

echo
echo "Starting the website..."
echo
echo "========================================"
echo "Website will be available at:"
echo "http://localhost:8000"
echo "========================================"
echo
echo "Press Ctrl+C to stop the server"
echo

python run.py 