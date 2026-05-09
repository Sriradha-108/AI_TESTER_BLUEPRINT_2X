# LLM Connection SOP

## Goal
Establish a reliable connection to a specified LLM Provider (Ollama, Groq, OpenAI) to generate the Test Plan.

## Inputs
Must match the `LLMConnectionPayload` and `LLMProcessingPayload` in `gemini.md`.
- `provider`: Explicit string (Ollama, Groq, etc.)
- `baseUrl`: Required for local providers (Ollama), optional for cloud.
- `apiKey`: Required for cloud (Groq, OpenAI).
- `model`: Target system model (e.g., llama3, mixtral-8x7b-32768).

## Tool Logic (`tools/llm_connector.py`)
1. Read credentials from `.env` or input payload.
2. Initialize HTTP client / SDK client (e.g., standard `requests` for generic REST, or specific Python SDK).
3. Formulate the prompt using the `test_plan_template.md` guidelines mixed with the raw ALM issue data.
4. Attempt completion generation.
5. Save raw completion payload to `.tmp/raw_llm_response.txt`.
6. Return `TestPlanResultPayload`.

## Edge Cases
- Provider offline (e.g., Ollama server down) -> Throw connection error.
- Invalid API Key -> Return 401 error.
- Context window exceeded -> Warn user and truncate payload.
