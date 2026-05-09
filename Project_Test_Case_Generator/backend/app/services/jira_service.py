"""Jira integration service using REST API v3"""
import httpx
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class JiraService:
    """Service for interacting with Jira API v3"""
    
    def __init__(self, jira_url: str, email: str, api_token: str):
        """
        Initialize Jira service with credentials.
        
        Args:
            jira_url: Base URL of Jira instance (e.g., https://company.atlassian.net)
            email: User email for authentication
            api_token: API token for authentication
        """
        self.jira_url = jira_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        
        # Create httpx client with auth
        self.client = httpx.Client(
            auth=(email, api_token),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30.0
        )
    
    def test_connection(self) -> bool:
        """
        Test connection to Jira instance.
        
        Returns:
            True if connection successful, raises exception otherwise
        """
        try:
            url = urljoin(self.jira_url, "/rest/api/3/myself")
            response = self.client.get(url)
            response.raise_for_status()
            logger.info(f"Jira connection test successful for {self.email}")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Jira connection test failed: {str(e)}")
            raise Exception(f"Jira connection failed: {str(e)}")
    
    def fetch_issue(self, issue_key: str) -> Dict:
        """
        Fetch issue details from Jira.
        
        Args:
            issue_key: Jira issue key (e.g., PROJ-123)
            
        Returns:
            Dictionary with issue details including custom fields
        """
        try:
            url = urljoin(self.jira_url, f"/rest/api/3/issue/{issue_key}")
            params = {
                "expand": "changelog,names,schema",
                "fields": "summary,description,issuetype,priority,created,updated,component"
            }
            response = self.client.get(url, params=params)
            response.raise_for_status()
            
            issue_data = response.json()
            logger.info(f"Successfully fetched issue {issue_key}")
            return issue_data
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise Exception(f"Issue {issue_key} not found")
            raise Exception(f"Failed to fetch issue: {str(e)}")
        except httpx.HTTPError as e:
            raise Exception(f"Jira API error: {str(e)}")
    
    def parse_issue(self, issue_data: Dict) -> Dict:
        """
        Parse raw Jira issue data into structured format.
        
        Args:
            issue_data: Raw issue data from Jira API
            
        Returns:
            Parsed issue with extracted fields
        """
        fields = issue_data.get("fields", {})
        
        # Extract description (may be in ADF format)
        description = self._extract_text_from_adf(fields.get("description"))
        
        # Extract acceptance criteria from custom field or description
        acceptance_criteria = self._extract_acceptance_criteria(
            description,
            fields.get("customfield_10000")  # Adjust custom field ID as needed
        )
        
        # Extract components
        components = [c.get("name", "") for c in fields.get("components", [])]
        
        parsed = {
            "id": issue_data.get("id"),
            "key": issue_data.get("key"),
            "summary": fields.get("summary", ""),
            "description": description,
            "acceptance_criteria": acceptance_criteria,
            "issue_type": fields.get("issuetype", {}).get("name", "Unknown"),
            "priority": fields.get("priority", {}).get("name", "Medium"),
            "linked_components": components,
            "created_at": fields.get("created", ""),
            "updated_at": fields.get("updated", ""),
        }
        
        logger.info(f"Parsed issue {issue_data.get('key')}")
        return parsed
    
    def _extract_text_from_adf(self, adf_content) -> str:
        """
        Extract plain text from Atlassian Document Format (ADF).
        
        Args:
            adf_content: ADF content (dict or string)
            
        Returns:
            Plain text string
        """
        if not adf_content:
            return ""
        
        if isinstance(adf_content, str):
            return adf_content
        
        if isinstance(adf_content, dict):
            # Extract text from ADF structure
            text_parts = []
            self._traverse_adf(adf_content, text_parts)
            return " ".join(text_parts).strip()
        
        return str(adf_content)
    
    def _traverse_adf(self, node, text_parts):
        """Recursively traverse ADF structure to extract text."""
        if isinstance(node, dict):
            if "text" in node:
                text_parts.append(node["text"])
            
            for key, value in node.items():
                if isinstance(value, (dict, list)):
                    self._traverse_adf(value, text_parts)
        
        elif isinstance(node, list):
            for item in node:
                self._traverse_adf(item, text_parts)
    
    def _extract_acceptance_criteria(self, description: str, custom_field=None) -> str:
        """
        Extract acceptance criteria from description or custom field.
        
        Args:
            description: Issue description text
            custom_field: Custom field value for acceptance criteria
            
        Returns:
            Acceptance criteria string
        """
        if custom_field:
            return self._extract_text_from_adf(custom_field)
        
        # Look for "Acceptance Criteria" section in description
        if "acceptance criteria" in description.lower():
            lines = description.split('\n')
            in_section = False
            criteria = []
            
            for line in lines:
                if "acceptance criteria" in line.lower():
                    in_section = True
                    continue
                if in_section:
                    if line.strip().startswith(('*', '-', '•', '1.', '2.', '3.')):
                        criteria.append(line.strip())
                    elif line.strip() and not any(c in line for c in [':', '*']):
                        break
            
            return "\n".join(criteria) if criteria else ""
        
        return ""
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
