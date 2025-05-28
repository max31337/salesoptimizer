# Development Guide

## 🏗️ Project Structure

```
salesoptimizer/
├── api/                    # Backend FastAPI application
├── domain/                 # Domain entities and business logic
├── infrastructure/         # Database, repositories, external services
├── tests/                  # Backend tests
├── alembic/               # Database migrations
├── web/                   # Frontend Next.js application
└── docs/                  # Documentation
```

## 🔧 Development Setup

### Backend Setup (Root Directory)

1. **Python Environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. **Database Setup**
```bash
# Create PostgreSQL database
createdb -U postgres SalesOptimizerDB

# Run migrations
alembic upgrade head

# Start development server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup (Web Directory)

1. **Node.js Environment**
```bash
cd web
npm install
```

2. **Environment Configuration**
```bash
cp .env.example .env.local
# Edit .env.local with API URLs
```

3. **Development Server**
```bash
npm run dev
```

## 🧪 Testing

### Backend Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=. tests/

# Run specific test file
pytest tests/test_api/test_user_routes.py -v

# Run domain tests only
pytest tests/test_domain/ -v

# Run integration tests
pytest tests/test_infrastructure/ -v
```

### Frontend Testing
```bash
cd web

# Run unit tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run E2E tests
npm run test:e2e

# Generate coverage report
npm run test:coverage
```

## 📝 Coding Standards

### Backend Standards

**File Structure**
- Domain entities in `domain/entities/`
- API routes in `api/routes/`
- DTOs in `api/dtos/`
- Database models in `infrastructure/db/models/`
- Repositories in `infrastructure/repositories/`

**Code Style**
```bash
# Format code
black . && isort .

# Type checking
mypy .

# Linting
flake8 .
```

**Naming Conventions**
- Classes: `PascalCase` (e.g., `UserEntity`, `UserRepository`)
- Functions/Variables: `snake_case` (e.g., `get_user_by_id`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_ATTEMPTS`)

### Frontend Standards

**File Structure**
- Components in `src/components/`
- Feature modules in `src/features/`
- Hooks in `src/hooks/`
- Types in `src/types/`

**Code Style**
```bash
# Format and lint
npm run lint:fix
npm run format

# Type checking
npm run type-check
```

**Naming Conventions**
- Components: `PascalCase` (e.g., `UserProfile.tsx`)
- Hooks: `camelCase` with `use` prefix (e.g., `useUserData.ts`)
- Utils: `camelCase` (e.g., `formatCurrency.ts`)
- Types: `PascalCase` (e.g., `UserRole`, `ApiResponse`)

## 🗄️ Database Management

### Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1

# Check current revision
alembic current

# View migration history
alembic history --verbose
```

### Database Seeding
```bash
# Run seed scripts
python scripts/seed_database.py

# Create test data
python scripts/create_test_data.py
```

## 🔍 Debugging

### Backend Debugging
- Set `echo=True` in database engine for SQL logging
- Use FastAPI's automatic interactive docs at `/docs`
- Enable debug logs in `.env`: `LOG_LEVEL=DEBUG`

### Frontend Debugging
- Use React Developer Tools browser extension
- Enable verbose logging: `NEXT_PUBLIC_LOG_LEVEL=debug`
- Use browser network tab for API call inspection

## 🚀 Build and Deployment

### Backend Build
```bash
# Install production dependencies
pip install -r requirements.txt

# Run production server
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Frontend Build
```bash
cd web

# Build for production
npm run build

# Start production server
npm start

# Export static files (if needed)
npm run export
```

## 🔒 Security Guidelines

1. **Environment Variables**
   - Never commit `.env` files
   - Use strong passwords and secrets
   - Rotate JWT secrets regularly

2. **Input Validation**
   - Validate all user inputs with Pydantic
   - Sanitize data before database operations
   - Use parameterized queries

3. **Authentication**
   - Implement proper JWT token validation
   - Use refresh tokens for security
   - Implement rate limiting on auth endpoints

## 📊 Performance Guidelines

### Backend Performance
- Use database indexes for frequently queried fields
- Implement query pagination for large datasets
- Use Redis caching for expensive operations
- Monitor API response times

### Frontend Performance
- Implement lazy loading for routes
- Optimize images and assets
- Use React.memo for expensive components
- Implement proper error boundaries

## 🔧 Git Workflow

1. **Branch Naming**
   - Features: `feature/user-authentication`
   - Bugs: `bugfix/login-validation`
   - Hotfixes: `hotfix/security-patch`

2. **Commit Messages**
   ```
   type(scope): description
   
   Examples:
   feat(auth): add JWT authentication
   fix(api): resolve user creation bug
   docs(readme): update installation guide
   ```

3. **Pull Request Process**
   - Create feature branch from `main`
   - Write tests for new functionality
   - Ensure all tests pass
   - Update documentation if needed
   - Request code review

## 📈 Monitoring and Logging

### Backend Logging
```python
# Use structured logging
import logging

logger = logging.getLogger(__name__)
logger.info("User created", extra={"user_id": user.id})
```

### Frontend Logging
```typescript
// Use console methods appropriately
console.error('API Error:', error);
console.warn('Deprecated feature used');
```

## 🔧 Troubleshooting

### Common Issues

**Database Connection Failed**
- Check PostgreSQL service is running
- Verify database credentials in `.env`
- Ensure database exists

**Frontend Build Errors**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version compatibility
- Verify environment variables

**Import Errors**
- Check Python path configuration
- Verify virtual environment activation
- Ensure all dependencies installed

### Getting Help

1. Check existing [GitHub Issues](https://github.com/max31337/salesoptimizer/issues)
2. Review documentation in `docs/` folder
3. Create new issue with detailed description
4. Join development discussions