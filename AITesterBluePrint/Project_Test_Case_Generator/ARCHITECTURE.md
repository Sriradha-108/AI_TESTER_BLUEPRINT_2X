# Architecture & Technical Design

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Browser                               │
│                    (React 18 + TypeScript)                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Header | Connection | Input | Context | Output Table        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  HTTP/JSON (Axios)                                                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ↓
        ┌──────────────────────────────────────────┐
        │      Nginx Reverse Proxy (Optional)      │
        │  (rate limiting, SSL, compression)      │
        └──────────────────────────────────────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                             │
│                    (Python 3.11 + async)                            │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Main Application (FastAPI)                                  │   │
│  │  ├── Routes (/health, /api/...)                             │   │
│  │  ├── CORS Middleware                                        │   │
│  │  └── Error Handlers                                         │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          │                                           │
│  ┌────────────────────────┼─────────────────────────────────┐       │
│  │                        │                                  │       │
│  ↓                        ↓                                  ↓       │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐         │
│  │ Jira Service   │  │ LLM Service    │  │ Export Service         │
│  │  (httpx)       │  │ (Anthropic)    │  │ (CSV/TSV/MD)  │         │
│  │                │  │                │  │               │         │
│  │ • Auth         │  │ • Claude API   │  │ • Formatting  │         │
│  │ • Fetch issue  │  │ • Prompting    │  │ • Validation  │         │
│  │ • Parse fields │  │ • Stream resp  │  │ • Conversion  │         │
│  │ • Extract text │  │ • Error handle │  │               │         │
│  └────────────────┘  └────────────────┘  └───────────────┘         │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Pydantic Models (Type Safety)                               │   │
│  │  • JiraConnectionRequest                                    │   │
│  │  • TestCase, GeneratedTestCases                             │   │
│  │  • IssueData, ErrorResponse                                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
         │                          │
         ↓                          ↓
    ┌─────────────┐         ┌─────────────────┐
    │  Jira REST  │         │ Anthropic API   │
    │  API v3     │         │  (Claude)       │
    └─────────────┘         └─────────────────┘
```

## Data Flow

### Test Case Generation Flow

```
User Input
  │
  ├─ Jira Config (URL, email, token)
  └─ Issue ID (e.g., PROJ-123)
         │
         ↓
 [1] POST /api/jira/fetch-issue
         │
         ├─ Authenticate with Jira
         ├─ Fetch issue via REST API v3
         ├─ Parse ADF to plain text
         └─ Extract acceptance criteria
         │
         ↓
 Parsed Issue Data
  ├─ summary
  ├─ description
  ├─ acceptance_criteria
  ├─ issue_type
  ├─ priority
  └─ linked_components
         │
         ↓ (User reviews context)
         │
 User selects template + num_cases
         │
         ↓
 [2] POST /api/testcases/generate
         │
         ├─ Build system prompt (template-specific)
         ├─ Build user prompt (issue details)
         ├─ Call Claude API (streaming)
         ├─ Parse JSON response
         ├─ Validate test cases
         ├─ Normalize structure
         └─ Log token usage + latency
         │
         ↓
 Generated Test Cases (≥5)
  ├─ TC_001: Positive
  ├─ TC_002: Negative
  ├─ TC_003: Edge
  └─ ...
         │
         ↓ (Frontend renders table)
         │
 User edits (optional) + selects export format
         │
         ↓
 [3] POST /api/testcases/export
         │
         ├─ Format test cases
         │  ├─ CSV: comma-separated
         │  ├─ TSV: tab-separated (for Jira)
         │  └─ Markdown: formatted document
         └─ Return as file download
         │
         ↓
 [Download] test_cases_YYYY-MM-DD.{csv|tsv|md}
```

## Component Interactions

```
┌──────────────────────────────────────────────────────────────┐
│                    Frontend Components                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Header                                                      │
│    ├─ Shows connection status                               │
│    └─ Displays app title/version                            │
│                                                              │
│  ConnectionPanel                                             │
│    ├─ Input: Jira URL, email, token                        │
│    ├─ Action: Test connection                               │
│    └─ Output: Connection status (success/error)             │
│           │                                                 │
│           └─→ triggers: onConnect()                         │
│                                                              │
│  InputPanel                                                  │
│    ├─ Input: Issue ID                                       │
│    ├─ Input: Template selection                             │
│    ├─ Input: Num cases (5-20)                               │
│    ├─ Action: Generate test cases                           │
│    └─ Output: Loading state, error message                  │
│           │                                                 │
│           └─→ API calls:                                    │
│               1. jiraAPI.fetchIssue()                       │
│               2. testCasesAPI.generate()                    │
│                                                              │
│  ContextCard                                                 │
│    ├─ Input: Parsed Jira issue                              │
│    ├─ Display: Summary, description, criteria               │
│    └─ Purpose: Verification before generation               │
│                                                              │
│  TestCasesTable                                              │
│    ├─ Input: Array of generated test cases                  │
│    ├─ Features:                                              │
│    │  ├─ View mode (readonly)                               │
│    │  ├─ Edit mode (editable)                               │
│    │  ├─ Copy to clipboard (TSV)                            │
│    │  └─ Export (CSV, MD)                                   │
│    └─ Output: Exported file or copied data                  │
│           │                                                 │
│           └─→ API call: testCasesAPI.export()               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Database & State Management

**Current Design: Stateless + Session Only**

- No persistent database (SQLite/Postgres)
- All data stored in-memory (session)
- API tokens held in browser session only
- Credentials NOT sent to backend storage
- State cleared on browser refresh

**State Flow:**
```
App State (React)
  ├─ credentials (session memory)
  ├─ selectedIssue (memory)
  ├─ testCases (memory)
  ├─ templates (fetched once)
  └─ UI state (loading, error)
        │
        ↓
  Lost on page refresh
```

For future persistence, add:
- SQLite local DB (dev/single-user)
- PostgreSQL (team-shared)
- Redis sessions (multi-instance)

## Security Considerations

### Credential Handling

```
Browser                Backend              External
  │                       │                    │
User enters Jira creds    │                    │
  └─→ Held in JS memory   │                    │
      (NO localStorage)   │                    │
         │                │                    │
         ├─ POST (HTTPS)──┤ /api/jira/...     │
         │                │                    │
         │         ┌────────────────┐         │
         │         │ Use credentials│         │
         │         │ in memory only │         │
         │         │ (never written)│         │
         │         └────────────────┘         │
         │                │                    │
         │                ├─────────────────→ │ Jira API
         │                │                    │ (auth headers)
         │                │                    │
         │                ├─────────────────→ │ Anthropic API
         │                │                    │ (API key only)
         │                │                    │
         │        ✓ Discard after use ✓       │
         │                │                    │
   [Auth flow safe]  [No persistence]  [No exposure]
```

### Network Security

- HTTPS/TLS in production (enforced)
- CORS validation (whitelist origins)
- CSRF tokens if session-based (future)
- Rate limiting at proxy level
- Input validation (Pydantic)

### Data Protection

✅ Jira tokens → memory only, never logged  
✅ API keys → env vars only, never exposed  
✅ Test cases → in-memory only  
✅ Errors → generic client-side, detailed logs server-side  

## Performance Optimization

### Frontend

- **Code Splitting:** Components lazy-loaded
- **API Caching:** Axios interceptor (optional)
- **UI Rendering:** React.memo, useMemo for expensive ops
- **Bundle Size:** Tree-shaking, minification
- **Asset Loading:** Vite fast refresh

### Backend

- **Async/Await:** Non-blocking I/O (httpx, FastAPI)
- **Connection Pooling:** httpx ClientSession reuse
- **Response Streaming:** Large file downloads
- **Pydantic Validation:** Fast schema validation
- **Logging Levels:** INFO (dev), ERROR (prod)

### Database (Future)

- Query indexing on `jira_issue_id`, `created_at`
- Connection pooling (SQLAlchemy)
- Read replicas for scaling

## Error Handling

### Backend Error Flow

```
Request → Validation
            │
   ┌────────┼────────┐
   │        │        │
 Error   Success   Error
   │        │        │
   └─ Return HTTP error code
   └─ Pydantic validation
   └─ Return generic message
   └─ Log detailed trace

┌─────────────────────────────────────────┐
│ Error Codes                             │
├─────────────────────────────────────────┤
│ JIRA_AUTH_FAILED    → 401               │
│ JIRA_NOT_FOUND      → 404               │
│ INVALID_REQUEST     → 400               │
│ LLM_TIMEOUT         → 504               │
│ INTERNAL_ERROR      → 500               │
└─────────────────────────────────────────┘
```

### Frontend Error Handling

```
API Call
  ├─ Success → Update state
  ├─ Error   → Show error toast
  │           ├─ 401: "Connection failed"
  │           ├─ 404: "Issue not found"
  │           └─ 500: "Server error"
  └─ Auto-dismiss after 5s
```

## Testing Strategy

### Backend

**Unit Tests** (pytest):
```
tests/
  ├─ test_jira_service.py
  ├─ test_llm_service.py
  └─ test_export_service.py
```

**Integration Tests**:
```
tests/
  └─ test_api_endpoints.py
      ├─ test_connection_flow
      ├─ test_generation_flow
      └─ test_export_formats
```

### Frontend

**Component Tests** (Vitest):
```
tests/
  ├─ components/
  │  ├─ Header.test.tsx
  │  ├─ ConnectionPanel.test.tsx
  │  └─ TestCasesTable.test.tsx
  └─ integration.test.tsx
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] HTTPS certificate valid
- [ ] Database migrations (if applicable)
- [ ] API rate limiting configured
- [ ] Logging aggregation set up
- [ ] Error tracking (Sentry) configured
- [ ] Monitoring/alerts configured
- [ ] Backups scheduled
- [ ] Security headers set
- [ ] Load balancer health checks

## Future Enhancements

**Phase 2:**
- [ ] User authentication (OAuth2)
- [ ] Test case persistence (PostgreSQL)
- [ ] Advanced filtering & search
- [ ] Test case versioning
- [ ] Integration with TestRail/Xray

**Phase 3:**
- [ ] Custom test templates upload
- [ ] Webhook for auto-generation
- [ ] Multi-language support
- [ ] API client library (Python/JS)
- [ ] CLI tool

**Phase 4:**
- [ ] AI model fine-tuning
- [ ] Batch test generation
- [ ] Test coverage analysis
- [ ] Metrics dashboard
- [ ] Team collaboration features
