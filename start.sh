#!/bin/bash

# Start the automation loop in the background
echo "🚀 Starting Moltbook Automation Engine..."
python moltbook_engage.py &

# Start the web dashboard in the foreground
echo "📊 Starting Web Dashboard on port 5000..."
python web_dashboard.py
