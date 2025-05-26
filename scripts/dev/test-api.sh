# scripts/dev/test-api.sh
#!/bin/bash
# Test API endpoints

echo "🧪 Trading App - API Testing"
echo "============================"

BASE_URL="http://localhost:8000"

echo "1️⃣ Testing health endpoint..."
curl -s "$BASE_URL/health" | python -m json.tool

echo ""
echo "2️⃣ Testing watchlist..."
curl -s "$BASE_URL/api/watchlist" | python -m json.tool

echo ""
echo "3️⃣ Testing stats..."
curl -s "$BASE_URL/api/stats" | python -m json.tool

echo ""
echo "4️⃣ Testing recommendations (low confidence for speed)..."
curl -s "$BASE_URL/api/recommendations?confidence_threshold=20&max_recommendations=2" | python -m json.tool

echo ""
echo "✅ API testing complete!"
