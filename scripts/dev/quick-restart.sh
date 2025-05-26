# scripts/dev/quick-restart.sh
#!/bin/bash
# Quick restart without full rebuild

echo "⚡ Quick Restart - Trading App"
echo "============================="

echo "🛑 Stopping containers..."
docker-compose down

echo "🚀 Starting containers..."
docker-compose up -d

echo "⏳ Waiting for startup..."
sleep 5

echo "📊 Status check..."
docker-compose ps

echo "✅ Quick restart complete!"
