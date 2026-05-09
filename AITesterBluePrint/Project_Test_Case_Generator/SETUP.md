# Installation & Setup Guide

## Option 1: Local Development Setup

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Verify installation
npm run lint  # Optional: check code
```

### Running Locally

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or: venv\Scripts\activate on Windows
python -m app.main

# Or use uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev

# Expected output shows:
# VITE v5.x.x ready in xxx ms
# ➜  Local:   http://localhost:5173/
```

Access the app:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Option 2: Docker Setup

### Prerequisites
- Docker installed and running
- Docker Compose v2+

### Build and Run

```bash
# Set API key before running
export ANTHROPIC_API_KEY=sk-ant-xxxxx

# Run development stack (with hot reload)
docker-compose up --build

# Or run background
docker-compose up -d --build
```

View logs:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

Stop services:
```bash
docker-compose down
```

Access:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

---

## Option 3: Production Deployment

### Using Docker Compose (Production)

```bash
# Copy and configure .env
cp .env.example .env

# Edit .env with production values
ENVIRONMENT=production
ANTHROPIC_API_KEY=<your-key>
ALLOWED_ORIGINS=https://yourdomain.com

# Build production images
docker-compose -f docker-compose.prod.yml build

# Run production stack
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Using Kubernetes (Advanced)

See `kubernetes/` directory for manifests.

---

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Use different port if needed
uvicorn app.main:app --port 8001
```

### Frontend can't reach backend
```bash
# Check if backend is running
curl http://localhost:8000/health

# Update proxy in frontend/vite.config.ts if needed
# Ensure CORS allows frontend origin
```

### No module named 'anthropic'
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### npm install fails
```bash
# Clear cache and retry
npm cache clean --force
npm install
```

---

## Verification Checklist

- [ ] Backend running without errors
- [ ] Frontend loads on http://localhost:5173
- [ ] Can view API docs at http://localhost:8000/docs
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] .env file configured with ANTHROPIC_API_KEY
- [ ] Can test Jira connection (after entering credentials)
