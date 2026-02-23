#!/bin/bash
# Railway start script for CyberTrace Backend

# Use PORT from Railway environment or default to 8000
PORT="${PORT:-8000}"

echo "Starting CyberTrace API on port $PORT..."

# Start FastAPI with Uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
