export interface JiraCredentials {
  jira_url: string
  email: string
  api_token: string
}

export interface IssueData {
  id: string
  key: string
  summary: string
  description: string
  acceptance_criteria: string
  issue_type: string
  priority: string
  linked_components: string[]
  created_at: string
  updated_at: string
}

export interface TestCase {
  id: string
  title: string
  type: 'Positive' | 'Negative' | 'Edge' | 'Boundary' | 'Security'
  priority: 'P0' | 'P1' | 'P2'
  preconditions: string
  steps: string[]
  test_data: string
  expected_result: string
  linked_jira_id: string
}

export interface GeneratedTestCasesResponse {
  test_cases: TestCase[]
  count: number
  generation_time_ms: number
  template_used: string
  llm_model: string
  tokens_used?: {
    input_tokens: number
    output_tokens: number
    total_tokens: number
  }
}

export interface Template {
  name: string
  label: string
  description: string
}

export type Step = string

export interface AppState {
  jiraCredentials: JiraCredentials | null
  selectedIssue: IssueData | null
  generatedTestCases: TestCase[]
  selectedTemplate: string
  isLoading: boolean
  error: string | null
  templates: Template[]
}
