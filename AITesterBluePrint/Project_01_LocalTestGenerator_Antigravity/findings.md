# Findings

## Research
- The application will generate both API and Web application test cases.
- Both functional and non-functional tests will be covered.
- Inputs are plain text Jira requirements via UI chat or copy-paste.
- Output format must strictly conform to a Jira ticket/issue format.
- Based on `design/LocalLLMTestcaseGenerator.png`, the UI requires:
  - A test case display window
  - A requirements input window 
  - A History sidebar
  - A Configuration panel allowing API key inputs and connection testing.

## Discoveries
- Required local and cloud LLM integrations include: Ollama API, LM Studio API, Groq API, OpenAI, Claude API, and Gemini API.
- Tech Stack: Node.js (TypeScript) for backend, React (TypeScript) for frontend.

## Constraints
- All generation logic must be formatted for Jira.
- The UI must align visually and functionally with the provided static design frame.
- Strict adherence to Protocol 0 which enforces explicit halts before starting implementations until blueprints are completely approved.
