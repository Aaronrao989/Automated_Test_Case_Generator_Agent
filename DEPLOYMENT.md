# Production Deployment Guide

This guide covers deploying the Automated Test Case Generator Agent to production.

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│   Load Balancer / Reverse Proxy         │
│   (Nginx / HAProxy)                     │
└────────────┬────────────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
┌───▼──┐ ┌──▼───┐ ┌──▼───┐
│ Web1 │ │ Web2 │ │ Web3 │
└──────┘ └──────┘ └──────┘
    │        │        │
    └────────┼────────┘
             │
    ┌────────▼─────────┐
    │ Message Broker   │
    │ (Redis)          │
    └──────────────────┘
    │        │
┌───▼──┐ ┌──▼───┐
│Work1 │ │Work2 │
└──────┘ └──────┘
    │        │
    └────────┼────────┐
             │        │
    ┌────────▼──┐  ┌──▼────────┐
    │ Database  │  │ Cache     │
    └───────────┘  └───────────┘
```

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database backups configured
- [ ] SSL/TLS certificates ready
- [ ] CDN configured for static assets
- [ ] Monitoring and alerting set up
- [ ] Disaster recovery plan in place
- [ ] Documentation updated

## AWS Deployment (ECS)

### 1. Prepare Docker Images

```bash
# Build images
docker build -t test-gen-backend:latest ./backend
docker build -t test-gen-frontend:latest ./frontend

# Tag for ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag test-gen-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/test-gen-backend:latest
docker tag test-gen-frontend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/test-gen-frontend:latest

docker push <account>.dkr.ecr.us-east-1.amazonaws.com/test-gen-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/test-gen-frontend:latest
```

### 2. Create ECS Task Definitions

Create `ecs-task-backend.json`:

```json
{
  "family": "test-gen-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account>.dkr.ecr.us-east-1.amazonaws.com/test-gen-backend:latest",
      "portMappings": [{
        "containerPort": 8000,
        "protocol": "tcp"
      }],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://..."},
        {"name": "REDIS_URL", "value": "redis://..."}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/test-gen-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 3. Create ECS Service

```bash
aws ecs create-service \
  --cluster test-gen-cluster \
  --service-name test-gen-backend \
  --task-definition test-gen-backend \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
```

## Kubernetes Deployment

### 1. Create Docker Image Registry Secret

```bash
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password>
```

### 2. Deploy with Helm

Create `values.yaml`:

```yaml
backend:
  image: test-gen-backend:latest
  replicas: 3
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1024Mi"
      cpu: "500m"

frontend:
  image: test-gen-frontend:latest
  replicas: 2

database:
  host: postgres.default
  port: 5432

redis:
  host: redis.default
  port: 6379
```

Deploy:

```bash
helm install test-gen ./helm-chart -f values.yaml
```

## Environment Setup

### Production .env

```bash
# Backend
DATABASE_URL=postgresql://prod_user:secure_password@prod-db.rds.amazonaws.com/testgen
REDIS_URL=redis://prod-redis.elasticache.amazonaws.com:6379/0
OPENAI_API_KEY=sk-prod-key
OPENAI_MODEL=gpt-4
SECRET_KEY=generate_random_secret_key

# Frontend
NEXT_PUBLIC_API_URL=https://api.example.com

# Security
CORS_ORIGINS=https://example.com,https://www.example.com
ALLOWED_HOSTS=api.example.com

# Monitoring
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
LANGSMITH_API_KEY=ls-prod-key
```

## Database Setup

### 1. AWS RDS PostgreSQL

```bash
aws rds create-db-instance \
  --db-instance-identifier testgen-prod-db \
  --db-instance-class db.t3.small \
  --engine postgres \
  --master-username admin \
  --master-user-password <strong-password> \
  --allocated-storage 100 \
  --storage-type gp3 \
  --backup-retention-period 7 \
  --multi-az
```

### 2. Initialize Database

```bash
# Port forward or connect directly
psql -h testgen-prod-db.xxxxx.us-east-1.rds.amazonaws.com -U admin -d testgen < backend/migrations.sql

# Run Alembic migrations
alembic upgrade head
```

## Redis Setup

### AWS ElastiCache

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id testgen-prod-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --engine-version 7.0 \
  --num-cache-nodes 1
```

## SSL/TLS Certificate

### Using Let's Encrypt with Certbot

```bash
sudo certbot certonly --standalone -d api.example.com -d example.com
```

### Configure in Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    
    location / {
        proxy_pass http://backend:8000;
    }
}
```

## Monitoring & Logging

### CloudWatch Setup

```bash
# Create log group
aws logs create-log-group --log-group-name /testgen/prod

# Create metrics
aws cloudwatch put-metric-alarm \
  --alarm-name testgen-high-error-rate \
  --alarm-description "Alert if error rate > 5%" \
  --threshold 5
```

### Application Performance Monitoring

```python
# In app/main.py
from sentry_sdk import init as sentry_init
from opentelemetry import trace, metrics

sentry_init("https://xxxxx@sentry.io/xxxxx")

tracer = trace.get_tracer(__name__)
```

## CI/CD Pipeline

### GitHub Actions for Deployment

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster prod-cluster \
            --service test-gen-backend \
            --force-new-deployment
```

## Backup & Disaster Recovery

### Database Backup

```bash
# Automated backups with RDS
# Manual backup
aws rds create-db-snapshot \
  --db-instance-identifier testgen-prod-db \
  --db-snapshot-identifier testgen-backup-$(date +%Y%m%d)
```

### Restore from Backup

```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier testgen-restore \
  --db-snapshot-identifier testgen-backup-20231215
```

## Performance Optimization

### Database Connection Pooling

```python
# backend/app/db/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
)
```

### Caching Strategy

```python
from functools import lru_cache
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=128)
def get_cached_result(job_id):
    cached = cache.get(f"result:{job_id}")
    if cached:
        return json.loads(cached)
    # Fetch from DB
```

### CDN for Frontend

```html
<!-- Use CloudFront for static assets -->
<img src="https://d111111abcdef8.cloudfront.net/image.jpg" />
```

## Security Hardening

### Secrets Management

```bash
# Use AWS Secrets Manager
aws secretsmanager create-secret \
  --name testgen/prod/db-password \
  --secret-string "password"
```

### WAF Setup

```bash
aws wafv2 create-web-acl \
  --scope REGIONAL \
  --name testgen-waf \
  --default-action Block={}
```

### DDoS Protection

Enable AWS Shield and WAF for DDoS protection.

## Monitoring Dashboard

Create a monitoring dashboard to track:

- API Response Time
- Error Rate
- Database Connection Pool
- Cache Hit Rate
- Celery Task Queue Depth
- Disk Usage
- Memory Usage
- CPU Usage

## Health Checks

Setup health check endpoints:

```python
@app.get("/health")
def health_check():
    try:
        # Check database
        db.execute("SELECT 1")
        # Check Redis
        cache.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503
```

## Rollback Procedure

In case of deployment issues:

```bash
# Revert to previous version
aws ecs update-service \
  --cluster prod-cluster \
  --service test-gen-backend \
  --task-definition test-gen-backend:previous
```

## Support & Troubleshooting

- Monitor logs: `docker logs container-id`
- Check metrics: AWS CloudWatch
- Review performance: Application Insights
- Security scanning: AWS Inspector

---

For questions, check the README.md or open an issue in the repository.
