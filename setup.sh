#!/bin/bash

# Healthcare Voice AI - Setup Script
# This script helps set up the development environment for new contributors

set -e

echo "🏥 Healthcare Voice AI - Setup Script"
echo "===================================="

# Check if Python 3.9+ is installed
echo "🔍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION is installed, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION is installed"

# Check if Docker is installed
echo "🔍 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker and Docker Compose."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Check if Node.js is installed (for frontend)
echo "🔍 Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is not installed. Frontend development will not be available."
    echo "   Please install Node.js 16+ for frontend development."
else
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION is installed"
fi

# Create .env file if it doesn't exist
echo "🔧 Setting up environment configuration..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "📝 Please edit .env file with your actual configuration values"
    else
        echo "❌ .env.example file not found"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if [ -f pyproject.toml ]; then
    pip install -e ".[dev]"
    echo "✅ Python dependencies installed"
else
    echo "❌ pyproject.toml not found"
    exit 1
fi

# Install frontend dependencies if Node.js is available
if command -v node &> /dev/null && [ -d "frontend" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs uploads temp quarantine backups
echo "✅ Directories created"

# Set up pre-commit hooks if available
echo "🔧 Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "✅ Pre-commit hooks installed"
else
    echo "⚠️  Pre-commit not available, skipping hook installation"
fi

# Set up database
echo "🗄️ Setting up database..."
if [ -f "dental_voice_ai.db" ]; then
    echo "⚠️  Database file already exists. Skipping database setup."
    echo "   Use 'make db-reset' to reset the database if needed."
else
    echo "🏗️ Creating initial database schema..."
    python3 -m alembic upgrade head
    echo "✅ Database schema created"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your actual configuration values"
echo "2. Run 'make dev' to start the development environment"
echo "3. Visit http://localhost:8000 for the API"
echo "4. Visit http://localhost:3000 for the frontend (if available)"
echo ""
echo "Available commands:"
echo "  make help     - Show all available commands"
echo "  make dev      - Start development environment"
echo "  make test     - Run tests"
echo "  make lint     - Run linting"
echo "  make format   - Format code"
echo ""
echo "For more information, see README.md"
