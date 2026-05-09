import React, { useState, useEffect } from 'react'
import { Loader, AlertCircle } from 'lucide-react'
import { jiraAPI, testCasesAPI, Template } from '../api'
import { IssueData, TestCase } from '../types'

interface InputPanelProps {
  credentials: { jira_url: string; email: string; api_token: string } | null
  onIssueLoaded: (issue: IssueData) => void
  onTestCasesGenerated: (testCases: TestCase[]) => void
  onLoading: (loading: boolean) => void
  onError: (error: string) => void
}

export const InputPanel: React.FC<InputPanelProps> = ({
  credentials,
  onIssueLoaded,
  onTestCasesGenerated,
  onLoading,
  onError,
}) => {
  const [issueId, setIssueId] = useState('')
  const [selectedTemplate, setSelectedTemplate] = useState('functional')
  const [selectedProvider, setSelectedProvider] = useState<'claude' | 'groq'>('groq')
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(false)
  const [numCases, setNumCases] = useState(5)

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const response = await testCasesAPI.listTemplates()
        setTemplates(response.templates)
      } catch {
        console.error('Failed to load templates')
      }
    }
    fetchTemplates()
  }, [])

  const handleGenerate = async () => {
    if (!credentials) {
      onError('Please connect to Jira first')
      return
    }

    if (!issueId.trim()) {
      onError('Please enter a Jira issue ID')
      return
    }

    setLoading(true)
    onLoading(true)
    onError('')

    try {
      // Fetch issue
      const issueResponse = await jiraAPI.fetchIssue(credentials, issueId)
      const issue = issueResponse.issue
      onIssueLoaded(issue)

      // Generate test cases
      const generatedResponse = await testCasesAPI.generate(
        issue.summary,
        issue.description,
        issue.acceptance_criteria,
        selectedTemplate,
        numCases,
        issue.key,
        selectedProvider
      )

      console.log('✅ Test cases generated:', generatedResponse)
      console.log('📊 Test cases count:', generatedResponse.test_cases?.length)
      
      onTestCasesGenerated(generatedResponse.test_cases)
    } catch (err: any) {
      console.error('❌ Generation error:', err)
      console.error('Response data:', err.response?.data)
      console.error('Status:', err.response?.status)
      
      const errorMsg = err.response?.data?.detail || 
                       err.response?.data?.message ||
                       'Failed to generate test cases. Check the issue ID and API keys.'
      onError(errorMsg)
    } finally {
      setLoading(false)
      onLoading(false)
    }
  }

  const isDisabled = !credentials || loading

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <span className="text-green-600">🎯</span> Generate Test Cases
      </h2>

      <div className="space-y-4">
        {/* Issue ID */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Jira Issue ID <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            placeholder="e.g., PROJ-123"
            value={issueId}
            onChange={e => setIssueId(e.target.value.toUpperCase())}
            disabled={isDisabled}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-100"
            onKeyPress={e => e.key === 'Enter' && handleGenerate()}
          />
        </div>

        {/* Template Selection */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Test Template
          </label>
          <select
            value={selectedTemplate}
            onChange={e => setSelectedTemplate(e.target.value)}
            disabled={isDisabled}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-100"
          >
            {templates.map(template => (
              <option key={template.name} value={template.name}>
                {template.label}
              </option>
            ))}
          </select>
          {templates.find(t => t.name === selectedTemplate) && (
            <p className="text-xs text-gray-500 mt-1">
              {templates.find(t => t.name === selectedTemplate)?.description}
            </p>
          )}
        </div>

        {/* LLM Provider Selection */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            LLM Provider
          </label>
          <select
            value={selectedProvider}
            onChange={e => setSelectedProvider(e.target.value as 'claude' | 'groq')}
            disabled={isDisabled}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-100"
          >
            <option value="claude">Claude (Anthropic)</option>
            <option value="groq">Groq (Mixtral-8x7b)</option>
          </select>
          <p className="text-xs text-gray-500 mt-1">
            {selectedProvider === 'claude' 
              ? 'Using Claude 3.5 Sonnet for high-quality test cases'
              : 'Using Groq Mixtral 8x7b for fast test case generation'}
          </p>
        </div>

        {/* Number of Cases */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Number of Test Cases
          </label>
          <input
            type="range"
            min="5"
            max="20"
            value={numCases}
            onChange={e => setNumCases(Number(e.target.value))}
            disabled={isDisabled}
            className="w-full"
          />
          <div className="flex justify-between items-center mt-2">
            <span className="text-sm text-gray-600">5</span>
            <span className="text-lg font-bold text-green-600">{numCases} cases</span>
            <span className="text-sm text-gray-600">20</span>
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={isDisabled || !issueId.trim()}
          className="w-full py-3 px-4 bg-green-600 text-white rounded-lg font-bold hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition flex items-center justify-center gap-2 text-lg"
        >
          {loading ? (
            <>
              <Loader size={20} className="animate-spin" />
              Generating...
            </>
          ) : (
            '✨ Generate Test Cases'
          )}
        </button>

        {!credentials && (
          <div className="flex gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700">
            <AlertCircle size={20} className="flex-shrink-0 mt-0.5" />
            <span className="text-sm">Connect to Jira first to generate test cases</span>
          </div>
        )}
      </div>
    </div>
  )
}
