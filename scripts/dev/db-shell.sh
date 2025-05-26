# scripts/dev/db-shell.sh
#!/bin/bash
# Connect to database shell

echo "🗄️ Connecting to PostgreSQL database..."
docker-compose exec postgres psql -U trading_user -d trading_app

