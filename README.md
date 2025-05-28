# SalesOptimizer 🚀

A multi-tenant sales optimization platform with predictive analytics, built using Domain-Driven Design (DDD) principles.

## 🎯 Project Overview

SalesOptimizer is a comprehensive sales management platform that leverages machine learning to predict opportunity success rates and optimize sales processes across multiple organizations. The system provides role-based access control with predictive analytics capabilities.

## 🛠️ Technology Stack

### Backend
- **Framework**: Python FastAPI with Pydantic
- **Architecture**: Domain-Driven Design (DDD)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for session management and caching
- **ML/Analytics**: scikit-learn, pandas, numpy
- **Authentication**: JWT with refresh tokens
- **Type Safety**: Strict Pydantic models and type hints
- **Message Queue**: Celery with Redis broker
- **Testing**: pytest with 90%+ coverage

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript with strict mode
- **Architecture**: Component-based with feature modules
- **State Management**: Zustand + React Query (TanStack Query)
- **UI Components**: shadcn/ui + Tailwind CSS
- **Charts**: Recharts for analytics visualization
- **PWA**: Progressive Web App with service workers
- **Push Notifications**: Web Push API integration

### Infrastructure
- **Containerization**: Docker multi-stage builds
- **Database**: PostgreSQL 15+ with connection pooling
- **Cache**: Redis 7+ for sessions and real-time data
- **CI/CD**: GitHub Actions with automated testing
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured logging with Python logging

## 🏗️ Project Structure

```
salesoptimizer/
├── backend/                     # FastAPI Python Backend
│   ├── app/
│   │   ├── domain/             # DDD Domain Layer
│   │   │   ├── organization/
│   │   │   ├── sales/
│   │   │   ├── analytics/
│   │   │   ├── tasks/
│   │   │   └── notifications/
│   │   ├── application/        # Application Layer
│   │   │   ├── services/
│   │   │   ├── handlers/
│   │   │   └── dto/
│   │   ├── infrastructure/     # Infrastructure Layer
│   │   │   ├── database/
│   │   │   ├── external/
│   │   │   └── messaging/
│   │   └── presentation/       # API Layer
│   │       ├── api/
│   │       ├── middleware/
│   │       └── schemas/
│   ├── tests/
│   ├── alembic/               # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Next.js React Frontend
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   ├── components/        # Reusable UI components
│   │   │   ├── ui/           # Base UI components
│   │   │   ├── forms/        # Form components
│   │   │   ├── charts/       # Chart components
│   │   │   └── layout/       # Layout components
│   │   ├── features/          # Feature-based modules
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── sales/
│   │   │   ├── analytics/
│   │   │   ├── tasks/
│   │   │   └── admin/
│   │   ├── lib/              # Utilities and configurations
│   │   ├── hooks/            # Custom React hooks
│   │   ├── store/            # State management
│   │   └── types/            # TypeScript type definitions
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md
│   ├── FEATURES.md
│   ├── DEVELOPMENT.md
│   ├── API.md
│   ├── ROADMAP.md
│   └── DEPLOYMENT.md
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/max31337/salesoptimizer.git
cd salesoptimizer
```

2. **Start with Docker Compose**
```bash
# Development environment
docker-compose up --build

# Or run services individually
docker-compose up postgres redis -d
```

3. **Backend Setup**
```bash
on root directory 
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Frontend Setup**
```bash
cd web
npm install

# Set up environment variables
cp .env.example .env.local

# Start Next.js development server
npm run dev
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Database Admin: Connect to postgres://localhost:5432

## 🔧 Available Scripts

### Backend
```bash
# Development
uvicorn app.main:app --reload

# Testing
pytest --cov=app tests/

# Type checking
mypy app/

# Code formatting
black app/ && isort app/

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend
```bash
# Development
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint

# Testing
npm run test
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [Architecture](docs/ARCHITECTURE.md) | System design, DDD structure, database schema |
| [Features](docs/FEATURES.md) | Detailed feature specifications and user roles |
| [Development](docs/DEVELOPMENT.md) | Setup, coding standards, testing guidelines |
| [API Documentation](docs/API.md) | REST API endpoints and examples |
| [Roadmap](docs/ROADMAP.md) | Development phases and timeline |
| [Deployment](docs/DEPLOYMENT.md) | Production deployment guide |

## 🎯 Key Features

- **Multi-tenant Architecture**: Secure organization isolation
- **Role-based Access Control**: Super Admin, Org Admin, Manager, Sales Rep
- **Predictive Analytics**: ML-powered opportunity success prediction
- **Real-time Notifications**: Web push notifications and live updates
- **Advanced Task Management**: Collaborative and private task systems
- **Progressive Web App**: Offline capabilities and native-like experience
- **CSV Data Import**: Bulk data operations with validation
- **Comprehensive Analytics**: Dashboard with interactive charts

## 🔐 Security Features

- JWT authentication with refresh tokens
- Multi-tenant data isolation
- Role-based permission system
- SQL injection prevention with ORM
- CORS and security headers
- Input validation with Pydantic
- Rate limiting and request throttling

## 🧪 Testing

- **Backend**: pytest with 90%+ coverage, integration tests
- **Frontend**: Jest + React Testing Library
- **E2E**: Playwright for critical user journeys
- **API**: Automated API testing with FastAPI TestClient

## 📈 Performance

- **Backend**: <100ms API response times
- **Frontend**: Lighthouse score >90
- **Database**: Optimized queries with proper indexing
- **Caching**: Redis for session and query caching
- **CDN**: Static asset optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Follow the coding standards in [DEVELOPMENT.md](docs/DEVELOPMENT.md)
4. Write tests for new functionality
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- 📧 Email: support@salesoptimizer.com
- 📝 Issues: [GitHub Issues](https://github.com/max31337/salesoptimizer/issues)
- 📖 Documentation: [Project Wiki](https://github.com/max31337/salesoptimizer/wiki)

---

**Built with ❤️ by Max31337**

*Transforming sales through intelligent predictions and modern architecture.*