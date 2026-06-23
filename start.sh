#!/bin/bash
# Start script for Replit / any deployment platform

export PORT=${PORT:-8000}
python -m uvicorn main:app --host 0.0.0.0 --port $PORT --reload
