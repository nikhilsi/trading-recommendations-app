# scripts/dev/logs.sh
#!/bin/bash
# View logs for different services

SERVICE=${1:-backend}

case $SERVICE in
    "backend"|"be")
        echo "📋 Backend Logs (last 20 lines, following):"
        docker-compose logs backend -f --tail=20
        ;;
    "frontend"|"fe")
        echo "📋 Frontend Logs (last 20 lines, following):"
        docker-compose logs frontend -f --tail=20
        ;;
    "db"|"database")
        echo "📋 Database Logs (last 20 lines, following):"
        docker-compose logs postgres -f --tail=20
        ;;
    "all")
        echo "📋 All Service Logs (last 10 lines each, following):"
        docker-compose logs -f --tail=10
        ;;
    *)
        echo "📋 Usage: ./logs.sh [backend|frontend|db|all]"
        echo "   backend/be  - Backend service logs"
        echo "   frontend/fe - Frontend service logs"
        echo "   db/database - Database service logs"
        echo "   all         - All service logs"
        ;;
esac