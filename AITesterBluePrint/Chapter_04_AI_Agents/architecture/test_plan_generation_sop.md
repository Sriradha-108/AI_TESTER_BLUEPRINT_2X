# Test Plan Generation SOP

## Goal
To synthesize ALM (Jira/ADO) issue logic with the provided Test Plan Template using the configured LLM, resulting in a completed Test Plan.

## Inputs
- `IssueFetchRequest`: To gather targeted ALM requirements.
- `AdditionalContext`: User-provided textual instructions.
- `template_content`: The markdown read from `test_plan_template.md`.

## Tool Logic
1. Route data through `alm_connector.py` to extract features/user stories.
2. If `alm_connector` succeeds, load `test_plan_template.md`.
3. Concatenate instructions:
   ```text
   You are an Expert QA Test Automation Engineer.
   Below is a User Story from Jira:
   [Jira JSON Data]
   
   Additional User Context:
   [AdditionalContext]
   
   Generate a comprehensive Test Plan adhering STRICTLY to the following Template:
   [Template Content]
   ```
4. Pass concatenated prompt to `llm_connector.py`.
5. Write final output to `.tmp/generated_test_plan.md`.
6. Return success to the router layer.

## Edge Cases
- Empty Jira response -> Abort generation and inform user.
- Empty template -> Use fallback generic QA test plan template.
- LLM generation failure -> Retries x2 before hard stop.
