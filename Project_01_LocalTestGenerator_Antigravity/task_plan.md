# Task Plan

## Phases

### Phase 1: Initialization & Discovery
- [x] Create project files (`task_plan.md`, `findings.md`, `progress.md`, `context.md`)
- [x] Answer discovery questions
- [ ] Approve blueprint/task plan

### Phase 2: Design & Architecture (The Blueprint)
*Blueprint approved. Moving to execution.*

**Architecture Overview:**
- **Frontend:** React (TypeScript) providing a chat-like UI.
  - Sidebar for `History`.
  - Main display for `Generated Test Cases (Jira format)`.
  - Input field for `Jira Requirements`.
  - Settings Modal/Page for configurations (`Ollama API`, `LM Studio`, `Groq`, `OpenAI`, `Claude`, `Gemini`), with `Save button` and `Test Connection`.
- **Backend:** Node.js server (TypeScript) to handle API proxying, test case generation prompting, and interactions with various LLM providers.
- **Output Requirements:** Test cases must be generated for both API and Web applications, cover functional and non-functional tests, and strictly follow a Jira format.

**Design Steps:**
1. Setup a Monorepo/Workspace with Node.js backend (`/server`) and React frontend (`/client`).
2. Design the interface according to `LocalLLMTestcaseGenerator.png` layout.
3. Build flexible LLM configuration handlers in the backend.
4. Craft effective system prompts to consistently output Jira-formatted test cases based on requirements.

### Phase 3: Implementation
- [x] Setup Next.js/Vite React frontend and Node.js backend.
- [x] Implement Settings and Configuration UI + API connection testing.
- [x] Implement the Chat/Generator UI.
- [x] Integrate various local & cloud LLMs in the backend service.
- [x] Test the pipeline with sample Jira requirements.

## Goals
- Build a dual-purpose (Web/API) functional/non-functional test generator.
- Implement robust multi-LLM support (Local + Cloud).

## Checklists
- [x] User approves this Blueprint.
- [x] Initialize the React and Node.js codebases.
