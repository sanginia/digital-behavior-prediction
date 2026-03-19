#!/bin/bash

# Digital Behavior Prediction - Development Runner
# Starts all services for local development

set -e

echo "================================"
echo "Digital Behavior Prediction - Dev Mode"
echo "================================"
echo

# Check if Docker is available
if command -v docker-compose &> /dev/null; then
    echo "🐳 Starting with Docker Compose..."
    docker-compose up
else
    echo "Docker Compose not found. Starting services manually..."
    echo

    # Start backend
    echo "🚀 Starting backend..."
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..

    # Start frontend
    echo "🚀 Starting frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..

    # Trap SIGINT and SIGTERM to kill background processes
    trap "kill $BACKEND_PID $FRONTEND_PID" SIGINT SIGTERM

    echo
    echo "Services started:"
    echo "  Backend:  http://localhost:8000"
    echo "  Frontend: http://localhost:3000"
    echo
    echo "Press Ctrl+C to stop all services"

    # Wait for background processes
    wait
fi
