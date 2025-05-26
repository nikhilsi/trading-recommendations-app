# Trading App Scripts

This directory contains utility scripts for development, production, and maintenance tasks.

## Development Scripts (`scripts/dev/`)

### Quick Actions
```bash
# Complete reset and rebuild (your main request!)
./scripts/dev/reset.sh

# Quick restart without rebuild
./scripts/dev/quick-restart.sh

# Check overall system status
./scripts/dev/status.sh
```

### Debugging & Logs
```bash
# View backend logs (follow mode)
./scripts/dev/logs.sh backend

# View frontend logs
./scripts/dev/logs.sh frontend

# View all logs
./scripts/dev/logs.sh all
```

### Testing & Cleanup
```bash
# Test all API endpoints
./scripts/dev/test-api.sh

# Clean up development artifacts
./scripts/dev/cleanup.sh

# Access database shell
./scripts/dev/db-shell.sh
```

## Production Scripts (`scripts/production/`)

### Deployment
```bash
# Production deployment
./scripts/production/deploy.sh

# Create data backup
./scripts/production/backup.sh

# Monitor production services
./scripts/production/monitor.sh
```

## Maintenance Scripts (`scripts/maintenance/`)

### Code Maintenance
```python
# Enhanced codebase cleanup
python scripts/maintenance/cleanup_codebase.py

# Database maintenance
python scripts/maintenance/database_maintenance.py

# Check for outdated dependencies
python scripts/maintenance/check_dependencies.py
```

## Usage Examples

### Most Common Workflows

**When something is broken:**
```bash
./scripts/dev/reset.sh        # Nuclear option - complete rebuild
./scripts/dev/status.sh       # Check what's wrong
./scripts/dev/logs.sh backend # Debug the issue
```

**Daily development:**
```bash
./scripts/dev/quick-restart.sh  # Restart after code changes
./scripts/dev/test-api.sh       # Test your changes
./scripts/dev/status.sh         # Verify everything works
```

**Weekly maintenance:**
```bash
python scripts/maintenance/cleanup_codebase.py      # Clean up files
python scripts/maintenance/database_maintenance.py  # Optimize database
python scripts/maintenance/check_dependencies.py    # Update packages
```

## Script Features

- **Color-coded output** for easy reading
- **Error handling** with helpful messages
- **Progress indicators** for long-running tasks
- **Health checks** to verify success
- **Automatic cleanup** of temporary resources

## Requirements

- Docker and docker-compose
- Python 3.11+
- curl (for API testing)
- bash shell

## Customization

Each script can be customized by editing the variables at the top of the file. Common customizations:

- Change port numbers
- Modify timeout values
- Add additional health checks
- Include custom cleanup patterns

## Quick Reference

| Task | Command |
|------|---------|
| 🔄 **Complete Reset** | `./scripts/dev/reset.sh` |
| ⚡ **Quick Restart** | `./scripts/dev/quick-restart.sh` |
| 📊 **Check Status** | `./scripts/dev/status.sh` |
| 📋 **View Logs** | `./scripts/dev/logs.sh backend` |
| 🧪 **Test API** | `./scripts/dev/test-api.sh` |
| 🧹 **Cleanup** | `./scripts/dev/cleanup.sh` |

## Troubleshooting

**If scripts don't run:**
```bash
# Make sure they're executable
chmod +x scripts/dev/*.sh
chmod +x scripts/production/*.sh
```

**If you get "command not found":**
```bash
# Run from the main trading-app directory
cd /path/to/trading-app
./scripts/dev/reset.sh
```