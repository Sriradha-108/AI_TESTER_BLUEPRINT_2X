"""FastAPI main application"""
import logging
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn

from app.models.schemas import (
    JiraConnectionRequest,
    FetchIssueRequest,
    TestCaseGenerationRequest,
    ExportRequest,
    FetchIssueResponse,
    GeneratedTestCases,
    TestCase,
    ConnectionTestResponse,
    ErrorResponse,
)
from app.services.jira_service import JiraService
from app.services.llm_service import LLMService
from app.services.test_case_generator import ExportService, TestCaseValidator

# ============= Configuration =============

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Test Case Generator API",
    description="Generate test cases from Jira issues using Claude LLM",
    version="1.0.0",
)

# CORS middleware
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= Routes =============

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post(
    "/api/jira/test-connection",
    response_model=ConnectionTestResponse,
    tags=["Jira"],
    summary="Test Jira connection"
)
async def test_jira_connection(request: JiraConnectionRequest):
    """
    Test connection to Jira instance.
    
    Validates credentials and connectivity without storing any data.
    """
    try:
        with JiraService(request.jira_url, request.email, request.api_token) as jira:
            jira.test_connection()
        
        return ConnectionTestResponse(
            status="success",
            message="Successfully connected to Jira",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Jira connection test failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Connection failed: {str(e)}"
        )


@app.post(
    "/api/jira/fetch-issue",
    response_model=FetchIssueResponse,
    tags=["Jira"],
    summary="Fetch and parse Jira issue"
)
async def fetch_jira_issue(request: FetchIssueRequest):
    """
    Fetch and parse a Jira issue.
    
    Returns parsed issue data: summary, description, acceptance criteria, etc.
    """
    try:
        with JiraService(request.jira_url, request.email, request.api_token) as jira:
            # Fetch issue
            raw_issue = jira.fetch_issue(request.issue_id)
            
            # Parse issue
            parsed = jira.parse_issue(raw_issue)
        
        return FetchIssueResponse(
            issue=parsed,
            status="success"
        )
    
    except Exception as e:
        logger.error(f"Failed to fetch issue {request.issue_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post(
    "/api/testcases/generate",
    response_model=GeneratedTestCases,
    tags=["Test Cases"],
    summary="Generate test cases using LLM"
)
async def generate_test_cases(request: TestCaseGenerationRequest):
    """
    Generate test cases from user story using selected LLM provider (Claude or Groq).
    
    Takes parsed issue data and template selection, returns ≥5 test cases.
    """
    try:
        # Validate API key based on provider
        if request.llm_provider == "claude":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise Exception("ANTHROPIC_API_KEY not configured")
        elif request.llm_provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise Exception("GROQ_API_KEY not configured")
        else:
            raise Exception(f"Unsupported LLM provider: {request.llm_provider}")
        
        # Initialize LLM service with selected provider
        llm = LLMService(api_key, provider=request.llm_provider)
        
        # Generate test cases
        result = llm.generate_test_cases(
            issue_summary=request.issue_summary,
            issue_description=request.issue_description,
            acceptance_criteria=request.acceptance_criteria,
            template_name=request.template_name,
            num_cases=request.num_cases,
            linked_jira_id=request.linked_jira_id,
        )
        
        # Validate result
        is_valid, errors = TestCaseValidator.validate_test_cases(
            result["test_cases"],
            min_cases=5
        )
        
        if not is_valid:
            logger.warning(f"Validation errors: {errors}")
            # Log but don't fail - return the cases anyway
        
        # Convert to response model
        test_cases = [TestCase(**tc) for tc in result["test_cases"]]
        
        return GeneratedTestCases(
            test_cases=test_cases,
            count=len(test_cases),
            generation_time_ms=result["generation_time_ms"],
            template_used=result["template_used"],
            llm_model=result["llm_model"],
            llm_provider=result["llm_provider"],
            tokens_used=result.get("tokens_used"),
        )
    
    except Exception as e:
        logger.error(f"Test case generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Generation failed: {str(e)}"
        )


@app.post(
    "/api/testcases/export",
    tags=["Test Cases"],
    summary="Export test cases"
)
async def export_test_cases(request: ExportRequest):
    """
    Export test cases in requested format (CSV, TSV, or Markdown).
    
    Returns file download with appropriate content type.
    """
    try:
        export_format = request.format.lower()
        
        if export_format == "csv":
            content = ExportService.export_to_csv(request.test_cases)
            filename = "test_cases.csv"
            media_type = "text/csv"
        
        elif export_format == "tsv":
            content = ExportService.export_to_tsv(request.test_cases)
            filename = "test_cases.tsv"
            media_type = "text/tab-separated-values"
        
        elif export_format == "markdown":
            content = ExportService.export_to_markdown(request.test_cases)
            filename = "test_cases.md"
            media_type = "text/markdown"
        
        else:
            raise ValueError(f"Unsupported format: {export_format}")
        
        logger.info(f"Exported {len(request.test_cases)} test cases as {export_format}")
        
        return StreamingResponse(
            iter([content]),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Export failed: {str(e)}"
        )


@app.get("/api/templates", tags=["Templates"], summary="List available templates")
async def list_templates():
    """List available test case templates."""
    templates = [
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
        },
    ]
    return {"templates": templates}


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return ErrorResponse(
        status="error",
        error_code="INTERNAL_ERROR",
        message=str(exc),
        timestamp=datetime.now().isoformat()
    )


# ============= Main =============

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development"
    )
