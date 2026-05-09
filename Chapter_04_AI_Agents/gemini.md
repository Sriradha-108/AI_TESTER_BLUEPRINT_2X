# Project Constitution

## Data Schemas
```json
{
  "ALMConnectionPayload": {
    "provider": "string (e.g., Jira, ADO, X-Ray)",
    "connectionName": "string",
    "url": "string",
    "email": "string",
    "apiToken": "string"
  },
  "LLMConnectionPayload": {
    "provider": "string (e.g., Ollama, Groq, OpenAI)",
    "baseUrl": "string",
    "apiKey": "string",
    "model": "string"
  },
  "IssueFetchRequest": {
    "productName": "string",
    "projectKey": "string",
    "issueOrSprintId": "string",
    "additionalContext": "string"
  },
  "LLMProcessingPayload": {
    "issueData": "object (Raw data from ALM)",
    "additionalContext": "string",
    "testPlanTemplate": "string (Markdown template)"
  },
  "TestPlanResultPayload": {
    "generatedTestPlanMarkdown": "string",
    "status": "string (Success / Error)",
    "errorMessage": "string"
  }
}
```

## Behavioral Rules
1. **Dynamic Connection**: Always test and validate ALM and LLM connections "on the fly" before attempting to fetch issues or generate plans.
2. **Strict Templating**: The LLM must adhere strictly to the structure provided in `test_plan_template.md`.
3. **Context Awareness**: The LLM must intelligently combine the structured ALM issue data with user-provided "Additional Context" to generate the final Test Plan.

## Architectural Invariants
- 3-Layer Build:
  - Layer 1: Architecture (`architecture/` - SOPs)
  - Layer 2: Navigation (Decision Making - routing between SOPs and Tools)
  - Layer 3: Tools (`tools/` - Python Scripts)
- All intermediate file operations must happen in `.tmp/`.
- No guessing at business logic.
- Updates to logic must trace to Architecture documentation prior to code changes.

## Maintenance Log
**Date**: April 22, 2026
**Version**: 1.0.0 (B.L.A.S.T Framework Complete)
**Deployments**: Dockerized backend (FastAPI) and frontend (React/Vite). Managed via `docker-compose.yml`.
**Triggers**: API Webhooks at `/api/generate-plan`. 
**Known Behaviors**:
- Jira Token authentication requires Basic Auth schema as defined in `alm_connector.py`.
- LLM failures gracefully bubble up 401s to the UI to notify the user.
