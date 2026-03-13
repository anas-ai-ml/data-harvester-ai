@echo off
REM Data Harvester Docker Deployment Script for Windows
REM This script helps deploy the data harvester using Docker

echo 🐳 Data Harvester Docker Deployment
echo ==================================

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found!
    echo Please copy env.template to .env and configure your API keys:
    echo copy env.template .env
    pause
    exit /b 1
)

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed!
    echo Please install Docker first: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed!
    echo Please install Docker Compose first: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Build and start services
echo 🔨 Building Docker image...
docker-compose build

if %errorlevel% neq 0 (
    echo ❌ Docker build failed!
    pause
    exit /b 1
)

echo 🚀 Starting services...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start services!
    pause
    exit /b 1
)

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak

REM Check service status
echo 📊 Checking service status...
docker-compose ps

REM Show logs
echo 📋 Showing recent logs...
docker-compose logs --tail=50 data-harvester

echo.
echo 🎉 Deployment complete!
echo =====================
echo Data Harvester is running at: http://localhost:8000
echo Redis is available at: localhost:6379
echo PostgreSQL is available at: localhost:5432
echo.
echo Useful commands:
echo   View logs: docker-compose logs -f data-harvester
echo   Stop services: docker-compose down
echo   Restart services: docker-compose restart
echo   Access container: docker-compose exec data-harvester bash
echo.
pause
