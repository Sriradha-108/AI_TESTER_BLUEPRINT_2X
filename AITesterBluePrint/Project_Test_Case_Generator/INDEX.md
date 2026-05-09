# 📚 Project Navigation & Getting Started

## 🎯 Start Here

New to this project? **Start with this order:**

1. **[README.md](README.md)** ← Begin here!
   - 🎬 5-min feature overview
   - 🚀 Quick start guide
   - 📊 Architecture diagram

2. **[SETUP.md](SETUP.md)** ← Then install
   - 🛠️ Option 1: Local dev
   - 🐳 Option 2: Docker
   - ✅ Verification checklist

3. **[CHEATSHEET.md](CHEATSHEET.md)** ← Use daily
   - ⌨️ Keyboard shortcuts
   - 🔑 Common workflows
   - 💡 Tips & tricks

4. **[API_REFERENCE.md](API_REFERENCE.md)** ← When building
   - 📡 All 6 endpoints documented
   - 💻 Request/response examples
   - 🧪 Testing code samples

5. **[ARCHITECTURE.md](ARCHITECTURE.md)** ← Deep dive
   - 🏗️ System design
   - 🔄 Data flows
   - 🔐 Security measures

---

## 📂 File Purpose Guide

### Documentation

| File | Size | Purpose | Read Time |
|------|------|---------|-----------|
| **README.md** | 9KB | Full feature guide + tutorial | 15 min |
| **SETUP.md** | 5KB | Installation & troubleshooting | 10 min |
| **CHEATSHEET.md** | 4KB | Quick reference | 5 min |
| **API_REFERENCE.md** | 12KB | API endpoints + examples | 20 min |
| **ARCHITECTURE.md** | 15KB | Technical design details | 25 min |
| **PROJECT_SUMMARY.md** | 8KB | File structure + stats | 10 min |
| **INDEX.md** | 3KB | This file | 5 min |

### Backend (Python + FastAPI)

```
backend/
├── app/main.py              ← FastAPI app (routes, middleware)
├── app/models/schemas.py    ← Pydantic types (request/response)
├── app/services/
│   ├── jira_service.py      ← Jira API client
│   ├── llm_service.py       ← Claude integration
│   └── test_case_generator.py ← Export utilities
├── requirements.txt         ← Dependencies list
├── Dockerfile               ← Docker build config
├── .env.example             ← Environment template
└── .gitignore               ← Git exclusions
```

**Start reading:** `backend/app/main.py` (routes) → `jira_service.py` → `llm_service.py`

### Frontend (React + TypeScript)

```
frontend/
├── src/
│   ├── App.tsx              ← Main component (state)
│   ├── api.ts               ← HTTP client
│   ├── types.ts             ← TypeScript interfaces
│   ├── index.css            ← Global styles
│   └── components/
│       ├── Header.tsx       ← Navigation
│       ├── ConnectionPanel.tsx  ← Jira auth
│       ├── InputPanel.tsx   ← Issue fetcher
│       ├── ContextCard.tsx  ← Issue display
│       └── TestCasesTable.tsx ← Main table
├── index.html               ← HTML template
├── package.json             ← Node dependencies
├── vite.config.ts           ← Build config
├── tailwind.config.js       ← CSS config
└── Dockerfile.prod          ← Production image
```

**Start reading:** `src/App.tsx` (main logic) → components in order

### Configuration

```
├── docker-compose.yml       ← Dev setup (hot reload)
├── docker-compose.prod.yml  ← Production (health checks)
├── templates/               ← Test templates (YAML)
│   ├── functional.yaml
│   ├── regression.yaml
│   ├── smoke.yaml
│   ├── edge.yaml
│   └── security.yaml
└── .env.example             ← Environment vars template
```

---

## 🚀 Common Workflows

### I want to...

#### 🎯 **Get started in 5 minutes**
1. [SETUP.md](SETUP.md) → Option 1 (Local)
2. Run backend + frontend
3. Open http://localhost:5173
✅ Done! Generate first test cases

#### 🐳 **Use Docker**
1. [SETUP.md](SETUP.md) → Option 2 (Docker)
2. `docker-compose up --build`
3. Open http://localhost:5173
✅ Done!

#### 📖 **Understand the API**
1. [API_REFERENCE.md](API_REFERENCE.md) - All endpoints
2. `http://localhost:8000/docs` - Interactive Swagger UI
3. Try example cURL commands
✅ Ready to integrate!

#### 🏗️ **Understand architecture**
1. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
2. Diagram showing data flow
3. Security considerations
4. Performance optimization tips
✅ Ready to scale!

#### 🔧 **Deploy to production**
1. [SETUP.md](SETUP.md) → Option 3 (Production)
2. Configure `.env` with prod values
3. `docker-compose -f docker-compose.prod.yml up`
4. Set up Nginx SSL
✅ Live!

#### 💻 **Extend the codebase**
1. [ARCHITECTURE.md](ARCHITECTURE.md) - Technical design
2. Browse `backend/app/services/` for service patterns
3. Browse `frontend/src/components/` for UI patterns
4. Add new features following conventions
✅ Contributing!

---

## 🎓 Learning Paths

### For Frontend Developers
1. [README.md](README.md#-dashboard-requirements) - UI requirements
2. `frontend/src/App.tsx` - State management
3. `frontend/src/components/` - Component structure
4. `frontend/src/api.ts` - API client pattern
5. [API_REFERENCE.md](API_REFERENCE.md) - Backend contracts

### For Backend Developers
1. [README.md](README.md#-backend-endpoints) - API spec
2. `backend/app/main.py` - Route definitions
3. `backend/app/services/` - Service implementations
4. [API_REFERENCE.md](API_REFERENCE.md) - Full endpoint docs
5. [ARCHITECTURE.md](ARCHITECTURE.md) - Data flow

### For DevOps / SRE
1. [SETUP.md](SETUP.md#option-3-production-deployment)
2. `docker-compose.prod.yml` - Production config
3. `frontend/nginx.conf` - Reverse proxy config
4. [ARCHITECTURE.md](ARCHITECTURE.md#deployment-checklist) - Checklist
5. `.env.example` - Environment variables

### For QA / Product Managers
1. [README.md](README.md#-usage-guide) - User guide
2. [CHEATSHEET.md](CHEATSHEET.md) - Quick reference
3. [API_REFERENCE.md](API_REFERENCE.md) - Test scenarios
4. Features → Templates → Output → Export workflows

---

## 📞 Quick Help

### Errors

| Error | Solution | Doc |
|-------|----------|-----|
| "Cannot connect to backend" | Ensure port 8000 free, backend running | [SETUP.md](SETUP.md#troubleshooting) |
| "Jira connection failed" | Check URL/email/token format | [README.md](README.md#step-1-connect-to-jira) |
| "No anthropic module" | `pip install -r requirements.txt` | [SETUP.md](SETUP.md) |
| "npm install fails" | `npm cache clean --force` | [SETUP.md](SETUP.md#npm-install-fails) |

### Questions

| Question | Answer | Doc |
|----------|--------|-----|
| How many test cases generated? | 5-20 (customizable) | [README.md](README.md#_dashboard-requirements) |
| Are credentials stored? | No, session-only | [README.md](README.md#-non-functional-requirements) |
| What export formats? | CSV, TSV, Markdown | [README.md](README.md#step-4-export) |
| How long to generate? | ~8-12 sec for 5 cases | [README.md](README.md#-performance-metrics) |
| Can I customize templates? | Yes, add YAML files to `templates/` | [ARCHITECTURE.md](ARCHITECTURE.md#future-enhancements) |

---

## 🔍 File Search Index

**Looking for something specific?**

### By Feature
- **Jira Integration** → `backend/app/services/jira_service.py`
- **LLM/Claude** → `backend/app/services/llm_service.py`
- **Export Logic** → `backend/app/services/test_case_generator.py`
- **API Routes** → `backend/app/main.py`
- **UI Layout** → `frontend/src/App.tsx`
- **Test Cases Table** → `frontend/src/components/TestCasesTable.tsx`
- **HTTP Client** → `frontend/src/api.ts`
- **CSS Styles** → `frontend/src/index.css`, `frontend/tailwind.config.js`

### By Technology
- **FastAPI** → `backend/app/main.py`, [API_REFERENCE.md](API_REFERENCE.md)
- **Pydantic** → `backend/app/models/schemas.py`
- **React** → `frontend/src/App.tsx`, `frontend/src/components/`
- **Docker** → `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile.prod`
- **TypeScript** → `frontend/src/types.ts`, all `.tsx` files

### By Purpose
- **Testing connection** → `backend/app/services/jira_service.py`, `ConnectionPanel.tsx`
- **Fetching issues** → `backend/app/services/jira_service.py`, `InputPanel.tsx`
- **Generating tests** → `backend/app/services/llm_service.py`
- **Exporting** → `backend/app/services/test_case_generator.py`, `TestCasesTable.tsx`

---

## 📊 Project Stats

- **Total Files:** 41
- **Total LOC:** ~5,000
- **Backend Services:** 3 (Jira, LLM, Export)
- **Frontend Components:** 5
- **API Endpoints:** 6
- **Templates:** 5
- **Documentation Pages:** 6
- **Deployment Options:** 3 (Local, Docker, Prod)

---

## ✅ Verification Checklist

Before using, verify:

- [ ] Backend running: `http://localhost:8000/health`
- [ ] Frontend loaded: `http://localhost:5173`
- [ ] API docs available: `http://localhost:8000/docs`
- [ ] .env configured with `ANTHROPIC_API_KEY`
- [ ] Can test Jira connection
- [ ] Can generate test cases

---

## 🎓 Learning Resources

### Python/FastAPI
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Async Python Guide](https://docs.python.org/3/library/asyncio.html)

### React/TypeScript
- [React Official Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

### Jira/API
- [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Jira Authentication](https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/)

### Claude/LLM
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference/getting-started)
- [Claude Prompting Guide](https://docs.anthropic.com/claude/docs/prompts)

### DevOps
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Guide](https://docs.docker.com/compose/)

---

## 🚀 Next Steps

1. **Read:** [README.md](README.md) (15 min)
2. **Install:** [SETUP.md](SETUP.md) (10 min)
3. **Try:** Generate first test cases! (5 min)
4. **Explore:** [CHEATSHEET.md](CHEATSHEET.md) (5 min)
5. **Reference:** Keep [API_REFERENCE.md](API_REFERENCE.md) handy

---

**Happy Testing! 🎉**

For issues or questions, refer to the [README troubleshooting section](README.md#-troubleshooting) or [SETUP.md issues guide](SETUP.md#troubleshooting).

---

**Last Updated:** May 7, 2026  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
