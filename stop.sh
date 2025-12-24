#!/bin/bash

# Search Service - Stop Script

SERVICE_NAME="search_service"
PID_FILE=".${SERVICE_NAME}.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ $SERVICE_NAME is not running (no PID file found)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠️  $SERVICE_NAME is not running (PID $PID not found)"
    rm "$PID_FILE"
    exit 1
fi

echo "🛑 Stopping $SERVICE_NAME (PID: $PID)..."

# Try graceful shutdown first
kill "$PID"

# Wait for process to stop (max 10 seconds)
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ $SERVICE_NAME stopped successfully"
        rm "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if still running
echo "⚠️  Force killing $SERVICE_NAME..."
kill -9 "$PID"
sleep 1

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ $SERVICE_NAME stopped (forced)"
    rm "$PID_FILE"
    exit 0
else
    echo "❌ Failed to stop $SERVICE_NAME"
    exit 1
fi
