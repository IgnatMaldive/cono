#!/bin/bash
source myenv/bin/activate

# Check if requirements.txt exists and install dependencies
if [ -f requirements.txt ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping dependency installation."
fi

# Check and kill processes on port 5000
echo "Checking for processes on port 5000..."
PID=$(lsof -t -i:5000)
if [ -n "$PID" ]; then
    echo "Killing process $PID on port 5000..."
    kill -9 "$PID"
    echo "Process killed."
else
    echo "No process found on port 5000."
fi

export FLASK_APP=api/index.py
flask run