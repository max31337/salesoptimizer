# SalesOptimizer 🚀

A multi-tenant sales optimization platform with predictive analytics, built using Domain-Driven Design (DDD) principles.

## 🎯 Overview

SalesOptimizer leverages machine learning to predict opportunity success rates and optimize sales processes across multiple organizations. Features include role-based access control, real-time analytics, and collaborative task management.

## 🛠️ Tech Stack

**Backend (Root Directory)**
- FastAPI + Python 3.11+
- PostgreSQL + SQLAlchemy
- Redis + Celery
- JWT Authentication

**Frontend (Web Directory)**
- Next.js 14 + TypeScript
- shadcn/ui + Tailwind CSS
- Zustand + React Query
- Progressive Web App

## 🚀 Quick Start

### Prerequisites
- Python 3.11+, Node.js 18+, PostgreSQL 15+, Redis 7+

### Development
```bash
# Clone repository
git clone https://github.com/max31337/salesoptimizer.git
cd salesoptimizer

# Backend setup (root directory)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn api.main:app --reload

# Frontend setup (separate terminal)
cd web
npm install
cp .env.example .env.local
npm run dev
```

### Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design and DDD structure |
| [Features](docs/FEATURES.md) | Feature specifications and user roles |
| [Development](docs/DEVELOPMENT.md) | Setup, coding standards, testing |
| [Roadmap](docs/ROADMAP.md) | Development phases and timeline |
| [Deployment](docs/DEPLOYMENT.md) | Production deployment guide |

## 🔧 Key Commands

```bash
# Backend (root directory)
uvicorn api.main:app --reload        # Development server
pytest tests/ -v                    # Run tests
alembic revision --autogenerate     # Create migration
alembic upgrade head                 # Apply migrations

# Frontend (web directory)
npm run dev                          # Development server
npm run build                        # Production build
npm run test                         # Run tests
npm run lint                         # Code linting
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/name`
3. Follow [development guidelines](docs/DEVELOPMENT.md)
4. Submit pull request

---

**Built with ❤️ by Max31337** | [Support](mailto:navarro.markanthony.tud@gmail.com) | [Issues](https://github.com/max31337/salesoptimizer/issues)