#!/bin/bash

# Data Harvester Docker Deployment Script
# This script helps deploy the data harvester using Docker

set -e

echo "🐳 Data Harvester Docker Deployment"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy env.template to .env and configure your API keys:"
    echo "cp env.template .env"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Build and start services
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Show logs
echo "📋 Showing recent logs..."
docker-compose logs --tail=50 data-harvester

echo ""
echo "🎉 Deployment complete!"
echo "====================="
echo "Data Harvester is running at: http://localhost:8000"
echo "Redis is available at: localhost:6379"
echo "PostgreSQL is available at: localhost:5432"
echo ""
echo "Useful commands:"
echo "  View logs: docker-compose logs -f data-harvester"
echo "  Stop services: docker-compose down"
echo "  Restart services: docker-compose restart"
echo "  Access container: docker-compose exec data-harvester bash"
