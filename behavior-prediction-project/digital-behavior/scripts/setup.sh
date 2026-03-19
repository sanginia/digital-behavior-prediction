#!/bin/bash

# Digital Behavior Prediction - Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "================================"
echo "Digital Behavior Prediction - Setup"
echo "================================"
echo

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "  Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "  Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "  Creating .env file..."
    cp .env.example .env
    echo "  ⚠ Please update backend/.env with your database credentials"
fi

cd ..

# Frontend setup
echo
echo "📦 Setting up frontend..."
cd frontend

# Install dependencies
echo "  Installing Node.js dependencies..."
npm install --silent

# Create .env file if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "  Creating .env.local file..."
    cp .env.example .env.local
fi

cd ..

# Extension setup
echo
echo "📦 Setting up Chrome extension..."
cd extension

# Install dependencies
echo "  Installing Node.js dependencies..."
npm install --silent

# Build extension
echo "  Building extension..."
npm run build

cd ..

echo
echo "================================"
echo "✓ Setup completed!"
echo "================================"
echo
echo "Next steps:"
echo "  1. Update backend/.env with your database URL"
echo "  2. Start the services:"
echo "     - With Docker: docker-compose up"
echo "     - Without Docker:"
echo "       - Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "       - Frontend: cd frontend && npm run dev"
echo "  3. Load the extension in Chrome:"
echo "     - Open chrome://extensions/"
echo "     - Enable Developer mode"
echo "     - Click 'Load unpacked'"
echo "     - Select the extension/dist folder"
echo
