# Test Case Generator - Full-Stack Application

An AI-powered tool that connects to Jira, fetches user stories, and auto-generates structured test cases using Claude LLM. Output is copy-ready and exportable in multiple formats.

## 🎯 Features

✅ **Jira Integration** - Fetch user stories by issue ID using REST API v3  
✅ **Claude LLM** - Generate ≥5 structured test cases using Claude Sonnet 4.6  
✅ **Multiple Templates** - Functional, Regression, Smoke, Edge, and Security testing profiles  
✅ **Editable Table** - In-app editing and preview of generated test cases  
✅ **Multi-Format Export** - Copy to clipboard (TSV), CSV, and Markdown exports  
✅ **Responsive UI** - Mobile-friendly design with React + Tailwind CSS  
✅ **Secure Credentials** - Never persists API tokens (session-only)  
✅ **Stateless Architecture** - Single-dev tool with no database required  

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Header │ Connection │ Input │ Context │ Output Table │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/JSON
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                 Backend (FastAPI + Python)                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Jira Integration │ LLM Service │ Test Case Generator  │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
         │                          │
         ↓                          ↓
    [Jira REST API]         [Claude Sonnet API]
```

## 📋 Test Case Schema

Each generated test case follows this strict JSON structure:

```json
{
  "id": "TC_001",
  "title": "User can login with valid credentials",
  "type": "Positive",
  "priority": "P0",
  "preconditions": "Browser open at login page",
  "steps": [
    "Enter valid email",
    "Enter valid password",
    "Click Submit button"
  ],
  "test_data": "Email: user@test.com, Password: TestPass123",
  "expected_result": "User logged in successfully, redirected to dashboard",
  "linked_jira_id": "PROJ-123"
}
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** for backend
- **Node.js 18+** for frontend
- **Docker** (optional, for containerized deployment)
- **Jira Account** with API token
- **Anthropic API Key** (Claude access)

### 1. Clone and Setup

```bash
cd Project_Test_Case_Generator

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Frontend setup
cd ../frontend
npm install
```

### 2. Configure Environment

**Backend** - `backend/.env`:
```env
ENVIRONMENT=development
ANTHROPIC_API_KEY=sk-ant-xxxxx
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
SESSION_TIMEOUT_MINUTES=30
```

### 3. Run Locally

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python -m app.main
# or use: uvicorn app.main:app --reload
# Backend runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

### 4. Docker Compose (Alternative)

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
docker-compose up
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

## 📖 Usage Guide

### Step 1: Connect to Jira
1. Enter your Jira base URL (e.g., `https://company.atlassian.net`)
2. Enter your email and API token
3. Click **Test Connection** to verify credentials
4. ✅ Success message confirms connection

### Step 2: Fetch Issue
1. Enter Jira Issue ID (e.g., `PROJ-123`)
2. Select test template type
3. Adjust number of test cases (5-20)
4. Click **Generate Test Cases**

### Step 3: View & Edit (Optional)
- Review parsed issue in the **Context Card**
- Edit any test case using the **Edit** button
- Verify test case content before export

### Step 4: Export
- **Copy TSV** → Paste into Jira, Xray, or TestRail
- **Export CSV** → Download for spreadsheet tools
- **Export MD** → Download as markdown document

## 🔌 API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Health check |
| `POST` | `/api/jira/test-connection` | Validate Jira credentials |
| `POST` | `/api/jira/fetch-issue` | Fetch and parse Jira issue |
| `POST` | `/api/testcases/generate` | Generate test cases using LLM |
| `POST` | `/api/testcases/export` | Export test cases (CSV/TSV/MD) |
| `GET` | `/api/templates` | List available templates |

### Example: Generate Test Cases

```bash
curl -X POST http://localhost:8000/api/testcases/generate \
  -H "Content-Type: application/json" \
  -d '{
    "issue_summary": "User login feature",
    "issue_description": "Users should be able to login with email and password",
    "acceptance_criteria": "Given valid credentials, When user enters them, Then user is logged in",
    "template_name": "functional",
    "num_cases": 5,
    "linked_jira_id": "PROJ-123"
  }'
```

## 📝 Templates

### Functional (Default)
- **Purpose:** Validate happy paths and main business logic
- **Distribution:** 3 Positive, 1 Negative, 1 Edge
- **Use When:** Testing new features

### Regression
- **Purpose:** Test previously found bugs and edge cases
- **Distribution:** 2 Edge, 2 Negative, 1 Positive
- **Use When:** After bug fixes or maintenance

### Smoke
- **Purpose:** Critical path validation only
- **Distribution:** 5 Positive (happy paths only)
- **Use When:** Quick sanity checks before deployment

### Edge
- **Purpose:** Boundary conditions and unusual inputs
- **Distribution:** 3 Edge, 2 Boundary
- **Use When:** Testing robustness

### Security
- **Purpose:** Auth, authorization, and data protection
- **Distribution:** 5 Security-focused tests
- **Use When:** Security audit or penetration testing

## 🔐 Security Considerations

✅ **No Token Storage** - API tokens held in session only, never persisted to disk  
✅ **HTTPS Recommended** - Use TLS in production deployment  
✅ **CORS Configured** - Frontend origin restricted to known domains  
✅ **Rate Limiting** - Implement at reverse proxy level in production  
✅ **Error Handling** - Generic error messages, detailed logs server-side only  

## 📊 Logging & Monitoring

Backend logs include:
- Request/response timestamps
- Token usage (input/output/total)
- Generation latency (milliseconds)
- Error traces (for debugging)

View logs:
```bash
tail -f backend/app.log
```

## 🐳 Production Deployment

### Docker Build & Push

```bash
# Build images
docker build -t tcg-backend:1.0 ./backend
docker build -t tcg-frontend:1.0 -f frontend/Dockerfile.prod ./frontend

# Run with docker-compose in production
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables (Production)

```env
# backend/.env
ENVIRONMENT=production
LOG_LEVEL=INFO
ANTHROPIC_API_KEY=<secure-vault-key>
ALLOWED_ORIGINS=https://yourdomain.com
SESSION_TIMEOUT_MINUTES=60
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name tcg.company.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    location / {
        proxy_pass http://frontend:80;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
        rate_limit_zone $binary_remote_addr zone=api:10m rate=100r/m;
    }
}
```

## 🛠️ Development

### Project Structure

```
Project_Test_Case_Generator/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic models
│   │   ├── services/
│   │   │   ├── jira_service.py    # Jira REST API client
│   │   │   ├── llm_service.py     # Claude integration
│   │   │   └── test_case_generator.py  # Export utilities
│   │   └── main.py                # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── ConnectionPanel.tsx
│   │   │   ├── InputPanel.tsx
│   │   │   ├── ContextCard.tsx
│   │   │   └── TestCasesTable.tsx
│   │   ├── api.ts                 # HTTP client
│   │   ├── App.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── index.html
├── templates/
│   ├── functional.yaml
│   ├── regression.yaml
│   ├── smoke.yaml
│   ├── edge.yaml
│   └── security.yaml
├── docker-compose.yml
└── README.md
```

### Running Tests

Backend:
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest backend/ -v
```

Frontend:
```bash
# Run Vitest (configured in package.json)
npm run test
```

## 🐛 Troubleshooting

### Backend Issues

**"Jira connection failed"**
- Verify Jira URL format: `https://company.atlassian.net` (no trailing slash)
- Check email and API token are correct
- Ensure API token has required scopes

**"ANTHROPIC_API_KEY not found"**
- Set `ANTHROPIC_API_KEY` environment variable
- Verify key has correct prefix: `sk-ant-`

**"LLM generation failed"**
- Check API quota and rate limits
- Verify issue description is not empty
- Retry (Claude may have temporary issues)

### Frontend Issues

**"Cannot reach backend"**
- Ensure backend is running on `localhost:8000`
- Check CORS settings in `.env`
- Verify proxy configuration in `vite.config.ts`

**"Export downloads empty file"**
- Ensure test cases are generated successfully
- Check browser console for errors
- Try different export format

## 📈 Performance Metrics

Benchmarks on typical hardware:

| Operation | Time | Notes |
|-----------|------|-------|
| Jira connection test | ~500ms | Network dependent |
| Fetch issue | ~1-2s | Depends on Jira API |
| Generate 5 test cases | ~8-12s | Claude API latency |
| Export to CSV | <100ms | Local operation |

## 🎓 Example Workflow

```bash
# 1. User enters Jira credentials
URL: https://mycompany.atlassian.net
Email: user@mycompany.com
Token: {api_token}

# 2. User enters issue ID
Issue ID: PROJECT-456

# 3. System fetches from Jira
Fetched: Summary, Description, Acceptance Criteria

# 4. User selects template & generates
Template: Regression Testing
Cases: 10

# 5. Claude generates test cases
Generated 10 structured test cases (~10s)

# 6. User reviews in table
Edits 2 test cases for clarity

# 7. User exports
Exports as CSV for ImportTestRail.csv

# 8. QA team imports into TestRail
✅ Ready for execution
```

## 📚 References

- [Jira REST API v3 Docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference/getting-started)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React + TypeScript Docs](https://react.dev/learn/typescript)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ❓ FAQ

**Q: Can I use this with Jira Server (on-premise)?**  
A: Yes, but you'll need to configure proxy settings and authentication accordingly.

**Q: Does it support other LLM providers?**  
A: Currently Claude only, but the architecture supports adding GPT-4, Ollama, etc. See `backend/app/services/llm_service.py`.

**Q: How many test cases can I generate?**  
A: 5-20 per issue. For larger suites, generate multiple issues and combine.

**Q: Is the frontend responsive?**  
A: Yes, fully responsive for mobile, tablet, and desktop (≥1280px for optimal experience).

**Q: Can I customize the test case template?**  
A: Currently built-in templates only. Custom YAML templates can be added in `templates/` directory.

---

**Version:** 1.0.0  
**Last Updated:** May 2026  
**Author:** AI Test Generation Team
