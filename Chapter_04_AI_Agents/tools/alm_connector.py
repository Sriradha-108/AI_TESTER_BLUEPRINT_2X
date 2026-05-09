import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_jira_issue(issue_key: str):
    """
    Fetches user story details from Jira using REST API v3.
    """
    jira_url = os.getenv("JIRA_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    if not all([jira_url, email, api_token]):
        return {"status": "error", "message": "Missing Jira credentials in .env"}

    # Jira REST API endpoint for getting an issue
    url = f"{jira_url.rstrip('/')}/rest/api/3/issue/{issue_key}"

    headers = {
        "Accept": "application/json"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            auth=HTTPBasicAuth(email, api_token)
        )
        
        if response.status_code == 200:
            data = response.json()
            # Extract summary and description (v3 formatting is ADF, simplified here)
            summary = data.get("fields", {}).get("summary", "")
            description = data.get("fields", {}).get("description", "")
            
            payload = {
                "status": "success",
                "issueKey": issue_key,
                "summary": summary,
                "description": description,
                "raw_response": data
            }
            
            # Save raw payload to .tmp as per SOP
            os.makedirs(".tmp", exist_ok=True)
            import json
            with open(f".tmp/raw_alm_payload_{issue_key}.json", "w") as f:
                json.dump(payload, f, indent=4)
                
            return payload
            
        elif response.status_code == 401:
            return {"status": "error", "message": "Unauthorized. Please check your Jira Email and API Token."}
        elif response.status_code == 404:
            return {"status": "error", "message": f"Issue '{issue_key}' not found."}
        else:
            return {"status": "error", "message": f"Jira API returned {response.status_code}: {response.text}"}
            
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Network Error: {str(e)}"}
