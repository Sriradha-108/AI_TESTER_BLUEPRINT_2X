from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

# ============= Request Models =============

class JiraConnectionRequest(BaseModel):
    """Jira connection credentials"""
    jira_url: str = Field(..., description="Base URL of Jira instance (e.g., https://company.atlassian.net)")
    email: str = Field(..., description="Jira user email")
    api_token: str = Field(..., description="Jira API token")


class FetchIssueRequest(BaseModel):
    """Request to fetch Jira issue"""
    jira_url: str
    email: str
    api_token: str
    issue_id: str = Field(..., description="Jira issue ID (e.g., PROJ-123)")


class TestCaseGenerationRequest(BaseModel):
    """Request to generate test cases"""
    issue_summary: str
    issue_description: str
    acceptance_criteria: str
    issue_type: str = Field(default="Story", description="Jira issue type")
    priority: str = Field(default="P1", description="Priority level")
    linked_components: Optional[List[str]] = None
    template_name: str = Field(default="functional", description="Template type")
    num_cases: int = Field(default=5, ge=5, le=20, description="Number of test cases to generate")
    linked_jira_id: str
    llm_provider: Literal["claude", "groq"] = Field(default="groq", description="LLM provider to use")


class ExportRequest(BaseModel):
    """Request to export test cases"""
    test_cases: List[dict]
    format: Literal["csv", "markdown", "tsv"] = "csv"
    include_linked_jira_id: bool = True


# ============= Response Models =============

class TestCase(BaseModel):
    """Individual test case"""
    id: str = Field(..., description="Unique test case ID (TC_001, TC_002, etc.)")
    title: str
    type: Literal["Positive", "Negative", "Edge", "Boundary", "Security"]
    priority: Literal["P0", "P1", "P2"]
    preconditions: str
    steps: List[str]
    test_data: str
    expected_result: str
    linked_jira_id: str


class GeneratedTestCases(BaseModel):
    """Response with generated test cases"""
    test_cases: List[TestCase]
    count: int
    generation_time_ms: float
    template_used: str
    llm_model: str
    llm_provider: str
    tokens_used: Optional[dict] = None


class JiraIssue(BaseModel):
    """Parsed Jira issue data"""
    id: str
    key: str
    summary: str
    description: str
    acceptance_criteria: str
    issue_type: str
    priority: str
    linked_components: List[str]
    created_at: str
    updated_at: str


class FetchIssueResponse(BaseModel):
    """Response from fetching Jira issue"""
    issue: JiraIssue
    status: str = "success"


class ConnectionTestResponse(BaseModel):
    """Response from connection test"""
    status: str = Field(..., description="success or error")
    message: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    error_code: str
    message: str
    details: Optional[dict] = None
    timestamp: str
