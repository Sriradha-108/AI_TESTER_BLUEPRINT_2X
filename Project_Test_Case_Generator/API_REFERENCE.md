# API Reference Guide

## Base URLs

- **Development:** `http://localhost:8000`
- **Production:** `https://tcg.company.com`

## Authentication

All endpoints are unauthenticated for this version (stateless, session-only).
Credentials (Jira tokens) are passed per-request and never stored.

## Response Format

All successful responses return JSON:
```json
{
  "status": "success|error",
  "data": {},
  "timestamp": "2024-05-07T10:30:00Z"
}
```

## Error Responses

HTTP Status Codes:
- `200` - Success
- `400` - Bad Request (validation error)
- `401` - Unauthorized (Jira auth failed)
- `500` - Internal Server Error

Error format:
```json
{
  "status": "error",
  "error_code": "JIRA_AUTH_FAILED",
  "message": "Invalid Jira credentials",
  "details": {},
  "timestamp": "2024-05-07T10:30:00Z"
}
```

---

## Endpoints

### 1. Health Check

**GET** `/health`

Check if API is running.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-05-07T10:30:00Z",
  "version": "1.0.0"
}
```

---

### 2. Test Jira Connection

**POST** `/api/jira/test-connection`

Validate Jira credentials without storing them.

**Request:**
```json
{
  "jira_url": "https://mycompany.atlassian.net",
  "email": "user@company.com",
  "api_token": "ATATT3xxxxxxxxxxxxx"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Successfully connected to Jira",
  "timestamp": "2024-05-07T10:30:00Z"
}
```

**Response (401):**
```json
{
  "error_code": "JIRA_AUTH_FAILED",
  "message": "Invalid email or API token"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/jira/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "jira_url": "https://mycompany.atlassian.net",
    "email": "user@company.com",
    "api_token": "ATATT3xxxxxxxxxxxxx"
  }'
```

---

### 3. Fetch Jira Issue

**POST** `/api/jira/fetch-issue`

Fetch and parse a Jira issue by ID.

**Request:**
```json
{
  "jira_url": "https://mycompany.atlassian.net",
  "email": "user@company.com",
  "api_token": "ATATT3xxxxxxxxxxxxx",
  "issue_id": "PROJ-123"
}
```

**Response (200):**
```json
{
  "issue": {
    "id": "10000",
    "key": "PROJ-123",
    "summary": "User should be able to login",
    "description": "As a user, I want to login with email/password...",
    "acceptance_criteria": "Given valid credentials\nWhen I enter them\nThen I am logged in",
    "issue_type": "Story",
    "priority": "High",
    "linked_components": ["Frontend", "API"],
    "created_at": "2024-04-01T10:00:00Z",
    "updated_at": "2024-05-01T15:30:00Z"
  },
  "status": "success"
}
```

**Response (404):**
```json
{
  "error_code": "ISSUE_NOT_FOUND",
  "message": "Issue PROJ-999 not found"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/jira/fetch-issue \
  -H "Content-Type: application/json" \
  -d '{
    "jira_url": "https://mycompany.atlassian.net",
    "email": "user@company.com",
    "api_token": "ATATT3xxxxxxxxxxxxx",
    "issue_id": "PROJ-123"
  }'
```

---

### 4. Generate Test Cases

**POST** `/api/testcases/generate`

Generate test cases using Claude LLM.

**Request:**
```json
{
  "issue_summary": "User login feature",
  "issue_description": "Users should be able to login with email and password",
  "acceptance_criteria": "Given valid credentials\nWhen user enters them\nThen user is logged in",
  "issue_type": "Story",
  "priority": "High",
  "template_name": "functional",
  "num_cases": 7,
  "linked_jira_id": "PROJ-123"
}
```

**Parameters:**

| Param | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| `issue_summary` | string | required | - | Issue title |
| `issue_description` | string | optional | - | Issue details |
| `acceptance_criteria` | string | optional | - | Acceptance criteria |
| `template_name` | string | "functional" | functional, regression, smoke, edge, security | Template type |
| `num_cases` | integer | 5 | 5-20 | Number of test cases |
| `linked_jira_id` | string | required | - | Jira issue ID |

**Response (200):**
```json
{
  "test_cases": [
    {
      "id": "TC_001",
      "title": "Valid user can login successfully",
      "type": "Positive",
      "priority": "P0",
      "preconditions": "Browser open at login page",
      "steps": [
        "Enter valid email in email field",
        "Enter valid password in password field",
        "Click Submit button"
      ],
      "test_data": "Email: user@test.com, Password: TestPass123!",
      "expected_result": "User is logged in, redirected to dashboard",
      "linked_jira_id": "PROJ-123"
    },
    {
      "id": "TC_002",
      "title": "Invalid password shows error",
      "type": "Negative",
      "priority": "P1",
      "preconditions": "Browser open at login page",
      "steps": [
        "Enter valid email",
        "Enter invalid password",
        "Click Submit"
      ],
      "test_data": "Email: user@test.com, Password: WrongPassword",
      "expected_result": "Error message displayed: 'Invalid credentials'",
      "linked_jira_id": "PROJ-123"
    }
  ],
  "count": 7,
  "generation_time_ms": 8523.45,
  "template_used": "functional",
  "llm_model": "claude-3-5-sonnet-20241022",
  "tokens_used": {
    "input_tokens": 445,
    "output_tokens": 1234,
    "total_tokens": 1679
  }
}
```

**Error (400):**
```json
{
  "error_code": "INVALID_REQUEST",
  "message": "num_cases must be between 5 and 20"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/testcases/generate \
  -H "Content-Type: application/json" \
  -d '{
    "issue_summary": "User login feature",
    "issue_description": "Users should be able to login",
    "acceptance_criteria": "Given valid credentials, when user enters them, then user is logged in",
    "template_name": "functional",
    "num_cases": 5,
    "linked_jira_id": "PROJ-123"
  }'
```

---

### 5. Export Test Cases

**POST** `/api/testcases/export`

Export generated test cases in various formats.

**Request:**
```json
{
  "test_cases": [
    {
      "id": "TC_001",
      "title": "Valid user can login",
      "type": "Positive",
      "priority": "P0",
      "preconditions": "Browser at login",
      "steps": ["Step 1", "Step 2"],
      "test_data": "user@test.com",
      "expected_result": "Logged in",
      "linked_jira_id": "PROJ-123"
    }
  ],
  "format": "csv",
  "include_linked_jira_id": true
}
```

**Parameters:**

| Param | Type | Options | Description |
|-------|------|---------|-------------|
| `test_cases` | array | - | Array of test case objects |
| `format` | string | csv, tsv, markdown | Export format |
| `include_linked_jira_id` | boolean | true/false | Include Jira ID in export |

**Response (200):**
```
ID,Title,Type,Priority,Preconditions,Steps,Test Data,Expected Result,Linked Jira ID
TC_001,Valid user can login,Positive,P0,Browser at login,"Step 1; Step 2",user@test.com,Logged in,PROJ-123
```

**Content-Type:** 
- CSV: `text/csv`
- TSV: `text/tab-separated-values`
- Markdown: `text/markdown`

**Headers:**
- `Content-Disposition: attachment; filename=test_cases_2024-05-07.csv`

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/testcases/export \
  -H "Content-Type: application/json" \
  -d '{
    "test_cases": [...],
    "format": "csv"
  }' > test_cases.csv
```

---

### 6. List Available Templates

**GET** `/api/templates`

Retrieve list of available test templates.

**Response (200):**
```json
{
  "templates": [
    {
      "name": "functional",
      "label": "Functional Testing",
      "description": "Test happy path and main business logic"
    },
    {
      "name": "regression",
      "label": "Regression Testing",
      "description": "Test for previously found bugs and edge cases"
    },
    {
      "name": "smoke",
      "label": "Smoke Testing",
      "description": "Critical path tests only"
    },
    {
      "name": "edge",
      "label": "Edge Case Testing",
      "description": "Boundary conditions and unusual inputs"
    },
    {
      "name": "security",
      "label": "Security Testing",
      "description": "Authentication, authorization, and data protection"
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/templates
```

---

## Rate Limiting

Currently not implemented per-request, but recommended for production:
- 100 requests per minute per IP
- 10 test case generation requests per minute per IP

---

## Timeouts

- API request timeout: 30 seconds
- LLM generation timeout: 60 seconds

---

## Testing Endpoints

### Using Postman

1. Import collection from `collections/tcg-api.postman_collection.json`
2. Set environment variables:
   - `base_url`: http://localhost:8000
   - `jira_url`: Your Jira URL
   - `email`: Your email
   - `api_token`: Your token
3. Run requests

### Using Python

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Test connection
response = requests.post(
    f"{BASE_URL}/api/jira/test-connection",
    json={
        "jira_url": "https://mycompany.atlassian.net",
        "email": "user@company.com",
        "api_token": "ATATT3xxxxxxxxxxxxx"
    }
)
print(response.json())

# Fetch issue
response = requests.post(
    f"{BASE_URL}/api/jira/fetch-issue",
    json={
        "jira_url": "https://mycompany.atlassian.net",
        "email": "user@company.com",
        "api_token": "ATATT3xxxxxxxxxxxxx",
        "issue_id": "PROJ-123"
    }
)
issue = response.json()["issue"]

# Generate test cases
response = requests.post(
    f"{BASE_URL}/api/testcases/generate",
    json={
        "issue_summary": issue["summary"],
        "issue_description": issue["description"],
        "acceptance_criteria": issue["acceptance_criteria"],
        "template_name": "functional",
        "num_cases": 5,
        "linked_jira_id": issue["key"]
    }
)
test_cases = response.json()["test_cases"]
print(f"Generated {len(test_cases)} test cases")
```

### Using JavaScript/TypeScript

```typescript
// See frontend/src/api.ts for complete client library
import { jiraAPI, testCasesAPI } from './api'

// Test connection
const connectionStatus = await jiraAPI.testConnection({
  jira_url: 'https://mycompany.atlassian.net',
  email: 'user@company.com',
  api_token: 'ATATT3xxxxxxxxxxxxx'
})

// Fetch issue
const { issue } = await jiraAPI.fetchIssue(
  { /* credentials */ },
  'PROJ-123'
)

// Generate test cases
const result = await testCasesAPI.generate(
  issue.summary,
  issue.description,
  issue.acceptance_criteria,
  'functional',
  5,
  issue.key
)
```

---

## Webhooks & Events

Not currently implemented. For future consideration:
- Issue updated → re-generate test cases
- Test cases exported → log event
- Generation failed → alert admin
