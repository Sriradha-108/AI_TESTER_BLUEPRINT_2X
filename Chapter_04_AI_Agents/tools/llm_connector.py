import os
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_completion(prompt_payload: str):
    """
    Sends generic completion requests to the chosen LLM Provider.
    """
    provider = os.getenv("LLM_PROVIDER", "").lower()
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")
    
    if provider == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an Expert QA Test Automation Engineer."},
                {"role": "user", "content": prompt_payload}
            ]
        }
    else:
        return {"status": "error", "message": f"Provider '{provider}' not strictly implemented yet in SOP."}

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            
            os.makedirs(".tmp", exist_ok=True)
            with open(".tmp/raw_llm_response.txt", "w", encoding="utf-8") as f:
                f.write(content)
                
            return {"status": "success", "text": content}
            
        elif response.status_code == 401:
            return {"status": "error", "message": "Unauthorized. Please check LLM API Key."}
        else:
            return {"status": "error", "message": f"LLM API returned {response.status_code}: {response.text}"}
            
    except Exception as e:
         return {"status": "error", "message": f"Network/Parsing Error: {str(e)}"}
