# scripts/dev/cleanup.sh
#!/bin/bash
# Clean up development artifacts

echo "🧹 Trading App - Development Cleanup"
echo "===================================="

echo "1️⃣ Stopping containers..."
docker-compose down

echo "2️⃣ Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "3️⃣ Removing .pyc files..."
find . -name "*.pyc" -delete 2>/dev/null || true

echo "4️⃣ Removing temporary files..."
find . -name "*~" -delete 2>/dev/null || true
find . -name "*.tmp" -delete 2>/dev/null || true

echo "5️⃣ Removing old backup files..."
find . -name "*_backup*" -type f -delete 2>/dev/null || true
find . -name "*_old*" -type f -delete 2>/dev/null || true

echo "6️⃣ Cleaning Docker resources..."
docker system prune -f

echo "✅ Cleanup complete!"
