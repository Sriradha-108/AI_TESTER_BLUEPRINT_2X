# ALM Connection SOP

## Goal
Establish a deterministic connection to Atlassian Jira (or ADO/X-Ray) to fetch User Stories or Requirements based on an Issue ID/Sprint ID.

## Inputs
Must match the `IssueFetchRequest` schema in `gemini.md`.
- `productName` (e.g. App.vwo.com)
- `projectKey` (e.g. VWOAPP)
- `issueOrSprintId` (e.g. Sprint 15 or KAN-1)

## Tool Logic (`tools/alm_connector.py`)
1. Read `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` from `.env` or payload.
2. Execute a GET request to `<JIRA_URL>/rest/api/3/issue/<issueOrSprintId>` (or equivalent for ADO/XRay).
3. Extract `summary` and `description` fields.
4. Save raw result to `.tmp/raw_alm_payload.json`.
5. Return structured JSON payload for LLM consumption.

## Edge Cases
- Missing API Token -> Throw unauthorized error immediately.
- Issue ID not found -> Return 404 message cleanly.
- Network Timeout -> Retry once, then fail gracefully.
