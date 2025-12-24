#!/bin/bash

# Search Service - Start Script
# Port: 8011

SERVICE_NAME="search_service"
PORT=8011
PID_FILE=".${SERVICE_NAME}.pid"
LOG_FILE="logs/${SERVICE_NAME}.log"

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if service is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "❌ $SERVICE_NAME is already running (PID: $PID)"
        exit 1
    else
        echo "⚠️  Removing stale PID file"
        rm "$PID_FILE"
    fi
fi

echo "🚀 Starting $SERVICE_NAME on port $PORT..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi

# Start the service
nohup uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --reload \
    > "$LOG_FILE" 2>&1 &

PID=$!
echo $PID > "$PID_FILE"

# Wait a moment and check if process started successfully
sleep 2

if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ $SERVICE_NAME started successfully"
    echo "   PID: $PID"
    echo "   Port: $PORT"
    echo "   Logs: $LOG_FILE"
    echo "   API Docs: http://localhost:$PORT/docs"
else
    echo "❌ Failed to start $SERVICE_NAME"
    rm "$PID_FILE"
    exit 1
fi
