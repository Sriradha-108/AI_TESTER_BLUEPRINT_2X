"""LLM integration service supporting Claude and Groq APIs"""
import os
import json
import logging
import time
from typing import Dict, List, Optional, Literal

try:
    from anthropic import Anthropic
except ImportError:
    raise ImportError("anthropic package not found. Install with: pip install anthropic")

try:
    from groq import Groq
except ImportError:
    raise ImportError("groq package not found. Install with: pip install groq")

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with LLM providers (Claude or Groq)"""
    
    def __init__(self, api_key: str, provider: Literal["claude", "groq"] = "claude"):
        """
        Initialize LLM service with API key and provider selection.
        
        Args:
            api_key: API key for the selected provider
            provider: "claude" (Anthropic) or "groq" (Groq)
        """
        self.provider = provider
        self.api_key = api_key
        
        if provider == "claude":
            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model
        elif provider == "groq":
            self.client = Groq(api_key=api_key)
            # Allow override via env var if needed (some accounts may have different model names)
            self.model = os.getenv("GROQ_MODEL", "mixtral-8x7b")
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def generate_test_cases(
        self,
        issue_summary: str,
        issue_description: str,
        acceptance_criteria: str,
        template_name: str = "functional",
        num_cases: int = 5,
        linked_jira_id: str = ""
    ) -> Dict:
        """
        Generate test cases using selected LLM provider.
        
        Args:
            issue_summary: Summary of the user story
            issue_description: Description of the user story
            acceptance_criteria: Acceptance criteria
            template_name: Template type (functional, regression, smoke, edge, security)
            num_cases: Number of test cases to generate
            linked_jira_id: Jira issue ID for linking
            
        Returns:
            Dictionary with generated test cases
        """
        start_time = time.time()
        
        system_prompt = self._build_system_prompt(template_name)
        user_prompt = self._build_user_prompt(
            issue_summary,
            issue_description,
            acceptance_criteria,
            num_cases,
            linked_jira_id
        )
        
        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                response_text = response.content[0].text
                tokens_used = {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                }
            
            elif self.provider == "groq":
                # Groq SDK expects system prompt as a message; remove unsupported 'system' kwarg
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=4000,
                    temperature=0.7,
                )
                # Groq response structure: choices[0].message.content
                response_text = response.choices[0].message.content
                tokens_used = {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            
            generation_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Extract and parse response
            test_cases = self._parse_test_cases(response_text, linked_jira_id)
            
            logger.info(
                f"[{self.provider.upper()}] Generated {len(test_cases)} test cases "
                f"({tokens_used['total_tokens']} tokens, {generation_time:.2f}ms)"
            )
            
            return {
                "test_cases": test_cases,
                "count": len(test_cases),
                "generation_time_ms": generation_time,
                "template_used": template_name,
                "llm_model": self.model,
                "llm_provider": self.provider,
                "tokens_used": tokens_used,
            }
            
        except Exception as e:
            logger.error(f"[{self.provider.upper()}] Failed to generate test cases: {str(e)}")
            raise Exception(f"LLM generation failed ({self.provider}): {str(e)}")
    
    def _build_system_prompt(self, template_name: str) -> str:
        """
        Build system prompt based on template type.
        
        Args:
            template_name: Template type
            
        Returns:
            System prompt string
        """
        base_prompt = """You are an expert QA engineer specializing in test case design.
Your task is to generate high-quality, structured test cases based on user stories.

Requirements:
1. Generate EXACTLY the requested number of test cases.
2. Return ONLY valid JSON array with no markdown code blocks (no triple backticks).
3. Each test case MUST conform to this exact schema:
{
    "id": "TC_001",
    "title": "descriptive test case title",
    "type": "Positive|Negative|Edge|Boundary|Security",
    "priority": "P0|P1|P2",
    "preconditions": "any setup required",
    "steps": ["step 1", "step 2", "step 3"],
    "test_data": "data needed for the test",
    "expected_result": "what should happen",
    "linked_jira_id": "JIRA-123"
}
4. Cover both happy path and edge cases.
5. Ensure test cases are independent and can run in any order."""

        template_specific = {
            "functional": """
Additional guidance for FUNCTIONAL tests:
- Focus on positive scenarios and main business logic.
- Ensure all happy paths are covered.
- Include at least one negative test per feature.""",
            "regression": """
Additional guidance for REGRESSION tests:
- Create tests for previously found bugs and their fixes.
- Include boundary value tests.
- Focus on areas likely to break during maintenance.""",
            "smoke": """
Additional guidance for SMOKE tests:
- Create only the most critical happy-path tests.
- Prioritize P0 tests that verify core functionality.
- Can be run quickly as a sanity check.""",
            "edge": """
Additional guidance for EDGE CASE tests:
- Focus on boundary conditions and unusual inputs.
- Include null, empty, and extreme value tests.
- Test error handling and recovery paths.""",
            "security": """
Additional guidance for SECURITY tests:
- Focus on authentication, authorization, and data protection.
- Include SQL injection, XSS, CSRF scenarios if applicable.
- Test access control and permission boundaries.""",
        }
        
        return base_prompt + template_specific.get(template_name, "")
    
    def _build_user_prompt(
        self,
        summary: str,
        description: str,
        criteria: str,
        num_cases: int,
        jira_id: str
    ) -> str:
        """Build user prompt with issue details."""
        prompt = f"""Generate exactly {num_cases} test cases for this user story:

SUMMARY:
{summary}

DESCRIPTION:
{description if description else "No additional description provided"}

ACCEPTANCE CRITERIA:
{criteria if criteria else "No specific acceptance criteria provided"}

JIRA ID: {jira_id}

Requirements:
1. Return a JSON array with exactly {num_cases} test case objects.
2. Assign unique IDs (TC_001, TC_002, etc.).
3. Each test case must have all required fields filled.
4. steps must be an array of strings, not a single string.
5. Return ONLY the JSON array, no markdown, no code blocks, no explanations.

Start with [ and end with ], with no additional text."""
        
        return prompt
    
    def _parse_test_cases(self, response_text: str, linked_jira_id: str) -> List[Dict]:
        """
        Parse LLM response and extract test cases.
        
        Args:
            response_text: Raw response from LLM
            linked_jira_id: Jira issue ID to link
            
        Returns:
            List of parsed test case dictionaries
        """
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Parse JSON
            test_cases = json.loads(response_text.strip())
            
            if not isinstance(test_cases, list):
                test_cases = [test_cases]
            
            # Normalize test cases
            normalized = []
            for i, tc in enumerate(test_cases, 1):
                normalized.append(self._normalize_test_case(tc, i, linked_jira_id))
            
            return normalized
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse test cases JSON: {str(e)}")
            logger.debug(f"Response text: {response_text[:200]}")
            raise Exception(f"Invalid JSON in LLM response: {str(e)}")
    
    def _normalize_test_case(self, tc: Dict, index: int, linked_jira_id: str) -> Dict:
        """
        Normalize and validate test case structure.
        
        Args:
            tc: Test case dictionary
            index: Index for ID generation
            linked_jira_id: Jira issue ID
            
        Returns:
            Normalized test case
        """
        # Ensure steps is a list
        steps = tc.get("steps", [])
        if isinstance(steps, str):
            # Split by newline or comma
            steps = [s.strip() for s in steps.split('\n') if s.strip()]
        
        return {
            "id": tc.get("id", f"TC_{index:03d}"),
            "title": tc.get("title", "Untitled Test Case"),
            "type": tc.get("type", "Positive"),
            "priority": tc.get("priority", "P1"),
            "preconditions": tc.get("preconditions", ""),
            "steps": steps or ["Step not defined"],
            "test_data": tc.get("test_data", ""),
            "expected_result": tc.get("expected_result", "Verify expected behavior"),
            "linked_jira_id": tc.get("linked_jira_id", linked_jira_id),
        }
