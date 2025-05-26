# scripts/dev/reset.sh
#!/bin/bash
# Complete reset and rebuild script

echo "🔄 Trading App - Complete Reset & Rebuild"
echo "========================================"

echo "1️⃣ Stopping all containers..."
docker-compose down

echo "2️⃣ Cleaning up Docker resources..."
docker system prune -f
docker volume prune -f

echo "3️⃣ Removing specific images..."
docker rmi trading-app-backend trading-app-frontend 2>/dev/null || echo "Images not found"

echo "4️⃣ Rebuilding containers..."
docker-compose build --no-cache

echo "5️⃣ Starting services..."
docker-compose up -d

echo "6️⃣ Waiting for services to start..."
sleep 10

echo "7️⃣ Checking service status..."
docker-compose ps

echo "✅ Reset complete! Services should be running."
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"