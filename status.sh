#!/bin/bash

# Search Service - Status Script

SERVICE_NAME="search_service"
PORT=8011
PID_FILE=".${SERVICE_NAME}.pid"

echo "📊 $SERVICE_NAME Status"
echo "================================"

if [ ! -f "$PID_FILE" ]; then
    echo "Status: ❌ Not Running"
    echo "PID File: Not found"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "Status: ✅ Running"
    echo "PID: $PID"
    echo "Port: $PORT"
    
    # Get memory and CPU usage
    MEM=$(ps -p "$PID" -o rss= | awk '{printf "%.1f MB\n", $1/1024}')
    CPU=$(ps -p "$PID" -o %cpu= | awk '{print $1"%"}')
    UPTIME=$(ps -p "$PID" -o etime= | awk '{print $1}')
    
    echo "Memory: $MEM"
    echo "CPU: $CPU"
    echo "Uptime: $UPTIME"
    
    # Check if port is listening
    if command -v lsof > /dev/null 2>&1; then
        if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "Port $PORT: ✅ Listening"
        else
            echo "Port $PORT: ⚠️  Not listening"
        fi
    fi
    
    echo ""
    echo "API Docs: http://localhost:$PORT/docs"
    echo "Health Check: http://localhost:$PORT/health"
else
    echo "Status: ❌ Not Running"
    echo "PID File: Found (stale)"
    echo "PID: $PID (process not found)"
    exit 1
fi
