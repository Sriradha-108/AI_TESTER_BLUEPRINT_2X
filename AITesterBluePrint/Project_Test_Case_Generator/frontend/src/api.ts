import axios from 'axios'

const API_URL = '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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

export interface Template {
  name: string
  label: string
  description: string
}

// ============= Jira API =============

export const jiraAPI = {
  testConnection: async (credentials: JiraCredentials) => {
    const response = await api.post('/jira/test-connection', credentials)
    return response.data
  },

  fetchIssue: async (credentials: JiraCredentials, issueId: string) => {
    const response = await api.post('/jira/fetch-issue', {
      ...credentials,
      issue_id: issueId,
    })
    return response.data
  },
}

// ============= Test Cases API =============

export const testCasesAPI = {
  generate: async (
    summary: string,
    description: string,
    criteria: string,
    templateName: string,
    numCases: number,
    jiraId: string,
    llmProvider: 'claude' | 'groq' = 'groq'
  ) => {
    const response = await api.post('/testcases/generate', {
      issue_summary: summary,
      issue_description: description,
      acceptance_criteria: criteria,
      template_name: templateName,
      num_cases: numCases,
      linked_jira_id: jiraId,
      llm_provider: llmProvider,
    })
    return response.data
  },

  export: async (
    testCases: TestCase[],
    format: 'csv' | 'tsv' | 'markdown'
  ) => {
    const response = await api.post(
      '/testcases/export',
      {
        test_cases: testCases,
        format: format,
        include_linked_jira_id: true,
      },
      { responseType: 'blob' }
    )
    return response.data
  },

  listTemplates: async () => {
    const response = await api.get('/templates')
    return response.data
  },
}

export default api
