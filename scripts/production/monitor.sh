# scripts/production/monitor.sh
#!/bin/bash
# Production monitoring script

echo "📊 Trading App - Production Monitoring"
echo "======================================"

while true; do
    clear
    echo "🕐 $(date)"
    echo "=================="
    
    echo "📈 Container Stats:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    
    echo ""
    echo "🏥 Health Status:"
    ./scripts/dev/status.sh
    
    echo ""
    echo "📋 Recent Logs (Backend):"
    docker-compose logs backend --tail=5 --since=1m
    
    echo ""
    echo "⏳ Refreshing in 30 seconds... (Ctrl+C to stop)"
    sleep 30
done