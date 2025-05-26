# scripts/dev/status.sh
#!/bin/bash
# Comprehensive status check

echo "🏥 Trading App - Health Check"
echo "============================="

echo "📊 Container Status:"
docker-compose ps

echo ""
echo "🔧 Service Health Checks:"

# Backend health
echo -n "Backend API: "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

# Frontend check
echo -n "Frontend: "
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Accessible"
else
    echo "❌ Not accessible"
fi

# Database check
echo -n "Database: "
if docker-compose exec postgres pg_isready -q 2>/dev/null; then
    echo "✅ Connected"
else
    echo "❌ Connection failed"
fi

echo ""
echo "📈 Quick API Test:"
curl -s "http://localhost:8000/api/stats" | python -m json.tool 2>/dev/null || echo "❌ API not responding"

echo ""
echo "🔗 Quick Links:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000/health"
