# Trading Intelligence Platform - Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Authentication System](#authentication-system)
3. [API Reference](#api-reference)
4. [Database Schema](#database-schema)
5. [Frontend Architecture](#frontend-architecture)
6. [Security Considerations](#security-considerations)
7. [Deployment Guide](#deployment-guide)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React)                          │
│  - Authentication (JWT)                                     │
│  - Market Scanner/Screener                                  │
│  - AI Recommendations                                       │
│  - User Dashboard                                           │
│  - Admin Panel                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                      HTTPS + JWT Auth
                            │
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  - JWT Authentication & Authorization                       │
│  - RESTful API                                              │
│  - WebSocket Support (future)                               │
│  - Email Service                                            │
│  - Rate Limiting                                            │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                             │
│  - RecommendationService                                    │
│  - MarketDataService (Polygon/Yahoo)                        │
│  - TechnicalAnalysisService                                 │
│  - DatabaseService                                          │
│  - EmailService                                             │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│              Data Layer (PostgreSQL + Redis)                │
│  - User data with row-level security                        │
│  - Watchlists (per user)                                    │
│  - Recommendations (per user)                               │
│  - Session management                                       │
│  - Rate limiting                                            │
└─────────────────────────────────────────────────────────────┘
```

## Authentication System

### Overview
The platform uses JWT-based authentication with refresh tokens and an invite-only registration system.

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: Enter invite code + credentials
    Frontend->>Backend: POST /auth/register
    Backend->>Database: Validate invite code
    Backend->>Database: Create user
    Backend->>Frontend: Return JWT tokens
    Frontend->>Frontend: Store tokens
    Frontend->>Backend: API requests with Bearer token
    Backend->>Backend: Validate JWT
    Backend->>Frontend: Return data
```

### Token Management

#### Access Token
- **Lifetime**: 15 minutes
- **Purpose**: API authentication
- **Storage**: Memory/Redux (not localStorage for security)
- **Refresh**: Automatic using refresh token

#### Refresh Token
- **Lifetime**: 7 days
- **Purpose**: Get new access tokens
- **Storage**: httpOnly cookie (recommended) or secure storage
- **Revocation**: On logout or password change

### Security Features
- Password requirements: 8+ chars, 1 number, 1 special char
- Bcrypt password hashing
- Invite codes expire after 7 days
- Session tracking with IP and user agent
- Automatic token refresh with axios interceptors

## API Reference

### Authentication Endpoints

#### Register New User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "invite_code": "ABC12345"
}

Response: {
  "access_token": "eyJ...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

#### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "..."
}
```

### Protected Endpoints

All endpoints require `Authorization: Bearer <token>` header.

#### Watchlist Management
```http
GET /api/watchlist - Get user's watchlist
POST /api/watchlist - Add symbol
DELETE /api/watchlist/{symbol} - Remove symbol
```

#### Recommendations
```http
GET /api/recommendations?confidence_threshold=50&max_recommendations=5
GET /api/recommendations/history?limit=50
```

#### Market Scanner (Public)
```http
GET /api/market/scan?scan_type=momentum&limit=15
POST /api/market/screen - Advanced screening with filters
```

### Admin Endpoints

Requires `is_admin=true` on user account.

```http
POST /auth/invites - Create invite
GET /auth/invites - List invites
DELETE /auth/invites/{id} - Revoke invite
```

## Database Schema

### Core Tables

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    email_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMP
);
```

#### watchlist (Multi-tenant)
```sql
CREATE TABLE watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(10) NOT NULL,
    user_id UUID REFERENCES users(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(user_id, symbol)
);
```

#### invites
```sql
CREATE TABLE invites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(32) UNIQUE NOT NULL,
    email VARCHAR(255),
    created_by UUID REFERENCES users(id),
    used_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    notes TEXT
);
```

### Data Isolation
- All user-specific tables include `user_id` foreign key
- API endpoints filter by authenticated user's ID
- Row-level security prevents cross-user data access

## Frontend Architecture

### Component Structure
```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.js
│   │   ├── RegisterForm.js
│   │   └── ChangePassword.js
│   ├── admin/
│   │   ├── AdminPanel.js
│   │   └── InviteManager.js
│   ├── market-scanner/
│   ├── recommendations/
│   └── common/
├── contexts/
│   └── AuthContext.js
├── hooks/
│   ├── useAuth.js
│   ├── useMarketScanner.js
│   └── useRecommendations.js
└── pages/
    └── LoginPage.js
```

### Auth Context
```javascript
const AuthContext = {
  user: User | null,
  isAuthenticated: boolean,
  loading: boolean,
  login: (email, password) => Promise<Result>,
  register: (email, password, inviteCode) => Promise<Result>,
  logout: () => void,
  refreshAccessToken: () => Promise<string>
}
```

### Protected Routes
```javascript
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) return <LoadingSpinner />;
  if (!isAuthenticated) return <Navigate to="/login" />;
  
  return children;
}
```

## Security Considerations

### Best Practices Implemented
1. **JWT Security**
   - Short-lived access tokens (15 min)
   - Refresh token rotation
   - Token blacklisting on logout

2. **Password Security**
   - Bcrypt hashing with salt rounds
   - Complexity requirements enforced
   - Password change revokes all sessions

3. **API Security**
   - CORS properly configured
   - Rate limiting per user/endpoint
   - Input validation with Pydantic
   - SQL injection prevention with ORM

4. **Data Protection**
   - User data isolation
   - HTTPS enforced in production
   - Sensitive data not logged
   - Secure session management

### Security Checklist
- [ ] Change SECRET_KEY in production
- [ ] Use HTTPS in production
- [ ] Configure proper CORS origins
- [ ] Enable rate limiting
- [ ] Set secure cookie flags
- [ ] Implement CSRF protection
- [ ] Regular security audits
- [ ] Monitor for suspicious activity

## Deployment Guide

### Environment Variables
```env
# Required
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-production-secret-key-min-32-chars
POLYGON_API_KEY=your-polygon-api-key

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=app-specific-password

# Security
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com
```

### Docker Production Build
```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER nobody
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Database Migrations
```bash
# Run migrations in production
docker exec -it backend alembic upgrade head

# Create backup before migrations
docker exec postgres pg_dump -U user dbname > backup.sql
```

### Monitoring
- Health check endpoint: `/health`
- Metrics endpoint: `/metrics` (coming soon)
- Log aggregation with ELK stack
- Error tracking with Sentry

### Scaling Considerations
1. **Database**: Use read replicas for heavy queries
2. **Caching**: Redis for session and API responses
3. **Load Balancing**: Nginx with multiple backend instances
4. **Background Jobs**: Celery for email and heavy processing
5. **CDN**: Static assets and API caching

## API Rate Limits

### Default Limits (Free Tier)
- Market scans: 50/day
- Screener: 20/day with 3 filters max
- Recommendations: 100/day
- API calls: 60/hour

### Premium Limits
- Market scans: 500/day
- Screener: Unlimited with unlimited filters
- Recommendations: 1000/day
- API calls: 600/hour

### Enterprise
- All limits removed
- Priority API access
- Dedicated support

---

For more information, see:
- [README.md](README.md) - Getting started
- [ROADMAP.md](ROADMAP.md) - Future development plans
- [API Docs](http://localhost:8000/docs) - Interactive API documentation