# Deployment Guide

## 🎯 Deployment Overview

This guide covers deploying SalesOptimizer to production environments using Docker, cloud providers, and traditional hosting.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB minimum, SSD recommended
- **CPU**: 2 cores minimum, 4 cores recommended

### Required Software
- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)
- Nginx (for reverse proxy)

## 🐳 Docker Deployment (Recommended)

### 1. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: salesoptimizer-backend
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/salesoptimizer_db
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    networks:
      - salesoptimizer-network

  frontend:
    build:
      context: ./web
      dockerfile: Dockerfile.prod
    container_name: salesoptimizer-frontend
    restart: unless-stopped
    environment:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
      - NODE_ENV=production
    depends_on:
      - backend
    networks:
      - salesoptimizer-network

  db:
    image: postgres:15-alpine
    container_name: salesoptimizer-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=salesoptimizer_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - salesoptimizer-network

  redis:
    image: redis:7-alpine
    container_name: salesoptimizer-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - salesoptimizer-network

  nginx:
    image: nginx:alpine
    container_name: salesoptimizer-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend
      - frontend
    networks:
      - salesoptimizer-network

volumes:
  postgres_data:
  redis_data:

networks:
  salesoptimizer-network:
    driver: bridge
```

### 2. Production Environment File

Create `.env.prod`:

```bash
# Database
POSTGRES_PASSWORD=your_secure_postgres_password
DATABASE_URL=postgresql://postgres:your_secure_postgres_password@db:5432/salesoptimizer_db

# Redis
REDIS_PASSWORD=your_secure_redis_password
REDIS_URL=redis://:your_secure_redis_password@redis:6379

# Application
JWT_SECRET_KEY=your_super_secret_jwt_key_min_32_chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_email_password

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 3. Production Dockerfiles

**Backend Dockerfile.prod:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Frontend Dockerfile.prod:**

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

FROM node:18-alpine AS runner

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### 4. Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_session_timeout 1d;
        ssl_session_cache shared:MozTLS:10m;
        ssl_session_tickets off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000" always;

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Authentication rate limiting
        location /api/v1/auth/login {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 5. Deploy Commands

```bash
# Clone repository
git clone https://github.com/max31337/salesoptimizer.git
cd salesoptimizer

# Set up environment
cp .env.example .env.prod
# Edit .env.prod with production values

# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Run database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

## ☁️ Cloud Deployment

### AWS Deployment

**Using AWS ECS:**

1. **Create ECS Cluster**
```bash
aws ecs create-cluster --cluster-name salesoptimizer-cluster
```

2. **Create Task Definition**
```json
{
  "family": "salesoptimizer",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-registry/salesoptimizer-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/salesoptimizer"
        }
      ]
    }
  ]
}
```

3. **Create Service**
```bash
aws ecs create-service \
  --cluster salesoptimizer-cluster \
  --service-name salesoptimizer-service \
  --task-definition salesoptimizer:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Google Cloud Platform

**Using Cloud Run:**

```bash
# Build and push images
gcloud builds submit --tag gcr.io/PROJECT-ID/salesoptimizer-backend
gcloud builds submit --tag gcr.io/PROJECT-ID/salesoptimizer-frontend ./web

# Deploy backend
gcloud run deploy salesoptimizer-backend \
  --image gcr.io/PROJECT-ID/salesoptimizer-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy frontend
gcloud run deploy salesoptimizer-frontend \
  --image gcr.io/PROJECT-ID/salesoptimizer-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### DigitalOcean App Platform

Create `app.yaml`:

```yaml
name: salesoptimizer
services:
- name: backend
  source_dir: /
  github:
    repo: max31337/salesoptimizer
    branch: main
  run_command: uvicorn api.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
  envs:
  - key: DATABASE_URL
    value: ${db.DATABASE_URL}

- name: frontend
  source_dir: /web
  github:
    repo: max31337/salesoptimizer
    branch: main
  run_command: npm start
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 3000

databases:
- name: db
  engine: PG
  version: "15"
```

## 🔧 Manual Server Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm postgresql postgresql-contrib redis-server nginx certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash salesoptimizer
sudo usermod -aG sudo salesoptimizer
```

### 2. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE salesoptimizer_db;
CREATE USER salesoptimizer WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE salesoptimizer_db TO salesoptimizer;
\q
```

### 3. Application Deployment

```bash
# Switch to application user
sudo su - salesoptimizer

# Clone repository
git clone https://github.com/max31337/salesoptimizer.git
cd salesoptimizer

# Backend setup
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with production values

# Run migrations
alembic upgrade head

# Frontend setup
cd web
npm install
npm run build
cd ..
```

### 4. Systemd Services

**Backend Service** (`/etc/systemd/system/salesoptimizer-backend.service`):

```ini
[Unit]
Description=SalesOptimizer Backend
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=salesoptimizer
Group=salesoptimizer
WorkingDirectory=/home/salesoptimizer/salesoptimizer
Environment=PATH=/home/salesoptimizer/salesoptimizer/venv/bin
ExecStart=/home/salesoptimizer/salesoptimizer/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Frontend Service** (`/etc/systemd/system/salesoptimizer-frontend.service`):

```ini
[Unit]
Description=SalesOptimizer Frontend
After=network.target

[Service]
Type=exec
User=salesoptimizer
Group=salesoptimizer
WorkingDirectory=/home/salesoptimizer/salesoptimizer/web
Environment=NODE_ENV=production
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 5. Enable and Start Services

```bash
# Enable and start services
sudo systemctl enable salesoptimizer-backend salesoptimizer-frontend
sudo systemctl start salesoptimizer-backend salesoptimizer-frontend

# Check status
sudo systemctl status salesoptimizer-backend
sudo systemctl status salesoptimizer-frontend
```

## 🔒 SSL Certificate Setup

### Using Certbot (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal setup
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Logging

### 1. Log Configuration

Create `logging.conf`:

```ini
[loggers]
keys=root,uvicorn

[handlers]
keys=console,file

[formatters]
keys=default

[logger_root]
level=INFO
handlers=console,file

[logger_uvicorn]
level=INFO
handlers=console,file
qualname=uvicorn

[handler_console]
class=StreamHandler
level=INFO
formatter=default
args=(sys.stdout,)

[handler_file]
class=handlers.RotatingFileHandler
level=INFO
formatter=default
args=('/var/log/salesoptimizer/app.log', 'a', 10485760, 5)

[formatter_default]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### 2. Health Checks

Add health check endpoint in `api/main.py`:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
```

### 3. Basic Monitoring Script

Create `scripts/monitor.sh`:

```bash
#!/bin/bash

# Check if services are running
if ! systemctl is-active --quiet salesoptimizer-backend; then
    echo "Backend service is down! Restarting..."
    sudo systemctl restart salesoptimizer-backend
fi

if ! systemctl is-active --quiet salesoptimizer-frontend; then
    echo "Frontend service is down! Restarting..."
    sudo systemctl restart salesoptimizer-frontend
fi

# Check disk space
DISK_USAGE=$(df / | grep -vE '^Filesystem' | awk '{print $5}' | sed 's/%//g')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage is above 80%: ${DISK_USAGE}%"
fi
```

## 🔄 Backup and Recovery

### 1. Database Backup Script

Create `scripts/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="salesoptimizer_backup_$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -h localhost -U salesoptimizer salesoptimizer_db > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Remove backups older than 7 days
find $BACKUP_DIR -name "salesoptimizer_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

### 2. Automated Backup

Add to crontab:

```bash
# Daily backup at 2 AM
0 2 * * * /home/salesoptimizer/salesoptimizer/scripts/backup.sh
```

## 🚨 Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check logs
   sudo journalctl -u salesoptimizer-backend -f
   
   # Check configuration
   sudo systemctl status salesoptimizer-backend
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   psql -h localhost -U salesoptimizer -d salesoptimizer_db
   
   # Check PostgreSQL status
   sudo systemctl status postgresql
   ```

3. **Permission Denied**
   ```bash
   # Fix ownership
   sudo chown -R salesoptimizer:salesoptimizer /home/salesoptimizer/salesoptimizer
   
   # Fix permissions
   chmod +x /home/salesoptimizer/salesoptimizer/scripts/*.sh
   ```

### Performance Tuning

1. **Database Optimization**
   ```sql
   -- Add indexes for frequently queried columns
   CREATE INDEX idx_users_email ON users(email);
   CREATE INDEX idx_opportunities_status ON opportunities(status);
   ```

2. **Nginx Optimization**
   ```nginx
   # Add to nginx.conf
   gzip on;
   gzip_types text/plain text/css application/json application/javascript;
   
   # Enable caching
   location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

---

*For additional support, please refer to our [GitHub Issues](https://github.com/max31337/salesoptimizer/issues) or contact support@salesoptimizer.com*