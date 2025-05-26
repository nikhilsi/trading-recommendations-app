# scripts/production/backup.sh
#!/bin/bash
# Backup production data

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "💾 Trading App - Data Backup"
echo "==========================="

echo "1️⃣ Creating database backup..."
docker-compose exec postgres pg_dump -U trading_user trading_app > "$BACKUP_DIR/database.sql"

echo "2️⃣ Backing up configuration..."
cp .env "$BACKUP_DIR/env_backup"
cp docker-compose.yml "$BACKUP_DIR/"

echo "3️⃣ Creating archive..."
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "✅ Backup created: $BACKUP_DIR.tar.gz"
