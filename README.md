# Trading Intelligence Platform

A professional, invite-only stock trading platform with real-time market scanning, AI-powered recommendations, and advanced technical analysis.

## 🚀 Features

### Core Features
- **🔍 Market Scanner**: Analyze 8,000+ stocks in real-time
- **🤖 AI Recommendations**: Intelligent trading signals based on technical analysis
- **📊 Advanced Screener**: Professional filters for price, volume, and technical indicators
- **📈 User Watchlists**: Personalized stock monitoring
- **🔐 Secure Authentication**: JWT-based auth with invite-only registration
- **👥 Multi-User Support**: Individual user data isolation
- **🎨 Professional UI**: Responsive React dashboard with Tailwind CSS

### Technical Capabilities
- Real-time market data from Polygon.io (8,000+ stocks)
- Fallback to Yahoo Finance for free tier
- Technical indicators (RSI, SMA, momentum)
- Volume analysis and unusual activity detection
- Historical data tracking and persistence
- Email notifications for invites

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database with full user isolation
- **Redis** - Caching and session management
- **SQLAlchemy** - ORM with migrations
- **JWT** - Secure authentication
- **Docker** - Containerized deployment

### Frontend
- **React 18** - UI framework
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client
- **Context API** - State management
- **Lucide Icons** - Beautiful icons

### Data Providers
- **Polygon.io** - Professional market data ($29/month)
- **Yahoo Finance** - Free fallback provider

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Polygon.io API key (recommended) or use Yahoo Finance fallback
- Gmail account for sending invites (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/nikhilsi/trading-intelligence.git
cd trading-intelligence
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Run database migrations**
```bash
# First, start the database
docker-compose up -d postgres

# Apply authentication migration
docker-compose exec postgres psql -U trading_user -d trading_app < database/migrations/001_add_authentication.sql
```

4. **Create admin user and initial invites**
```bash
# Start all services
docker-compose up -d

# Run setup script
docker-compose exec backend python app/setup_auth.py
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📧 Email Configuration (Optional)

To enable email invitations, add these to your `.env`:

```env
# Gmail SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Trading Intelligence
APP_URL=http://localhost:3000
```

### Getting Gmail App Password:
1. Go to https://myaccount.google.com/security
2. Enable 2-factor authentication
3. Go to "App passwords"
4. Generate a password for "Mail"
5. Use that password as SMTP_PASSWORD

## 👤 User Management

### Creating Users
This is an invite-only platform. To create new users:

1. **As Admin**: 
   - Login to the platform
   - Click "Admin" button
   - Go to Invites tab
   - Click "Create Invite"
   - Share the 8-character code

2. **Via API**:
```bash
curl -X POST http://localhost:8000/auth/invites \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"expires_in_days": 7, "email": "newuser@example.com"}'
```

### User Tiers
- **Free**: 20 stocks watchlist, 50 scans/day
- **Premium**: Coming soon
- **Enterprise**: Unlimited everything (admin users)

## 📚 API Usage

### Authentication Required Endpoints

All `/api/*` endpoints now require authentication except market scanning:

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use the token
curl http://localhost:8000/api/watchlist \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Public Endpoints
- `POST /auth/register` - Register with invite code
- `POST /auth/login` - Login
- `GET /api/market/scan` - Market scanner (works without auth)
- `GET /health` - Health check

## 🔧 Development

### Running Locally
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Restart after code changes
docker-compose restart backend

# Run database shell
docker-compose exec postgres psql -U trading_user -d trading_app
```

### Project Structure
```
trading-intelligence/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── core/         # Auth, config, security
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── contexts/     # Auth context
│   │   ├── hooks/        # Custom hooks
│   │   └── pages/        # Page components
├── database/
│   └── migrations/       # SQL migrations
└── scripts/              # Utility scripts
```

## 🐛 Troubleshooting

### Authentication Issues
```bash
# Reset admin password
docker-compose exec backend python
>>> from models.database import SessionLocal
>>> from models.auth import User
>>> from core.security import get_password_hash
>>> db = SessionLocal()
>>> admin = db.query(User).filter(User.email == "admin@example.com").first()
>>> admin.password_hash = get_password_hash("newpassword")
>>> db.commit()
```

### Database Issues
```bash
# Complete database reset
docker-compose down -v
docker-compose up -d
# Re-run migrations and setup
```

### Port Conflicts
```bash
# Change ports in docker-compose.yml
# Frontend: 3000 → 3001
# Backend: 8000 → 8001
# Database: 5432 → 5433
```

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Polygon.io](https://polygon.io) for professional market data
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent framework
- [React](https://reactjs.org/) for the frontend framework

## ⚠️ Disclaimer

This platform is for educational and research purposes only. Trading involves substantial risk and may not be suitable for all investors. Always conduct your own research and consider your risk tolerance before making investment decisions.

---

Built with ❤️ by Nikhil Singhal