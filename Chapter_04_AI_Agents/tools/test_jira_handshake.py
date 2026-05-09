from alm_connector import fetch_jira_issue
import json

def run_handshake():
    print("Initiating Jira Handshake Verification...\n")
    # Using a typical demo issue ID structure like 'KAN-1' or 'VWOAPP-1'
    test_issue = "KAN-1"  
    print(f"Fetching Issue: {test_issue}...")
    
    result = fetch_jira_issue(test_issue)
    
    if result["status"] == "success":
        print(f"[SUCCESS] HandshakeSUCCESS!")
        print(f"Summary: {result.get('summary')}")
        print("Raw payload saved to .tmp folder.")
    else:
        print(f"[FAILED] Handshake FAILED!")
        print(f"Reason: {result.get('message')}")
        print("\nPlease update the .env file with your valid Jira credentials.")

if __name__ == "__main__":
    run_handshake()
