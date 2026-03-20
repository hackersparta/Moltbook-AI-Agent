#!/bin/bash

# Start the engagement/scheduler loop in the background
echo "🚀 Starting Moltbook Automation Engine..."
python moltbook_engage.py &

# Start the web dashboard with gunicorn (production)
echo "📊 Starting Web Dashboard on port $PORT..."
gunicorn web_dashboard:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
