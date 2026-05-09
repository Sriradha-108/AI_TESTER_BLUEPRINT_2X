from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from tools.alm_connector import fetch_jira_issue
from tools.llm_connector import generate_completion
import os

app = FastAPI(title="Intelligent Test Planning Agent API")

class IssueFetchRequest(BaseModel):
    productName: str
    projectKey: str
    issueOrSprintId: str
    additionalContext: Optional[str] = ""

class JiraConfigPayload(BaseModel):
    url: str
    email: str
    apiToken: str

class LLMConfigPayload(BaseModel):
    provider: str
    apiKey: str
    model: str
    baseUrl: Optional[str] = None

@app.post("/api/connections/alm")
def update_alm_connection(config: JiraConfigPayload):
    """Dynamically set credentials for testing ALM."""
    os.environ["JIRA_URL"] = config.url
    os.environ["JIRA_EMAIL"] = config.email
    os.environ["JIRA_API_TOKEN"] = config.apiToken
    return {"status": "success", "message": "ALM configuration temporarily bound."}

@app.post("/api/connections/llm")
def update_llm_connection(config: LLMConfigPayload):
    """Dynamically set credentials for testing LLM."""
    os.environ["LLM_PROVIDER"] = config.provider
    os.environ["LLM_API_KEY"] = config.apiKey
    os.environ["LLM_MODEL"] = config.model
    if config.baseUrl:
        os.environ["LLM_BASE_URL"] = config.baseUrl
    return {"status": "success", "message": "LLM configuration temporarily bound."}

@app.post("/api/generate-plan")
def trigger_generation(req: IssueFetchRequest):
    """
    Phase 3: The Binding Router logic.
    1. Grabs ALM Issue.
    2. Loads Test Plan Template.
    3. Calls LLM with strict instructions.
    """
    # 1. Fetch Issue Data
    alm_result = fetch_jira_issue(req.issueOrSprintId)
    if alm_result["status"] != "success":
        raise HTTPException(status_code=400, detail=f"ALM Fetch Failed: {alm_result.get('message')}")

    # 2. Extract Data & Load Template
    summary = alm_result.get("summary", "")
    description = alm_result.get("description", "")
    
    try:
        with open("test_plan_template/test_plan_template.md", "r", encoding="utf-8") as f:
            template_content = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Could not locate test_plan_template.md")

    # 3. Construct Prompt
    llm_prompt = f"""
    You are an Expert QA Test Automation Engineer.
    
    Below is a User Story from Jira for the project '{req.projectKey}' ({req.productName}):
    [Summary]
    {summary}
    [Description]
    {description}
    
    Additional User Context:
    {req.additionalContext}
    
    Generate a comprehensive Test Plan adhering STRICTLY to the following Template. Output ONLY the completed markdown template.
    [TEMPLATE START]
    {template_content}
    [TEMPLATE END]
    """

    # 4. Generate Completion
    llm_result = generate_completion(llm_prompt)
    if llm_result["status"] != "success":
        raise HTTPException(status_code=500, detail=f"LLM Generation Failed: {llm_result.get('message')}")

    return {
        "status": "success",
        "jiraIssueId": req.issueOrSprintId,
        "markdownContent": llm_result.get("text")
    }

if __name__ == "__main__":
    import uvicorn
    # Start the local Dev Server for verification
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
