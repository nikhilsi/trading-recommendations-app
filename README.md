# Trading Recommendations App

A professional stock trading recommendations application with real-time market data analysis, technical indicators, and comprehensive database persistence.

## 🚀 Features

- **Real-time Market Data**: Integration with Alpha Vantage API for live stock prices
- **Technical Analysis**: RSI, moving averages, momentum indicators, and volume analysis
- **Smart Recommendations**: AI-powered BUY/SELL signals with confidence scoring
- **Dynamic Controls**: Customizable confidence thresholds and recommendation limits
- **Watchlist Management**: Persistent stock monitoring with database storage
- **Professional UI**: Clean, responsive React dashboard with real-time updates
- **Database Persistence**: Historical recommendation tracking and performance analysis
- **Rate Limiting**: Intelligent API usage optimization with fallback mechanisms

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Python 3.11+**: Latest performance optimizations
- **PostgreSQL**: Robust relational database for data persistence
- **SQLAlchemy**: Professional ORM with migration support
- **Redis**: Caching and session management
- **Pydantic**: Data validation and serialization

### Frontend
- **React 18**: Modern UI framework with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API communication
- **Lucide React**: Beautiful, customizable icons

### Infrastructure
- **Docker**: Containerized deployment
- **Docker Compose**: Multi-service orchestration
- **Nginx**: Reverse proxy and load balancing (production)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER                            │
│  React Dashboard (Port 3000)                                       │
│  ├── Real-time price updates                                        │
│  ├── Dynamic recommendation controls                                │
│  ├── Watchlist management                                           │
│  └── Performance analytics                                          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY LAYER                           │
│  FastAPI Server (Port 8000)                                        │
│  ├── Authentication middleware                                      │
│  ├── Rate limiting                                                  │
│  ├── Input validation                                               │
│  └── Error handling                                                 │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       BUSINESS LOGIC LAYER                         │
│  Services Architecture                                              │
│  ├── RecommendationService (Main orchestrator)                     │
│  ├── MarketDataService (Alpha Vantage integration)                 │
│  ├── TechnicalAnalysisService (Indicators & signals)               │
│  └── DatabaseService (Data persistence)                            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA STORAGE LAYER                         │
│  PostgreSQL Database + Redis Cache                                 │
│  ├── Stock prices and historical data                              │
│  ├── Recommendations and performance tracking                      │
│  ├── User preferences and watchlists                               │
│  └── Technical indicators and analysis results                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Alpha Vantage API key (free tier available)
- 4GB+ RAM recommended

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trading-app
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Alpha Vantage API key
   ```

3. **Start the application**
   ```bash
   # Complete setup (first time)
   ./scripts/dev/reset.sh
   
   # Or quick start
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📚 Usage

### Basic Workflow

1. **Configure Settings**: Adjust confidence threshold and max recommendations
2. **Manage Watchlist**: Add/remove stocks you want to monitor
3. **Generate Recommendations**: Click "Start Analysis" for AI-powered suggestions
4. **Review Results**: Analyze recommendations with detailed reasoning and metrics
5. **Track Performance**: Monitor historical recommendation accuracy

### API Usage

```bash
# Get recommendations
curl "http://localhost:8000/api/recommendations?confidence_threshold=70&max_recommendations=5"

# Manage watchlist
curl -X POST "http://localhost:8000/api/watchlist" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "AAPL"}'

# View statistics
curl "http://localhost:8000/api/stats"
```

## 🛠️ Development

### Project Structure
```
trading-app/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API integration
│   │   └── App.js          # Main application
│   ├── Dockerfile
│   └── package.json
├── database/               # Database initialization
├── scripts/                # Utility scripts
├── docker-compose.yml      # Service orchestration
└── README.md
```

### Development Scripts

```bash
# Complete reset and rebuild
./scripts/dev/reset.sh

# Quick restart after code changes
./scripts/dev/quick-restart.sh

# Check system status
./scripts/dev/status.sh

# View logs
./scripts/dev/logs.sh backend

# Test all APIs
./scripts/dev/test-api.sh
```

See [scripts/README.md](scripts/README.md) for complete documentation.

### Adding New Features

1. **Backend**: Add new services in `backend/app/services/`
2. **API**: Add endpoints in `backend/app/api/`
3. **Frontend**: Add components in `frontend/src/components/`
4. **Database**: Add models in `backend/app/models/`

## 🧪 Testing

```bash
# Test API endpoints
./scripts/dev/test-api.sh

# Manual testing
curl http://localhost:8000/health
```

## 📊 Monitoring

### Health Checks
- Backend Health: http://localhost:8000/health
- Database Status: http://localhost:8000/api/stats
- Service Status: `./scripts/dev/status.sh`

### Performance Metrics
- API Response Times: Built-in FastAPI metrics
- Database Statistics: Available via `/api/stats` endpoint
- Recommendation Accuracy: Historical tracking in database

## 🚀 Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
./scripts/production/deploy.sh
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | Yes | - |
| `DATABASE_URL` | PostgreSQL connection string | No | Auto-generated |
| `REDIS_URL` | Redis connection string | No | Auto-generated |
| `ENVIRONMENT` | Deployment environment | No | `development` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style
- Python: Follow PEP 8, use Black formatter
- JavaScript: Use Prettier formatter
- Commit messages: Use conventional commits format

## 📋 Roadmap

### Current Features ✅
- [x] Real-time market data integration
- [x] Technical analysis and recommendations
- [x] Watchlist management
- [x] Professional UI/UX
- [x] Database persistence
- [x] Docker containerization

### Planned Features 🚧
- [ ] Advanced technical indicators (Bollinger Bands, MACD)
- [ ] Portfolio tracking and performance analysis
- [ ] Email/SMS alerts for high-confidence signals
- [ ] Machine learning prediction models
- [ ] Multi-user support with authentication
- [ ] Mobile app (React Native)
- [ ] Advanced charting and visualization

### Future Enhancements 🔮
- [ ] Options trading analysis
- [ ] Cryptocurrency support
- [ ] Social trading features
- [ ] Advanced risk management tools
- [ ] Integration with brokers for automated trading

## 🐛 Troubleshooting

### Common Issues

**App won't start:**
```bash
./scripts/dev/reset.sh  # Complete reset
```

**API rate limits:**
- Free tier: 25 requests/day
- Premium plans available at Alpha Vantage
- App includes intelligent rate limiting and fallback mechanisms

**Database connection issues:**
```bash
docker-compose logs postgres  # Check database logs
./scripts/dev/status.sh        # Overall health check
```

**Performance issues:**
- Reduce confidence threshold for faster results
- Limit watchlist size
- Check Docker resource allocation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Alpha Vantage](https://www.alphavantage.co/) for market data API
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [React](https://reactjs.org/) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com/) for styling utilities

## 📞 Support

- 📖 Documentation: See [scripts/README.md](scripts/README.md) for utility scripts
- 🐛 Issues: Open an issue on GitHub
- 💬 Discussions: Use GitHub Discussions for questions

---

**⚠️ Disclaimer**: This application is for educational and research purposes only. Trading involves substantial risk and may not be suitable for all investors. Always conduct your own research and consider your risk tolerance before making investment decisions.