# Deployment & Operations Guide

## Pre-Deployment Checklist

- [ ] Both backend & frontend tested locally
- [ ] All environment variables configured
- [ ] ANTHROPIC_API_KEY obtained and verified
- [ ] Jira credentials tested
- [ ] SSL certificates ready (production)
- [ ] Domain/DNS configured
- [ ] Backups configured
- [ ] Monitoring/alerting configured

---

## Scenario 1: Localhost Development

**Setup Time:** 5 minutes  
**Hardware:** Any machine  
**Best For:** Development, testing, local use

### Steps

```bash
# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env - set ANTHROPIC_API_KEY

# 2. Frontend
cd ../frontend
npm install

# 3. Run (in 2 terminals)
# Terminal 1:
cd backend && source venv/bin/activate
python -m app.main

# Terminal 2:
cd frontend && npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Logs:**
- Backend: Console output
- Frontend: Browser console (F12)

---

## Scenario 2: Docker Compose (Development)

**Setup Time:** 10 minutes  
**Hardware:** Docker-enabled machine  
**Best For:** Team development, consistent environments

### Steps

```bash
# 1. Configure
cp .env.example .env
# Edit .env - set ANTHROPIC_API_KEY

# 2. Run
docker-compose up --build

# 3. Wait for startup (~20 sec)
```

**Access:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

**Useful Commands:**

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart backend
docker-compose restart frontend

# Stop gracefully
docker-compose down

# Rebuild images
docker-compose up --build
```

---

## Scenario 3: Docker Compose (Production)

**Setup Time:** 20 minutes  
**Hardware:** VPS/Cloud instance  
**Best For:** Team deployment, small-to-medium teams

### Prerequisites

- Docker & Docker Compose installed
- Domain with DNS pointing to server
- SSL certificate (Let's Encrypt recommended)
- 2GB+ RAM, 10GB disk

### Steps

```bash
# 1. Clone/download project
git clone <repo-url>
cd Project_Test_Case_Generator

# 2. Configure production environment
cp .env.example .env

# Edit .env:
ENVIRONMENT=production
ANTHROPIC_API_KEY=sk-ant-xxxxx
ALLOWED_ORIGINS=https://yourdomain.com

# 3. Configure SSL
mkdir -p certs
# Copy certificate to certs/cert.pem
# Copy key to certs/key.pem
# Or generate with: certbot certonly --standalone -d yourdomain.com

# 4. Update Nginx config
# Edit frontend/nginx.conf - set server_name to your domain

# 5. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 6. Verify
curl https://yourdomain.com/api/health
```

**Access:**
- Frontend: https://yourdomain.com
- API: https://yourdomain.com/api/

**Monitoring:**

```bash
# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Health check
curl https://yourdomain.com/api/health
```

**Maintenance:**

```bash
# Update images
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Backup
docker-compose -f docker-compose.prod.yml exec backend cp -r /app ./ /backups/

# Restart services
docker-compose -f docker-compose.prod.yml restart backend
```

---

## Scenario 4: Cloud Platforms (AWS ECS)

**Setup Time:** 30 minutes  
**Hardware:** AWS resources  
**Best For:** Enterprise, high availability, scaling

### Architecture

```
┌─────────────────────────────┐
│   AWS ECS Cluster           │
│  ┌───────────────────────┐  │
│  │  ALB                  │  │
│  │  (Application Load    │  │
│  │   Balancer)           │  │
│  └───────────────────────┘  │
│    │            │           │
│    ↓            ↓           │
│  ┌──────┐  ┌──────┐        │
│  │ Task │  │ Task │        │
│  │Backend│  │Frontend│      │
│  └──────┘  └──────┘        │
│                             │
└─────────────────────────────┘
       │         │
       ↓         ↓
    [CloudWatch] [RDS - optional]
    [S3 - logs]  [Secrets Manager]
```

### Steps (Using AWS CLI)

```bash
# 1. Push images to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag tcg-backend:1.0 <account-id>.dkr.ecr.us-east-1.amazonaws.com/tcg-backend:1.0
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/tcg-backend:1.0

# 2. Create ECS task definitions (JSON)
# - backend-task-def.json
# - frontend-task-def.json

# 3. Register task definitions
aws ecs register-task-definition --cli-input-json file://backend-task-def.json
aws ecs register-task-definition --cli-input-json file://frontend-task-def.json

# 4. Create ECS services
aws ecs create-service --cluster tcg --service-name backend --task-definition tcg-backend --desired-count 2
aws ecs create-service --cluster tcg --service-name frontend --task-definition tcg-frontend --desired-count 2

# 5. Configure ALB routing
# - HTTP(S) → frontendservice:80
# - HTTPS: /api/* → backendservice:8000
```

**Monitoring:**
- CloudWatch logs: `/aws/ecs/tcg`
- Metrics: CPU, memory, request count
- ALB target health: All targets healthy

---

## Scenario 5: Kubernetes (Advanced)

**Setup Time:** 1 hour (first time)  
**Hardware:** K8s cluster (3+ nodes)  
**Best For:** Enterprise, multi-region, auto-scaling

### Basic Manifests

**backend-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tcg-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tcg-backend
  template:
    metadata:
      labels:
        app: tcg-backend
    spec:
      containers:
      - name: backend
        image: tcg-backend:1.0
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: tcg-secrets
              key: anthropic-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
```

**Deployment:**
```bash
# 1. Create namespace
kubectl create namespace tcg

# 2. Create secrets
kubectl create secret generic tcg-secrets \
  --from-literal=anthropic-api-key=sk-ant-xxxxx \
  -n tcg

# 3. Apply manifests
kubectl apply -f backend-deployment.yaml -n tcg
kubectl apply -f frontend-deployment.yaml -n tcg
kubectl apply -f services.yaml -n tcg
kubectl apply -f ingress.yaml -n tcg

# 4. Check status
kubectl get pods -n tcg
kubectl get services -n tcg
kubectl get ingress -n tcg

# 5. Check logs
kubectl logs -f deployment/tcg-backend -n tcg
```

---

## Monitoring & Logging

### Setup Logging

**Option 1: Local files**
```bash
mkdir -p logs
# Backend logs to backend/logs/app.log
# View: tail -f backend/logs/app.log
```

**Option 2: ELK Stack (Elasticsearch)**
```yaml
# Configure in docker-compose
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
```

**Option 3: Cloud (CloudWatch, Datadog)**
```bash
# AWS CloudWatch
docker-compose logs --follow --timestamps

# Datadog
# Add Datadog agent sidecar to ECS task
```

### Setup Monitoring

**Health Checks:**
```bash
# Simple health check
curl http://localhost:8000/health

# Full status check
curl -X GET http://localhost:8000/health | jq .
```

**Metrics to Monitor:**
- API response time (target: <1s)
- LLM generation time (target: <15s)
- Error rate (target: <1%)
- Instance CPU (target: <70%)
- Instance memory (target: <80%)

---

## Backup & Recovery

### Backup Strategy (Stateless)

Since this app is stateless:
- **No database backup needed**
- **Backup configuration only:** `.env` files, custom templates
- **Backup templates:** Version control (Git)

```bash
# Backup configuration
tar -czf backup-$(date +%Y%m%d).tar.gz \
  .env \
  templates/

# Store securely (S3, Azure Blob, etc)
aws s3 cp backup-$(date +%Y%m%d).tar.gz s3://backups/tcg/
```

### Disaster Recovery

```bash
# 1. Restore configuration
tar -xzf backup-YYYYMMDD.tar.gz

# 2. Restart services
docker-compose -f docker-compose.prod.yml up -d

# 3. Verify health
curl https://yourdomain.com/api/health
```

---

## Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Check ports in use
lsof -i :8000
lsof -i :5173

# Rebuild images
docker-compose up --build --force-recreate
```

### API slow/timing out

```bash
# Check Jira API health
curl https://yourjira.atlassian.net/rest/api/3/myself

# Check Claude API (costs money)
# Verify ANTHROPIC_API_KEY is valid

# Check network
ping https://api.anthropic.com

# Scale backend
docker-compose up -d --scale backend=3
```

### SSL certificate issues

```bash
# Check certificate validity
openssl x509 -in certs/cert.pem -text -noout

# Renew with Let's Encrypt
certbot renew --force-renewal

# Restart Nginx
docker-compose restart nginx  # if using nginx container
```

---

## Cost Optimization (Cloud)

| Component | Monthly Cost (AWS) | Optimization |
|-----------|-------------------|--------------|
| ECS (2 tasks) | $30 | Reduce to 1 during off-hours |
| ALB | $16 | N/A |
| Data transfer | $5-20 | Cache where possible |
| CloudWatch logs | $10-30 | Increase retention limit |
| **Total** | **$61-96** | Consider spot instances |

---

## Production Checklist (Pre-Launch)

- [ ] SSL certificates installed and valid
- [ ] Database backups scheduled (if applicable)
- [ ] Logging aggregation running
- [ ] Monitoring/alerts configured
- [ ] Auto-scaling policies defined
- [ ] Disaster recovery plan documented
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Performance baselines established
- [ ] On-call support scheduled

---

## Operations Playbook

### Daily
- Check health endpoint: `curl /api/health`
- Review error logs: `docker-compose logs | grep ERROR`
- Verify uptime: Dashboard or monitoring tool

### Weekly
- Review metrics: CPU, memory, response times
- Check for security updates
- Backup configurations

### Monthly
- Full system health review
- Update dependencies
- Optimize costs
- Review security logs

### Quarterly
- Disaster recovery drill
- Security audit
- Performance optimization review
- Capacity planning

---

**Version:** 1.0.0  
**Last Updated:** May 7, 2026
