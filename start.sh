#!/bin/bash

# Configuration
PORT=7860

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Installing dependencies..."
    .venv/bin/pip install -r requirements.txt
fi

# Load .env variables if file exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Activate virtual environment and run app
echo "🚀 Starting PatiPedia on port $PORT..."
echo "📱 Application URL: http://localhost:$PORT"

export PORT=$PORT
.venv/bin/python app.py
