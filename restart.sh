#!/bin/bash

# Search Service - Restart Script

SERVICE_NAME="search_service"

echo "🔄 Restarting $SERVICE_NAME..."
echo ""

# Stop the service
if [ -f "stop.sh" ]; then
    ./stop.sh
    echo ""
fi

# Wait a moment
sleep 2

# Start the service
if [ -f "start.sh" ]; then
    ./start.sh
else
    echo "❌ start.sh not found"
    exit 1
fi
