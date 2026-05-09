from llm_connector import generate_completion

def run_handshake():
    print("Initiating LLM Handshake Verification...\n")
    
    test_prompt = "Respond with exactly the word 'Poshkal'."
    print(f"Sending prompt: '{test_prompt}'...")
    
    result = generate_completion(test_prompt)
    
    if result["status"] == "success":
        print(f"[SUCCESS] Handshake SUCCESS!")
        print(f"Response: {result.get('text')}")
        print("Raw payload saved to .tmp/raw_llm_response.txt.")
    else:
        print(f"[FAILED] Handshake FAILED!")
        print(f"Reason: {result.get('message')}")
        print("\nPlease update the .env file with your valid LLM credentials.")

if __name__ == "__main__":
    run_handshake()
