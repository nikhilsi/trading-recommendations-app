# scripts/production/deploy.sh
#!/bin/bash
# Production deployment script

echo "🚀 Trading App - Production Deployment"
echo "======================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with production configuration"
    exit 1
fi

# Check if API key is set
if ! grep -q "ALPHA_VANTAGE_API_KEY" .env; then
    echo "❌ Error: ALPHA_VANTAGE_API_KEY not found in .env"
    exit 1
fi

echo "1️⃣ Building production images..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

echo "2️⃣ Running database migrations..."
docker-compose exec backend python -c "from models.database import create_tables; create_tables()"

echo "3️⃣ Starting production services..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo "4️⃣ Waiting for services to be ready..."
sleep 15

echo "5️⃣ Running health checks..."
./scripts/dev/status.sh

echo "✅ Production deployment complete!"
