# Quick Start Cheatsheet

## Installation (5 min)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY
```

### Frontend
```bash
cd ../frontend
npm install
```

## Running (2 terminals)

**Terminal 1 - Backend:**
```bash
cd backend && source venv/bin/activate
python -m app.main
# http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend && npm run dev
# http://localhost:5173
```

## First Use

1. **Enter Jira Credentials:**
   - URL: `https://company.atlassian.net`
   - Email: `your-email@company.com`
   - Token: [from Jira Settings → API Token]
   - Click **Test Connection**

2. **Generate Test Cases:**
   - Issue ID: `PROJ-123`
   - Template: `Functional` (default)
   - Cases: `5-20`
   - Click **Generate**

3. **Export:**
   - **Copy TSV** → Paste into Jira
   - **Export CSV** → Spreadsheet
   - **Export MD** → Documentation

## Troubleshooting

**"Cannot connect to Jira"**
→ Check URL format (no trailing slash), email, token

**"Backend not found"**
→ Ensure `uvicorn app.main:app --reload` is running on `:8000`

**"No module anthropic"**
→ `pip install -r requirements.txt`

**"npm dependencies missing"**
→ `npm install` in frontend/

## File Structure

```
Project_Test_Case_Generator/
├── backend/          ← FastAPI + Jira + Claude
├── frontend/         ← React + Vite + Tailwind
├── templates/        ← Test templates (YAML)
├── docker-compose.yml
├── README.md         ← Full documentation
├── SETUP.md          ← Installation guide
├── API_REFERENCE.md  ← API endpoints
└── ARCHITECTURE.md   ← Technical design
```

## Key Endpoints

- `GET /health` → Health check
- `POST /api/jira/test-connection` → Validate Jira
- `POST /api/jira/fetch-issue` → Get issue details
- `POST /api/testcases/generate` → Generate test cases
- `POST /api/testcases/export` → Export to CSV/MD/TSV
- `GET /api/templates` → List templates

## Environment

```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
ALLOWED_ORIGINS=http://localhost:5173
ENVIRONMENT=development
```

## Test Case Output

Each generated test case:
```json
{
  "id": "TC_001",
  "title": "User can login with valid credentials",
  "type": "Positive|Negative|Edge|Boundary|Security",
  "priority": "P0|P1|P2",
  "preconditions": "Setup steps",
  "steps": ["Step 1", "Step 2", ...],
  "test_data": "Data needed",
  "expected_result": "What should happen",
  "linked_jira_id": "PROJ-123"
}
```

## Templates

| Template | Use Case | Distribution |
|----------|----------|-------------|
| **Functional** | Happy path | 3P, 1N, 1E |
| **Regression** | Bug fixes | 2E, 2N, 1P |
| **Smoke** | Quick check | 5P |
| **Edge** | Boundary tests | 3E, 2B |
| **Security** | Auth & data | 5 Security |

## Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Generate cases | Enter (in Issue ID field) |
| Copy to clipboard | Copy TSV button |
| Edit test case | Edit button |
| Save changes | Save button |
| Cancel edits | X button |

## Common Workflows

### Workflow 1: Quick Test Generation
```
1. Load credentials
2. Enter issue ID
3. Click Generate
4. Copy TSV → Paste into Jira
```

### Workflow 2: Comprehensive Testing
```
1. Load credentials
2. Enter issue ID
3. Select "Regression" template
4. Generate 15 cases
5. Edit 2-3 cases for clarity
6. Export as CSV
7. Import into TestRail
```

### Workflow 3: Security Testing
```
1. Load credentials
2. Enter issue ID
3. Select "Security" template
4. Generate 10 cases
5. Export as Markdown
6. Review with security team
7. Share in documentation
```

## Tips & Tricks

💡 **Copy to Clipboard** - Fastest way to import into Jira/Xray  
💡 **Edit Test Cases** - Customize before export  
💡 **Save Markdown** - Good for documentation  
💡 **Multiple Issues** - Generate for each story, combine results  
💡 **Templates** - Try different templates for same issue  

## Performance

| Operation | Time |
|-----------|------|
| Test connection | ~500ms |
| Fetch issue | ~1-2s |
| Generate 5 cases | ~8-12s |
| Export to CSV | <100ms |

## Support

- **API Docs:** http://localhost:8000/docs (interactive)
- **README:** Full documentation
- **API_REFERENCE:** Endpoint details
- **ARCHITECTURE:** Technical deep-dive

## Version
v1.0.0 • May 2026
